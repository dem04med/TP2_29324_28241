#!/usr/bin/env python3
"""
Cliente gRPC para obter XML armazenado
Uso: python client_get_xml.py <xml_id> [output_file.xml]
"""

import sys
import os

# Adicionar pasta server ao path para importar protobuf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

import grpc
import xml_service_pb2 as pb2
import xml_service_pb2_grpc as pb2_grpc

def main():
    if len(sys.argv) < 2:
        print("Uso: python client_get_xml.py <xml_id> [output_file.xml]")
        sys.exit(1)
    
    xml_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.XMLServiceStub(channel)
    
    # Recuperar XML
    response = stub.GetXML(pb2.GetXMLRequest(xml_id=xml_id))
    
    if not response.success:
        print(f"Erro: {response.message}")
        sys.exit(1)
    
    xml_content = response.xml_content
    filename = response.filename
    
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
