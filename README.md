# Space Mining & Manufacturing

Un laboratorio abierto para diseñar, probar y documentar sistemas de minería y manufactura fuera de la Tierra. Aquí convertiremos preguntas grandes —cómo extraer recursos, procesarlos y fabricar infraestructura en la Luna, asteroides u órbita— en simulaciones pequeñas, reproducibles y útiles.

## Visión

Construir un conjunto de laboratorios computacionales que ayuden a explorar una cadena completa de **ISRU** (*In-Situ Resource Utilization*):

1. Localizar y caracterizar recursos.
2. Extraer regolito, hielo o material asteroidal.
3. Refinar materias primas en condiciones espaciales.
4. Convertirlas en energía, propelente y productos manufacturados.
5. Comparar arquitecturas por masa, energía, tiempo, coste y riesgo.

No buscamos prometer una colonia mañana: buscamos modelos honestos, con supuestos explícitos, que hagan mejores las decisiones de ingeniería.

## Laboratorios propuestos

| Laboratorio | Pregunta central | Primera simulación |
| --- | --- | --- |
| `01-recursos-lunares` | ¿Dónde conviene extraer y qué tan variable es el recurso? | Mapa simplificado de hielo/regolito y rendimiento esperado. |
| `02-extraccion` | ¿Cuánta energía, desgaste y tiempo requiere mover material? | Excavadora o rover con balances de masa y potencia. |
| `03-procesamiento-isru` | ¿Cómo se transforma regolito o hielo en productos útiles? | Balance de masa/energía para oxígeno, agua y metales. |
| `04-manufactura` | ¿Qué piezas pueden fabricarse localmente? | Comparativa entre impresión 3D, sinterizado y material enviado desde Tierra. |
| `05-logistica-y-economia` | ¿Qué arquitectura escala mejor? | Simulador discreto de flota, inventario y ventanas de misión. |
| `06-gemelo-de-mision` | ¿Qué ocurre cuando todo se integra? | Escenario de base lunar con fallos y sensibilidad de parámetros. |

## Principios del proyecto

- **Reproducible:** cada resultado debe indicar datos, código, versión y parámetros.
- **Trazable:** separar hechos, estimaciones y supuestos.
- **Modular:** un laboratorio puede evolucionar sin romper los demás.
- **Realista:** incluir incertidumbre, degradación, mantenimiento y fallos.
- **Abierto a aprender:** los modelos iniciales pueden ser sencillos; deben ser fáciles de cuestionar y mejorar.

## Estructura prevista

```text
.
├── labs/             # Experimentos y simulaciones independientes
├── models/           # Componentes reutilizables: masa, energía, térmica, operaciones
├── data/             # Datos de entrada y sus fuentes
├── docs/             # Decisiones, notas técnicas y glosario
├── results/          # Resultados generados (no datos fuente)
├── README.md
└── AGENTS.md
```

## Cómo empezamos

El primer hito será un **balance de masa y energía de una planta lunar de oxígeno**. Un modelo mínimo debe permitir variar:

- producción objetivo (kg de O₂/día);
- ley de oxígeno del regolito;
- eficiencia de extracción;
- potencia disponible y ciclo día/noche;
- masa de equipos, repuestos y consumibles.

Con eso podremos responder: *¿qué arquitectura produce más oxígeno por kilogramo enviado desde la Tierra?*

## Convenciones

- Unidades SI: kg, m, s, K, W, Pa.
- Los parámetros viven fuera del código cuando sea posible.
- Cada simulación tiene un `README` breve: objetivo, supuestos, entradas, salidas y cómo ejecutarla.
- No mezclar datos originales con resultados derivados.

## Contribuir

Las ideas y las dudas son contribuciones. Antes de crear un modelo nuevo, abre una nota corta con la pregunta que intenta responder, los supuestos y la métrica de éxito. Consulta [AGENTS.md](AGENTS.md) para las reglas de trabajo del repositorio.

---

**Horizonte:** hacer que la manufactura espacial sea una disciplina que se pueda experimentar, debatir y mejorar desde el código.
