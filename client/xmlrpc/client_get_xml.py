#!/usr/bin/env python3
"""
Cliente para obter XML armazenado via XML-RPC
Uso: python client_get_xml.py <xml_id> [output_file.xml]
"""

import sys
import xmlrpc.client

def main():
    if len(sys.argv) < 2:
        print("Uso: python client_get_xml.py <xml_id> [output_file.xml]")
        sys.exit(1)
    
    xml_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Conectar ao servidor XML-RPC
    server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    # Recuperar XML
    result = server.retrieve_xml(xml_id)
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")
        sys.exit(1)
    
    xml_content = result['data']['content']
    filename = result['data']['filename']
    
    # Guardar em ficheiro ou mostrar
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"XML guardado em: {output_file}")
    else:
        print(f"Filename: {filename}")
        print(f"Size: {len(xml_content)} bytes")
        print("\nConteúdo:")
        print(xml_content[:500] + "..." if len(xml_content) > 500 else xml_content)

if __name__ == '__main__':
    main()
