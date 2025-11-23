#!/usr/bin/env python3
"""
Cliente para conversão de CSV para XML via XML-RPC
Uso: python client_convert.py <caminho_csv> [--generate-schema]
"""

import sys
import xmlrpc.client
import os

def main():
    if len(sys.argv) < 2:
        print("Uso: python client_convert.py <caminho_csv> [--generate-schema]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    generate_schema = '--generate-schema' in sys.argv
    
    if not os.path.exists(csv_path):
        print(f"Erro: Ficheiro {csv_path} não encontrado")
        sys.exit(1)
    
    # Conectar ao servidor XML-RPC
    server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    # Ler ficheiro CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_data = f.read()
    
    # Converter CSV para XML
    filename = os.path.basename(csv_path).replace('.csv', '.xml')
    result = server.convert_csv_to_xml(csv_data, 'dataset', 'record')
    
    if not result.get('success'):
        print(f"Erro na conversão: {result.get('error')}")
        sys.exit(1)
    
    xml_content = result['xml_content']
    
    # Armazenar no MongoDB
    store_result = server.store_xml(filename, xml_content)
    
    if not store_result.get('success'):
        print(f"Erro ao armazenar: {store_result.get('error')}")
        sys.exit(1)
    
    xml_id = store_result['xml_id']
    print(f"XML ID: {xml_id}")
    
    # Gerar schema XSD se solicitado
    if generate_schema:
        xsd_result = server.generate_xsd_schema(xml_id)
        
        if xsd_result.get('success'):
            xsd_filename = f"data/xml_schemas/{os.path.basename(csv_path).replace('.csv', '.xsd')}"
            os.makedirs('data/xml_schemas', exist_ok=True)
            
            with open(xsd_filename, 'w', encoding='utf-8') as f:
                f.write(xsd_result['xsd_content'])
            
            print(f"XSD Schema: {xsd_filename}")
        else:
            print(f"Aviso: Erro ao gerar XSD: {xsd_result.get('error')}")

if __name__ == '__main__':
    main()
