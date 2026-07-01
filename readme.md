# 🤖 Sistema Multi-Agente: Promoción de Mallas Control-M
## 📝 Historial de Versiones
* **v1.0 (Actual):** Arquitectura inicial  para mallas de transferencia. Script `lectura_mallas.py` con protección de metadatos, fusión de correos y orquestación base de 4 agentes auditores.

Este repositorio contiene un ecosistema automatizado impulsado por Inteligencia Artificial (GitHub Copilot / Gemini) diseñado para promover mallas XML de Control-M desde entornos de desarrollo (`-dev`) hacia producción, utilizando un archivo base o cascarón (`-dim`).

El sistema combina la precisión algorítmica de **Python** (para la manipulación segura de XML) con la capacidad cognitiva de **Agentes de IA** (para la orquestación, auditoría y aseguramiento de calidad).

---

## 🎯 ¿Cómo funciona la arquitectura?

Para garantizar el 100% de integridad en la codificación (UTF-8) y evitar la corrupción de sintaxis nativa de Control-M (como las variables `%%`), el sistema divide el trabajo en dos capas:

1. **El Motor de Ejecución (Python):** Un script especializado (`lectura_mallas.py`) se encarga de leer, estructurar, fusionar correos y aplicar las reglas duras de negocio en el XML.
2. **El Equipo de Auditoría (Agentes IA):** Un escuadrón de agentes especializados que orquestan el flujo, validan que el script haya cumplido las reglas y generan reportes detallados, **sin editar el XML manualmente**.

---

## 📂 Estructura del Workspace

El proyecto está diseñado bajo un principio de "inmutabilidad de insumos" para proteger los archivos originales:

```text
📁 optimizacion_ma_bluetab/
├── 📁 .github/                         # Cerebro del sistema
│   ├── 📁 agents/                      # Prompts y reglas de cada agente (.md)
│   ├── 📁 skills/                      # Herramientas ejecutables (lectura_mallas.py)
│   └── 📄 copilot-instructions.md      # Leyes supremas del workspace (Guardrails)
├── 📁 workspace_mallas/                # Entorno de trabajo aislado
│   ├── 📁 01_insumos/                  # 🔒 SOLO LECTURA: Archivos origen (-dev, -dim)
│   ├── 📁 02_temporal/                 # ⚙️ ÁREA DE TRABAJO: XMLs en proceso de inyección
│   └── 📁 03_produccion/               # ✅ DESTINO FINAL: XML productivo e Informe QA (.md)
└── 📄 readme.md                        # Documentación del proyecto
```

---

## 🧠 El Equipo de Agentes

Cada agente tiene un rol estricto y delimitado:

* 👔 **Orquestador Mallas Control-M:** El Front-end. Interactúa con el usuario, valida la nomenclatura de la malla solicitada, recolecta los insumos y detona el proceso.
* ⚙️ **Experto en Mallas:** El coordinador técnico. Su única labor es ejecutar el script de Python con los parámetros correctos y coordinar las auditorías posteriores.
* 🔍 **Auditores Especializados (Sub-agentes):**
    * **Experto en Nomenclatura:** Valida que los jobs transferidos hayan cambiado correctamente la letra de entorno (ej. de "D" a "P") en `JOBNAME` y condiciones (`<DOCOND>`).
    * **Experto en Parámetros:** Verifica la correcta fusión de los correos en `DEST` y `CC_DEST`, protegiendo el buzón de incidentes obligatorio, y audita los namespaces.
    * **Experto en Variables:** Garante de que la lógica de negocio (variables `%%$CALCDATE`, etc.) inyectada desde desarrollo llegue intacta a producción.
* 🛡️ **Experto QA en Mallas:** La última línea de defensa. Audita que el XML esté bien formado, aprueba la promoción, mueve el archivo final a `03_produccion/` y redacta el informe en Markdown (`.md`).

---

## 📋 Reglas de Negocio Automatizadas

Este sistema aplica automáticamente reglas complejas de Control-M:
1.  **Protección de Metadatos:** En jobs modificados, se congelan atributos de auditoría de producción (`CHANGE_USERID`, `CHANGE_DATE`, `VERSION_HOST`, etc.).
2.  **Fusión Inteligente de Correos:** No se sobrescriben las listas de distribución; se concatenan respetando el orden original y separando `DEST` de `CC_DEST`.
3.  **Prevención de Rastros:** Limpieza de comentarios residuales y aseguramiento del encabezado de exportación original.

---

## 🚀 Guía Rápida de Uso (Paso a Paso)

### Requisitos Previos
* Python 3.8+ instalado localmente.
* VS Code con la extensión de GitHub Copilot Chat configurada para agentes en el workspace.

### Pasos para Promover una Malla

**1. Deposita los Insumos**
Coloca tus archivos de desarrollo y cascarón (ej. `CR-COFFIRDIA-T04-dev.xml` y `CR-COFFIRDIA-T04-dim.xml`) estrictamente en la carpeta `workspace_mallas/01_insumos/`.

**2. Configura el Agente en VS Code**
* Abre el panel de chat de la IA en tu editor.
* Haz clic en el selector de agentes (menú desplegable superior) y selecciona explícitamente a **`Orchestrator Mallas Control-M`**.
* Asegúrate de tener seleccionado un modelo compatible en la configuración inferior (puedes dejarlo en `Auto` o elegir modelos robustos como `Claude Sonnet 4.6` o `GPT-5.5` si tu administrador lo permite).

**3. Inicia la Interacción**
Escribe el siguiente prompt inicial para despertar al agente:
> *"Hola, necesito realizar una promoción de malla a producción."*

**4. Confirma el Análisis del Orquestador**
El agente escaneará la carpeta de insumos y desglosará automáticamente la nomenclatura detectada (Id Malla, Geografía, UUAA, etc.). Al final, te pedirá confirmar las rutas y los jobs a migrar. 
* **Responde de forma directa aprobando los datos**, por ejemplo: *"Correcto CFFIRTD0007"*.

**5. Ejecución Automática (Handoff)**
Tras tu confirmación, verás en el chat cómo el Orquestador transfiere el control al agente **`Experto en Mallas Control-M`** dándole la orden de ejecutar el script `lectura_mallas.py`. El sistema orquestará las validaciones de forma autónoma.

**6. Revisa tus Entregables**
Al finalizar, el agente te entregará un resumen de validación de cierre (confirmando parseo correcto y ausencia de rastros de desarrollo). 
Dirígete a la carpeta `workspace_mallas/03_produccion/` para recolectar tu trabajo:
* **XML de producción:** El archivo limpio y listo para despliegue (ej. `CR-COFFIRDIA-T04.xml`).
* **Informe de promoción:** Tu bitácora de auditoría detallada en formato Markdown (ej. `Informe_Promocion_CR-COFFIRDIA-T04.md`).