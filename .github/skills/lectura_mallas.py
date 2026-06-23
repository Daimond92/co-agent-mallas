import xml.etree.ElementTree as ET
import argparse
import sys
import os

def extract_and_inject_jobs(dev_path, dim_path, output_path, job_names=None):
    """
    Integra de forma inteligente los jobs seleccionados de desarrollo en la malla de producción.
    
    - Si el job es NUEVO: Se inyecta completo.
    - Si el job es MODIFICADO: Se actualiza su lógica de desarrollo pero se preservan los 10 atributos de producción.
    - Jobs no mencionados: Permanecen en la malla de producción completamente inalterados.
    """
    try:
        # 1. Parsear el archivo de desarrollo preservando comentarios internos
        parser_dev = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree_dev = ET.parse(dev_path, parser=parser_dev)
        root_dev = tree_dev.getroot()
        folder_dev = root_dev.find('FOLDER')
        
        if folder_dev is None:
            raise ValueError(f"No se encontró la etiqueta <FOLDER> en {dev_path}")

        # Mapear y filtrar los jobs de desarrollo que el usuario solicitó procesar
        jobs_from_dev = {}
        for job in folder_dev.findall('JOB'):
            name = job.get('JOBNAME')
            if not job_names or name in job_names:
                jobs_from_dev[name] = job
                
        if not jobs_from_dev:
            print(f"Advertencia: No se encontraron los jobs especificados en el archivo de desarrollo.")
            return False

        # 2. Parsear el archivo cascarón actual (dim) preservando comentarios y encabezados
        parser_dim = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree_dim = ET.parse(dim_path, parser=parser_dim)
        root_dim = tree_dim.getroot()
        folder_dim = root_dim.find('FOLDER')
        
        if folder_dim is None:
            raise ValueError(f"No se encontró la etiqueta <FOLDER> en {dim_path}")

        # Atributos estrictamente protegidos para JOBS MODIFICADOS (Vienen de producción actual)
        PROTECTED_ATTRIBUTES = [
            "APPLICATION", "SUB_APPLICATION", "JOBNAME", "CREATED_BY", 
            "CREATION_USER", "CREATION_DATE", "CREATION_TIME", 
            "VERSION_SERIAL", "VERSION_HOST", "PARENT_FOLDER"
        ]

        # 3. Mapear los jobs que ya existen actualmente en la malla de producción (dim)
        existing_dim_jobs = {}
        for job_dim in folder_dim.findall('JOB'):
            name_dim = job_dim.get('JOBNAME')
            existing_dim_jobs[name_dim] = job_dim

        # 4. Orquestar la fusión (Merge) inteligente de los jobs
        for job_name, dev_job in jobs_from_dev.items():
            
            if job_name in existing_dim_jobs:
                # -------------------------------------------------------------
                # CASO A: JOB MODIFICADO (Ya existe en la malla de producción)
                # -------------------------------------------------------------
                dim_job = existing_dim_jobs[job_name]
                
                # Resguardamos los valores originales de producción para los atributos protegidos
                saved_metadata = {attr: dim_job.get(attr) for attr in PROTECTED_ATTRIBUTES if dim_job.get(attr) is not None}
                
                # Limpiamos el contenido interno del job viejo (etiquetas hijas antiguas como variables o condiciones)
                for child in list(dim_job):
                    dim_job.remove(child)
                
                # Inyectamos la nueva estructura interna proveniente de desarrollo
                for child in list(dev_job):
                    dim_job.append(child)
                    
                # Actualizamos todos los atributos genéricos del job con los nuevos parámetros operativos de dev
                dim_job.attrib.clear()
                dim_job.attrib.update(dev_job.attrib)
                
                # Forzamos la restauración de los 10 metadatos protegidos de producción original
                for attr, original_value in saved_metadata.items():
                    dim_job.set(attr, original_value)
                    
                print(f" -> Job Modificado Integrado (Metadatos Protegidos): {job_name}")
                
            else:
                # -------------------------------------------------------------
                # CASO B: JOB NUEVO (No existe en producción actual)
                # -------------------------------------------------------------
                # Al ser completamente nuevo, se anexa directo a la carpeta sin restricciones previas
                folder_dim.append(dev_job)
                print(f" -> Job Nuevo Inyectado con éxito: {job_name}")

        # 5. Guardar el archivo consolidado en la carpeta temporal manteniendo la integridad del XML
        tree_dim.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"\nÉxito: Malla consolidada generada correctamente en {output_path}")
        return True

    except Exception as e:
        print(f"Error crítico procesando la fusión de XMLs: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fusiona inteligentemente mallas Control-M respetando reglas de negocio.")
    parser.add_argument("--dev", required=True, help="Ruta al archivo XML de desarrollo")
    parser.add_argument("--dim", required=True, help="Ruta al archivo XML de dimensiones (Producción actual)")
    parser.add_argument("--out", required=True, help="Ruta de salida para el archivo temporal consolidado")
    parser.add_argument("--jobs", nargs="*", help="Lista de JOBNAMEs específicos a validar")
    
    args = parser.parse_args()
    
    success = extract_and_inject_jobs(args.dev, args.dim, args.out, args.jobs)
    if not success:
        sys.exit(1)