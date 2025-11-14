# XML-RPC Server com PostgreSQL

Servidor XML-RPC para processamento e armazenamento de documentos XML com base de dados PostgreSQL.

## Pré-requisitos

- Docker Desktop ([Download](https://www.docker.com/products/docker-desktop/))
- PowerShell (Windows)

## Início Rápido

```powershell
# Construir e iniciar
.\docker-manager.ps1 build
.\docker-manager.ps1 start

# Testar funcionamento
.\docker-manager.ps1 test
```

## Comandos Principais

| Comando | Descrição |
|---------|-----------|
| `.\docker-manager.ps1 build` | Construir imagens Docker |
| `.\docker-manager.ps1 start` | Iniciar serviços |
| `.\docker-manager.ps1 test` | Executar testes |
| `.\docker-manager.ps1 status` | Verificar estado |
| `.\docker-manager.ps1 logs` | Ver logs |
| `.\docker-manager.ps1 stop` | Parar serviços |
| `.\docker-manager.ps1 clean` | Limpar containers e volumes |

## Estrutura do Projeto

```
TP2_29324_28241/
├── docker-compose.yml       # Orquestração de containers
├── docker-manager.ps1       # Script de gestão
└── server/
    ├── xmlrpc_server.py     # Servidor XML-RPC (porta 8000)
    ├── xml_converter.py     # Processamento XML/CSV
    ├── db_utils.py          # Utilitários PostgreSQL
    └── test_client.py       # Cliente de teste
```

## Funcionalidades

- **Conversão CSV → XML** com deteção automática de tipos
- **Geração de schemas XSD** a partir de XML
- **Consultas XPath/XQuery** sobre documentos armazenados
- **Conversão XML ↔ JSON** bidirecional
- **Validação XML** contra schemas XSD
- **Armazenamento PostgreSQL** de documentos
- **API XML-RPC** na porta 8000

## API XML-RPC (localhost:8000)

### Métodos Principais

- `ping()` - Testa conectividade
- `get_server_status()` - Status do servidor e BD
- `store_xml(filename, xml_content)` - Armazena XML
- `retrieve_xml(xml_id)` - Recupera XML por ID
- `list_xml_files()` - Lista todos os documentos
- `convert_xml_to_json(xml_id)` - XML para JSON
- `convert_json_to_xml(json_content, root_element)` - JSON para XML
- `validate_xml_content(xml_content, schema_filename)` - Valida XML
- `convert_csv_to_xml(csv_content, root_element, row_element)` - CSV para XML
- `generate_xsd_schema(xml_content, target_namespace)` - Gera XSD
- `query_xml_xpath(xml_id, xpath_expression)` - Consulta XPath
- `query_xml_xquery(xml_id, xquery_expression)` - Consulta XQuery

### Exemplo de Uso

```python
import xmlrpc.client

server = xmlrpc.client.ServerProxy('http://localhost:8000')

# Armazenar XML
result = server.store_xml("exemplo.xml", "<root><item>valor</item></root>")
xml_id = result["xml_id"]

# Converter para JSON
json_result = server.convert_xml_to_json(xml_id)
print(json_result["json_content"])
```

## Base de Dados PostgreSQL

- **Host:** localhost:5432
- **Database:** xmlrpc_db
- **User/Password:** user/password

Acesso via Docker:
```powershell
.\docker-manager.ps1 db
```

## Resolução de Problemas

**Portas ocupadas:** Altere as portas no `docker-compose.yml`

**Erro de conexão:** Reinicie os serviços
```powershell
.\docker-manager.ps1 restart
```

**Reset completo:**
```powershell
.\docker-manager.ps1 clean
.\docker-manager.ps1 build
.\docker-manager.ps1 start
```
