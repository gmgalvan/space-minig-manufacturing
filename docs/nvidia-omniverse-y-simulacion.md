# Stack NVIDIA para minería y manufactura espacial

Mapa técnico de las tecnologías NVIDIA que pueden apoyar estos laboratorios, desde un rover OpenUSD hasta un gemelo digital de extracción, procesamiento y manufactura lunar.

## Decisión actual

Para el MVP usamos:

```text
OpenUSD
  └── Isaac Sim sobre Omniverse Kit
        ├── PhysX: gravedad, colisiones, juntas y motores
        ├── RTX: visualización
        ├── WebRTC livestream: interfaz remota
        └── Isaac Lab: lanzamiento y futuras tareas de control/aprendizaje

NVIDIA Brev + L40S
  └── ejecución remota porque la GPU local no es adecuada para este flujo
```

El Lab 01 ya comprobó esta cadena con un desplazamiento de `3.928 m` en `8.01 s`. Esa cifra valida integración de software, no realismo sobre regolito.

## Arquitectura objetivo

```text
CAD / datos científicos / GIS
              │
              ▼
           OpenUSD  ◄──────────── capas y variantes del experimento
              │
              ▼
       Omniverse Kit + RTX
              │
        ┌─────┴───────────┐
        ▼                 ▼
   Isaac Sim            Kit-CAE
   PhysX/sensores       térmica/FEM/CFD
        │
   ┌────┴───────────┐
   ▼                ▼
Isaac Lab       Replicator
control/RL      datos sintéticos
   │
   ▼
Isaac ROS + Jetson ──► prototipo físico

CUDA-X / Modulus / cuOpt ──► cómputo, modelos sustitutos y planificación
```

## Tecnologías y prioridad

| Tecnología | Función | Uso en este proyecto | Prioridad |
| --- | --- | --- | --- |
| [OpenUSD](https://docs.omniverse.nvidia.com/dev-guide/latest/dev-usd.html) | composición de escenas 3D | fuente de verdad para activos, referencias, capas y variantes | P0, en uso |
| [Omniverse Kit](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html) | runtime y SDK extensible | aplicación, UI, scripting Python y carga de escenas | P0, en uso indirecto |
| [Omniverse RTX Renderer](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html) | render acelerado | inspección visual y futuras cámaras sintéticas | P0, en uso |
| [PhysX / Omni Physics](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/extensions/runtime/source/omni.physx/docs/index.html) | dinámica y colisiones | gravedad lunar, cuerpos rígidos, ruedas, juntas y actuadores | P0, en uso |
| [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_simulation/index.html) | simulación robótica sobre Kit | rover, excavadora, brazo, sensores y ROS 2 | P0, en uso |
| [Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html) | framework de aprendizaje y tareas robóticas | lanzamiento actual; después control, entornos paralelos y políticas | P0/P1, en uso básico |
| Livestream WebRTC | interfaz remota de Kit | observar Isaac Sim desde navegador a través de Brev | P0, en uso |
| [Isaac Sim Replicator](https://docs.isaacsim.omniverse.nvidia.com/latest/replicator_tutorials/index.html) | generación de datos sintéticos | imágenes, etiquetas y variación de iluminación/terreno | P1 |
| [Isaac ROS](https://developer.nvidia.com/isaac/ros) | ROS 2 acelerado | trasladar percepción/navegación de simulación a hardware | P1 |
| [Jetson](https://developer.nvidia.com/embedded-computing) | cómputo embebido | autonomía a bordo del prototipo físico | P2 |
| [Kit-CAE](https://docs.omniverse.nvidia.com/guide-kit-cae/latest/index.html) | visualización e integración CAE | campos térmicos, estructurales y de flujo en el gemelo | P2 |
| [NVIDIA Modulus](https://developer.nvidia.com/modulus) | IA guiada por física | modelos sustitutos para térmica, polvo o procesos | P2 |
| [CUDA-X](https://developer.nvidia.com/cuda-x) | bibliotecas GPU | visión, IA, cálculo científico y procesamiento masivo | P2 |
| [cuOpt](https://developer.nvidia.com/cuopt) | optimización de rutas/decisiones | flota, recarga, transporte e inventario | P3 |
| [NVIDIA Brev](https://brev.nvidia.com/) | aprovisionamiento GPU | sandbox reproducible con L40S e Isaac Launchable | infraestructura actual |

**Prioridad:** P0 es necesaria para el laboratorio actual; P1 corresponde a la siguiente fase; P2 entra cuando exista una pregunta multidominio concreta; P3 se reserva para optimización del sistema completo.

## Qué hace cada capa

### OpenUSD: contrato del mundo

OpenUSD describe jerarquía, transformaciones, geometría, metadatos, referencias y composición. En este repositorio:

```text
activo visual
  + variante física
  + escena/entorno
  + parámetros de experimento
```

La referencia de la escena al rover es relativa para mantener portabilidad. USD no ejecuta por sí solo la dinámica; expresa datos que Isaac Sim y PhysX interpretan.

### Omniverse Kit: aplicación y extensiones

Kit carga la escena, ejecuta extensiones y ofrece la interfaz que aparece en el viewer. Los mensajes `[ext: ...] startup`, `Simulation App Starting` y `app ready` pertenecen a este arranque. Para el Lab 01 no desarrollamos todavía una extensión propia: usamos scripts de Isaac Lab que inician Kit.

### PhysX: física del rover

El modelo actual incluye:

- gravedad `1.62 m/s²` hacia `-Z`;
- chasis rígido de `35 kg`;
- cuatro ruedas rígidas de `2.5 kg` cada una;
- colisión para chasis, ruedas y suelo;
- cuatro `RevoluteJoint` con eje `Y`;
- cuatro `DriveAPI` angulares configuradas al ejecutar.

Una advertencia de cuerpos de junta desalineados no es cosmética: indica que PhysX puede ensamblar las piezas mediante un salto. Los scripts actuales alinean `localPos0` con el centro de cada rueda y usan `localPos1 = (0, 0, 0)`.

### Isaac Sim: integración robótica

Isaac Sim aporta el stage vivo, la línea de tiempo, PhysX, RTX, sensores y herramientas de inspección. `run_lunar_rover.py` abre la escena; `drive_lunar_rover.py` aplica los motores y mide el desplazamiento mundial del chasis.

### Isaac Lab: experimentos y escalado

En el MVP, Isaac Lab proporciona `AppLauncher` y el entorno de ejecución. Más adelante debe encapsular:

- observaciones: pose, velocidad, IMU, cámara, batería y carga;
- acciones: velocidad/par de ruedas y herramienta;
- eventos: variaciones de fricción, pendiente, masa e iluminación;
- terminación: distancia, tiempo, vuelco, energía o colisión;
- métricas: productividad, Wh/m, deslizamiento y seguridad.

No conviene entrenar una política antes de contar con una política determinista y métricas verificables.

### RTX y Replicator: percepción

RTX sirve para inspección y render de sensores. Replicator permitirá generar conjuntos sintéticos con etiquetas para rocas, obstáculos, excavación y llenado de tolva. La iluminación lunar extrema debe variarse de forma controlada y registrar cada semilla.

### Isaac ROS y Jetson: sim-to-real

Isaac ROS puede ejecutar percepción y navegación aceleradas en ROS 2. Jetson es un objetivo posible para el prototipo; ninguno es necesario para demostrar el rover virtual. La transferencia a hardware exige calibración, latencia, ruido de sensor y límites térmicos/energéticos que el MVP no modela.

### Kit-CAE, Modulus, CUDA-X y cuOpt

Estas herramientas entran sólo cuando haya preguntas concretas:

- **Kit-CAE:** visualizar resultados de térmica, FEM o CFD dentro del contexto 3D;
- **Modulus:** aproximar soluciones físicas costosas después de contar con ecuaciones/datos de validación;
- **CUDA-X:** acelerar cálculo, visión y análisis;
- **cuOpt:** optimizar operaciones de flota cuando un planificador sencillo deje de ser suficiente.

## Hardware: local frente a nube

La máquina local reportó una Quadro T2000 Max-Q con `4 GiB` de VRAM. Es útil para:

- editar Python y `.usda`;
- ejecutar `usd-core` y validaciones estructurales;
- Git y documentación.

La sesión completa se ejecutó en una L40S remota porque Isaac Sim con RTX, Isaac Lab y livestream necesita mucha más memoria y un entorno compatible. Separar ambos flujos reduce coste:

```text
local: crear, validar, revisar y versionar
nube: integrar, renderizar, simular y medir
```

## Manifiesto de una corrida

Para poder comparar resultados, registra:

```yaml
date: 2026-08-12
git_commit: <hash>
gpu: NVIDIA L40S
driver: 595.71.05
cuda_reported: 13.2
isaac_sim: 6.0.1
isaac_lab: 3.0.0-beta2-post1
scene: labs/01-lunar-rover/lunar_rover_scene_v0.usda
script: labs/01-lunar-rover/scripts/drive_lunar_rover.py
duration_s: 8
wheel_speed_deg_s: 120
displacement_m: 3.928
```

El hash de commit es indispensable: una escena con el mismo nombre puede haber cambiado.

## Roadmap técnico

1. **Rover reproducible:** OpenUSD, PhysX, livestream y desplazamiento medido — completado como integración básica.
2. **Control por distancia:** detener en un objetivo y guardar telemetría.
3. **Terreno parametrizado:** pendiente, rugosidad y fricción; medir deslizamiento.
4. **Sensores:** cámara/IMU y datos sintéticos.
5. **Herramienta:** excavación aproximada, masa movida, energía y desgaste.
6. **Isaac Lab:** tarea paralela con aleatorización y política base.
7. **ISRU/CAE:** acoplar movilidad, inventario y procesamiento.
8. **Flota:** planificación y economía operacional.

## Límites científicos actuales

- El terreno no representa partículas de regolito.
- Fricción, motor y damping son provisionales.
- No hay suspensión ni modelo de neumático/rueda-terreno validado.
- No se mide torque, potencia o energía.
- La iluminación no está configurada como un escenario lunar científico.
- El resultado de distancia no se ha comparado con datos experimentales.

## Documentos operativos

- [Repetir el Lab 01](../labs/01-lunar-rover/README.md)
- [Desplegar en NVIDIA Brev](nvidia-brev-isaac-launchable.md)
- [Convenciones para colaboradores](../AGENTS.md)

## Fuentes oficiales

- [Omniverse Kit](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html)
- [OpenUSD en Omniverse](https://docs.omniverse.nvidia.com/dev-guide/latest/dev-usd.html)
- [Omni Physics](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/index.html)
- [Isaac Sim: simulación de robots](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_simulation/index.html)
- [Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/index.html)
- [Isaac ROS](https://developer.nvidia.com/isaac/ros)
- [Kit-CAE](https://docs.omniverse.nvidia.com/guide-kit-cae/latest/index.html)

_Última actualización del procedimiento: 12 de agosto de 2026._
