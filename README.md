# Space Mining & Manufacturing

Laboratorio abierto para diseñar y probar sistemas de minería, robótica y manufactura fuera de la Tierra. El proyecto usa modelos pequeños y reproducibles para convertir preguntas de ingeniería —movilidad, extracción, procesamiento, energía y logística— en código, escenas OpenUSD y resultados medibles.

## Estado actual

El primer laboratorio funcional es un rover lunar mínimo:

- activo geométrico creado con OpenUSD;
- variante física con masas, colisiones y cuatro juntas revolutas;
- escenario con terreno y gravedad lunar de `1.62 m/s²`;
- ejecución remota en NVIDIA Isaac Sim/Isaac Lab mediante NVIDIA Brev;
- cuatro motores PhysX a `120 grados/s`;
- prueba observada: `3.928 m` de desplazamiento en `8.01 s`, aproximadamente `0.49 m/s`.

El resultado es una prueba de integración, no una predicción del desempeño de un rover real. El suelo es una placa rígida, no hay modelo granular de regolito y aún no se calcula consumo eléctrico.

## Mapa de documentación

| Documento | Cuándo usarlo |
| --- | --- |
| [Lab 01 — rover lunar](labs/01-lunar-rover/README.md) | Crear, validar y ejecutar el rover paso a paso. |
| [NVIDIA Brev + Isaac Launchable](docs/nvidia-brev-isaac-launchable.md) | Repetir el despliegue remoto completo, resolver fallos y controlar el coste. |
| [Stack NVIDIA](docs/nvidia-omniverse-y-simulacion.md) | Entender qué tecnología NVIDIA corresponde a cada capa del proyecto. |
| [Guía para agentes y colaboradores](AGENTS.md) | Mantener convenciones, reproducibilidad y calidad al modificar el repositorio. |

## Inicio rápido local

La parte OpenUSD funciona localmente sin instalar Isaac Sim. Requisitos:

- Linux o WSL 2;
- Git;
- `curl` para instalar `uv`;
- Python 3.10 administrado por `uv`.

Desde la raíz del repositorio:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

uv venv --python 3.10
uv pip install --python .venv/bin/python usd-core

uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py
```

Salidas esperadas:

```text
assets/usd/robots/lunar_rover_v0.usda
assets/usd/robots/lunar_rover_physics_v0.usda
labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

La validación debe terminar con:

```text
Validación correcta: rover, unidades y 4 ruedas presentes.
```

Para la simulación RTX/PhysX completa, continúa con la [guía de NVIDIA Brev](docs/nvidia-brev-isaac-launchable.md).

## Estructura del repositorio

```text
.
├── assets/
│   └── usd/robots/                 # Activos OpenUSD visual y físico
├── docs/
│   ├── nvidia-brev-isaac-launchable.md
│   └── nvidia-omniverse-y-simulacion.md
├── labs/
│   └── 01-lunar-rover/
│       ├── README.md
│       ├── lunar_rover_scene_v0.usda
│       └── scripts/
├── .gitignore
├── AGENTS.md
└── README.md
```

Los archivos `.usda` se conservan en texto para poder revisar referencias, unidades, masas, juntas y cambios físicos mediante Git.

## Flujo de trabajo reproducible

1. Cambiar los scripts fuente, no sólo el archivo USD generado.
2. Regenerar el activo visual, la variante física y la escena.
3. Ejecutar `validate_rover.py` localmente.
4. Hacer commit y `git push`.
5. En Brev, ejecutar `git pull` dentro del contenedor `vscode`.
6. Ejecutar la simulación y registrar parámetros, versiones y resultado.
7. Detener el proceso con `Ctrl+C` y detener la instancia cuando termine la sesión.

## Roadmap

1. **Movilidad lunar:** mejorar fricción, suspensión, control de distancia y telemetría.
2. **Sensores:** cámara, IMU, LiDAR y datos sintéticos con Replicator.
3. **Extracción:** herramienta, carga útil, masa movida, desgaste y energía.
4. **Procesamiento ISRU:** balances de masa y energía para agua, oxígeno y metales.
5. **Manufactura:** sinterizado e impresión con material local frente a carga enviada desde Tierra.
6. **Operación integrada:** flota, inventario, mantenimiento, fallos y economía de misión.

## Convenciones

- Usar SI internamente: kg, m, s, K, W y Pa.
- Separar hechos, mediciones, estimaciones y supuestos.
- Versionar parámetros y comandos junto con el experimento.
- No tratar una visualización exitosa como validación física.
- Documentar limitaciones que puedan cambiar una conclusión.

## Seguridad y coste

Una instancia GPU remota genera cargos mientras está activa. Antes de desplegar, revisa el precio mostrado por Brev. No publiques URLs privadas, IP, códigos de acceso ni credenciales. Guarda el trabajo en Git antes de detener o eliminar una instancia.

## Contribuir

Cada laboratorio debe responder una pregunta concreta y definir una métrica de éxito. Consulta [AGENTS.md](AGENTS.md) antes de implementar cambios.
