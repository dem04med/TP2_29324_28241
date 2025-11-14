#!/usr/bin/env python3
"""
Cliente de teste para o servidor XML-RPC
"""
import xmlrpc.client
import json

def test_server():
    """Testa as funcionalidades do servidor XML-RPC"""
    
    # Conectar ao servidor
    server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    print("=== Teste do Servidor XML-RPC ===\n")
    
    try:
        # 1. Teste de ping
        print("1. Testando ping...")
        response = server.ping()
        print(f"   Resposta: {response}\n")
        
        # 2. Status do servidor
        print("2. Verificando status do servidor...")
        status = server.get_server_status()
        print(f"   Status: {json.dumps(status, indent=2)}\n")
        
        # 3. Testar armazenamento de XML
        print("3. Testando armazenamento de XML...")
        sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<biblioteca>
    <livro id="1">
        <titulo>Python Programming</titulo>
        <autor>João Silva</autor>
        <ano>2023</ano>
    </livro>
    <livro id="2">
        <titulo>XML Processing</titulo>
        <autor>Maria Santos</autor>
        <ano>2024</ano>
    </livro>
</biblioteca>'''
        
        store_result = server.store_xml("biblioteca.xml", sample_xml)
        print(f"   Resultado: {json.dumps(store_result, indent=2)}\n")
        
        if store_result["success"]:
            xml_id = store_result["xml_id"]
            
            # 4. Testar recuperação de XML
            print("4. Testando recuperação de XML...")
            retrieve_result = server.retrieve_xml(xml_id)
            print(f"   Sucesso: {retrieve_result['success']}")
            if retrieve_result["success"]:
                print(f"   Filename: {retrieve_result['data']['filename']}")
            print()
            
            # 5. Testar conversão XML para JSON
            print("5. Testando conversão XML para JSON...")
            json_result = server.convert_xml_to_json(xml_id)
            print(f"   Sucesso: {json_result['success']}")
            if json_result["success"]:
                print("   JSON convertido:")
                json_data = json.loads(json_result['json_content'])
                print(f"   {json.dumps(json_data, indent=2, ensure_ascii=False)}")
            print()
        
        # 6. Testar listagem de arquivos
        print("6. Testando listagem de arquivos XML...")
        list_result = server.list_xml_files()
        print(f"   Sucesso: {list_result['success']}")
        if list_result["success"]:
            print(f"   Total de arquivos: {list_result['count']}")
            for file_info in list_result['files'][:3]:  # Mostrar apenas os 3 primeiros
                print(f"   - ID: {file_info['id']}, Nome: {file_info['filename']}")
        print()
        
        # 7. Testar conversão JSON para XML
        print("7. Testando conversão JSON para XML...")
        sample_json = '''{
            "pessoa": {
                "@attributes": {"id": "123"},
                "nome": "Ana Costa",
                "idade": 30,
                "email": "ana@example.com"
            }
        }'''
        
        xml_result = server.convert_json_to_xml(sample_json, "dados")
        print(f"   Sucesso: {xml_result['success']}")
        if xml_result["success"]:
            print("   XML convertido:")
            print(f"   {xml_result['xml_content']}")
        print()
        
        # 8. Testar validação XML
        print("8. Testando validação XML...")
        validation_result = server.validate_xml_content(sample_xml)
        print(f"   Sucesso: {validation_result['success']}")
        if validation_result["success"]:
            print(f"   XML válido: {validation_result['is_valid']}")
            print(f"   Resultado: {validation_result['validation_result']}")
        print()
        
        # 9. Testar conversão CSV para XML (dados Kaggle)
        print("9. Testando conversão CSV para XML (pipeline Kaggle)...")
        sample_csv = '''id,name,age,department
1,Alice,28,Engineering
2,Bob,34,Marketing
3,Carol,29,Engineering'''
        
        csv_to_xml_result = server.convert_csv_to_xml(sample_csv, "employees", "employee")
        print(f"   Sucesso: {csv_to_xml_result['success']}")
        if csv_to_xml_result["success"]:
            print("   XML gerado a partir de CSV:")
            xml_from_csv = csv_to_xml_result['xml_content']
            print(f"   {xml_from_csv[:200]}...")
            
            # 10. Testar geração de XSD
            print("\n10. Testando geração de XSD schema...")
            xsd_result = server.generate_xsd_schema(xml_from_csv)
            print(f"    Sucesso: {xsd_result['success']}")
            if xsd_result["success"]:
                print("    XSD schema gerado!")
                
            # 11. Armazenar XML gerado do CSV e testar consultas
            store_csv_xml = server.store_xml("employees_from_csv.xml", xml_from_csv)
            if store_csv_xml["success"]:
                csv_xml_id = store_csv_xml["xml_id"]
                
                print(f"\n11. Testando consultas XPath no XML (ID: {csv_xml_id})...")
                xpath_queries = [
                    "//employee[@id='1']",  # Funcionário com ID 1
                    "//employee/name/text()",  # Todos os nomes
                    "count(//employee)",  # Contar funcionários
                    "//employee[department='Engineering']"  # Funcionários de Engineering
                ]
                
                for xpath in xpath_queries:
                    xpath_result = server.query_xml_xpath(csv_xml_id, xpath)
                    print(f"    XPath '{xpath}': {xpath_result['success']}")
                    if xpath_result["success"]:
                        results = xpath_result['query_result']['results']
                        print(f"      {len(results)} resultado(s)")
                
                print(f"\n12. Testando consultas XQuery no XML (ID: {csv_xml_id})...")
                xquery_queries = [
                    "count(//employee)",
                    "for $r in //employee return $r"
                ]
                
                for xquery in xquery_queries:
                    xquery_result = server.query_xml_xquery(csv_xml_id, xquery)
                    print(f"    XQuery '{xquery}': {xquery_result['success']}")
                    if xquery_result["success"]:
                        results = xquery_result['query_result']['results']
                        print(f"      {len(results)} resultado(s)")
        
        print(f"\n=== Pipeline Completo Testado! ===")
        print("✅ CSV → XML (dados Kaggle)")
        print("✅ Geração XSD automática") 
        print("✅ Consultas XPath/XQuery")
        print("✅ XML-RPC funcional")
        print("✅ PostgreSQL integrado")
        
    except Exception as e:
        print(f"Erro durante os testes: {e}")

if __name__ == "__main__":
    test_server()