# 🤖 Optimización y Promoción de Mallas Control-M (Sistema Multi-Agente)
Este repositorio contiene un sistema automatizado basado en agentes de Inteligencia Artificial (GitHub Copilot / Gemini) diseñado para promover mallas de Control-M desde entornos de desarrollo (-dev) hacia producción (-prod). El sistema utiliza un archivo base (-dim) como cascarón y coordina a múltiples agentes especializados para asegurar una migración sin errores manuales.

## 📋 Requisitos Previos
Para que el sistema de agentes funcione correctamente y pueda ejecutar las automatizaciones de código subyacentes, es estrictamente necesario contar con lo siguiente en el entorno local:

- Python 3.8 o superior: Los agentes utilizan Skills (scripts de Python) para analizar e inyectar de forma segura la estructura XML sin corromper el documento.

- Visual Studio Code (VS Code): El entorno de desarrollo principal.

- Extensión de GitHub Copilot Chat: Configurada y habilitada para reconocer agentes personalizados en el workspace.

## 📂 Estructura del Proyecto
El proyecto está organizado para separar la lógica de los agentes de los archivos de negocio (XMLs), garantizando que los agentes no modifiquen accidentalmente los insumos originales.

```text
📁 optimizacion_ma_bluetab/
├── 📁 .github/                         # Núcleo del sistema multi-agente
│   ├── 📁 agents/                      # Definiciones YAML de cada agente (.md)
│   ├── 📁 skills/                      # Herramientas ejecutables (ej. lectura_mallas.py)
│   └── 📄 copilot-instructions.md      # Cerebro y reglas globales del workspace
├── 📁 workspace_mallas/                # Entorno de trabajo para las mallas
│   ├── 📁 01_insumos/                  # Archivos originales de solo lectura (-dev.xml, -dim.xml)
│   ├── 📁 02_temporal/                 # Archivos en proceso de transformación
│   └── 📁 03_produccion/               # Archivos finales listos para despliegue (-prod.xml)
└── 📄 README.md       
```

## Documentación del proyecto
🧠 Arquitectura de Agentes
El flujo de trabajo es gestionado por un equipo de agentes virtuales que se comunican entre sí mediante handoffs (transferencias de contexto):

- Orquestador Mallas Control-M: El punto de entrada (Front-end). Interactúa con el usuario, solicita los insumos, valida que existan en 01_insumos/ y delega la ejecución.

- Experto en Mallas: El coordinador técnico. Ejecuta el script de Python para inyectar los Jobs de desarrollo en el cascarón base y coordina a los especialistas.

- Especialistas Técnicos (Sub-agentes):

    - Experto en Nomenclatura: Estandariza nombres de Jobs y condiciones (de Dev a Prod).

    - Experto en Parámetros: Ajusta rutas, servidores (Hosts), correos y namespaces.

    - Experto en Variables: Protege y formatea las variables dinámicas de Control-M (ej. %%YEAR).

- Experto QA en Mallas: El validador final. Revisa el archivo ensamblado en la carpeta temporal. Si encuentra un error, lo devuelve; si todo es correcto, lo mueve a 03_produccion/.

## 🚀 Cómo usar el sistema
1. Preparar los insumos: Coloca el archivo de desarrollo (ej. CR-COBILMEN-T04-dev.xml) y el archivo cascarón (ej. CR-COBILMEN-T04-dim.xml) dentro de la carpeta workspace_mallas/01_insumos/.

2. Iniciar la orquestación: Abre el chat de GitHub Copilot en VS Code.

3. Invocar al agente principal: Escribe el siguiente comando en el chat:

    ```text
    Hola, necesito realizar una promoción de malla a producción.
    ```

4. Seguir las instrucciones: El Orquestador te pedirá los nombres de los archivos y los jobs específicos que deseas migrar. Simplemente responde a sus preguntas y el sistema hará el resto.