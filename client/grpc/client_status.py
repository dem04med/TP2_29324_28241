#!/usr/bin/env python3
"""
Cliente gRPC para verificar status do servidor
Uso: python client_status.py
"""

import sys
import os

# Adicionar pasta server ao path para importar protobuf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

import grpc
import xml_service_pb2 as pb2
import xml_service_pb2_grpc as pb2_grpc

def main():
    try:
        # Conectar ao servidor gRPC
        channel = grpc.insecure_channel('localhost:50051')
        stub = pb2_grpc.XMLServiceStub(channel)
        
        # Ping
        response = stub.Ping(pb2.Empty())
        print(f"Ping: {response.message}")
        
        print("\n✓ Servidor gRPC operacional")
        
    except Exception as e:
        print(f"✗ Erro ao conectar ao servidor: {e}")
        print("\nVerifique se o servidor está a correr:")
        print("  docker-compose up -d")

if __name__ == '__main__':
    main()
