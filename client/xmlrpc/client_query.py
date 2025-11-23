#!/usr/bin/env python3
"""
Cliente para consultas XPath via XML-RPC
Uso: python client_query.py <xml_id> <xpath_expression>
"""

import sys
import xmlrpc.client

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
    
    # Conectar ao servidor XML-RPC
    server = xmlrpc.client.ServerProxy('http://localhost:8000')
    
    # Executar consulta XPath
    result = server.query_xml_xpath(xml_id, xpath_expression)
    
    if not result.get('success'):
        print(f"Erro: {result.get('error')}")
        sys.exit(1)
    
    query_result = result['query_result']
    results = query_result['results']
    
    # Mostrar resultados
    if len(results) == 1:
        print(results[0])
    else:
        for i, item in enumerate(results, 1):
            print(f"{i}. {item}")

if __name__ == '__main__':
    main()
