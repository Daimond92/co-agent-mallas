# Contexto Global del Workspace: Optimización de Mallas Control-M

Este workspace está dedicado a un sistema multiagente que automatiza la promoción de mallas XML de Control-M desde entornos de desarrollo (`-dev`) a producción (`-prod`), utilizando un cascarón de dimensiones (`-dim`).

Todos los agentes de este entorno deben regirse estrictamente por las siguientes reglas:

## 1. Reglas del Sistema de Archivos (Workspace Rules)
La integridad de los datos es la máxima prioridad. Los agentes deben respetar la estructura de carpetas `workspace_mallas/`:
* **`01_insumos/`:** Es de **SOLO LECTURA**. Contiene los archivos originales (`-dev.xml` y `-dim.xml`). Ningún agente tiene permitido editar, borrar o sobrescribir archivos aquí.
* **`02_temporal/`:** Es el **ÁREA DE TRABAJO**. Todos los archivos intermedios generados por las Skills de Python y modificados por los sub-agentes deben guardarse y procesarse aquí.
* **`03_produccion/`:** Es el **DESTINO FINAL**. Solo el Agente Experto QA en Mallas puede mover o aprobar archivos para que se guarden en esta carpeta una vez validados.

## 2. Reglas de Ejecución y Herramientas (Skills)
* **Uso de Python:** Para cualquier extracción estructural, creación de archivos o inyección de nodos `<JOB>`, los agentes DEBEN usar la herramienta de ejecución para llamar al script `lectura_mallas.py`. Está prohibido intentar inyectar bloques XML masivos directamente usando herramientas de edición de texto.
* **Handoffs (Transferencias):** Al pasar una tarea de un agente a otro, el agente saliente debe proporcionar un resumen claro de lo que hizo y la ruta exacta del archivo en `02_temporal/` que el siguiente agente debe revisar.

## 3. Restricciones Técnicas de Control-M (Guardrails)
* **Variables:** La sintaxis de Control-M (ej. `%%YEAR`, `%%MONTH`, `%%$CALCDATE`) es sagrada. Ningún agente debe alterar estos formatos ni intentar "corregirlos", ya que son interpretados por el servidor de Control-M, no por lenguajes estándar.
* **Estructura XML:** Todo documento final debe mantener la declaración XML original (`<?xml version="1.0" encoding="utf-8"?>`) y la etiqueta raíz `<DEFTABLE>`.
* **No Asumir:** Si una regla de negocio entre dev y prod es ambigua (por ejemplo, un correo que no tiene un equivalente claro documentado), el agente debe detenerse y pedir confirmación al usuario a través del Orquestador.
* **Estructura XML y Encabezados:** Todo documento final debe mantener la declaración XML original EXACTA (usando comillas dobles `<?xml version="1.0" encoding="utf-8"?>`) y preservar los comentarios de exportación (ej. `<!--Exported at 19-05-2025 09:34:59-->`). Está PROHIBIDO que los agentes o los scripts eliminen o modifiquen la primera y segunda línea del archivo `-dim.xml` original.