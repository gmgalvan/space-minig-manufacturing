# Lab 01 — Rover lunar mínimo en OpenUSD

## Objetivo

Generar un rover lunar sencillo y legible en OpenUSD. Este activo será la base que abriremos más adelante en NVIDIA Isaac Sim para añadir física, terreno, sensores y control.

## Qué contiene

- Chasis de `1.20 × 0.80 × 0.35 m`.
- Cuatro ruedas de radio `0.18 m`.
- Cámara frontal y antena como marcadores visuales.
- Metadatos de masa y configuración de gravedad lunar (`1.62 m/s²`).

El archivo generado es geométrico y declarativo: aún **no** simula el movimiento. Es la manera correcta de separar la creación del activo de su futura simulación con PhysX.

## Preparación local con `uv`

Instala `uv` una sola vez si todavía no lo tienes:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Reabre la terminal o carga la ruta de `uv`, y desde la raíz del repositorio ejecuta:

```bash
uv venv --python 3.10
uv pip install --python .venv/bin/python usd-core
```

No se necesita `sudo` ni el paquete `python3.10-venv`: `uv` crea y gestiona el entorno.

## Generar el rover

```bash
.venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
```

Esto escribe `assets/usd/robots/lunar_rover_v0.usda`.

## Validar el archivo

```bash
.venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
```

La validación comprueba unidades, gravedad, componentes requeridos y número de ruedas.

## Preparar física y escena lunar

Con el activo visual validado, genera una variante con cuerpos rígidos, masas, colisionadores y juntas revolutas para las ruedas. Después genera una escena que lo referencia y define gravedad lunar:

```bash
uv run --python .venv/bin/python python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python python labs/01-lunar-rover/scripts/create_lunar_scene.py
```

El resultado para abrir en Isaac Sim será `labs/01-lunar-rover/lunar_rover_scene_v0.usda`.

## Próximo paso: sandbox NVIDIA

Al tener un sandbox NVIDIA con GPU RTX:

1. Crear un entorno con Python 3.12.
2. Instalar Isaac Sim.
3. Subir o clonar este repositorio en el sandbox.
4. Abrir `assets/usd/robots/lunar_rover_v0.usda`.
5. Añadir colisionadores, juntas de rueda, actuadores y un terreno con gravedad lunar.

No haremos esa instalación hasta tener disponible el sandbox, pues la Quadro T2000 local no tiene RT Cores ni VRAM suficientes para Isaac Sim.
