#!/usr/bin/env python3
"""
Cliente para validar XML via XML-RPC
Uso: python client_validate.py <xml_id> [schema.xsd]
"""

import sys
import xmlrpc.client

def main():
    if len(sys.argv) < 2:
        print("Uso: python client_validate.py <xml_id> [schema.xsd]")
        sys.exit(1)
    
    xml_id = sys.argv[1]
    schema_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Conectar ao servidor XML-RPC
    server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    # Validar XML
    result = server.validate_xml_content(xml_id, schema_file)
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")
        sys.exit(1)
    
    is_valid = result['is_valid']
    validation_result = result['validation_result']
    
    if is_valid:
        print(f"✓ XML válido: {validation_result}")
    else:
        print(f"✗ XML inválido: {validation_result}")
        sys.exit(1)

if __name__ == '__main__':
    main()
