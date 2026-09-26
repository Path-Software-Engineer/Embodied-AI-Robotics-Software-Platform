FROM ros:jazzy-ros-base-noble@sha256:c3706ef0a0aa45413c07803cf433602f543b22e45b4855f6fca955c2d8ecc4e8

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv ros-jazzy-ros-gz ros-jazzy-tf2-msgs ros-jazzy-rosgraph-msgs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY ros_ws/src ros_ws/src
RUN . /opt/ros/jazzy/setup.sh \
    && cd ros_ws && colcon build --packages-up-to safety_supervisor
COPY services/requirements.lock services/requirements.lock
RUN python3 -m venv --system-site-packages /opt/embodied-venv \
    && /opt/embodied-venv/bin/pip install --no-cache-dir -r services/requirements.lock
ENV PATH=/opt/embodied-venv/bin:$PATH
ENV PYTHONPATH=/workspace:/workspace/services/generated
COPY contracts contracts
COPY architecture architecture
COPY apps/web/src apps/web/src
COPY infra/migrations infra/migrations
COPY tests tests
COPY services services
RUN python -m grpc_tools.protoc -I contracts/proto \
    --python_out=services/generated --grpc_python_out=services/generated \
    contracts/proto/robot_state.proto
COPY sim sim
COPY scripts scripts
COPY infra/start-simulator.sh /usr/local/bin/start-simulator
RUN chmod +x /usr/local/bin/start-simulator
ENV GZ_SIM_RESOURCE_PATH=/workspace/sim/models
EXPOSE 50051 8000
