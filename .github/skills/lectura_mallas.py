import xml.etree.ElementTree as ET
import argparse
import sys
import os
import re

def extract_and_inject_jobs(dev_path, dim_path, output_path, job_names=None):
    """
    Integra de forma inteligente los jobs seleccionados de desarrollo en la malla de producción.
    
    - Si el job es MODIFICADO (existe su equivalente con 'P' en prod): Se actualiza su estructura interna preservando metadatos.
    - Si el job es NUEVO: Se anexa directo a la carpeta.
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
            print("Advertencia: No se encontraron los jobs especificados en el archivo de desarrollo.")
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
            "CHANGE_USERID", "CHANGE_DATE", "CHANGE_TIME",
            "VERSION_SERIAL", "VERSION_HOST", "PARENT_FOLDER"
        ]

        # 3. Mapear los jobs que ya existen actualmente en la malla de producción (dim)
        existing_dim_jobs = {}
        for job_dim in folder_dim.findall('JOB'):
            name_dim = job_dim.get('JOBNAME')
            existing_dim_jobs[name_dim] = job_dim

        # 4. Orquestar la fusión (Merge) inteligente de los jobs
        for job_name, dev_job in jobs_from_dev.items():
            # Regla de negocio inteligente: El equivalente productivo cambia la 'D' de entorno por 'P' antes de los 4 dígitos
            prod_name_target = re.sub(r'D(\d{4})$', r'P\1', job_name)
            
            if prod_name_target in existing_dim_jobs:
                # -------------------------------------------------------------
                # CASO A: JOB MODIFICADO (Ya existe su versión productiva)
                # -------------------------------------------------------------
                dim_job = existing_dim_jobs[prod_name_target]
                
                # Resguardamos los valores originales de producción para los atributos protegidos
                saved_metadata = {attr: dim_job.get(attr) for attr in PROTECTED_ATTRIBUTES if dim_job.get(attr) is not None}
                
                # Limpiamos el contenido interno del job viejo (usando copia de lista para borrado seguro)
                for child in list(dim_job):
                    dim_job.remove(child)
                
                # Inyectamos la nueva estructura interna de desarrollo
                for child in list(dev_job):
                    dim_job.append(child)
                    
                # Actualizamos todos los atributos operativos con los nuevos de dev
                dim_job.attrib.clear()
                dim_job.attrib.update(dev_job.attrib)
                
                # Forzamos la restauración de los 10 metadatos protegidos de la producción original
                for attr, original_value in saved_metadata.items():
                    dim_job.set(attr, original_value)
                    
                print(f" -> Job Modificado Integrado (Metadatos Protegidos): {prod_name_target}")
                
            else:
                # -------------------------------------------------------------
                # CASO B: JOB NUEVO (No existe en producción actual)
                # -------------------------------------------------------------
                folder_dim.append(dev_job)
                print(f" -> Job Nuevo Inyectado con éxito: {job_name}")

        # 5. Dar formato estructurado (Pretty-Print) y guardar en carpeta temporal
        if hasattr(ET, 'indent'):
            ET.indent(tree_dim, space="    ", level=0)
            
        tree_dim.write(output_path, encoding="utf-8", xml_declaration=True)
        
        # 6. POST-PROCESAMIENTO INFALIBLE: Garantizar el comentario exacto de -dim.xml y limpieza final
        with open(dim_path, 'r', encoding='utf-8') as f_dim:
            # Buscar la línea exacta que contiene el comentario en el archivo cascarón
            export_comment = next((line for line in f_dim if "" in line), '')
            
        if export_comment:
            # 1. LEER el archivo temporal estructurado
            with open(output_path, 'r', encoding='utf-8') as f_out:
                out_content = f_out.read()
            
            # 2. BORRAR el comentario de exportación desalineado de forma segura
            out_content = re.sub(r'', '', out_content)
            
            # 3. Inyectar el comentario original de dim justo debajo de la declaración XML
            out_content = out_content.replace('?>\n', '?>\n' + export_comment)
            
            # 4. Eliminar matemáticamente cualquier salto de línea basura al final del archivo
            out_content = out_content.strip() + '\n'
            
            # 5. Sobrescribir el archivo final con la estructura impecable
            with open(output_path, 'w', encoding='utf-8') as f_out:
                f_out.write(out_content)

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