"""Generate the minimal lunar rover OpenUSD asset."""

from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = REPOSITORY_ROOT / "assets" / "usd" / "robots" / "lunar_rover_v0.usda"

LUNAR_GRAVITY_M_S2 = 1.62


def define_box(stage: Usd.Stage, path: str, size: tuple[float, float, float], position: tuple[float, float, float]):
    """Create a box centered at `position`, with dimensions in meters."""
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(1.0)
    cube.AddTranslateOp().Set(Gf.Vec3d(*position))
    cube.AddScaleOp().Set(Gf.Vec3f(*size))
    return cube


def define_wheel(stage: Usd.Stage, name: str, position: tuple[float, float, float]):
    """Create a visual wheel whose axis runs along Y."""
    wheel = UsdGeom.Cylinder.Define(stage, f"/LunarRover/Wheels/{name}")
    wheel.CreateRadiusAttr(0.18)
    wheel.CreateHeightAttr(0.12)
    wheel.CreateAxisAttr(UsdGeom.Tokens.y)
    wheel.AddTranslateOp().Set(Gf.Vec3d(*position))
    wheel.GetPrim().SetCustomDataByKey("component", "wheel")
    return wheel


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    stage = Usd.Stage.CreateNew(str(OUTPUT_PATH))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    rover = UsdGeom.Xform.Define(stage, "/LunarRover")
    rover.GetPrim().SetCustomDataByKey("description", "Minimal lunar rover for Lab 01")
    rover.GetPrim().SetCustomDataByKey("mass_kg", 45.0)
    rover.GetPrim().SetCustomDataByKey("lunar_gravity_m_s2", LUNAR_GRAVITY_M_S2)

    UsdGeom.Xform.Define(stage, "/LunarRover/Chassis")
    define_box(stage, "/LunarRover/Chassis/Body", (1.20, 0.80, 0.35), (0.0, 0.0, 0.53))
    define_box(stage, "/LunarRover/Chassis/SolarPanel", (0.95, 0.60, 0.03), (0.0, 0.0, 0.72))

    UsdGeom.Xform.Define(stage, "/LunarRover/Wheels")
    for name, position in {
        "FrontLeft": (0.42, 0.46, 0.18),
        "FrontRight": (0.42, -0.46, 0.18),
        "RearLeft": (-0.42, 0.46, 0.18),
        "RearRight": (-0.42, -0.46, 0.18),
    }.items():
        define_wheel(stage, name, position)

    sensors = UsdGeom.Xform.Define(stage, "/LunarRover/Sensors")
    sensors.GetPrim().SetCustomDataByKey("camera_fov_degrees", 90.0)
    define_box(stage, "/LunarRover/Sensors/FrontCamera", (0.10, 0.14, 0.08), (0.62, 0.0, 0.70))
    define_box(stage, "/LunarRover/Sensors/Antenna", (0.03, 0.03, 0.40), (-0.35, 0.0, 0.94))

    stage.SetDefaultPrim(rover.GetPrim())
    stage.GetRootLayer().Save()
    print(f"Rover created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
