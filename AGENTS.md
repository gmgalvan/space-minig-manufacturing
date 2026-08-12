# Agent and Contributor Guide

This repository explores space mining and manufacturing with OpenUSD, NVIDIA Omniverse, Isaac Sim, and scientific models. Prefer clear, verifiable, reproducible experiments before increasing fidelity.

## Lead with the result

Every contribution must state:

1. the engineering question;
2. the success metric;
3. assumptions and units;
4. the expected result or acceptance criterion;
5. limitations that prevent the result from being interpreted as physical reality.

Lab 01 example:

```text
Question: Can four PhysX wheel joints move the rover?
Metric: Chassis displacement in meters during an 8 s run.
Input: Target wheel speed = 120 degrees/s.
Success: Positive displacement with no misaligned-joint errors.
Limitation: Flat rigid terrain and no energy model.
```

## Repository organization

- `labs/`: self-contained experiments with objectives, inputs, outputs, assumptions, commands, expected results, and troubleshooting.
- `assets/`: shared assets. Generated files must identify their source script.
- `models/`: reusable models independent of a single scenario.
- `data/raw/`: original data; do not modify it.
- `data/processed/`: derived data and the process that produced it.
- `results/`: generated artifacts; never use them as source truth.
- `docs/`: architecture, setup, operations, decisions, and references.

## Source files and generated artifacts

The canonical Lab 01 generation chain is:

```text
create_rover.py
  └── assets/usd/robots/lunar_rover_v0.usda
        └── prepare_physics_rover.py
              └── assets/usd/robots/lunar_rover_physics_v0.usda
                    └── create_lunar_scene.py
                          └── labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

When geometry, physics, or composition changes, edit the corresponding script and regenerate the `.usda` files. Do not patch only a generated artifact because the next generation will overwrite the change.

## Modeling conventions

- Use SI internally and include units in names such as `mass_kg`, `power_w`, and `gravity_m_s2`.
- In USD, use `metersPerUnit = 1` and `Z` as the up axis unless a documented decision says otherwise.
- Keep prim paths stable because control scripts depend on them.
- Separate visual geometry, rigid bodies, collision geometry, joints, and the world scene.
- Apply mass to the intended rigid body rather than an arbitrary visual descendant.
- Align joint anchors in the local coordinates of both connected bodies.
- Avoid magic numbers. Every physical value needs a name, unit, and source or a clear provisional label.
- Record random seeds whenever randomization is used.
- Check mass and energy conservation whenever a process model requires them.

## Reproducibility requirements

Every laboratory README must include:

- known software and hardware versions;
- the directory from which each command runs;
- inputs and defaults;
- output files;
- expected messages or metrics;
- how to stop persistent processes;
- how to repeat safely;
- known symptoms and minimum diagnostics.

Record at least the following for remote runs:

```text
date
Git commit
GPU
driver
CUDA
Isaac Sim
Isaac Lab
script and arguments
result
relevant warnings
```

Never commit secrets, temporary login codes, public IP addresses, or private service URLs.

## Lab 01 change workflow

From the local repository root:

```bash
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py

git diff --check
git status --short
```

Update the copy inside Brev's Isaac container with:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git pull --ff-only'
```

The host copy at `~/space-minig-manufacturing` and the container copy at `/workspace/space-minig-manufacturing` do not update each other.

## Acceptance checks

Before delivering a physics or control change:

1. run the local OpenUSD validation;
2. run `git diff --check`;
3. execute Isaac Sim;
4. verify all four motors are configured;
5. verify positive displacement and no new joint warnings;
6. update the documented result only after observing a real run.

Headless GLFW or `/var/run/utmp` warnings can be harmless in Brev. A `joint with disjointed body transforms` warning changes the physical assembly and must be fixed.

## Change quality

- Preserve unrelated user changes and never delete data without authorization.
- Keep changes focused.
- Use relative USD references for portability.
- Do not commit `.venv`, caches, logs, credentials, or accidental large files.
- Document when a persistent process requires `Ctrl+C`.
- Mark provisional data clearly and create a follow-up note.

## Git

Before publishing:

```bash
git status --short
git diff --check
git diff
```

Configure identity only for this repository when needed:

```bash
git config user.name "YOUR NAME"
git config user.email "YOUR EMAIL"
```

## Communication

Explain the result first, followed by the procedure. Distinguish between:

- **structural validation:** the USD contains the expected prims and metadata;
- **integration validation:** Isaac Sim opens and runs the scene;
- **physical validation:** the model accurately represents a real system.

Lab 01 currently provides basic structural and integration validation. It is not physical validation of mobility over lunar regolith.
