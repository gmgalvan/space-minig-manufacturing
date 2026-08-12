"""Valida las propiedades mínimas del rover OpenUSD."""

from pathlib import Path

from pxr import Usd, UsdGeom


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ROVER_PATH = REPOSITORY_ROOT / "assets" / "usd" / "robots" / "lunar_rover_v0.usda"


def main() -> None:
    stage = Usd.Stage.Open(str(ROVER_PATH))
    if stage is None:
        raise RuntimeError(f"No se pudo abrir {ROVER_PATH}. Ejecuta create_rover.py primero.")

    assert UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z
    assert UsdGeom.GetStageMetersPerUnit(stage) == 1.0

    rover = stage.GetPrimAtPath("/LunarRover")
    assert rover.IsValid(), "Falta el prim raíz /LunarRover"
    assert rover.GetCustomDataByKey("mass_kg") == 45.0
    assert rover.GetCustomDataByKey("lunar_gravity_m_s2") == 1.62

    wheels = [prim for prim in stage.Traverse() if prim.GetCustomDataByKey("component") == "wheel"]
    assert len(wheels) == 4, f"Se esperaban 4 ruedas; se encontraron {len(wheels)}"
    assert stage.GetPrimAtPath("/LunarRover/Sensors/FrontCamera").IsValid()

    print("Validación correcta: rover, unidades y 4 ruedas presentes.")


if __name__ == "__main__":
    main()
