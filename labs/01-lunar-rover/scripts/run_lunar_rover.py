"""Abre y ejecuta la escena lunar del Lab 01 en Isaac Sim/Isaac Lab."""

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCENE_PATH = REPOSITORY_ROOT / "labs" / "01-lunar-rover" / "lunar_rover_scene_v0.usda"


parser = argparse.ArgumentParser(description="Ejecuta el rover lunar del Lab 01.")
parser.add_argument(
    "--scene",
    type=Path,
    default=DEFAULT_SCENE_PATH,
    help="Ruta absoluta o relativa a una escena USD.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


def main() -> None:
    """Carga la escena USD y mantiene activa la simulación para el livestream."""
    import omni.timeline
    import omni.usd

    scene_path = args_cli.scene.expanduser().resolve()
    if not scene_path.is_file():
        raise FileNotFoundError(f"No existe la escena USD: {scene_path}")

    usd_context = omni.usd.get_context()
    if not usd_context.open_stage(str(scene_path)):
        raise RuntimeError(f"Isaac Sim no pudo abrir la escena: {scene_path}")

    # Espera a que Kit termine de cargar referencias y capas de la escena.
    for _ in range(60):
        simulation_app.update()

    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    print(f"[INFO]: Escena lunar abierta: {scene_path}")
    print("[INFO]: Simulación activa; detener con Ctrl+C.")

    while simulation_app.is_running():
        simulation_app.update()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
