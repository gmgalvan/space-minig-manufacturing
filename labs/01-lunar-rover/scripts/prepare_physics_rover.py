"""Crea una variante del rover preparada para PhysX/Isaac Sim."""

from pathlib import Path

from pxr import Gf, Usd, UsdPhysics


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SOURCE_PATH = REPOSITORY_ROOT / "assets" / "usd" / "robots" / "lunar_rover_v0.usda"
OUTPUT_PATH = REPOSITORY_ROOT / "assets" / "usd" / "robots" / "lunar_rover_physics_v0.usda"

WHEEL_POSITIONS_M = {
    "FrontLeft": (0.42, 0.46, 0.18),
    "FrontRight": (0.42, -0.46, 0.18),
    "RearLeft": (-0.42, 0.46, 0.18),
    "RearRight": (-0.42, -0.46, 0.18),
}
CHASSIS_POSITION_M = (0.0, 0.0, 0.53)


def add_rigid_body(prim: Usd.Prim, mass_kg: float) -> None:
    UsdPhysics.RigidBodyAPI.Apply(prim)
    UsdPhysics.CollisionAPI.Apply(prim)
    mass_api = UsdPhysics.MassAPI.Apply(prim)
    mass_api.CreateMassAttr(mass_kg)


def main() -> None:
    if not SOURCE_PATH.exists():
        raise RuntimeError("Primero ejecuta create_rover.py para generar el activo visual.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    stage = Usd.Stage.Open(str(SOURCE_PATH))
    stage.GetRootLayer().Export(str(OUTPUT_PATH))
    stage = Usd.Stage.Open(str(OUTPUT_PATH))

    chassis = stage.GetPrimAtPath("/LunarRover/Chassis/Body")
    add_rigid_body(chassis, mass_kg=35.0)
    chassis.SetCustomDataByKey("physics_role", "chassis")

    for wheel_name, wheel_position in WHEEL_POSITIONS_M.items():
        wheel_path = f"/LunarRover/Wheels/{wheel_name}"
        wheel = stage.GetPrimAtPath(wheel_path)
        add_rigid_body(wheel, mass_kg=2.5)

        joint = UsdPhysics.RevoluteJoint.Define(stage, f"/LunarRover/Joints/{wheel_name}Axle")
        joint.CreateBody0Rel().SetTargets([chassis.GetPath()])
        joint.CreateBody1Rel().SetTargets([wheel.GetPath()])
        joint.CreateAxisAttr("Y")
        joint.CreateLocalPos0Attr(
            Gf.Vec3f(
                wheel_position[0] - CHASSIS_POSITION_M[0],
                wheel_position[1] - CHASSIS_POSITION_M[1],
                wheel_position[2] - CHASSIS_POSITION_M[2],
            )
        )
        joint.CreateLocalPos1Attr(Gf.Vec3f(0.0, 0.0, 0.0))
        joint.GetPrim().SetCustomDataByKey("drive_candidate", True)

    rover = stage.GetPrimAtPath("/LunarRover")
    rover.SetCustomDataByKey("physics_ready", True)
    rover.SetCustomDataByKey("physics_backend_target", "NVIDIA PhysX / Isaac Sim")
    stage.GetRootLayer().Save()
    print(f"Variante física creada: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
