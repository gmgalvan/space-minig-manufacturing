# Lab 01 — Minimal OpenUSD Lunar Rover in Isaac Sim

## Result

This laboratory generates an OpenUSD rover, adds PhysX behavior, places it in a lunar-gravity scene, and drives all four wheels in Isaac Sim. The reference run moved the chassis `3.928 m` in `8.01 s` with a target wheel speed of `120 degrees/s`.

The goal is to validate the complete OpenUSD → PhysX → Isaac Sim → livestream → measurement pipeline. This is not yet a validated model of mobility over lunar regolith.

## Engineering question and success criteria

**Question:** Can a portable OpenUSD rover move through four revolute joints in NVIDIA Isaac Sim?

**Success criteria:**

- the USD stage uses meters and a `Z` up axis;
- the chassis, four wheels, and front sensor marker exist;
- the scene uses gravity of `1.62 m/s²`;
- Isaac Sim resolves all references;
- all four motors are configured without misaligned-joint warnings;
- measured chassis displacement is positive.

## Generation pipeline

```text
create_rover.py
  │ generates geometry and metadata
  ▼
assets/usd/robots/lunar_rover_v0.usda
  │ adds rigid bodies, colliders, masses, and joints
  ▼
prepare_physics_rover.py
  ▼
assets/usd/robots/lunar_rover_physics_v0.usda
  │ is referenced by a portable scene
  ▼
create_lunar_scene.py
  ▼
labs/01-lunar-rover/lunar_rover_scene_v0.usda
  │
  ├── run_lunar_rover.py       opens the scene for inspection
  └── drive_lunar_rover.py     applies motors and measures distance
```

## Current model

| Component | Value |
| --- | --- |
| Visual chassis | `1.20 × 0.80 × 0.35 m` |
| Wheel radius | `0.18 m` |
| Wheel axial length | `0.12 m` |
| Chassis rigid-body mass | `35 kg` |
| Mass per wheel | `2.5 kg` |
| Total physical mass | `45 kg` |
| Gravity | `1.62 m/s²` toward `-Z` |
| Ground | static `20 × 20 × 0.10 m` box |
| Wheel and joint axis | `Y` |
| Default motor | `120 degrees/s`, maximum force `250`, damping `2` |
| Default run duration | `8 s` |

The front camera and antenna are currently geometry and metadata markers; they do not produce sensor observations.

## Part A — Local setup with `uv`

### 1. Enter the repository root

```bash
cd ~/memo/space-minig-manufacturing
```

Adjust the path if the repository was cloned elsewhere.

### 2. Install `uv`

Run once:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

If a new terminal reports `uv: command not found`, export the path again or restart the terminal.

### 3. Create the environment and install OpenUSD Python

```bash
uv venv --python 3.10
uv pip install --python .venv/bin/python usd-core
```

Verify the package:

```bash
uv run --python .venv/bin/python -c 'from pxr import Usd; print(Usd.GetVersion())'
```

## Part B — Generate and validate the USD files

Run in this exact order:

```bash
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py
```

Expected output:

```text
Rover created: .../assets/usd/robots/lunar_rover_v0.usda
Validation passed: rover, units, and 4 wheels are present.
Physics variant created: .../assets/usd/robots/lunar_rover_physics_v0.usda
Lunar scene created: .../labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

Confirm the files:

```bash
ls -lh assets/usd/robots/lunar_rover_v0.usda \
  assets/usd/robots/lunar_rover_physics_v0.usda \
  labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

The scene references the rover with this relative path:

```text
../../assets/usd/robots/lunar_rover_physics_v0.usda
```

Relative references make the repository portable across machines and containers.

## Part C — Publish before using Brev

```bash
git status --short
git diff --check
git add README.md AGENTS.md docs labs assets .gitignore
git commit -m "docs: standardize project documentation in English"
git push
```

Configure repository-only Git identity when needed:

```bash
git config user.name "YOUR NAME"
git config user.email "YOUR EMAIL"
```

## Part D — Prepare NVIDIA Brev

Follow the complete [NVIDIA Brev and Isaac Launchable guide](../../docs/nvidia-brev-isaac-launchable.md). In summary:

1. deploy **Isaac Launchable** on an RTX-capable GPU; the reference run used an L40S;
2. wait for `RUNNING`, `COMPLETED`, and `READY`;
3. connect with `brev shell space-mining-lab-01`;
4. recover the containers if the lifecycle script fails;
5. clone the repository into `/workspace` inside the `vscode` container;
6. open the `isaac` service and append `/viewer/` when necessary.

## Part E — Synchronize the container copy

Run on the remote host:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git pull --ff-only'
```

There are two independent copies:

- remote host: `~/space-minig-manufacturing`;
- Isaac container: `/workspace/space-minig-manufacturing`.

Isaac Sim uses the second copy. Pulling only on the host does not update the container.

## Part F — Open the scene without wheel motors

From the remote host:

```bash
cd ~/isaac-launchable/isaac-lab

docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/run_lunar_rover.py --livestream 2 --viz kit'
```

Wait for:

```text
[INFO]: Lunar scene opened: /workspace/space-minig-manufacturing/labs/01-lunar-rover/lunar_rover_scene_v0.usda
[INFO]: Simulation is active; stop it with Ctrl+C.
```

Keep the terminal open. In the browser, open the Isaac service and visit `/viewer/`. The script already calls `timeline.play()`, so no UI Play button is required.

Return to the terminal and press `Ctrl+C` once to stop the process. Continue only after the `ubuntu@brev-...$` prompt returns.

## Part G — Run the traction test

Make sure no other Isaac Sim livestream process is active, then run:

```bash
docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/drive_lunar_rover.py --livestream 2 --viz kit --duration 8 --wheel-speed 120'
```

The script:

1. opens the scene;
2. locates the four joints under `/World/LunarRover/Joints`;
3. applies an angular `UsdPhysics.DriveAPI` to each joint;
4. starts the timeline;
5. measures the chassis world transform;
6. stops physics after the requested duration;
7. keeps the application open for inspection.

Reference output:

```text
[DEBUG]: Scene loaded; configuring motors...
[DEBUG]: Motor configured: /World/LunarRover/Joints/FrontLeftAxle
[DEBUG]: Motor configured: /World/LunarRover/Joints/FrontRightAxle
[DEBUG]: Motor configured: /World/LunarRover/Joints/RearLeftAxle
[DEBUG]: Motor configured: /World/LunarRover/Joints/RearRightAxle
[INFO]: Motors active for 8.0 s.
[RESULT]: displacement=3.928 m; duration=8.01 s
[INFO]: The scene remains open for inspection. Stop it with Ctrl+C.
```

Distance can vary with software version, simulation step, and environment state. An approximate `5 m` run based on the observed speed is:

```bash
docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/drive_lunar_rover.py --livestream 2 --viz kit --duration 10.2 --wheel-speed 120'
```

This does not stop at exactly 5 m; it only extends the duration. Distance-based control is a planned improvement.

## Visual inspection

The Stage panel should contain:

```text
/World
├── PhysicsScene
├── LunarGround
└── LunarRover
    ├── Chassis
    ├── Wheels
    │   ├── FrontLeft
    │   ├── FrontRight
    │   ├── RearLeft
    │   └── RearRight
    ├── Sensors
    └── Joints
```

Select `LunarRover` and press `F` to frame it. Use the mouse wheel to zoom and the configured `Alt` + mouse controls to orbit.

## Known warnings

These warnings appeared remotely and did not block the reference run:

```text
Failed to open [/var/run/utmp]
Active user not found. Using default user [kiosk]
GLFW initialization failed
Possible version incompatibility ... IStageReaderWriter ...
```

They are acceptable in this headless environment when `Simulation App Startup Complete`, `app ready`, and the result follow.

This warning indicates a real model problem:

```text
CreateJoint - found a joint with disjointed body transforms
```

Do not accept that run. Regenerate with the current scripts and verify that every `localPos0` matches its wheel position and every `localPos1` is `(0, 0, 0)`.

## Repeat a run

1. Press `Ctrl+C` in the active process.
2. Confirm that the shell prompt returns.
3. Pull inside the container if the project changed.
4. Run `drive_lunar_rover.py` again.
5. Refresh `/viewer/` if it remains on `WAITING FOR STREAM`.

Never launch two Isaac Sim livestream processes simultaneously. They can compete for the session and produce `Got stop event while waiting for client connection`.

## Limitations

- flat, rigid ground;
- friction is not calibrated against regolith;
- no suspension or independent steering;
- provisional motor parameters;
- no battery, measured torque, power, or reported slip;
- no functional sensors;
- no validation against hardware or lunar test data.

## Next improvements

1. stop automatically at a target distance;
2. record position, speed, and energy telemetry;
3. parameterize friction and slope;
4. add suspension and differential control;
5. model battery energy;
6. add camera and IMU observations plus a navigation task.
