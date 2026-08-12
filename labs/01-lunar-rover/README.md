# Lab 01 — Rover lunar mínimo en OpenUSD e Isaac Sim

## Resultado

Este laboratorio genera un rover OpenUSD, añade física PhysX, lo coloca en una escena con gravedad lunar y activa las cuatro ruedas desde Isaac Sim. La corrida de referencia desplazó el chasis `3.928 m` en `8.01 s` con una velocidad angular objetivo de `120 grados/s`.

El propósito es validar la cadena completa OpenUSD → PhysX → Isaac Sim → livestream → métrica. No es todavía un modelo validado de movilidad sobre regolito.

## Pregunta y criterio de éxito

**Pregunta:** ¿podemos describir un rover portable en OpenUSD y moverlo mediante cuatro juntas revolutas en NVIDIA Isaac Sim?

**Criterios de éxito:**

- el USD usa metros y eje vertical `Z`;
- existen chasis, cuatro ruedas y sensor frontal;
- la escena usa gravedad de `1.62 m/s²`;
- Isaac Sim abre todas las referencias;
- se configuran los cuatro motores sin advertencias de juntas desalineadas;
- el desplazamiento medido del chasis es positivo.

## Arquitectura del laboratorio

```text
create_rover.py
  │ genera geometría y metadatos
  ▼
assets/usd/robots/lunar_rover_v0.usda
  │ añade cuerpos rígidos, colisiones, masas y juntas
  ▼
prepare_physics_rover.py
  ▼
assets/usd/robots/lunar_rover_physics_v0.usda
  │ se referencia desde una escena portable
  ▼
create_lunar_scene.py
  ▼
labs/01-lunar-rover/lunar_rover_scene_v0.usda
  │
  ├── run_lunar_rover.py       abre e inspecciona
  └── drive_lunar_rover.py     aplica motores y mide distancia
```

## Modelo actual

| Elemento | Valor |
| --- | --- |
| Chasis visual | `1.20 × 0.80 × 0.35 m` |
| Radio de rueda | `0.18 m` |
| Altura/longitud axial de rueda | `0.12 m` |
| Masa de chasis físico | `35 kg` |
| Masa por rueda | `2.5 kg` |
| Masa física total | `45 kg` |
| Gravedad | `1.62 m/s²` hacia `-Z` |
| Terreno | cubo estático `20 × 20 × 0.10 m` |
| Eje de rueda/junta | `Y` |
| Motor predeterminado | `120 grados/s`, fuerza máxima `250`, damping `2` |
| Duración predeterminada | `8 s` |

La cámara frontal y antena son geometría/metadata; aún no producen observaciones de sensor.

## Parte A — Preparación local con `uv`

### 1. Entrar a la raíz

Todos los comandos locales siguientes se ejecutan desde:

```bash
cd ~/memo/space-minig-manufacturing
```

Ajusta la ruta si clonaste el repositorio en otro lugar.

### 2. Instalar `uv`

Sólo la primera vez:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

Al abrir una terminal nueva, normalmente `~/.local/bin` ya estará disponible. Si `uv: command not found` reaparece, vuelve a exportar el `PATH` o reinicia la terminal.

### 3. Crear el entorno e instalar OpenUSD Python

```bash
uv venv --python 3.10
uv pip install --python .venv/bin/python usd-core
```

Si `.venv` ya existe y `uv` pregunta si debe reemplazarlo, responde `no` cuando quieras conservarlo. Para comprobar el paquete:

```bash
uv run --python .venv/bin/python -c 'from pxr import Usd; print(Usd.GetVersion())'
```

## Parte B — Generar todos los USD

Ejecuta en este orden:

```bash
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py
```

Salida esperada:

```text
Rover creado: .../assets/usd/robots/lunar_rover_v0.usda
Validación correcta: rover, unidades y 4 ruedas presentes.
Variante física creada: .../assets/usd/robots/lunar_rover_physics_v0.usda
Escena lunar creada: .../labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

Comprobar los archivos:

```bash
ls -lh assets/usd/robots/lunar_rover_v0.usda \
  assets/usd/robots/lunar_rover_physics_v0.usda \
  labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

La escena usa una referencia relativa:

```text
../../assets/usd/robots/lunar_rover_physics_v0.usda
```

Esto permite clonar el repositorio en otra máquina sin corregir rutas absolutas.

## Parte C — Publicar antes de usar Brev

Revisa y publica los cambios:

```bash
git status --short
git diff --check
git add README.md AGENTS.md docs labs assets .gitignore
git commit -m "docs: document reproducible lunar rover workflow"
git push
```

Adapta el `git add` si no quieres incluir todos esos directorios. La identidad de Git exclusiva del repositorio se configura con:

```bash
git config user.name "TU NOMBRE"
git config user.email "TU EMAIL"
```

## Parte D — Preparar NVIDIA Brev

Sigue la guía completa [NVIDIA Brev + Isaac Launchable](../../docs/nvidia-brev-isaac-launchable.md). El resumen es:

1. desplegar **Isaac Launchable** sobre una GPU RTX, en esta prueba una L40S;
2. esperar `RUNNING`, `COMPLETED` y `READY`;
3. entrar con `brev shell space-mining-lab-01`;
4. levantar/reparar los contenedores si el lifecycle script falla;
5. clonar el repositorio dentro de `/workspace` del contenedor `vscode`;
6. abrir el enlace `isaac` y añadir `/viewer/` si hace falta.

## Parte E — Sincronizar cambios en el contenedor

Desde el host remoto, normalmente en `~/isaac-launchable/isaac-lab`:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git pull --ff-only'
```

Hay dos copias independientes:

- host remoto: `~/space-minig-manufacturing`;
- contenedor Isaac: `/workspace/space-minig-manufacturing`.

La simulación usa la segunda. Hacer `git pull` sólo en el host no actualiza el contenedor.

## Parte F — Abrir la escena sin motores

Desde el host remoto:

```bash
cd ~/isaac-launchable/isaac-lab

docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/run_lunar_rover.py --livestream 2 --viz kit'
```

Esperar:

```text
[INFO]: Escena lunar abierta: /workspace/space-minig-manufacturing/labs/01-lunar-rover/lunar_rover_scene_v0.usda
[INFO]: Simulación activa; detener con Ctrl+C.
```

Mantén esa terminal abierta. En el navegador abre el servicio Isaac y visita `/viewer/`. El botón Play de la interfaz no es necesario: el script ya ejecuta `timeline.play()`.

Para cerrar, vuelve a la terminal y presiona `Ctrl+C` una vez. Si ves de nuevo el prompt `ubuntu@brev-...$`, el proceso terminó.

## Parte G — Ejecutar la prueba de tracción

Asegúrate de que no haya otro Isaac Sim usando el livestream. Luego ejecuta:

```bash
docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/drive_lunar_rover.py --livestream 2 --viz kit --duration 8 --wheel-speed 120'
```

El script:

1. abre la escena;
2. busca las cuatro juntas bajo `/World/LunarRover/Joints`;
3. aplica `UsdPhysics.DriveAPI` angular;
4. inicia la línea de tiempo;
5. mide la transformación mundial del chasis;
6. detiene la física después de la duración solicitada;
7. conserva la aplicación abierta para inspección.

Salida de referencia observada:

```text
[DEBUG]: Escena cargada; configurando motores...
[DEBUG]: Motor configurado: /World/LunarRover/Joints/FrontLeftAxle
[DEBUG]: Motor configurado: /World/LunarRover/Joints/FrontRightAxle
[DEBUG]: Motor configurado: /World/LunarRover/Joints/RearLeftAxle
[DEBUG]: Motor configurado: /World/LunarRover/Joints/RearRightAxle
[INFO]: Motores activos durante 8.0 s.
[RESULT]: desplazamiento=3.928 m; duración=8.01 s
[INFO]: La escena queda abierta para inspección. Detener con Ctrl+C.
```

La distancia puede variar según versión, paso de simulación y estado del entorno. Para una prueba aproximada de `5 m` usando la velocidad observada:

```bash
docker exec -it -u ubuntu:ubuntu -w /workspace/isaaclab vscode bash -lc \
  './isaaclab.sh -p /workspace/space-minig-manufacturing/labs/01-lunar-rover/scripts/drive_lunar_rover.py --livestream 2 --viz kit --duration 10.2 --wheel-speed 120'
```

Esto no controla exactamente 5 m; sólo aumenta el tiempo. Un controlador por distancia es una mejora pendiente.

## Inspección visual

En el panel **Stage** debe aparecer:

```text
/World
├── PhysicsScene
├── LunarGround
└── LunarRover
    ├── Chassis
    ├── Wheels
    │   ├── FrontLeft
    │   ├── FrontRight
    │   ├── RearLeft
    │   └── RearRight
    ├── Sensors
    └── Joints
```

Puedes seleccionar `LunarRover` y presionar `F` para enfocar la cámara. Usa rueda del ratón para acercar/alejar y `Alt` + botones del ratón para orbitar según la configuración del viewer.

## Advertencias conocidas

Estas advertencias aparecieron en la ejecución remota y no bloquearon la prueba:

```text
Failed to open [/var/run/utmp]
Active user not found. Using default user [kiosk]
GLFW initialization failed
Possible version incompatibility ... IStageReaderWriter ...
```

Son compatibles con un entorno remoto/headless si después aparecen `Simulation App Startup Complete`, `app ready` y el resultado.

Esta advertencia sí indica un error del modelo:

```text
CreateJoint - found a joint with disjointed body transforms
```

Si aparece, no aceptes la corrida. Regenera con los scripts actuales y confirma que cada `localPos0` coincide con la posición de su rueda y que `localPos1` es `(0, 0, 0)`.

## Repetir una corrida

1. Presiona `Ctrl+C` en el proceso actual.
2. Confirma que regresó el prompt.
3. Ejecuta `git pull --ff-only` dentro del contenedor si hubo cambios.
4. vuelve a lanzar `drive_lunar_rover.py`.
5. Recarga `/viewer/` si queda en `WAITING FOR STREAM`.

No lances dos procesos Isaac Sim con livestream al mismo tiempo: pueden competir por la sesión y producir `Got stop event while waiting for client connection`.

## Limitaciones

- suelo plano y rígido;
- fricción no calibrada contra regolito;
- ruedas sin suspensión ni dirección independiente;
- motor con parámetros provisionales;
- sin batería, potencia, par medido ni deslizamiento reportado;
- sin sensores funcionales;
- sin validación contra hardware o datos lunares.

## Próximas mejoras

1. detener automáticamente al alcanzar una distancia objetivo;
2. registrar posición, velocidad y consumo por paso;
3. parametrizar fricción y pendiente;
4. añadir suspensión y control diferencial;
5. modelar energía y estado de batería;
6. agregar cámara/IMU y una tarea de navegación.
