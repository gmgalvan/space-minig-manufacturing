"""Crea una escena lunar mínima que referencia el rover preparado para física."""

import os
from pathlib import Path

from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ROVER_PATH = REPOSITORY_ROOT / "assets" / "usd" / "robots" / "lunar_rover_physics_v0.usda"
OUTPUT_PATH = REPOSITORY_ROOT / "labs" / "01-lunar-rover" / "lunar_rover_scene_v0.usda"


def main() -> None:
    if not ROVER_PATH.exists():
        raise RuntimeError("Primero ejecuta prepare_physics_rover.py.")

    stage = Usd.Stage.CreateNew(str(OUTPUT_PATH))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    physics_scene = UsdPhysics.Scene.Define(stage, "/World/PhysicsScene")
    physics_scene.CreateGravityDirectionAttr(Gf.Vec3f(0.0, 0.0, -1.0))
    physics_scene.CreateGravityMagnitudeAttr(1.62)

    ground = UsdGeom.Cube.Define(stage, "/World/LunarGround")
    ground.CreateSizeAttr(1.0)
    ground.AddScaleOp().Set(Gf.Vec3f(20.0, 20.0, 0.10))
    ground.AddTranslateOp().Set(Gf.Vec3d(0.0, 0.0, -0.05))
    UsdPhysics.CollisionAPI.Apply(ground.GetPrim())
    ground.GetPrim().SetCustomDataByKey("material", "regolith_placeholder")

    rover = UsdGeom.Xform.Define(stage, "/World/LunarRover")
    rover_reference = os.path.relpath(ROVER_PATH, start=OUTPUT_PATH.parent)
    rover.GetPrim().GetReferences().AddReference(
        assetPath=rover_reference, primPath=Sdf.Path("/LunarRover")
    )

    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    stage.GetRootLayer().Save()
    print(f"Escena lunar creada: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
