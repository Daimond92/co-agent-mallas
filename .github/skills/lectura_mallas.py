import xml.etree.ElementTree as ET
import argparse
import sys
import os
import re

def extract_and_inject_jobs(dev_path, dim_path, output_path, job_names=None):
    """
    Integra de forma inteligente los jobs seleccionados de desarrollo en la malla de producción.
    """
    try:
        # 1. Parsear el archivo de desarrollo
        parser_dev = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree_dev = ET.parse(dev_path, parser=parser_dev)
        root_dev = tree_dev.getroot()
        folder_dev = root_dev.find('FOLDER')
        
        if folder_dev is None:
            raise ValueError(f"No se encontró la etiqueta <FOLDER> en {dev_path}")

        # Mapear y filtrar los jobs
        jobs_from_dev = {}
        for job in folder_dev.findall('JOB'):
            name = job.get('JOBNAME')
            if not job_names or name in job_names:
                jobs_from_dev[name] = job
                
        if not jobs_from_dev:
            print("Advertencia: No se encontraron los jobs especificados en el archivo de desarrollo.")
            return False

        # 2. Parsear el archivo cascarón actual (dim)
        parser_dim = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
        tree_dim = ET.parse(dim_path, parser=parser_dim)
        root_dim = tree_dim.getroot()
        folder_dim = root_dim.find('FOLDER')
        
        if folder_dim is None:
            raise ValueError(f"No se encontró la etiqueta <FOLDER> en {dim_path}")

        # Atributos protegidos
        PROTECTED_ATTRIBUTES = [
            "APPLICATION", "SUB_APPLICATION", "JOBNAME", "CREATED_BY", 
            "CREATION_USER", "CREATION_DATE", "CREATION_TIME", 
            "CHANGE_USERID", "CHANGE_DATE", "CHANGE_TIME",
            "VERSION_SERIAL", "VERSION_HOST", "PARENT_FOLDER"
        ]

        # 3. Mapear los jobs de producción
        existing_dim_jobs = {}
        for job_dim in folder_dim.findall('JOB'):
            name_dim = job_dim.get('JOBNAME')
            existing_dim_jobs[name_dim] = job_dim

        # 4. Orquestar la fusión
        for job_name, dev_job in jobs_from_dev.items():
            prod_name_target = re.sub(r'D(\d{4})$', r'P\1', job_name)
            
            if prod_name_target in existing_dim_jobs:
                dim_job = existing_dim_jobs[prod_name_target]
                saved_metadata = {attr: dim_job.get(attr) for attr in PROTECTED_ATTRIBUTES if dim_job.get(attr) is not None}
                
                # REGLA DE NEGOCIO: Extraer correos usando LISTAS para conservar el ORDEN EXACTO de producción
                existing_dim_emails = {'DEST': [], 'CC_DEST': []}
                for mail_node in dim_job.findall('.//DOMAIL'):
                    for attr in ['DEST', 'CC_DEST']:
                        val = mail_node.get(attr)
                        if val:
                            for email in val.split(';'):
                                email_clean = email.strip()
                                # Solo lo agregamos si no está ya en la lista, manteniendo su posición original
                                if email_clean and email_clean not in existing_dim_emails[attr]:
                                    existing_dim_emails[attr].append(email_clean)
                
                for child in list(dim_job):
                    dim_job.remove(child)
                
                for child in list(dev_job):
                    dim_job.append(child)
                    
                dim_job.attrib.clear()
                dim_job.attrib.update(dev_job.attrib)
                
                for attr, original_value in saved_metadata.items():
                    dim_job.set(attr, original_value)
                
                # FUSIONAR CORREOS: Priorizando el orden de producción
                for mail_node in dim_job.findall('.//DOMAIL'):
                    for attr in ['DEST', 'CC_DEST']:
                        dev_val = mail_node.get(attr) or ''
                        dev_emails = [e.strip() for e in dev_val.split(';') if e.strip()]
                        
                        # Iniciamos con el orden estricto que traía producción
                        final_emails = list(existing_dim_emails[attr])
                        
                        # Agregamos los correos de desarrollo que sean nuevos, poniéndolos al final
                        for dev_email in dev_emails:
                            if dev_email not in final_emails:
                                final_emails.append(dev_email)
                        
                        if final_emails:
                            mail_node.set(attr, ';'.join(final_emails))
                    
                print(f" -> Job Modificado Integrado (Metadatos y Orden de Correos Protegidos): {prod_name_target}")
                
            else:
                folder_dim.append(dev_job)
                print(f" -> Job Nuevo Inyectado con éxito: {job_name}")

        # 5. Formato XML
        if hasattr(ET, 'indent'):
            ET.indent(tree_dim, space="    ", level=0)
            
        tree_dim.write(output_path, encoding="utf-8", xml_declaration=True)
        
        # 6. Post-procesamiento
        with open(dim_path, 'r', encoding='utf-8') as f_dim:
            export_comment = next((line for line in f_dim if "" in line), '')
            
        if export_comment:
            with open(output_path, 'r', encoding='utf-8') as f_out:
                out_content = f_out.read()
            
            out_content = re.sub(r'', '', out_content)
            out_content = out_content.replace('?>\n', '?>\n' + export_comment)
            out_content = out_content.strip() + '\n'
            
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