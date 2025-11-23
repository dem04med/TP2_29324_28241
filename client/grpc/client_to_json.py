#!/usr/bin/env python3
"""
Cliente gRPC para conversão de XML para JSON
Uso: python client_to_json.py <xml_id> [output_file.json]
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
        print("Uso: python client_to_json.py <xml_id> [output_file.json]")
        sys.exit(1)
    
    xml_id = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.XMLServiceStub(channel)
    
    # Converter para JSON
    response = stub.ConvertToJSON(pb2.ConvertToJSONRequest(xml_id=xml_id))
    
    if not response.success:
        print(f"Erro: {response.message}")
        sys.exit(1)
    
    json_content = response.json_content
    
    # Guardar em ficheiro ou mostrar
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_content)
        print(f"JSON guardado em: {output_file}")
    else:
        print(json_content)

if __name__ == '__main__':
    main()
