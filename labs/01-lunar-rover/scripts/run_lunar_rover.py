"""Open and run the Lab 01 lunar scene in Isaac Sim and Isaac Lab."""

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCENE_PATH = REPOSITORY_ROOT / "labs" / "01-lunar-rover" / "lunar_rover_scene_v0.usda"


parser = argparse.ArgumentParser(description="Run the Lab 01 lunar rover.")
parser.add_argument(
    "--scene",
    type=Path,
    default=DEFAULT_SCENE_PATH,
    help="Absolute or relative path to a USD scene.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


def main() -> None:
    """Load the USD scene and keep the simulation active for livestreaming."""
    import omni.timeline
    import omni.usd

    scene_path = args_cli.scene.expanduser().resolve()
    if not scene_path.is_file():
        raise FileNotFoundError(f"USD scene does not exist: {scene_path}")

    usd_context = omni.usd.get_context()
    if not usd_context.open_stage(str(scene_path)):
        raise RuntimeError(f"Isaac Sim could not open the scene: {scene_path}")

    # Wait for Kit to finish loading scene references and layers.
    for _ in range(60):
        simulation_app.update()

    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    print(f"[INFO]: Lunar scene opened: {scene_path}")
    print("[INFO]: Simulation is active; stop it with Ctrl+C.")

    while simulation_app.is_running():
        simulation_app.update()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
