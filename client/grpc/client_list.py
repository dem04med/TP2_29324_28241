#!/usr/bin/env python3
"""
Cliente gRPC para listar XMLs armazenados
Uso: python client_list.py
"""

import sys
import os

# Adicionar pasta server ao path para importar protobuf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

import grpc
import xml_service_pb2 as pb2
import xml_service_pb2_grpc as pb2_grpc

def main():
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.XMLServiceStub(channel)
    
    # Listar XMLs
    response = stub.ListXMLs(pb2.Empty())
    
    print(f"Total: {response.count} ficheiro(s)")
    print()
    
    for file_info in response.files:
        print(f"ID: {file_info.xml_id}")
        print(f"Nome: {file_info.filename}")
        print(f"Data: {file_info.created_at}")
        print("-" * 60)

if __name__ == '__main__':
    main()
