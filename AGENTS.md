# Guía para agentes y colaboradores

Este repositorio explora minería y manufactura espacial mediante OpenUSD, NVIDIA Omniverse, Isaac Sim y modelos científicos. La prioridad es obtener experimentos claros, verificables y reproducibles antes de aumentar la fidelidad.

## Resultado primero

Toda contribución debe comenzar indicando:

1. pregunta de ingeniería;
2. métrica de éxito;
3. supuestos y unidades;
4. resultado esperado o criterio de aceptación;
5. limitaciones que impiden interpretar el resultado como realidad física.

Ejemplo para el Lab 01:

```text
Pregunta: ¿las cuatro ruedas y juntas PhysX pueden desplazar el rover?
Métrica: desplazamiento del chasis en metros durante una corrida de 8 s.
Entrada: velocidad objetivo de rueda = 120 grados/s.
Éxito: desplazamiento positivo, sin errores de juntas desalineadas.
Limitación: terreno rígido plano y sin modelo de energía.
```

## Organización

- `labs/`: experimentos autocontenidos. Cada laboratorio incluye objetivo, entradas, salidas, supuestos, comandos, resultado esperado y solución de problemas.
- `assets/`: activos compartidos. Los archivos generados deben indicar qué script es su fuente.
- `models/`: modelos reutilizables que no dependan de un único escenario.
- `data/raw/`: datos originales; no modificarlos.
- `data/processed/`: datos derivados y proceso que los produjo.
- `results/`: artefactos generados; no son fuente de verdad.
- `docs/`: arquitectura, instalación, operación, decisiones y referencias.

## Fuente y artefactos generados

En el Lab 01, el orden canónico es:

```text
create_rover.py
  └── assets/usd/robots/lunar_rover_v0.usda
        └── prepare_physics_rover.py
              └── assets/usd/robots/lunar_rover_physics_v0.usda
                    └── create_lunar_scene.py
                          └── labs/01-lunar-rover/lunar_rover_scene_v0.usda
```

Si cambia geometría, física o composición, modificar el script correspondiente y regenerar los `.usda`. No corregir únicamente el artefacto generado porque el cambio se perderá en la siguiente generación.

## Convenciones de modelado

- Usar SI internamente y expresar la unidad en nombres como `mass_kg`, `power_w` o `gravity_m_s2`.
- En USD, declarar `metersPerUnit = 1` y eje vertical `Z` salvo decisión documentada.
- Nombrar rutas de prim estables; los scripts de control dependen de ellas.
- Separar geometría visual, cuerpos rígidos, colisiones, juntas y escenario.
- Aplicar masa al cuerpo rígido correcto, no a un descendiente visual sin justificación.
- Alinear los anclajes de las juntas en las coordenadas locales de ambos cuerpos.
- Evitar números mágicos: cada valor físico debe tener nombre, unidad y procedencia o marcarse como provisional.
- Registrar semillas aleatorias cuando exista aleatorización.
- Verificar conservación de masa y energía cuando el laboratorio modele procesos físicos.

## Reproducibilidad obligatoria

Todo README de laboratorio debe incluir:

- versiones conocidas de software y hardware;
- ruta desde la cual se ejecuta cada comando;
- entradas y valores predeterminados;
- archivos de salida;
- texto o métrica esperada;
- cómo detener procesos persistentes;
- cómo limpiar o repetir sin destruir trabajo;
- síntomas conocidos y diagnóstico mínimo.

Para una corrida remota, registrar como mínimo:

```text
fecha
commit de Git
GPU
driver
CUDA
Isaac Sim
Isaac Lab
script y argumentos
resultado
advertencias relevantes
```

No incluir secretos, códigos temporales de login, IP públicas o URLs privadas en commits ni capturas públicas.

## Flujo para cambiar el Lab 01

Desde la raíz local:

```bash
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/validate_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/prepare_physics_rover.py
uv run --python .venv/bin/python labs/01-lunar-rover/scripts/create_lunar_scene.py
```

Después:

```bash
git diff --check
git status --short
```

En Brev, actualizar la copia dentro del contenedor:

```bash
docker exec -u ubuntu vscode bash -lc \
  'cd /workspace/space-minig-manufacturing && git pull --ff-only'
```

No asumir que la copia del host `~/space-minig-manufacturing` y la copia del contenedor `/workspace/space-minig-manufacturing` se actualizan juntas.

## Pruebas y criterios de aceptación

Antes de entregar cambios:

1. ejecutar la validación OpenUSD local;
2. revisar `git diff --check`;
3. si cambió física o control, ejecutar Isaac Sim;
4. confirmar que los cuatro motores se configuran;
5. comprobar desplazamiento y ausencia de advertencias nuevas sobre juntas;
6. actualizar el resultado documentado sólo si la corrida fue realmente observada.

Las advertencias headless de GLFW o `/var/run/utmp` pueden ser inocuas en Brev. Una advertencia de `joint with disjointed body transforms` sí afecta el modelo y debe corregirse, no ignorarse.

## Calidad de los cambios

- Preservar cambios ajenos y no eliminar datos o resultados sin autorización.
- Mantener cada cambio enfocado.
- Usar referencias USD relativas para que el repositorio sea portable.
- No agregar `.venv`, cachés, logs, credenciales ni archivos grandes accidentales.
- Preferir comandos no interactivos y documentar cuándo se necesita `Ctrl+C`.
- Cuando falten datos, usar un valor provisional claramente marcado y crear una nota de seguimiento.

## Git

Antes de publicar:

```bash
git status --short
git diff --check
git diff
```

Configurar identidad sólo para este repositorio cuando sea necesario:

```bash
git config user.name "TU NOMBRE"
git config user.email "TU EMAIL"
```

No guardar credenciales en archivos del repositorio.

## Comunicación

Explicar primero el resultado y después el procedimiento. Distinguir entre:

- **validación estructural:** el USD contiene los prims y metadatos esperados;
- **validación de integración:** Isaac Sim abre y ejecuta la escena;
- **validación física:** el modelo representa con precisión un sistema real.

El Lab 01 ya cumple las dos primeras de manera básica; todavía no constituye validación física de movilidad sobre regolito.
