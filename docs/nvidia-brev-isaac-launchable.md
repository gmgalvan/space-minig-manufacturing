# NVIDIA Brev and Isaac Launchable: Reproducible Guide

This guide covers the complete process for provisioning an NVIDIA GPU in Brev, recovering a failed Isaac Launchable startup, opening the web viewer, and running Lab 01. The commands and diagnostics come from a successful session completed on August 12, 2026.

## Reference result

| Component | Observed value |
| --- | --- |
| Provider | AWS through NVIDIA Brev |
| GPU | NVIDIA L40S, approximately `44.7 GiB` usable VRAM |
| CPU and RAM | 16 CPUs, 128 GiB RAM |
| Remote driver | `595.71.05` |
| CUDA reported by driver | `13.2` |
| Isaac Sim | `6.0.1` |
| Isaac Lab | `3.0.0-beta2-post1` / extension `3.0.0` |
| Main container | `vscode` |
| Project path in container | `/workspace/space-minig-manufacturing` |
| Traction result | `3.928 m` in `8.01 s` at `120 degrees/s` |

These values describe the reference session, not permanent requirements. Availability, region, provider, price, and images can change. Always use the values displayed by Brev at deployment time.

## Cost and security

- Brev charges while compute is active. The reference session reached approximately `$3.65/hour`.
- A `$10` credit balance does not make the instance free; it funds only about 2–3 hours at that rate.
- A stopped instance may continue charging for storage. The observed rate was `$0.04/hour`, or about `$0.96/day`.
- Review the displayed hourly rate before deploying.
- Never publish login codes, public IP addresses, hostnames, private viewer URLs, or credentials.
- Push important work before stopping or deleting the machine.
- **Stop** preserves a restartable instance and its storage. **Delete** permanently removes the remote disk and stops storage charges.

## Understand the three terminals

| Context | Typical prompt | Commands run there |
| --- | --- | --- |
| Local machine or WSL | `user@computer:~/memo/...$` | `uv`, Git, `brev login`, `brev shell` |
| Brev remote host | `ubuntu@brev-...:~$` | Docker Compose and `docker exec` |
| `vscode` container | usually entered through `docker exec` | Isaac Sim, Isaac Lab, and the `/workspace` repository |

Docker commands run on the remote host, not on the local machine and not inside another container.

## 1. Prepare and publish locally

From the local repository root:

```bash
cd ~/memo/space-minig-manufacturing

uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py

git status --short
git diff --check
git add README.md AGENTS.md docs labs assets .gitignore
git commit -m "docs: standardize project documentation in English"
git push
```

Repository URL:

```text
https://github.com/gmgalvan/space-minig-manufacturing
```

## 2. Deploy from the correct Brev page

1. Open [NVIDIA Brev](https://brev.nvidia.com/) and sign in.
2. Verify the available credit.
3. Open **Launchables**, search for **Isaac Launchable**, and open its dedicated page.
4. Verify that the description includes Isaac Sim and Isaac Lab.
5. Select **Deploy Launchable**.
6. Choose a compatible RTX GPU. The reference session used an **L40S**.
7. Select an available region. Changing regions does not fix a broken lifecycle script.
8. Use a stable name such as `space-mining-lab-01`.
9. Review the total hourly price and deploy.

Avoid adding Isaac Launchable through the generic **Create Environment → Edit → Launchables** form if it returns:

```text
Error creating instance: rpc error: code = Internal desc = lifecycle script is empty
```

The working path was the dedicated Isaac Launchable page.

## 3. Wait for provisioning

Expected progress:

```text
Provisioned GPU instance
Configuring the instance
Run startup script
Check service status
```

Expected instance states:

```text
Compute: Running
VM Mode: Built
Lifecycle script: Executing → Completed
Secure Link: Loading → Healthy
```

Building images and warming Isaac Sim caches can take several minutes. Opening the service too early may show:

```text
502 Bad Gateway
Host Error
```

Check instance state and logs instead of repeatedly refreshing the browser.

## 4. Install and authenticate the Brev CLI

Run on the local machine:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/bin/install-latest.sh)"
export PATH="$HOME/.local/bin:$PATH"
brev login
```

Enter the email associated with Brev. If the browser does not open, use the temporary URL printed by the CLI. Never save or share that URL.

List instances:

```bash
brev ls
```

Reference ready state:

```text
NAME                 STATUS   BUILD      SHELL  GPU
space-mining-lab-01  RUNNING  COMPLETED  READY  L40S
```

Connect:

```bash
brev shell space-mining-lab-01
```

The first attempt can report a hostname resolution failure while Brev refreshes SSH configuration. The connection is successful when the prompt changes to `ubuntu@brev-...:~$`.

## 5. Verify the remote host

Run on the remote host:

```bash
nvidia-smi
ls ~
cd ~/isaac-launchable/isaac-lab
ls
docker compose ps
```

The Launchable should create `~/isaac-launchable/isaac-lab`. If `docker compose ps` already shows `nginx`, `vscode`, and `web-viewer`, continue to section 7.

Expected services:

```text
isaac-lab-nginx-1
vscode
web-viewer
```

The `vscode` container may briefly report `health: starting`.

## 6. Recover a failed lifecycle script

### Observed symptoms

- compute is `Running` and VM Mode is `Built`;
- the lifecycle script ends as `Failed`;
- the Secure Link is `Unhealthy`;
- `docker compose ps` shows no active services;
- no `isaac-sim.sh` exists in the remote host's home directory.

Isaac Sim lives inside the `vscode` container under `/isaac-sim`, so its absence from the host home directory is expected.

### Observed cause

The lifecycle script contained `dockercompose up -d`. The valid command contains a space:

```bash
docker compose up -d
```

### Start the services manually

```bash
cd ~/isaac-launchable/isaac-lab
docker compose up -d
docker compose ps
```

These warnings did not block the reference startup:

```text
The "DEV_NGINX_PORT" variable is not set
Published ports are discarded when using host network mode
```

### Complete the skipped Isaac Sim preparation

```bash
docker exec -u root vscode sed -i \
  -e 's|^PORTABLE_ROOT="$SCRIPT_DIR/portable_root"$|PORTABLE_ROOT="$SCRIPT_DIR/kit"|' \
  -e 's|emptyStageOnStart=1|emptyStageOnStart=0|' \
  /isaac-sim/warmup.sh

docker exec -u root vscode install -d -o ubuntu -g ubuntu \
  /isaac-sim/kit/cache \
  /isaac-sim/kit/data \
  /isaac-sim/kit/logs \
  /root/.cache \
  /root/.nv/ComputeCache

docker exec -u ubuntu:ubuntu -w /isaac-sim vscode ./warmup.sh
```

The warmup runs in the foreground. Do not interrupt it while extensions are still loading. Wait for:

```text
Simulation App Startup Complete
app ready
[INFO]: Setup complete...
[INFO] Using Python: "/workspace/isaaclab/_isaac_sim/python.sh"
```

When the remote prompt returns, the warmup has ended. If it intentionally remains open after `app ready`, press `Ctrl+C` once and confirm the prompt returns.

## 7. Clone or update the project in the container

Run from the remote host:

```bash
docker exec -u ubuntu vscode bash -lc '
  if [ -d /workspace/space-minig-manufacturing/.git ]; then
    cd /workspace/space-minig-manufacturing && git pull --ff-only
  else
    cd /workspace && git clone https://github.com/gmgalvan/space-minig-manufacturing.git
  fi
'
```

Verify the copy and commit:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git status --short && git rev-parse --short HEAD && ls labs/01-lunar-rover'
```

Do not clone again when the directory already exists; use `git pull --ff-only`.

## 8. Open the viewer

Open the **isaac** service from the Brev instance page. If it opens a blank root page, append:

```text
/viewer/
```

`WAITING FOR STREAM` means no Isaac Sim process is currently publishing a livestream. Leave the viewer tab open and launch one of the following scripts through SSH.

## 9. Open the rover without motors

```bash
cd ~/isaac-launchable/isaac-lab

docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/run_lunar_rover.py --livestream 2 --viz kit'
```

Expected messages:

```text
[INFO]: Lunar scene opened: .../lunar_rover_scene_v0.usda
[INFO]: Simulation is active; stop it with Ctrl+C.
```

Return to the viewer. The Stage should include `World`, `PhysicsScene`, `LunarGround`, and `LunarRover`. The script already starts the timeline; no UI Play button is required.

Stop this process with `Ctrl+C` before starting the traction test.

## 10. Run and measure traction

```bash
docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/drive_lunar_rover.py --livestream 2 --viz kit --duration 8 --wheel-speed 120'
```

Reference result:

```text
[DEBUG]: Motor configured: /World/LunarRover/Joints/FrontLeftAxle
[DEBUG]: Motor configured: /World/LunarRover/Joints/FrontRightAxle
[DEBUG]: Motor configured: /World/LunarRover/Joints/RearLeftAxle
[DEBUG]: Motor configured: /World/LunarRover/Joints/RearRightAxle
[INFO]: Motors active for 8.0 s.
[RESULT]: displacement=3.928 m; duration=8.01 s
[INFO]: The scene remains open for inspection. Stop it with Ctrl+C.
```

The rover moves during the requested duration. The script then stops the timeline and leaves the application open for inspection. Press `Ctrl+C` when finished.

## 11. Short iteration loop

On the local machine:

```bash
git add <files>
git commit -m "describe the change"
git push
```

On the Brev remote host:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git pull --ff-only'
```

Project-only Python or `.usda` changes do not require rebuilding the containers.

## 12. Diagnostics

```bash
# Container health
cd ~/isaac-launchable/isaac-lab
docker compose ps

# GPU inside the container
docker exec vscode nvidia-smi

# Active Isaac or Kit processes
docker exec vscode bash -lc "ps -ef | grep -E '[k]it|[i]saac'"

# Recent logs
docker compose logs --tail=200
docker logs --tail=200 vscode
docker logs --tail=200 web-viewer

# Project state and commit
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git status --short && git rev-parse --short HEAD'
```

## 13. Known problems

| Symptom | Likely cause | Action |
| --- | --- | --- |
| `lifecycle script is empty` during deployment | broken generic-form integration | deploy from the dedicated Isaac Launchable page |
| lifecycle script is `Failed` | `dockercompose` typo | run `docker compose up -d` and the manual warmup |
| `502 Bad Gateway` | port 80 backend is not ready | check container health and logs, then wait |
| Secure Link is `Unhealthy` | nginx or viewer has no backend | inspect `docker compose ps` and logs |
| `WAITING FOR STREAM` | Isaac Sim is not streaming | launch exactly one rover script |
| `Got stop event while waiting for client connection` | stopped process or competing livestream | close old processes, open the viewer, and relaunch one process |
| `GLFW initialization failed` | headless session has no local window | acceptable when WebRTC and the result work |
| `Failed to open /var/run/utmp` | container has no desktop login record | acceptable when startup reaches `app ready` |
| `joint with disjointed body transforms` | incorrect joint anchors | update and regenerate the USD; reject that run |
| changes are missing | host copy was updated, container copy was not | pull inside `vscode` |
| destination already exists | repository is already cloned | use `git pull --ff-only` |

## 14. Stop or delete the paid environment

1. Press `Ctrl+C` in the terminal running Isaac Sim.
2. Confirm that the shell prompt returns.
3. Push important work.
4. Run `exit` to leave SSH.
5. Use **Stop** in Brev to stop compute while preserving storage, or **Delete** to remove all remote data and storage charges.
6. Confirm with `brev ls` that the environment is no longer `RUNNING`.

In the reference session, stopping preserved storage at `$0.04/hour`. Deleting the environment changed compute to `Terminating` and `$0.00/hour`, then removed the environment entirely.

## Reproduction checklist

- [ ] Local USD files generated, validated, committed, and pushed.
- [ ] Credit and hourly price reviewed.
- [ ] Isaac Launchable deployed from its dedicated page.
- [ ] `brev ls` reports a ready instance, or manual recovery is complete.
- [ ] Host and container recognize the GPU.
- [ ] `nginx`, `vscode`, and `web-viewer` are running.
- [ ] Repository is current inside `/workspace`.
- [ ] Viewer is open at `/viewer/`.
- [ ] Four motors are configured.
- [ ] Displacement result is recorded with the Git commit.
- [ ] Compute and storage charges are stopped when work is complete.
