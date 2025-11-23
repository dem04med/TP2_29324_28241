#!/usr/bin/env python3
"""
Cliente gRPC para consultas XPath
Uso: python client_query.py <xml_id> <xpath_expression>
"""

import sys
import os

# Adicionar pasta server ao path para importar protobuf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

import grpc
import xml_service_pb2 as pb2
import xml_service_pb2_grpc as pb2_grpc

def main():
    if len(sys.argv) < 3:
        print("Uso: python client_query.py <xml_id> <xpath_expression>")
        print("\nExemplos:")
        print('  python client_query.py 692358... "count(//record)"')
        print('  python client_query.py 692358... "//record[1]/date/text()"')
        print('  python client_query.py 692358... "sum(//record/total)"')
        sys.exit(1)
    
    xml_id = sys.argv[1]
    xpath_expression = sys.argv[2]
    
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.XMLServiceStub(channel)
    
    # Executar consulta XPath
    response = stub.QueryXPath(pb2.XPathRequest(
        xml_id=xml_id,
        expression=xpath_expression
    ))
    
    if not response.success:
        print(f"Erro: {response.message}")
        sys.exit(1)
    
    # Mostrar resultados
    if len(response.results) == 1:
        print(response.results[0])
    else:
        for i, item in enumerate(response.results, 1):
            print(f"{i}. {item}")

if __name__ == '__main__':
    main()
