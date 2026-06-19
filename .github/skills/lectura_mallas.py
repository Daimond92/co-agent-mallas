import xml.etree.ElementTree as ET
import argparse
import sys
import os

def extract_and_inject_jobs(dev_path, dim_path, output_path, job_names=None):
    """
    Lee los jobs de la malla de desarrollo y los inyecta en el cascarón de dimensiones.
    
    Args:
        dev_path (str): Ruta al archivo XML de desarrollo (-dev.xml)
        dim_path (str): Ruta al archivo XML base (-dim.xml)
        output_path (str): Ruta donde se guardará el XML consolidado
        job_names (list): Lista opcional de nombres de jobs específicos a extraer. 
                          Si está vacío o es None, extrae todos los jobs.
    """
    try:
        # 1. Parsear el archivo de desarrollo
        tree_dev = ET.parse(dev_path)
        root_dev = tree_dev.getroot()
        folder_dev = root_dev.find('FOLDER')
        
        if folder_dev is None:
            raise ValueError(f"No se encontró la etiqueta <FOLDER> en {dev_path}")

        # 2. Filtrar y extraer los jobs
        jobs_to_inject = []
        for job in folder_dev.findall('JOB'):
            name = job.get('JOBNAME')
            if not job_names or name in job_names:
                jobs_to_inject.append(job)
                
        if not jobs_to_inject:
            print(f"Advertencia: No se encontraron jobs para extraer en {dev_path}.")
            return False

        # 3. Parsear el archivo cascarón (dim)
        tree_dim = ET.parse(dim_path)
        root_dim = tree_dim.getroot()
        folder_dim = root_dim.find('FOLDER')
        
        if folder_dim is None:
            raise ValueError(f"No se encontró la etiqueta <FOLDER> en {dim_path}")

        # 4. Inyectar los jobs en el folder de dimensiones
        for job in jobs_to_inject:
            folder_dim.append(job)

        # 5. Guardar el archivo resultante preservando la declaración XML
        tree_dim.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"Éxito: {len(jobs_to_inject)} job(s) inyectado(s) correctamente en {output_path}")
        return True

    except Exception as e:
        print(f"Error procesando los XML: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    # Configuración de los argumentos de línea de comandos para que el agente lo ejecute
    parser = argparse.ArgumentParser(description="Extrae <JOB>s de un XML dev y los inyecta en un XML dim.")
    parser.add_argument("--dev", required=True, help="Ruta al archivo XML de desarrollo")
    parser.add_argument("--dim", required=True, help="Ruta al archivo XML de dimensiones")
    parser.add_argument("--out", required=True, help="Ruta de salida para el archivo consolidado")
    parser.add_argument("--jobs", nargs="*", help="Lista de JOBNAMEs específicos a extraer (opcional)")
    
    args = parser.parse_args()
    
    success = extract_and_inject_jobs(args.dev, args.dim, args.out, args.jobs)
    if not success:
        sys.exit(1)