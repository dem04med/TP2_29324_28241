#!/usr/bin/env python3
"""
Cliente gRPC para conversão de CSV para XML
Uso: python client_convert.py <caminho_csv> [--generate-schema]
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
        print("Uso: python client_convert.py <caminho_csv> [--generate-schema]")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    generate_schema = '--generate-schema' in sys.argv
    
    if not os.path.exists(csv_path):
        print(f"Erro: Ficheiro {csv_path} não encontrado")
        sys.exit(1)
    
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.XMLServiceStub(channel)
    
    # Ler ficheiro CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_data = f.read()
    
    # Converter CSV para XML (usando XML-RPC temporariamente para conversão)
    import xmlrpc.client
    xmlrpc_server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    filename = os.path.basename(csv_path).replace('.csv', '.xml')
    xml_result = xmlrpc_server.convert_csv_to_xml(csv_data, 'dataset', 'record')
    
    if not xml_result.get('success'):
        print(f"Erro na conversão: {xml_result.get('error')}")
        sys.exit(1)
    
    xml_content = xml_result['xml_content']
    
    # Armazenar via gRPC
    response = stub.StoreXML(pb2.StoreXMLRequest(
        filename=filename,
        xml_content=xml_content
    ))
    
    if not response.success:
        print(f"Erro ao armazenar: {response.message}")
        sys.exit(1)
    
    print(f"XML ID: {response.xml_id}")
    
    # Gerar schema XSD se solicitado
    if generate_schema:
        xsd_result = xmlrpc_server.generate_xsd_schema(response.xml_id)
        
        if xsd_result.get('success'):
            xsd_filename = f"data/xml_schemas/{os.path.basename(csv_path).replace('.csv', '.xsd')}"
            os.makedirs('data/xml_schemas', exist_ok=True)
            
            with open(xsd_filename, 'w', encoding='utf-8') as f:
                f.write(xsd_result['xsd_content'])
            
            print(f"XSD Schema: {xsd_filename}")

if __name__ == '__main__':
    main()
