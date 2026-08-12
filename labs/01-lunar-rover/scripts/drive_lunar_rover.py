"""Drive the Lab 01 rover using PhysX motors on all four wheels."""

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

parser = argparse.ArgumentParser(description="Lunar rover traction test.")
parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE_PATH)
parser.add_argument("--duration", type=float, default=8.0, help="Drive duration in seconds.")
parser.add_argument("--wheel-speed", type=float, default=120.0, help="Target angular velocity in degrees/s.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


def main() -> None:
    import omni.timeline
    import omni.usd
    from pxr import Usd, UsdGeom, UsdPhysics

    scene_path = args_cli.scene.expanduser().resolve()
    if not scene_path.is_file():
        raise FileNotFoundError(f"USD scene does not exist: {scene_path}")

    context = omni.usd.get_context()
    if not context.open_stage(str(scene_path)):
        raise RuntimeError(f"Could not open: {scene_path}")
    for _ in range(90):
        simulation_app.update()

    stage = context.get_stage()
    print("[DEBUG]: Scene loaded; configuring motors...", flush=True)
    for joint_path in WHEEL_JOINTS:
        joint = stage.GetPrimAtPath(joint_path)
        if not joint.IsValid():
            raise RuntimeError(f"Missing joint: {joint_path}")
        drive = UsdPhysics.DriveAPI.Apply(joint, "angular")
        drive.CreateTypeAttr("force")
        drive.CreateTargetVelocityAttr(args_cli.wheel_speed)
        drive.CreateMaxForceAttr(250.0)
        drive.CreateDampingAttr(2.0)
        drive.CreateStiffnessAttr(0.0)
        print(f"[DEBUG]: Motor configured: {joint_path}", flush=True)

    chassis_prim = stage.GetPrimAtPath("/World/LunarRover/Chassis")
    if not chassis_prim.IsValid():
        raise RuntimeError("The chassis rigid body is missing.")
    chassis = UsdGeom.Xformable(chassis_prim)
    time_code = Usd.TimeCode.Default()
    start_position = chassis.ComputeLocalToWorldTransform(time_code).ExtractTranslation()
    timeline = omni.timeline.get_timeline_interface()
    timeline.play()
    print(f"[INFO]: Motors active for {args_cli.duration:.1f} s.", flush=True)

    elapsed = 0.0
    previous_time = timeline.get_current_time()
    while simulation_app.is_running() and elapsed < args_cli.duration:
        simulation_app.update()
        current_time = timeline.get_current_time()
        elapsed += max(0.0, current_time - previous_time)
        previous_time = current_time

    timeline.stop()
    end_position = chassis.ComputeLocalToWorldTransform(time_code).ExtractTranslation()
    displacement_m = (end_position - start_position).GetLength()
    print(f"[RESULT]: displacement={displacement_m:.3f} m; duration={elapsed:.2f} s", flush=True)
    print("[INFO]: The scene remains open for inspection. Stop it with Ctrl+C.", flush=True)

    while simulation_app.is_running():
        simulation_app.update()


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        import traceback

        traceback.print_exc()
        raise
    finally:
        simulation_app.close()
