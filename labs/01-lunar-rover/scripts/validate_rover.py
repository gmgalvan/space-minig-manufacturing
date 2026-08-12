"""Validate the minimum required properties of the OpenUSD rover."""

from pathlib import Path

from pxr import Usd, UsdGeom


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ROVER_PATH = REPOSITORY_ROOT / "assets" / "usd" / "robots" / "lunar_rover_v0.usda"


def main() -> None:
    stage = Usd.Stage.Open(str(ROVER_PATH))
    if stage is None:
        raise RuntimeError(f"Could not open {ROVER_PATH}. Run create_rover.py first.")

    assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z
    assert UsdGeom.GetStageMetersPerUnit(stage) == 1.0

    rover = stage.GetPrimAtPath("/LunarRover")
    assert rover.IsValid(), "Missing root prim /LunarRover"
    assert rover.GetCustomDataByKey("mass_kg") == 45.0
    assert rover.GetCustomDataByKey("lunar_gravity_m_s2") == 1.62

    wheels = [prim for prim in stage.Traverse() if prim.GetCustomDataByKey("component") == "wheel"]
    assert len(wheels) == 4, f"Expected 4 wheels; found {len(wheels)}"
    assert stage.GetPrimAtPath("/LunarRover/Sensors/FrontCamera").IsValid()

    print("Validation passed: rover, units, and 4 wheels are present.")


if __name__ == "__main__":
    main()
