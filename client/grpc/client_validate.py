#!/usr/bin/env python3
"""
Cliente gRPC para validar XML contra schema XSD
Uso: python client_validate.py <xml_id> [schema.xsd]
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
        print("Uso: python client_validate.py <xml_id> [schema.xsd]")
        sys.exit(1)
    
    xml_id = sys.argv[1]
    schema_path = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.XMLServiceStub(channel)
    
    # Validar XML
    response = stub.ValidateXML(pb2.ValidateXMLRequest(
        xml_id=xml_id,
        schema_path=schema_path
    ))
    
    if not response.success:
        print(f"Erro: {response.message}")
        sys.exit(1)
    
    if response.is_valid:
        print(f"✓ XML válido: {response.validation_result}")
    else:
        print(f"✗ XML inválido: {response.validation_result}")
        sys.exit(1)

if __name__ == '__main__':
    main()
