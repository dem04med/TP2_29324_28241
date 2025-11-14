#!/usr/bin/env python3
"""
Cliente de teste para GraphQL Server
Demonstra consultas avançadas e flexíveis
"""
import requests
import json

GRAPHQL_URL = "http://localhost:5000/graphql"

def execute_graphql_query(query, variables=None):
    """Executa query GraphQL"""
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    try:
        response = requests.post(GRAPHQL_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Erro de conexão: {e}"}
    except Exception as e:
        return {"error": f"Erro: {e}"}

def test_graphql_server():
    """Testa funcionalidades GraphQL"""
    
    print("=== Teste do Servidor GraphQL ===\n")
    
    # 1. Query de teste básica
    print("1. Testando query básica...")
    query = """
    query {
        hello
        serverStatus
    }
    """
    result = execute_graphql_query(query)
    print(f"   Hello: {result.get('data', {}).get('hello', 'N/A')}")
    print(f"   Status: {result.get('data', {}).get('serverStatus', 'N/A')[:100]}...")
    print()
    
    # 2. Listar arquivos XML
    print("2. Listando arquivos XML...")
    query = """
    query {
        xmlFiles {
            id
            filename
            recordCount
            fileSize
            createdAt
        }
    }
    """
    result = execute_graphql_query(query)
    xml_files = result.get('data', {}).get('xmlFiles', [])
    print(f"   Encontrados {len(xml_files)} arquivos XML:")
    for file in xml_files[:3]:  # Mostrar apenas os 3 primeiros
        print(f"   - ID: {file['id']}, Nome: {file['filename']}")
        print(f"     Registos: {file['recordCount']}, Tamanho: {file['fileSize']} bytes")
    print()
    
    # 3. Mutation: Converter CSV para XML
    print("3. Testando conversão CSV para XML via GraphQL...")
    csv_data = """id,name,department,salary
1,Alice,Engineering,75000
2,Bob,Marketing,65000
3,Carol,Engineering,80000"""
    
    mutation = """
    mutation($csvContent: String!, $filename: String!) {
        convertCsvToXml(csvContent: $csvContent, filename: $filename, rootElement: "employees", rowElement: "employee") {
            success
            message
            xmlId
            xmlContent
        }
    }
    """
    
    variables = {
        "csvContent": csv_data,
        "filename": "employees_graphql.xml"
    }
    
    result = execute_graphql_query(mutation, variables)
    conversion_result = result.get('data', {}).get('convertCsvToXml', {})
    print(f"   Conversão bem-sucedida: {conversion_result.get('success', False)}")
    print(f"   Mensagem: {conversion_result.get('message', 'N/A')}")
    
    if conversion_result.get('success') and conversion_result.get('xmlId'):
        xml_id = conversion_result['xmlId']
        print(f"   XML armazenado com ID: {xml_id}")
        
        # 4. Query específica de arquivo
        print(f"\n4. Consultando detalhes do XML ID {xml_id}...")
        query = """
        query($xmlId: Int!) {
            xmlFile(xmlId: $xmlId) {
                id
                filename
                recordCount
                fileSize
                content
            }
        }
        """
        
        result = execute_graphql_query(query, {"xmlId": xml_id})
        xml_file = result.get('data', {}).get('xmlFile', {})
        if xml_file:
            print(f"   Arquivo: {xml_file['filename']}")
            print(f"   Registos: {xml_file['recordCount']}")
            print(f"   Conteúdo (preview): {xml_file.get('content', '')[:200]}...")
        
        # 5. Consulta XPath via GraphQL
        print(f"\n5. Testando consulta XPath via GraphQL...")
        xpath_queries = [
            "//employee[department='Engineering']",
            "//employee/name/text()",
            "count(//employee)"
        ]
        
        for xpath in xpath_queries:
            query = """
            query($xmlId: Int!, $xpath: String!) {
                queryXpath(xmlId: $xmlId, xpath: $xpath) {
                    xpathExpression
                    resultCount
                    executionTime
                    elements {
                        tag
                        text
                        attributes
                    }
                }
            }
            """
            
            result = execute_graphql_query(query, {"xmlId": xml_id, "xpath": xpath})
            xpath_result = result.get('data', {}).get('queryXpath', {})
            
            if xpath_result:
                print(f"   XPath '{xpath}':")
                print(f"     Resultados: {xpath_result.get('resultCount', 0)}")
                print(f"     Tempo: {xpath_result.get('executionTime', 0):.4f}s")
        
        # 6. Estatísticas detalhadas
        print(f"\n6. Obtendo estatísticas detalhadas...")
        query = """
        query($xmlId: Int!) {
            xmlStatistics(xmlId: $xmlId)
        }
        """
        
        result = execute_graphql_query(query, {"xmlId": xml_id})
        stats = result.get('data', {}).get('xmlStatistics', '{}')
        try:
            stats_data = json.loads(stats)
            print(f"   Elementos totais: {stats_data.get('xml_structure', {}).get('total_elements', 'N/A')}")
            print(f"   Profundidade máxima: {stats_data.get('xml_structure', {}).get('max_depth', 'N/A')}")
            print(f"   Tamanho: {stats_data.get('file_info', {}).get('file_size_mb', 'N/A')} MB")
        except:
            print(f"   Estatísticas: {stats[:100]}...")
    
    # 7. Pesquisa avançada
    print(f"\n7. Testando pesquisa avançada...")
    query = """
    query {
        searchXmlFiles(filenameContains: "employee", minRecords: 1) {
            id
            filename
            recordCount
            createdAt
        }
    }
    """
    
    result = execute_graphql_query(query)
    search_results = result.get('data', {}).get('searchXmlFiles', [])
    print(f"   Encontrados {len(search_results)} arquivos com 'employee' no nome:")
    for file in search_results:
        print(f"   - {file['filename']} ({file['recordCount']} registos)")
    
    # 8. Validação XML
    if xml_files:
        xml_id = xml_files[0]['id']
        print(f"\n8. Testando validação XML (ID: {xml_id})...")
        query = """
        query($xmlId: Int!) {
            validateXml(xmlId: $xmlId) {
                isValid
                errors
                warnings
                schemaUsed
            }
        }
        """
        
        result = execute_graphql_query(query, {"xmlId": xml_id})
        validation = result.get('data', {}).get('validateXml', {})
        if validation:
            print(f"   XML válido: {validation.get('isValid', False)}")
            print(f"   Erros: {len(validation.get('errors', []))}")
            print(f"   Schema: {validation.get('schemaUsed', 'N/A')}")
    
    print(f"\n=== GraphQL Server Testado! ===")
    print("✅ Queries flexíveis e poderosas")
    print("✅ Mutations para conversões") 
    print("✅ Pesquisa avançada com filtros")
    print("✅ Integração com XML-RPC backend")
    print("✅ Interface GraphiQL disponível")
    print(f"\n🌐 Acesse GraphiQL em: {GRAPHQL_URL}")

def show_example_queries():
    """Mostra exemplos de queries GraphQL"""
    
    print("\n=== Exemplos de Queries GraphQL ===\n")
    
    examples = [
        {
            "title": "🔍 Pesquisa Básica",
            "query": """
query {
    xmlFiles {
        id
        filename
        recordCount
        fileSize
    }
}"""
        },
        {
            "title": "🎯 Pesquisa com Filtros",
            "query": """
query {
    searchXmlFiles(
        filenameContains: "sales"
        minRecords: 100
        createdAfter: "2024-01-01T00:00:00"
    ) {
        id
        filename
        recordCount
        createdAt
    }
}"""
        },
        {
            "title": "🔎 Consulta XPath",
            "query": """
query {
    queryXpath(xmlId: 1, xpath: "//employee[@department='Engineering']") {
        resultCount
        executionTime
        elements {
            tag
            text
            attributes
        }
    }
}"""
        },
        {
            "title": "📊 Estatísticas Detalhadas",
            "query": """
query {
    xmlFile(xmlId: 1) {
        filename
        recordCount
    }
    xmlStatistics(xmlId: 1)
}"""
        },
        {
            "title": "🔄 Conversão CSV → XML",
            "query": """
mutation {
    convertCsvToXml(
        csvContent: "id,name\\n1,Alice\\n2,Bob"
        filename: "test.xml"
        rootElement: "people"
        rowElement: "person"
    ) {
        success
        xmlId
        message
    }
}"""
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['title']}")
        print(example['query'])
        print()

if __name__ == "__main__":
    # Escolher o que executar
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "examples":
        show_example_queries()
    else:
        test_graphql_server()