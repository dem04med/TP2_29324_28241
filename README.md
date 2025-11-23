# Sistema de Processamento XML com RPC Multi-Protocolo

Sistema de processamento e armazenamento de documentos XML com **XML-RPC** e **gRPC**, usando MongoDB com GridFS.

## Pré-requisitos

- Docker Desktop
- Python 3.12+ com pip

## Configuração Inicial

```powershell
# Iniciar serviços
docker-compose up -d

# Instalar dependências
python -m pip install grpcio grpcio-tools

# Testar
python client/xmlrpc/client_status.py
python client/grpc/client_status.py
```

## Arquitetura

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **xmlrpc_server** | 8000 | Servidor XML-RPC |
| **grpc_server** | 50051 | Servidor gRPC |
| **mongo** | 27017 | MongoDB 7 + GridFS |
| **mongo_express** | 8081 | Interface web MongoDB |

## Funcionalidades

-  Conversão CSV → XML com geração automática de XSD
-  Validação XML contra schemas XSD
-  Conversão XML ↔ JSON
-  Consultas XPath sobre documentos
-  GridFS automático para ficheiros >15MB
-  Dual protocol: XML-RPC e gRPC

## Uso Básico

### Workflow Completo

```powershell
# 1. Converter CSV para XML
python client/xmlrpc/client_convert.py data/datasets/Sales.csv --generate-schema

# 2. Listar XMLs (obter ID)
python client/xmlrpc/client_list.py

# 3. Consultas XPath
python client/xmlrpc/client_query.py <xml_id> "count(//record)"
python client/xmlrpc/client_query.py <xml_id> "sum(//record/revenue)"

# 4. Converter para JSON
python client/xmlrpc/client_to_json.py <xml_id> output.json

# 5. Validar XML
python client/xmlrpc/client_validate.py <xml_id> data/xml_schemas/Sales.xsd
```

**gRPC:** Substituir `client/xmlrpc/` por `client/grpc/`

## APIs Disponíveis

### XML-RPC (localhost:8000)

```python
import xmlrpc.client

server = xmlrpc.client.ServerProxy('http://localhost:8000')
result = server.query_xml_xpath(xml_id, "count(//record)")
```

**Métodos:** `ping`, `get_server_status`, `convert_csv_to_xml`, `generate_xsd_schema`, `store_xml`, `retrieve_xml`, `list_xml_files`, `query_xml_xpath`, `convert_xml_to_json`, `validate_xml_content`

### gRPC (localhost:50051)

```protobuf
service XMLService {
  rpc Ping(Empty) returns (XMLResponse);
  rpc StoreXML(StoreXMLRequest) returns (StoreXMLResponse);
  rpc GetXML(GetXMLRequest) returns (XMLResponse);
  rpc ListXMLs(Empty) returns (ListXMLResponse);
  rpc QueryXPath(XPathRequest) returns (XPathResponse);
  rpc ConvertToJSON(ConvertToJSONRequest) returns (ConvertToJSONResponse);
  rpc ValidateXML(ValidateXMLRequest) returns (ValidateXMLResponse);
}
```

## Estrutura do Projeto

```
TP2_29324_28241/
├── docker-compose.yml
├── server/
│   ├── xmlrpc_server.py
│   ├── grpc_server.py
│   ├── xml_service.proto
│   ├── xml_converter.py
│   └── db_utils.py (MongoDB + GridFS)
├── client/
│   ├── xmlrpc/          # 7 clientes + README
│   └── grpc/            # 7 clientes + README
└── data/
    ├── datasets/
    └── xml_schemas/
```

## Documentação Detalhada

- [client/xmlrpc/README.md](client/xmlrpc/README.md) - Comandos e exemplos XML-RPC
- [client/grpc/README.md](client/grpc/README.md) - Comandos e exemplos gRPC

## Troubleshooting

```powershell
# Ver logs
docker-compose logs xmlrpc_server
docker-compose logs grpc_server

# Reiniciar
docker-compose restart xmlrpc_server

# Reset completo
docker-compose down -v
docker-compose build
docker-compose up -d

# Acesso MongoDB
http://localhost:8081
```

## Tecnologias

Python 3.13 • MongoDB 7 • GridFS • XML-RPC • gRPC • lxml • pandas • Docker
