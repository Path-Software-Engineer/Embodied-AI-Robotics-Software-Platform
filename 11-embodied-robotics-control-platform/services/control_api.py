"""Local operator control API; all motion still crosses gRPC and ROS safety."""

from __future__ import annotations

import asyncio
import hmac
import json
import os
import re
import time
import uuid
from dataclasses import fields
from typing import Any, Literal

import asyncpg
import grpc
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from services.generated import robot_state_pb2, robot_state_pb2_grpc
from services.planning import (
    PlanRejected,
    TaskNode,
    TaskPlan,
    validate_for_execution,
    validate_graph,
)


class ModeCommand(BaseModel):
    requested_mode: Literal["Disarmed", "Manual", "Assisted", "AutonomousSim"]
    confirmed: bool
    reason: str = Field(min_length=5, max_length=300)


class PlanProposal(BaseModel):
    target_radians: float = Field(ge=-0.8, le=0.8)


class Approval(BaseModel):
    confirmed: bool
    reason: str = Field(min_length=5, max_length=300)


class SafetyOperation(BaseModel):
    confirmed: bool
    reason: str = Field(min_length=5, max_length=300)


def operator(authorization: str = Header(default=""), x_actor_id: str = Header(default="")) -> str:
    configured = os.environ.get("OPERATOR_TOKEN", "")
    candidate = authorization.removeprefix("Bearer ")
    if len(configured) < 32 or not hmac.compare_digest(candidate, configured):
        raise HTTPException(401, detail="operator token unavailable or invalid")
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,64}", x_actor_id):
        raise HTTPException(422, detail="valid X-Actor-Id required")
    return x_actor_id


def lease_header(x_control_lease: str = Header(default="")) -> str:
    if not re.fullmatch(r"[a-f0-9]{32}", x_control_lease):
        raise HTTPException(422, detail="valid X-Control-Lease required")
    return x_control_lease


def current_state(hub) -> dict[str, Any]:
    state = hub.latest
    if state is None:
        raise HTTPException(503, detail="fresh Gazebo world state unavailable")
    age_ns = time.time_ns() - state["observed_wall_time_ns"]
    if age_ns < 0 or age_ns > 1_000_000_000:
        raise HTTPException(503, detail="fresh Gazebo world state unavailable")
    return state


async def state_for_plan(hub, plan: TaskPlan) -> dict[str, Any]:
    for _ in range(10):
        state = current_state(hub)
        if state["run_id"] != plan.run_id or state["sequence"] >= plan.snapshot_sequence:
            return state
        await asyncio.sleep(0.05)
    raise HTTPException(503, detail="gateway has not synchronized the planner snapshot")


async def control_rpc(method: str, request, timeout: float = 3):
    target = os.environ.get("ROBOT_STATE_GRPC", "sim:50051")
    try:
        async with grpc.aio.insecure_channel(target) as channel:
            stub = robot_state_pb2_grpc.ControlServiceStub(channel)
            return await getattr(stub, method)(request, timeout=timeout)
    except grpc.aio.AioRpcError as error:
        if error.code() in {grpc.StatusCode.INVALID_ARGUMENT, grpc.StatusCode.FAILED_PRECONDITION}:
            raise HTTPException(409, detail=error.details()) from error
        raise HTTPException(503, detail="robot control bridge unavailable") from error


async def audit(
    *,
    run_id: str,
    actor: str,
    event_type: str,
    status: str,
    plan_id: str | None = None,
    correlation_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    try:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
        try:
            await connection.execute(
                "INSERT INTO control_events "
                "(run_id, plan_id, actor_id, correlation_id, event_type, status, payload) "
                "VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb)",
                run_id,
                plan_id,
                actor,
                correlation_id or str(uuid.uuid4()),
                event_type,
                status,
                json.dumps(payload or {}),
            )
        finally:
            await connection.close()
    except (asyncpg.PostgresError, OSError, TimeoutError) as error:
        raise HTTPException(503, detail="control audit database unavailable") from error


def as_plan(payload: dict[str, Any]) -> TaskPlan:
    keys = {field.name for field in fields(TaskPlan)}
    data = {key: value for key, value in payload.items() if key in keys and key != "nodes"}
    return TaskPlan(**data, nodes=tuple(TaskNode(**node) for node in payload["nodes"]))


async def plan_row(plan_id: str) -> dict[str, Any]:
    try:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
        try:
            row = await connection.fetchrow(
                "SELECT plan_id, run_id, actor_id, status, plan_payload "
                "FROM control_plans WHERE plan_id=$1",
                plan_id,
            )
        finally:
            await connection.close()
    except (asyncpg.PostgresError, OSError, TimeoutError) as error:
        raise HTTPException(503, detail="control database unavailable") from error
    if row is None:
        raise HTTPException(404, detail="plan not found")
    return {**dict(row), "plan_payload": json.loads(row["plan_payload"])}


async def authority(run_id: str, operation: str, actor: str = "", lease_id: str = "", **kw):
    request = robot_state_pb2.ControlRequest(
        operation=operation,
        run_id=run_id,
        lease_id=lease_id,
        actor_id=actor,
        requested_mode=kw.get("requested_mode", ""),
        ttl_seconds=kw.get("ttl_seconds", 0),
        confirmed=kw.get("confirmed", False),
        reason=kw.get("reason", ""),
    )
    return await control_rpc("Authority", request)


async def require_armed(run_id: str, actor: str, lease_id: str):
    response = await authority(run_id, "status", actor, lease_id)
    if not response.allowed or not response.lease_matches or response.lease_owner != actor:
        raise HTTPException(409, detail="exclusive control lease not active for this actor")
    if response.estop_latched or response.mode == "Disarmed":
        raise HTTPException(409, detail="supervisor is disarmed or emergency-stopped")
    return response


def create_router(hub) -> APIRouter:
    router = APIRouter(prefix="/api/v2", tags=["supervised simulation control"])

    @router.get("/control/status")
    async def status() -> dict[str, Any]:
        state = hub.latest
        if state is None:
            raise HTTPException(503, detail="simulation run unavailable")
        reply = await authority(state["run_id"], "status")
        return {
            "run_id": state["run_id"],
            "mode": reply.mode,
            "estop_latched": reply.estop_latched,
            "lease_owner": reply.lease_owner,
            "lease_expires_at_wall_ms": reply.expires_at_wall_ms,
            "state_sequence": state["sequence"],
            "state_stale": time.time_ns() - state["observed_wall_time_ns"] > 1_000_000_000,
            "source": "independent-ros-safety-supervisor",
        }

    @router.post("/control/leases")
    async def acquire(actor: str = Depends(operator)) -> dict[str, Any]:
        state = current_state(hub)
        await audit(run_id=state["run_id"], actor=actor, event_type="lease", status="requested")
        lease_id = uuid.uuid4().hex
        reply = await authority(state["run_id"], "acquire", actor, lease_id, ttl_seconds=30)
        await audit(
            run_id=state["run_id"],
            actor=actor,
            event_type="lease",
            status="acquired" if reply.allowed else "rejected",
            payload={"reason": reply.reason},
        )
        if not reply.allowed:
            raise HTTPException(409, detail=reply.reason)
        return {
            "run_id": state["run_id"],
            "lease_id": lease_id,
            "expires_at_wall_ms": reply.expires_at_wall_ms,
            "mode": reply.mode,
        }

    @router.post("/control/leases/heartbeat")
    async def heartbeat(
        actor: str = Depends(operator), lease_id: str = Depends(lease_header)
    ) -> dict[str, Any]:
        state = current_state(hub)
        reply = await authority(state["run_id"], "heartbeat", actor, lease_id, ttl_seconds=30)
        if not reply.allowed:
            raise HTTPException(409, detail=reply.reason)
        return {"expires_at_wall_ms": reply.expires_at_wall_ms, "mode": reply.mode}

    @router.post("/control/mode")
    async def mode(
        body: ModeCommand,
        actor: str = Depends(operator),
        lease_id: str = Depends(lease_header),
    ):
        state = current_state(hub)
        await audit(
            run_id=state["run_id"],
            actor=actor,
            event_type="mode",
            status="requested",
            payload={"requested_mode": body.requested_mode, "reason": body.reason},
        )
        reply = await authority(
            state["run_id"],
            "mode",
            actor,
            lease_id,
            requested_mode=body.requested_mode,
            confirmed=body.confirmed,
            reason=body.reason,
        )
        await audit(
            run_id=state["run_id"],
            actor=actor,
            event_type="mode",
            status="accepted" if reply.allowed else "rejected",
            payload={"mode": reply.mode, "reason": reply.reason},
        )
        if not reply.allowed:
            raise HTTPException(409, detail=reply.reason)
        return {"mode": reply.mode, "reason": reply.reason}

    @router.post("/control/{operation}")
    async def safety_operation(
        operation: Literal["stop", "estop", "reset_estop", "revoke"],
        body: SafetyOperation,
        actor: str = Depends(operator),
        lease_id: str = Header(default="", alias="X-Control-Lease"),
    ) -> dict[str, Any]:
        state = hub.latest
        if state is None:
            raise HTTPException(503, detail="simulation run unavailable")
        if not body.confirmed:
            raise HTTPException(422, detail="explicit confirmation required")
        if operation in {"stop", "revoke"}:
            lease_header(lease_id)
            await audit(
                run_id=state["run_id"],
                actor=actor,
                event_type=operation,
                status="requested",
                payload={"reason": body.reason},
            )
        reply = await authority(
            state["run_id"], operation, actor, lease_id, confirmed=True, reason=body.reason
        )
        try:
            await audit(
                run_id=state["run_id"],
                actor=actor,
                event_type=operation,
                status="accepted" if reply.allowed else "rejected",
                payload={"reason": reply.reason, "estop_latched": reply.estop_latched},
            )
            audit_persisted = True
        except HTTPException:
            audit_persisted = False
        if not reply.allowed:
            raise HTTPException(409, detail=reply.reason)
        return {
            "mode": reply.mode,
            "estop_latched": reply.estop_latched,
            "reason": reply.reason,
            "audit_persisted": audit_persisted,
        }

    @router.post("/plans")
    async def create_plan(body: PlanProposal, actor: str = Depends(operator)) -> dict[str, Any]:
        state = current_state(hub)
        plan_id = f"plan-{uuid.uuid4().hex}"
        reply = await control_rpc(
            "Plan",
            robot_state_pb2.PlanRequest(
                plan_id=plan_id, run_id=state["run_id"], target_radians=body.target_radians
            ),
        )
        payload = json.loads(reply.plan_json)
        plan = as_plan(payload)
        if plan.run_id != state["run_id"] or plan.robot_id != state["robot_id"]:
            raise HTTPException(409, detail="planner returned a different run or robot")
        try:
            validate_graph(plan.nodes)
        except PlanRejected as error:
            raise HTTPException(409, detail=str(error)) from error
        try:
            connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
            try:
                await connection.execute(
                    "INSERT INTO control_plans "
                    "(plan_id, run_id, actor_id, status, plan_payload) "
                    "VALUES ($1, $2, $3, 'proposed', $4::jsonb)",
                    plan_id,
                    state["run_id"],
                    actor,
                    json.dumps(payload),
                )
            finally:
                await connection.close()
        except (asyncpg.PostgresError, OSError, TimeoutError) as error:
            raise HTTPException(503, detail="control database unavailable") from error
        await audit(
            run_id=state["run_id"],
            actor=actor,
            plan_id=plan_id,
            event_type="plan",
            status="proposed",
            payload={"snapshot_hash": plan.snapshot_hash},
        )
        return {"status": "proposed", "plan": payload}

    @router.get("/plans")
    async def list_plans(limit: int = 20) -> dict[str, Any]:
        state = current_state(hub)
        if not 1 <= limit <= 100:
            raise HTTPException(422, detail="invalid limit")
        try:
            connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
            try:
                rows = await connection.fetch(
                    "SELECT plan_id, actor_id, status, plan_payload FROM control_plans "
                    "WHERE run_id=$1 ORDER BY created_at DESC LIMIT $2",
                    state["run_id"],
                    limit,
                )
            finally:
                await connection.close()
        except (asyncpg.PostgresError, OSError, TimeoutError) as error:
            raise HTTPException(503, detail="control database unavailable") from error
        return {
            "run_id": state["run_id"],
            "plans": [
                {**dict(row), "plan_payload": json.loads(row["plan_payload"])} for row in rows
            ],
        }

    @router.get("/plans/{plan_id}")
    async def get_plan(plan_id: str) -> dict[str, Any]:
        row = await plan_row(plan_id)
        return {"status": row["status"], "plan": row["plan_payload"], "actor_id": row["actor_id"]}

    @router.post("/plans/{plan_id}/approve")
    async def approve(
        plan_id: str,
        body: Approval,
        actor: str = Depends(operator),
        lease_id: str = Depends(lease_header),
    ) -> dict[str, Any]:
        row = await plan_row(plan_id)
        plan = as_plan(row["plan_payload"])
        state = await state_for_plan(hub, plan)
        if row["run_id"] != state["run_id"] or row["actor_id"] != actor:
            raise HTTPException(403, detail="plan belongs to another run or operator")
        if not body.confirmed:
            raise HTTPException(422, detail="explicit approval required")
        await require_armed(state["run_id"], actor, lease_id)
        try:
            validate_for_execution(plan, state, time.time_ns())
        except PlanRejected as error:
            raise HTTPException(409, detail=str(error)) from error
        try:
            connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
            try:
                changed = await connection.fetchrow(
                    "UPDATE control_plans SET status='approved', approved_at=now() "
                    "WHERE plan_id=$1 AND status='proposed' RETURNING plan_id",
                    plan_id,
                )
            finally:
                await connection.close()
        except (asyncpg.PostgresError, OSError, TimeoutError) as error:
            raise HTTPException(503, detail="control database unavailable") from error
        if changed is None:
            raise HTTPException(409, detail="plan already approved or terminal")
        await audit(
            run_id=state["run_id"],
            actor=actor,
            plan_id=plan_id,
            event_type="approval",
            status="approved",
            payload={"reason": body.reason},
        )
        return {"plan_id": plan_id, "status": "approved", "approved_by": actor}

    @router.post("/plans/{plan_id}/execute")
    async def execute(
        plan_id: str, actor: str = Depends(operator), lease_id: str = Depends(lease_header)
    ):
        row = await plan_row(plan_id)
        plan = as_plan(row["plan_payload"])
        state = await state_for_plan(hub, plan)
        if row["run_id"] != state["run_id"] or row["actor_id"] != actor:
            raise HTTPException(403, detail="plan belongs to another run or operator")
        await require_armed(state["run_id"], actor, lease_id)
        try:
            validate_for_execution(plan, state, time.time_ns())
        except PlanRejected as error:
            raise HTTPException(409, detail=str(error)) from error
        try:
            connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
            try:
                changed = await connection.fetchrow(
                    "UPDATE control_plans SET status='running' "
                    "WHERE plan_id=$1 AND status='approved' RETURNING plan_id",
                    plan_id,
                )
            finally:
                await connection.close()
        except (asyncpg.PostgresError, OSError, TimeoutError) as error:
            raise HTTPException(503, detail="control database unavailable") from error
        if changed is None:
            raise HTTPException(409, detail="plan was not approved or already executed")
        await audit(
            run_id=state["run_id"],
            actor=actor,
            plan_id=plan_id,
            correlation_id=plan_id,
            event_type="execution",
            status="running",
        )
        target = plan.nodes[0].target_radians
        try:
            outcome = await control_rpc(
                "Execute",
                robot_state_pb2.ExecuteRequest(
                    run_id=state["run_id"],
                    plan_id=plan_id,
                    lease_id=lease_id,
                    actor_id=actor,
                    target_radians=target,
                    correlation_id=plan_id,
                ),
                timeout=15,
            )
            terminal = (
                "completed" if outcome.succeeded else "cancelled" if outcome.canceled else "failed"
            )
            reason = outcome.reason
            final_radians = outcome.final_radians
        except HTTPException as error:
            terminal = "failed"
            reason = str(error.detail)
            final_radians = None
        connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
        try:
            await connection.execute(
                "UPDATE control_plans SET status=$2 WHERE plan_id=$1 AND status='running'",
                plan_id,
                terminal,
            )
        finally:
            await connection.close()
        await audit(
            run_id=state["run_id"],
            actor=actor,
            plan_id=plan_id,
            correlation_id=plan_id,
            event_type="execution",
            status=terminal,
            payload={"reason": reason, "final_radians": final_radians},
        )
        return {
            "plan_id": plan_id,
            "status": terminal,
            "reason": reason,
            "final_radians": final_radians,
            "correlation_id": plan_id,
        }

    @router.post("/plans/{plan_id}/cancel")
    async def cancel(
        plan_id: str, actor: str = Depends(operator), lease_id: str = Depends(lease_header)
    ):
        state = current_state(hub)
        row = await plan_row(plan_id)
        if row["run_id"] != state["run_id"] or row["actor_id"] != actor:
            raise HTTPException(403, detail="plan belongs to another run or operator")
        if row["status"] != "running":
            raise HTTPException(409, detail="plan is not running")
        cancel_request = robot_state_pb2.CancelRequest(
            run_id=state["run_id"], correlation_id=plan_id, lease_id=lease_id
        )
        for attempt in range(10):
            reply = await control_rpc("Cancel", cancel_request)
            if reply.accepted or attempt == 9:
                break
            await asyncio.sleep(0.05)
        await audit(
            run_id=state["run_id"],
            actor=actor,
            plan_id=plan_id,
            correlation_id=plan_id,
            event_type="cancel",
            status="requested" if reply.accepted else "rejected",
        )
        return {"accepted": reply.accepted, "reason": reply.reason}

    @router.get("/simulation-runs/{run_id}/control-events")
    async def control_events(run_id: str, limit: int = 100) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", run_id) or not 1 <= limit <= 500:
            raise HTTPException(422, detail="invalid run ID or limit")
        try:
            connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
            try:
                rows = await connection.fetch(
                    "SELECT observed_at, plan_id, actor_id, correlation_id, event_type, "
                    "status, payload FROM control_events WHERE run_id=$1 "
                    "ORDER BY observed_at, id LIMIT $2",
                    run_id,
                    limit,
                )
            finally:
                await connection.close()
        except (asyncpg.PostgresError, OSError, TimeoutError) as error:
            raise HTTPException(503, detail="control audit database unavailable") from error
        return {
            "run_id": run_id,
            "read_only": True,
            "events": [
                {
                    **dict(row),
                    "observed_at": row["observed_at"].isoformat(),
                    "payload": json.loads(row["payload"]),
                }
                for row in rows
            ],
        }

    return router
