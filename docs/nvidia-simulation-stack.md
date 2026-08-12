# NVIDIA Stack for Space Mining and Manufacturing Simulation

This document maps NVIDIA technologies to the project, from a minimal OpenUSD rover to a digital twin of lunar extraction, processing, and manufacturing operations.

## Current decision

The MVP uses:

```text
OpenUSD
  └── Isaac Sim on Omniverse Kit
        ├── PhysX: gravity, collision, joints, and motors
        ├── RTX: visualization
        ├── WebRTC livestream: remote user interface
        └── Isaac Lab: application launch and future control tasks

NVIDIA Brev + L40S
  └── remote execution because the local GPU is not suitable for this workflow
```

Lab 01 validated this integration chain with `3.928 m` traveled in `8.01 s`. That result verifies software integration, not realistic regolith mobility.

## Target architecture

```text
CAD / scientific data / GIS
              │
              ▼
           OpenUSD  ◄──────────── experiment layers and variants
              │
              ▼
       Omniverse Kit + RTX
              │
        ┌─────┴───────────┐
        ▼                 ▼
   Isaac Sim            Kit-CAE
   PhysX/sensors        thermal/FEM/CFD
        │
   ┌────┴───────────┐
   ▼                ▼
Isaac Lab       Replicator
control/RL      synthetic data
   │
   ▼
Isaac ROS + Jetson ──► physical prototype

CUDA-X / Modulus / cuOpt ──► compute, surrogate models, and planning
```

## Technology map and priority

| Technology | Function | Proposed project use | Priority |
| --- | --- | --- | --- |
| [OpenUSD](https://docs.omniverse.nvidia.com/dev-guide/latest/dev-usd.html) | 3D scene composition | source of truth for assets, references, layers, and variants | P0, active |
| [Omniverse Kit](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html) | extensible runtime and SDK | application, UI, Python scripting, and scene loading | P0, active indirectly |
| [Omniverse RTX Renderer](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html) | accelerated rendering | visual inspection and future synthetic cameras | P0, active |
| [PhysX / Omni Physics](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/extensions/runtime/source/omni.physx/docs/index.html) | dynamics and collision | lunar gravity, rigid bodies, wheels, joints, and actuators | P0, active |
| [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_simulation/index.html) | robotics simulation on Kit | rovers, excavators, arms, sensors, and ROS 2 | P0, active |
| [Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html) | robotics learning and task framework | current launch environment; future control, parallel environments, and policies | P0/P1, basic use |
| WebRTC livestream | remote Kit interface | browser-based Isaac Sim access through Brev | P0, active |
| [Isaac Sim Replicator](https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/index.html) | synthetic data generation | images, labels, and controlled lighting or terrain variation | P1 |
| [Isaac ROS](https://developer.nvidia.com/isaac/ros) | accelerated ROS 2 packages | transfer perception and navigation toward hardware | P1 |
| [Jetson](https://developer.nvidia.com/embedded-computing) | embedded edge compute | onboard autonomy for a future physical prototype | P2 |
| [Kit-CAE](https://docs.omniverse.nvidia.com/guide-kit-cae/latest/index.html) | CAE integration and visualization | thermal, structural, and fluid fields inside the twin | P2 |
| [NVIDIA Modulus](https://developer.nvidia.com/modulus) | physics-informed AI | surrogate models for thermal, dust, or process simulation | P2 |
| [CUDA-X](https://developer.nvidia.com/cuda-x) | accelerated computing libraries | vision, AI, scientific computing, and analysis | P2 |
| [cuOpt](https://developer.nvidia.com/cuopt) | routing and decision optimization | fleet routing, charging, transport, and inventory | P3 |
| [NVIDIA Brev](https://brev.nvidia.com/) | GPU provisioning | reproducible sandbox using an L40S and Isaac Launchable | current infrastructure |

**Priority:** P0 is required for the current laboratory; P1 is the next phase; P2 requires a concrete multidisciplinary question; P3 is reserved for full-system optimization.

## Responsibilities by layer

### OpenUSD: the world contract

OpenUSD describes hierarchy, transforms, geometry, metadata, references, and composition. This repository separates:

```text
visual asset
  + physics variant
  + world scene
  + experiment parameters
```

The scene references the rover with a relative path for portability. USD does not execute dynamics by itself; it stores data interpreted by Isaac Sim and PhysX.

### Omniverse Kit: application and extensions

Kit loads the stage, runs extensions, and provides the interface shown in the web viewer. Messages such as `[ext: ...] startup`, `Simulation App Starting`, and `app ready` belong to this startup process. Lab 01 currently uses Isaac Lab scripts to launch Kit rather than a custom extension.

### PhysX: rover dynamics

The current model contains:

- gravity of `1.62 m/s²` toward `-Z`;
- a `35 kg` rigid chassis;
- four `2.5 kg` rigid wheels;
- collision on the chassis, wheels, and ground;
- four `RevoluteJoint` objects on the `Y` axis;
- four angular `DriveAPI` instances configured at runtime.

A `joint with disjointed body transforms` warning is not cosmetic. It means PhysX may snap bodies together when assembling the joint. The current scripts align `localPos0` with each wheel center and use `localPos1 = (0, 0, 0)`.

### Isaac Sim: robotics integration

Isaac Sim supplies the live stage, timeline, PhysX integration, RTX rendering, sensor framework, and inspection tools. `run_lunar_rover.py` opens the scene; `drive_lunar_rover.py` applies motors and measures chassis displacement in world coordinates.

### Isaac Lab: experiments and scaling

The MVP uses Isaac Lab's `AppLauncher`. Future tasks should define:

- observations: pose, velocity, IMU, camera, battery, and payload;
- actions: wheel or tool velocity and torque;
- events: friction, slope, mass, and lighting variation;
- termination: distance, time, rollover, energy, or collision;
- metrics: productivity, Wh/m, slip, and safety.

Do not train a policy before a deterministic baseline and reliable metrics exist.

### RTX and Replicator: perception

RTX supports inspection and sensor rendering. Replicator can generate synthetic datasets with labels for rocks, obstacles, excavation state, and hopper fill. Extreme lunar illumination must be varied deterministically, with every random seed recorded.

### Isaac ROS and Jetson: simulation to hardware

Isaac ROS can run accelerated perception and navigation in ROS 2. Jetson is a possible onboard target, but neither is required for the virtual rover demonstration. Hardware transfer requires sensor calibration, latency, noise, thermal limits, and energy constraints that the MVP does not model.

### Kit-CAE, Modulus, CUDA-X, and cuOpt

Use these only for specific engineering questions:

- **Kit-CAE:** place thermal, FEM, or CFD results in 3D context;
- **Modulus:** approximate expensive physics after equations and validation data exist;
- **CUDA-X:** accelerate computation, vision, and analysis;
- **cuOpt:** optimize fleet operations when a simple planner is no longer sufficient.

## Local versus cloud hardware

The local machine reported a Quadro T2000 Max-Q with `4 GiB` VRAM. It is suitable for:

- editing Python and `.usda` files;
- running `usd-core` and structural validation;
- Git and documentation.

The full session ran on a remote L40S because Isaac Sim, RTX, Isaac Lab, and livestreaming require substantially more GPU memory and a compatible environment. Splitting the workflow reduces cost:

```text
local: author, validate, review, and version
cloud: integrate, render, simulate, and measure
```

## Run manifest

Record this information for comparable results:

```yaml
date: 2026-08-12
git_commit: <hash>
gpu: NVIDIA L40S
driver: 595.71.05
cuda_reported: 13.2
isaac_sim: 6.0.1
isaac_lab: 3.0.0-beta2-post1
scene: labs/01-lunar-rover/lunar_rover_scene_v0.usda
script: labs/01-lunar-rover/scripts/drive_lunar_rover.py
duration_s: 8
wheel_speed_deg_s: 120
displacement_m: 3.928
```

The Git commit is mandatory because a scene can change while keeping the same filename.

## Technical roadmap

1. **Reproducible rover:** OpenUSD, PhysX, livestream, and measured displacement — basic integration complete.
2. **Distance controller:** stop at a target and save telemetry.
3. **Parameterized terrain:** slope, roughness, friction, and measured slip.
4. **Sensors:** camera, IMU, and synthetic datasets.
5. **Tooling:** approximate excavation, moved mass, energy, and wear.
6. **Isaac Lab task:** parallel environments, randomization, and baseline policy.
7. **ISRU and CAE:** connect mobility, inventory, and processing.
8. **Fleet operations:** planning and operational economics.

## Current scientific limitations

- The terrain does not represent regolith particles.
- Friction, motor force, and damping are provisional.
- There is no suspension or validated wheel–soil interaction model.
- Torque, power, and energy are not measured.
- Illumination is not configured as a scientific lunar-lighting scenario.
- Distance results have not been compared with experimental data.

## Operational documents

- [Reproduce Lab 01](../labs/01-lunar-rover/README.md)
- [Deploy with NVIDIA Brev](nvidia-brev-isaac-launchable.md)
- [Contributor conventions](../AGENTS.md)

## Official sources

- [Omniverse Kit](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html)
- [OpenUSD in Omniverse](https://docs.omniverse.nvidia.com/dev-guide/latest/dev-usd.html)
- [Omni Physics](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/index.html)
- [Isaac Sim robot simulation](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_simulation/index.html)
- [Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html)
- [Isaac ROS](https://developer.nvidia.com/isaac/ros)
- [Kit-CAE](https://docs.omniverse.nvidia.com/guide-kit-cae/latest/index.html)

_Procedure last updated: August 12, 2026._
