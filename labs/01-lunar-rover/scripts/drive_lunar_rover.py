"""Hace avanzar el rover del Lab 01 con motores PhysX en las cuatro ruedas."""

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCENE_PATH = REPOSITORY_ROOT / "labs" / "01-lunar-rover" / "lunar_rover_scene_v0.usda"
WHEEL_JOINTS = [
    "/World/LunarRover/Joints/FrontLeftAxle",
    "/World/LunarRover/Joints/FrontRightAxle",
    "/World/LunarRover/Joints/RearLeftAxle",
    "/World/LunarRover/Joints/RearRightAxle",
]

parser = argparse.ArgumentParser(description="Prueba de tracción del rover lunar.")
parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE_PATH)
parser.add_argument("--duration", type=float, default=8.0, help="Segundos de avance.")
parser.add_argument("--wheel-speed", type=float, default=120.0, help="Velocidad angular objetivo (grados/s).")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


def main() -> None:
    import omni.timeline
    import omni.usd
    from pxr import Usd, UsdPhysics

    scene_path = args_cli.scene.expanduser().resolve()
    if not scene_path.is_file():
        raise FileNotFoundError(f"No existe la escena USD: {scene_path}")

    context = omni.usd.get_context()
    if not context.open_stage(str(scene_path)):
        raise RuntimeError(f"No se pudo abrir: {scene_path}")
    for _ in range(90):
        simulation_app.update()

    stage = context.get_stage()
    for joint_path in WHEEL_JOINTS:
        joint = stage.GetPrimAtPath(joint_path)
        if not joint.IsValid():
            raise RuntimeError(f"Falta la junta: {joint_path}")
        drive = UsdPhysics.DriveAPI.Apply(joint, "angular")
        drive.CreateTypeAttr("force")
        drive.CreateTargetVelocityAttr(args_cli.wheel_speed)
        drive.CreateMaxForceAttr(250.0)
        drive.CreateDampingAttr(2.0)
        drive.CreateStiffnessAttr(0.0)

    rover = stage.GetPrimAtPath("/World/LunarRover")
    time_code = Usd.TimeCode.Default()
    start_position = rover.ComputeLocalToWorldTransform(time_code).ExtractTranslation()
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    print(f"[INFO]: Motores activos durante {args_cli.duration:.1f} s.")

    elapsed = 0.0
    previous_time = timeline.get_current_time()
    while simulation_app.is_running() and elapsed < args_cli.duration:
        simulation_app.update()
        current_time = timeline.get_current_time()
        elapsed += max(0.0, current_time - previous_time)
        previous_time = current_time

    timeline.stop()
    end_position = rover.ComputeLocalToWorldTransform(time_code).ExtractTranslation()
    displacement_m = (end_position - start_position).GetLength()
    print(f"[RESULT]: desplazamiento={displacement_m:.3f} m; duración={elapsed:.2f} s")
    print("[INFO]: La escena queda abierta para inspección. Detener con Ctrl+C.")

    while simulation_app.is_running():
        simulation_app.update()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
