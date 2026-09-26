"""Read-only simulation gateway and bounded WebSocket fan-out."""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
import grpc
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from services.architecture import android_evidence_contract, architecture_catalog
from services.control_api import create_router
from services.generated import robot_state_pb2, robot_state_pb2_grpc


def as_state(message: robot_state_pb2.RobotState) -> dict[str, Any]:
    if message.schema_version != "robot-state.v1" or not message.links:
        raise ValueError("invalid robot state contract")
    if message.sequence < 1 or not all(
        (message.run_id, message.robot_id, message.frame_id, message.correlation_id)
    ):
        raise ValueError("missing robot state provenance")
    return {
        "schema_version": message.schema_version,
        "run_id": message.run_id,
        "robot_id": message.robot_id,
        "frame_id": message.frame_id,
        "clock_domain": message.clock_domain,
        "simulation_time_ns": message.simulation_time_ns,
        "observed_wall_time_ns": message.observed_wall_time_ns,
        "sequence": message.sequence,
        "source": message.source,
        "correlation_id": message.correlation_id,
        "links": [
            {
                "link_name": link.link_name,
                "position_m": {
                    "x": link.position_m.x,
                    "y": link.position_m.y,
                    "z": link.position_m.z,
                },
                "orientation": {
                    "x": link.orientation.x,
                    "y": link.orientation.y,
                    "z": link.orientation.z,
                    "w": link.orientation.w,
                },
            }
            for link in message.links
        ],
    }


class StateHub:
    def __init__(self) -> None:
        self.latest: dict[str, Any] | None = None
        self.clients: set[asyncio.Queue[dict[str, Any]]] = set()
        self.write_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
        self.dropped_write_samples = 0
        self.database_ready = False
        self.loop_events: list[dict[str, Any]] = []
        self.loop_clients: set[asyncio.Queue[dict[str, Any]]] = set()
        self.loop_write_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)

    def publish(self, state: dict[str, Any]) -> None:
        previous = self.latest
        if previous is not None and state["run_id"] == previous["run_id"]:
            if state["sequence"] <= previous["sequence"]:
                raise ValueError("duplicate or out-of-order state")
        self.latest = state
        for queue in tuple(self.clients):
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(state)
        if self.write_queue.full():
            self.write_queue.get_nowait()
            self.dropped_write_samples += 1
        self.write_queue.put_nowait(state)

    def publish_loop(self, event: dict[str, Any]) -> None:
        self.loop_events.append(event)
        if len(self.loop_events) > 256:
            self.loop_events.pop(0)
        for queue in tuple(self.loop_clients):
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(event)
        if self.loop_write_queue.full():
            self.loop_write_queue.get_nowait()
        self.loop_write_queue.put_nowait(event)


hub = StateHub()


def as_loop_event(message: robot_state_pb2.LoopEvent) -> dict[str, Any]:
    if message.schema_version != "embodied-loop-event.v1":
        raise ValueError("invalid loop event version")
    if message.clock_domain != "gazebo_sim" or message.simulation_time_ns < 0:
        raise ValueError("invalid loop event clock")
    stages = {"perception", "state", "memory", "intent", "safety", "action", "feedback"}
    if message.stage not in stages:
        raise ValueError("unknown loop stage")
    if not all((message.run_id, message.robot_id, message.correlation_id, message.status)):
        raise ValueError("missing loop event identity")
    return {
        "schema_version": message.schema_version,
        "run_id": message.run_id,
        "robot_id": message.robot_id,
        "correlation_id": message.correlation_id,
        "clock_domain": message.clock_domain,
        "simulation_time_ns": message.simulation_time_ns,
        "stage": message.stage,
        "status": message.status,
        "event_sequence": message.event_sequence,
        "observed_wall_time_ns": message.observed_wall_time_ns,
        "observed_joint_radians": message.observed_joint_radians,
        "target_joint_radians": message.target_joint_radians,
        "detail": message.detail,
    }


async def consume_ros_state() -> None:
    target = os.environ.get("ROBOT_STATE_GRPC", "sim:50051")
    while True:
        try:
            async with grpc.aio.insecure_channel(target) as channel:
                stub = robot_state_pb2_grpc.RobotStateServiceStub(channel)
                async for message in stub.Watch(robot_state_pb2.Empty()):
                    hub.publish(as_state(message))
        except (grpc.aio.AioRpcError, OSError, ValueError) as error:
            print(f"robot state stream unavailable: {error}", flush=True)
            await asyncio.sleep(1)


async def consume_ros_loop() -> None:
    target = os.environ.get("ROBOT_STATE_GRPC", "sim:50051")
    while True:
        try:
            async with grpc.aio.insecure_channel(target) as channel:
                stub = robot_state_pb2_grpc.RobotStateServiceStub(channel)
                async for message in stub.WatchLoop(robot_state_pb2.Empty()):
                    hub.publish_loop(as_loop_event(message))
        except (grpc.aio.AioRpcError, OSError, ValueError) as error:
            print(f"robot loop stream unavailable: {error}", flush=True)
            await asyncio.sleep(1)


async def persist_state() -> None:
    database_url = os.environ["DATABASE_URL"]
    connection: asyncpg.Connection | None = None
    pending: dict[str, Any] | None = None
    while True:
        try:
            if connection is None:
                connection = await asyncpg.connect(database_url, timeout=5)
                hub.database_ready = True
            if pending is None:
                pending = await hub.write_queue.get()
            await connection.execute(
                """
                INSERT INTO robot_state_samples
                  (observed_at, run_id, robot_id, sequence, simulation_time_ns,
                   frame_id, correlation_id, payload)
                VALUES (to_timestamp($1::double precision / 1000000000.0),
                        $2, $3, $4, $5, $6, $7, $8::jsonb)
                ON CONFLICT DO NOTHING
                """,
                pending["observed_wall_time_ns"],
                pending["run_id"],
                pending["robot_id"],
                pending["sequence"],
                pending["simulation_time_ns"],
                pending["frame_id"],
                pending["correlation_id"],
                json.dumps(pending),
            )
            pending = None
        except (asyncpg.PostgresError, OSError, TimeoutError) as error:
            hub.database_ready = False
            print(f"telemetry write unavailable: {error}", flush=True)
            if connection is not None:
                with contextlib.suppress(Exception):
                    await connection.close()
            connection = None
            await asyncio.sleep(1)


async def persist_loop_events() -> None:
    connection: asyncpg.Connection | None = None
    pending: dict[str, Any] | None = None
    while True:
        try:
            if connection is None:
                connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
            if pending is None:
                pending = await hub.loop_write_queue.get()
            await connection.execute(
                """INSERT INTO loop_events
                   (observed_at, run_id, robot_id, correlation_id, event_sequence,
                    stage, status, payload)
                   VALUES (to_timestamp($1::double precision / 1000000000.0),
                           $2, $3, $4, $5, $6, $7, $8::jsonb)
                   ON CONFLICT DO NOTHING""",
                pending["observed_wall_time_ns"],
                pending["run_id"],
                pending["robot_id"],
                pending["correlation_id"],
                pending["event_sequence"],
                pending["stage"],
                pending["status"],
                json.dumps(pending),
            )
            pending = None
        except (asyncpg.PostgresError, OSError, TimeoutError) as error:
            print(f"loop event write unavailable: {error}", flush=True)
            if connection is not None:
                with contextlib.suppress(Exception):
                    await connection.close()
            connection = None
            await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    catalog = architecture_catalog()
    connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
    try:
        await connection.execute(
            "INSERT INTO architecture_manifest_snapshots "
            "(manifest_sha256, schema_version, payload) VALUES ($1, $2, $3::jsonb) "
            "ON CONFLICT (manifest_sha256) DO NOTHING",
            catalog["manifest_sha256"],
            catalog["schema_version"],
            json.dumps(catalog),
        )
    finally:
        await connection.close()
    reader = asyncio.create_task(consume_ros_state())
    writer = asyncio.create_task(persist_state())
    loop_reader = asyncio.create_task(consume_ros_loop())
    loop_writer = asyncio.create_task(persist_loop_events())
    try:
        yield
    finally:
        for task in (reader, writer, loop_reader, loop_writer):
            task.cancel()
        await asyncio.gather(reader, writer, loop_reader, loop_writer, return_exceptions=True)


app = FastAPI(title="Embodied Robotics Simulation API", version="0.2.0", lifespan=lifespan)
app.include_router(create_router(hub))
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("WEB_ORIGIN", "http://127.0.0.1:3000")],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/api/v3/architecture/manifest")
def architecture_manifest() -> dict[str, Any]:
    """Public evidence catalog; never grants command authority."""
    return architecture_catalog()


@app.get("/api/v3/architecture/android-evidence")
def android_architecture_evidence() -> dict[str, Any]:
    """Versioned read-only export boundary for a future Project 66 blueprint."""
    return android_evidence_contract()


@app.get("/api/v3/architecture/snapshots")
async def architecture_snapshots(limit: int = 10) -> dict[str, Any]:
    if not 1 <= limit <= 50:
        raise HTTPException(422, detail="invalid limit")
    connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
    try:
        rows = await connection.fetch(
            "SELECT manifest_sha256, schema_version, recorded_at "
            "FROM architecture_manifest_snapshots "
            "ORDER BY recorded_at DESC, manifest_sha256 LIMIT $1",
            limit,
        )
    finally:
        await connection.close()
    return {
        "snapshots": [{**dict(row), "recorded_at": row["recorded_at"].isoformat()} for row in rows]
    }


@app.get("/api/v3/architecture/health")
def architecture_health() -> dict[str, Any]:
    """Runtime observations are kept separate from source declarations."""
    latest = hub.latest
    age_ms = (
        max(0, (time.time_ns() - latest["observed_wall_time_ns"]) // 1_000_000)
        if latest is not None
        else None
    )
    return {
        "schema_version": "architecture-health.v1",
        "run_id": latest["run_id"] if latest else None,
        "state_age_ms": age_ms,
        "simulation_state": "live" if age_ms is not None and age_ms <= 1000 else "unavailable",
        "telemetry_database": "ready" if hub.database_ready else "unavailable",
        "dropped_write_samples": hub.dropped_write_samples,
    }


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready")
def ready() -> dict[str, Any]:
    state = hub.latest
    if state is None:
        raise HTTPException(503, detail="no ROS/Gazebo state received")
    age_ms = max(0, (time.time_ns() - state["observed_wall_time_ns"]) // 1_000_000)
    if age_ms > 1000:
        raise HTTPException(503, detail=f"state stale: {age_ms} ms")
    if not hub.database_ready:
        raise HTTPException(503, detail="telemetry database unavailable")
    return {"status": "ready", "age_ms": age_ms}


@app.get("/api/v1/robots/embodied_demo/state")
def state() -> dict[str, Any]:
    if hub.latest is None:
        raise HTTPException(503, detail="waiting for Gazebo/ROS state")
    age_ms = max(0, (time.time_ns() - hub.latest["observed_wall_time_ns"]) // 1_000_000)
    return {"mode": "simulation", "age_ms": age_ms, "stale": age_ms > 1000, "state": hub.latest}


@app.get("/api/v1/simulation-runs")
async def simulation_runs(limit: int = 20) -> dict[str, Any]:
    if not 1 <= limit <= 100:
        raise HTTPException(422, detail="invalid limit")
    try:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
        try:
            rows = await connection.fetch(
                "SELECT run_id, MIN(observed_at) AS started_at, "
                "MAX(observed_at) AS last_sample_at, COUNT(*) AS sample_count "
                "FROM robot_state_samples GROUP BY run_id "
                "ORDER BY last_sample_at DESC LIMIT $1",
                limit,
            )
        finally:
            await connection.close()
    except (asyncpg.PostgresError, OSError, TimeoutError) as error:
        raise HTTPException(503, detail="telemetry database unavailable") from error
    return {
        "read_only": True,
        "runs": [
            {
                "run_id": row["run_id"],
                "started_at": row["started_at"].isoformat(),
                "last_sample_at": row["last_sample_at"].isoformat(),
                "sample_count": row["sample_count"],
            }
            for row in rows
        ],
    }


@app.get("/api/v1/simulation-runs/{run_id}/samples")
async def samples(run_id: str, offset: int = 0, limit: int = 100) -> dict[str, Any]:
    if not 0 <= offset <= 100_000 or not 1 <= limit <= 500:
        raise HTTPException(422, detail="invalid pagination")
    if len(run_id) > 100 or not run_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(422, detail="invalid run ID")
    try:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
        try:
            rows = await connection.fetch(
                "SELECT payload FROM robot_state_samples WHERE run_id=$1 "
                "ORDER BY observed_at, sequence LIMIT $2 OFFSET $3",
                run_id,
                limit,
                offset,
            )
        finally:
            await connection.close()
    except (asyncpg.PostgresError, OSError, TimeoutError) as error:
        raise HTTPException(503, detail="telemetry database unavailable") from error
    return {
        "mode": "replay",
        "read_only": True,
        "run_id": run_id,
        "samples": [json.loads(row["payload"]) for row in rows],
    }


@app.get("/api/v1/simulation-runs/{run_id}/loop-events")
async def loop_events(run_id: str, limit: int = 100) -> dict[str, Any]:
    valid_id = len(run_id) <= 100 and run_id.replace("-", "").replace("_", "").isalnum()
    if not 1 <= limit <= 500 or not valid_id:
        raise HTTPException(422, detail="invalid run ID or limit")
    try:
        connection = await asyncpg.connect(os.environ["DATABASE_URL"], timeout=5)
        try:
            rows = await connection.fetch(
                "SELECT payload FROM loop_events WHERE run_id=$1 "
                "ORDER BY observed_at DESC, event_sequence DESC LIMIT $2",
                run_id,
                limit,
            )
        finally:
            await connection.close()
    except (asyncpg.PostgresError, OSError, TimeoutError) as error:
        raise HTTPException(503, detail="loop event database unavailable") from error
    return {
        "mode": "replay",
        "read_only": True,
        "run_id": run_id,
        "events": [json.loads(row["payload"]) for row in reversed(rows)],
    }


@app.websocket("/api/v1/robots/embodied_demo/stream")
async def stream(websocket: WebSocket) -> None:
    await websocket.accept()
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=8)
    hub.clients.add(queue)
    if hub.latest is not None:
        queue.put_nowait(hub.latest)
    try:
        while True:
            try:
                next_state = await asyncio.wait_for(queue.get(), timeout=2)
            except TimeoutError:
                await websocket.send_json(
                    {
                        "type": "heartbeat",
                        "wall_time_ns": time.time_ns(),
                        "database_ready": hub.database_ready,
                        "dropped_write_samples": hub.dropped_write_samples,
                    }
                )
                continue
            await websocket.send_json(
                {
                    "type": "robot-state",
                    "mode": "simulation",
                    "state": next_state,
                    "database_ready": hub.database_ready,
                    "dropped_write_samples": hub.dropped_write_samples,
                }
            )
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        hub.clients.discard(queue)


@app.websocket("/api/v1/robots/embodied_demo/loop-stream")
async def loop_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=32)
    hub.loop_clients.add(queue)
    try:
        for event in hub.loop_events[-32:]:
            await websocket.send_json({"type": "loop-event", "event": event})
        while True:
            event = await queue.get()
            await websocket.send_json({"type": "loop-event", "event": event})
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        hub.loop_clients.discard(queue)
