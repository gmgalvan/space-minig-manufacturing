# Stack NVIDIA para minería y manufactura espacial

Este documento ordena las tecnologías de NVIDIA relevantes para nuestros laboratorios. La prioridad inicial es construir un **gemelo digital operativo** de una operación de excavación y procesamiento lunar: terreno, rover, herramienta, sensores, control y métricas de producción.

> Alcance: esta es una selección técnica para simulación, no una lista de productos a comprar. Antes de depender de una herramienta, confirmar licencia, compatibilidad de GPU, sistema operativo y versión vigente.

## Arquitectura recomendada

```text
OpenUSD ──> Omniverse Kit ──> RTX + PhysX
                  │                 │
                  │                 └── Isaac Sim: rover, brazo, sensores, ROS 2
                  │
                  ├── Replicator: datos sintéticos de cámaras
                  └── Kit-CAE: datos de térmica, FEM, CFD y modelos sustitutos

Isaac Lab ──> entrenamiento / optimización de políticas de operación
Isaac ROS + Jetson ──> percepción y control en el robot físico
CUDA-X / Modulus / cuOpt ──> cómputo científico y planificación especializada
```

## Tecnologías núcleo

| Tecnología | Rol | Uso propuesto en este proyecto | Prioridad |
| --- | --- | --- | --- |
| [OpenUSD](https://docs.omniverse.nvidia.com/dev-guide/latest/dev-usd.html) | Formato y composición de mundos 3D | Fuente de verdad del sitio minero, activos, capas de escenario y variantes. | P0 |
| [Omniverse Kit](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html) | SDK para aplicaciones/extensiones Omniverse | Crear la aplicación de laboratorio, UI, scripts Python y extensiones propias. | P0 |
| [Omniverse RTX Renderer](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html) | Render físicamente basado acelerado por RTX | Visualización y cámaras sintéticas con iluminación extrema lunar. | P0 |
| [Omni Physics / PhysX](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/latest/extensions/runtime/source/omni.physx/docs/index.html) | Motor de física conectado a USD | Gravedad lunar, colisiones, articulaciones, ruedas, brazo y herramientas. | P0 |
| [Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_simulation/index.html) | Simulador de robótica sobre Omniverse | Prototipar rovers, excavadoras, manipuladores, sensores y control. | P0 |
| [Isaac Lab](https://isaac-sim.github.io/IsaacLab/develop/source/setup/ecosystem.html) | Framework modular de aprendizaje robótico | Entrenar políticas para excavación, carga, navegación y manipulación bajo incertidumbre. | P1 |
| [Isaac Replicator / IRO](https://docs.isaacsim.omniverse.nvidia.com/latest/action_and_event_data_generation/tutorial_replicator_object.html) | Generación de datos sintéticos | Crear imágenes y etiquetas para detectar rocas, obstáculos, tolvas y estado del proceso. | P1 |
| [Isaac ROS](https://developer.nvidia.com/isaac/ros) | Paquetes ROS 2 acelerados con CUDA | Llevar percepción, navegación y sensores de la simulación al robot real. | P1 |
| [Jetson](https://developer.nvidia.com/embedded-computing) | Cómputo embebido en el borde | Objetivo de despliegue para autonomía a bordo; no es necesario para el MVP. | P2 |
| [Kit-CAE](https://docs.omniverse.nvidia.com/guide-kit-cae/latest/index.html) | Integración y visualización de datos CAE | Superponer campos térmicos, estructurales o de flujo sobre el gemelo digital. | P2 |
| [NVIDIA Modulus](https://developer.nvidia.com/modulus) | Física computacional y modelos ML guiados por ecuaciones | Modelos sustitutos de transferencia térmica, polvo o procesamiento cuando haya datos/ecuaciones. | P2 |
| [CUDA-X](https://developer.nvidia.com/cuda-x) | Bibliotecas GPU de cómputo acelerado | Acelerar cálculo numérico, visión, IA y pre/postproceso de simulaciones. | P2 |
| [cuOpt](https://developer.nvidia.com/cuopt) | Optimización de decisiones y rutas | Programar flota, recargas, rutas y turnos de extracción; integrar tras validar el modelo base. | P3 |

**Prioridad:** P0 = necesaria para el primer laboratorio; P1 = siguiente iteración; P2 = cuando el caso lo justifique; P3 = optimización de sistema completo.

## Qué aporta cada capa

### 1. Mundo, activos y escenarios: OpenUSD + Omniverse Kit

OpenUSD debe ser el contrato entre disciplinas. Un escenario puede componerse por capas: terreno lunar, rover, planta ISRU, sensores y una capa de experimento que cambie parámetros sin duplicar los activos. Kit proporciona el entorno extensible en Python/C++ para cargar ese mundo, automatizar corridas y construir herramientas de inspección.

Convención inicial de activos:

```text
assets/usd/
├── environments/moon_regolith/
├── robots/excavator_rover/
├── facilities/isru_plant/
└── sensors/
```

### 2. Física y robótica: PhysX + Isaac Sim

Isaac Sim es el punto de arranque para la simulación del rover. Su base física conecta contenido USD con PhysX; modelaremos cuerpos rígidos, colisiones, masas, articulaciones y actuadores. La interacción altamente granular del regolito es un riesgo de fidelidad: en el MVP se usará una aproximación de terreno y se documentará como limitación, antes de afirmar rendimiento de excavación real.

Variables mínimas del primer escenario:

- gravedad: `1.62 m/s²`;
- masa, centro de masa y límites articulares explícitos;
- pendiente, rugosidad y fricción del terreno como parámetros;
- potencia de tracción/herramienta y estado de batería;
- cámaras, IMU y odometría simuladas.

### 3. Percepción y autonomía: Replicator, Isaac Lab e Isaac ROS

Replicator genera variaciones controladas de escena y etiquetas para entrenar o probar visión. Isaac Lab permite ejecutar muchos entornos en paralelo para aprendizaje por refuerzo, demostraciones o planificación; entrenaremos sólo después de tener una política base y métricas deterministas. Isaac ROS es el puente ROS 2 para ejecutar la misma cadena de percepción en hardware acelerado.

### 4. Ingeniería multidominio y optimización: Kit-CAE, Modulus, CUDA-X y cuOpt

Estas piezas entran cuando el gemelo ya responda preguntas operativas. Kit-CAE permite contextualizar datos de solvers científicos en USD; Modulus es candidato a modelos sustitutos basados en física; CUDA-X sustenta cómputo GPU; cuOpt serviría para optimización combinatoria de flota y logística. Ninguna sustituye la validación contra datos experimentales.

## Roadmap de adopción

1. **MVP — rover sobre terreno lunar:** escena USD, gravedad lunar, PhysX, teleoperación/control básico, trayectoria, energía y masa movida.
2. **Sensores y seguridad:** cámaras RTX, IMU/LiDAR si aplica, detección sintética de rocas y zonas transitables.
3. **Operación autónoma:** tarea en Isaac Lab con aleatorización de pendientes, fricción, iluminación y carga útil.
4. **Integración física:** modelo de planta ISRU y datos térmicos/estructurales mediante Kit-CAE o solver externo.
5. **Flota:** planificación de rutas e inventario; evaluar cuOpt sólo si el problema excede un planificador simple.

## Decisiones iniciales

- El formato canónico de escena será **USD**, no un archivo propietario de una herramienta de CAD.
- El primer modelo validará navegación y manejo de carga; no intentará resolver de inmediato la mecánica granular del regolito.
- Se ejecutará en modo sin interfaz para lotes de experimentos y con visualización RTX para inspección y datos sintéticos.
- Cada escenario declarará versión de Isaac Sim, driver, GPU, semilla y parámetros físicos.

## Fuentes oficiales

- [Omniverse Kit y sus componentes](https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/overview.html)
- [OpenUSD en Omniverse](https://docs.omniverse.nvidia.com/dev-guide/latest/dev-usd.html)
- [Guía de arquitectura de física Omniverse](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.3/index.html)
- [Simulación de robots en Isaac Sim](https://docs.isaacsim.omniverse.nvidia.com/latest/robot_simulation/index.html)
- [Ecosistema Isaac Lab](https://isaac-sim.github.io/IsaacLab/develop/source/setup/ecosystem.html)
- [Plataforma Isaac e Isaac ROS](https://developer.nvidia.com/isaac/)
- [Kit-CAE](https://docs.omniverse.nvidia.com/guide-kit-cae/latest/index.html)

_Última verificación: 12 de agosto de 2026._
