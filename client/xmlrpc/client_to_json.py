#!/usr/bin/env python3
"""
Cliente para conversão de XML para JSON via XML-RPC
Uso: python client_to_json.py <xml_id> [output_file.json]
"""

import sys
import xmlrpc.client

def main():
    if len(sys.argv) < 2:
        print("Uso: python client_to_json.py <xml_id> [output_file.json]")
        sys.exit(1)
    
    xml_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Conectar ao servidor XML-RPC
    server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    # Converter para JSON
    result = server.convert_xml_to_json(xml_id)
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")
        sys.exit(1)
    
    json_content = result['json_content']
    
    # Guardar em ficheiro ou mostrar
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_content)
        print(f"JSON guardado em: {output_file}")
    else:
        print(json_content)

if __name__ == '__main__':
    main()
