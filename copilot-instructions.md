# Contexto Global del Workspace: Optimización de Mallas Control-M

Este workspace está dedicado a un sistema multiagente que automatiza la promoción de mallas XML de Control-M desde entornos de desarrollo (`-dev`) a producción (`-prod`), utilizando un cascarón de dimensiones (`-dim`).

Todos los agentes de este entorno deben regirse estrictamente por las siguientes reglas:

## 1. PROHIBICIÓN ABSOLUTA DE EDICIÓN DIRECTA DE XML (ANTI-CORRUPCIÓN)
* **Peligro de Codificación (UTF-8):** Los agentes de IA tienen **ESTRICTAMENTE PROHIBIDO** usar herramientas de edición nativas de texto (como edit, replace, o reescritura de archivos) para modificar o guardar los archivos `.xml`. Al hacerlo, corrompen caracteres especiales (tildes, eñes) y rompen la estructura de salto de línea del documento.
* **Todo Cambio Estructural Pasa por Python:** Dado que el script `lectura_mallas.py` ya hace la fusión de correos, la preservación de metadatos y el cambio de nomenclatura ("D" a "P") de manera algorítmica, los agentes **SOLO DEBEN LEER (`read`)** los XML para validarlos y auditar. 

## 2. Reglas del Sistema de Archivos (Workspace Rules)
La integridad de los datos es la máxima prioridad. Los agentes deben respetar la estructura de carpetas `workspace_mallas/`:
* **`01_insumos/`:** Es de **SOLO LECTURA**. Contiene los archivos originales (`-dev.xml` y `-dim.xml`). Ningún agente tiene permitido editar, borrar o sobrescribir archivos aquí.
* **`02_temporal/`:** Es el **ÁREA DE TRABAJO**. Los archivos aquí son generados EXCLUSIVAMENTE por las Skills de Python.
* **`03_produccion/`:** Es el **DESTINO FINAL**. Solo el Agente Experto QA en Mallas puede mover el archivo validado a esta carpeta, y debe hacerlo usando comandos nativos de terminal (ej. `cp` o `mv` en bash/cmd) para no alterar la codificación del archivo.

## 3. Reglas de Ejecución y Herramientas (Skills)
* **Uso de Python:** Para cualquier extracción estructural, creación de archivos o inyección de nodos `<JOB>`, los agentes DEBEN usar la herramienta de ejecución para llamar al script `lectura_mallas.py`. 
* **Handoffs (Transferencias):** Al pasar una tarea de un agente a otro, el agente saliente debe proporcionar un resumen claro de lo que auditó y la ruta exacta del archivo en `02_temporal/`.

## 4. Restricciones Técnicas de Control-M (Guardrails)
* **La Verdad de Desarrollo:** Las variables y la lógica interna que vienen del archivo `-dev.xml` son la verdad absoluta. Los agentes NUNCA deben revertir variables a versiones anteriores de producción.
* **Variables Intocables:** La sintaxis de Control-M (ej. `%%YEAR`, `%%MONTH`, `%%$CALCDATE`) es sagrada. Ningún agente debe alterar estos formatos.
* **Estructura XML y Encabezados:** Todo documento final debe mantener la declaración XML original EXACTA (usando comillas dobles `<?xml version="1.0" encoding="utf-8"?>`) y preservar el comentario de exportación original. **ESTÁ ESTRICTAMENTE PROHIBIDO actualizar la fecha y hora del comentario de exportación a la fecha actual.**