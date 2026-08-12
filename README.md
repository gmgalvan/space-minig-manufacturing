# Space Mining & Manufacturing

An open laboratory for designing and testing off-Earth mining, robotics, and manufacturing systems. The project turns engineering questions about mobility, extraction, processing, energy, and logistics into small, reproducible models, OpenUSD scenes, and measurable results.

## Current status

The first working laboratory is a minimal lunar rover:

- geometry authored with OpenUSD;
- a physics variant with masses, colliders, and four revolute joints;
- a scene with rigid terrain and lunar gravity of `1.62 m/s²`;
- remote execution in NVIDIA Isaac Sim and Isaac Lab through NVIDIA Brev;
- four PhysX wheel motors set to `120 degrees/s`;
- observed test result: `3.928 m` traveled in `8.01 s`, approximately `0.49 m/s` average speed.

This is an integration test, not a prediction of real rover performance. The ground is a rigid plate, granular regolith is not modeled, and electrical energy consumption is not yet calculated.

## Documentation map

| Document | Use it for |
| --- | --- |
| [Lab 01 — Lunar Rover](labs/01-lunar-rover/README.md) | Build, validate, and run the rover step by step. |
| [NVIDIA Brev and Isaac Launchable](docs/nvidia-brev-isaac-launchable.md) | Reproduce the remote deployment, recover failed startup, run Isaac Sim, and control cost. |
| [NVIDIA Simulation Stack](docs/nvidia-simulation-stack.md) | Understand which NVIDIA technology belongs to each project layer. |
| [Agent and contributor guide](AGENTS.md) | Follow modeling, reproducibility, testing, and repository conventions. |

## Local quick start

The OpenUSD generation workflow runs locally without installing Isaac Sim. Requirements:

- Linux or WSL 2;
- Git;
- `curl` to install `uv`;
- Python 3.10 managed by `uv`.

Run from the repository root:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

uv venv --python 3.10
uv pip install --python .venv/bin/python usd-core

uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py
```

Expected files:

```text
assets/usd/robots/lunar_rover_v0.usda
assets/usd/robots/lunar_rover_physics_v0.usda
labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

Expected validation message:

```text
Validation passed: rover, units, and 4 wheels are present.
```

Continue with the [NVIDIA Brev guide](docs/nvidia-brev-isaac-launchable.md) for the full RTX and PhysX simulation.

## Repository layout

```text
.
├── assets/
│   └── usd/robots/                 # Visual and physics-ready OpenUSD assets
├── docs/
│   ├── nvidia-brev-isaac-launchable.md
│   └── nvidia-simulation-stack.md
├── labs/
│   └── 01-lunar-rover/
│       ├── README.md
│       ├── lunar_rover_scene_v0.usda
│       └── scripts/
├── .gitignore
├── AGENTS.md
└── README.md
```

The `.usda` files remain text-based so references, units, masses, joints, and physics changes can be reviewed with Git.

## Reproducible workflow

1. Modify the source scripts, not only the generated USD files.
2. Regenerate the visual asset, physics variant, and scene.
3. Run `validate_rover.py` locally.
4. Commit and push the changes.
5. In Brev, run `git pull` inside the `vscode` container.
6. Run the simulation and record parameters, versions, commit, and result.
7. Stop the process with `Ctrl+C`, then stop or delete the paid instance.

## Roadmap

1. **Lunar mobility:** friction, suspension, distance control, and telemetry.
2. **Sensors:** camera, IMU, LiDAR, and synthetic data with Replicator.
3. **Extraction:** tooling, payload, moved mass, wear, and energy.
4. **ISRU processing:** mass and energy balances for water, oxygen, and metals.
5. **Manufacturing:** sintering and additive manufacturing with local material versus Earth-supplied mass.
6. **Integrated operations:** fleets, inventory, maintenance, failures, and mission economics.

## Conventions

- Use SI internally: kg, m, s, K, W, and Pa.
- Separate facts, measurements, estimates, and assumptions.
- Version parameters and commands with every experiment.
- Do not treat successful visualization as physical validation.
- Document every limitation that could change a conclusion.

## Security and cost

A remote GPU instance incurs charges while active. Review Brev's displayed price before deployment. Never publish private URLs, IP addresses, access codes, or credentials. Push important work to Git before stopping or deleting an instance.

## Contributing

Every laboratory must answer a concrete engineering question and define a success metric. Read [AGENTS.md](AGENTS.md) before making changes.
