# Guía para agentes y colaboradores

Este repositorio explora minería y manufactura espacial mediante modelos y simulaciones. Prioriza la claridad científica sobre la complejidad prematura.

## Forma de trabajar

1. Antes de implementar, define la pregunta de ingeniería y la métrica que responderá el modelo.
2. Declara los supuestos, unidades, rango de validez y fuentes de datos.
3. Empieza con el modelo más pequeño que sea útil; añade fidelidad sólo cuando cambie una decisión.
4. Mantén los experimentos reproducibles: parámetros versionados, semilla aleatoria si aplica y comandos de ejecución documentados.
5. Verifica conservación de masa y energía cuando corresponda; añade pruebas para ecuaciones y casos límite.

## Organización

- `labs/`: experimentos autocontenidos. Cada uno incluye un `README.md` con objetivo, entradas, salidas, supuestos y ejecución.
- `models/`: funciones y modelos reutilizables, sin detalles específicos de un único escenario.
- `data/raw/`: datos tal como se obtuvieron; no modificarlos.
- `data/processed/`: datos derivados, junto con el proceso que los generó.
- `results/`: artefactos generados. No usar como fuente de verdad.
- `docs/`: decisiones de arquitectura, referencias y glosario.

## Reglas de modelado

- Usar SI internamente y mostrar conversiones sólo en la capa de presentación.
- Nombrar explícitamente las variables: `mass_kg`, `power_w`, `temperature_k`.
- Distinguir parámetros medidos, estimados y supuestos; no presentar estimaciones como hechos.
- Incluir incertidumbre o análisis de sensibilidad en cuanto el modelo tenga decisiones relevantes.
- Registrar las fuentes en cada dataset o documento técnico, con fecha de consulta si es web.
- Evitar números mágicos: todo valor físico debe tener nombre, unidad y procedencia.

## Calidad y cambios

- No sobrescribir ni eliminar datos o resultados ajenos sin autorización explícita.
- Mantener los cambios enfocados; no reformatear archivos no relacionados.
- Ejecutar las pruebas y el formato disponibles antes de entregar un cambio.
- Al añadir una simulación, documentar un ejemplo mínimo de entrada y el resultado esperado.
- Si faltan datos, usar un valor provisional claramente marcado y crear una nota de seguimiento.

## Comunicación

Explica el resultado primero y luego cómo se obtuvo. Señala de forma visible las limitaciones que podrían cambiar la conclusión. Cuando haya varias arquitecturas plausibles, compara sus compromisos en vez de declarar una ganadora sin condiciones.
