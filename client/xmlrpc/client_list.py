#!/usr/bin/env python3
"""
Cliente para listar XMLs armazenados via XML-RPC
Uso: python client_list.py
"""

import xmlrpc.client

def main():
    # Conectar ao servidor XML-RPC
    server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    # Listar XMLs
    result = server.list_xml_files()
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")
        return
    
    count = result['count']
    files = result['files']
    
    print(f"Total: {count} ficheiro(s)")
    print()
    
    for file_info in files:
        print(f"ID: {file_info['_id']}")
        print(f"Nome: {file_info['filename']}")
        print(f"Data: {file_info.get('created_at', 'N/A')}")
        print(f"Tamanho: {file_info.get('size', 0)} bytes")
        print(f"Armazenamento: {file_info.get('storage', 'N/A')}")
        print("-" * 60)

if __name__ == '__main__':
    main()
