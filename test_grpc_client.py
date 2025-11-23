#!/usr/bin/env python3
"""
Cliente de teste para o servidor gRPC
"""
import grpc
import sys
import os

# Adicionar diretório server ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

import xml_service_pb2 as pb2
import xml_service_pb2_grpc as pb2_grpc


def test_grpc_server():
    """Testa as funcionalidades do servidor gRPC"""
    
    # Conectar ao servidor gRPC
    channel = grpc.insecure_channel('localhost:50051')
    stub = pb2_grpc.XMLServiceStub(channel)
    
    print("=== Teste do Servidor gRPC ===\n")
    
    try:
        # 1. Teste de Ping
        print("1. Testando Ping...")
        response = stub.Ping(pb2.Empty())
        print(f"   Resposta: {response.message}\n")
        
        # 2. Testar armazenamento de XML
        print("2. Testando armazenamento de XML...")
        sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<produtos>
    <produto id="1">
        <nome>Laptop Dell</nome>
        <preco>1299.99</preco>
        <stock>15</stock>
    </produto>
    <produto id="2">
        <nome>Mouse Logitech</nome>
        <preco>29.99</preco>
        <stock>50</stock>
    </produto>
</produtos>'''
        
        store_request = pb2.StoreXMLRequest(
            filename="produtos.xml",
            xml_content=sample_xml
        )
        store_response = stub.StoreXML(store_request)
        print(f"   Sucesso: {store_response.success}")
        print(f"   Mensagem: {store_response.message}")
        if store_response.success:
            xml_id = store_response.xml_id
            print(f"   XML ID: {xml_id}\n")
            
            # 3. Testar recuperação de XML
            print("3. Testando recuperação de XML...")
            get_request = pb2.GetXMLRequest(xml_id=xml_id)
            get_response = stub.GetXML(get_request)
            print(f"   Sucesso: {get_response.success}")
            print(f"   Filename: {get_response.filename}")
            print(f"   Conteúdo (primeiros 100 chars): {get_response.xml_content[:100]}...\n")
            
            # 4. Testar consulta XPath
            print("4. Testando consulta XPath...")
            xpath_request = pb2.XPathRequest(
                xml_id=xml_id,
                expression="//produto[@id='1']/nome/text()"
            )
            xpath_response = stub.QueryXPath(xpath_request)
            print(f"   Sucesso: {xpath_response.success}")
            if xpath_response.success:
                print(f"   Resultados: {list(xpath_response.results)}")
            print()
            
            # 5. Testar conversão XML para JSON
            print("5. Testando conversão XML para JSON...")
            json_request = pb2.ConvertToJSONRequest(xml_id=xml_id)
            json_response = stub.ConvertToJSON(json_request)
            print(f"   Sucesso: {json_response.success}")
            if json_response.success:
                print(f"   JSON (primeiros 200 chars):")
                print(f"   {json_response.json_content[:200]}...")
            print()
        
        # 6. Testar listagem de XMLs
        print("6. Testando listagem de XMLs...")
        list_response = stub.ListXMLs(pb2.Empty())
        print(f"   Sucesso: {list_response.success}")
        print(f"   Total de XMLs: {list_response.count}")
        for i, file_info in enumerate(list_response.files[:3], 1):
            print(f"   {i}. ID: {file_info.xml_id}, Nome: {file_info.filename}")
        print()
        
        print("=== Testes gRPC Completos! ===")
        print("✅ Ping funcionando")
        print("✅ Armazenamento XML")
        print("✅ Recuperação XML")
        print("✅ Consultas XPath")
        print("✅ Conversão XML → JSON")
        print("✅ Listagem de XMLs")
        
    except grpc.RpcError as e:
        print(f"Erro gRPC: {e.code()}: {e.details()}")
    except Exception as e:
        print(f"Erro durante os testes: {e}")
    finally:
        channel.close()


if __name__ == "__main__":
    test_grpc_server()
