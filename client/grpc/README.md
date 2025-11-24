# Cliente gRPC - Guia de Comandos

Comandos para interagir com o servidor gRPC (porta 50051).

## Pré-requisitos

Certifica-te que os servidores estão a correr:
```powershell
docker-compose up -d
```

Instalar dependências gRPC (se necessário):
```powershell
python -m pip install grpcio grpcio-tools
```

---

## 1. Verificar Status do Servidor

```powershell
python client/grpc/client_status.py
```

**Output esperado:**
```
Ping: pong

✓ Servidor gRPC operacional
```

---

## 2. Converter CSV para XML e Armazenar

**Nota:** A conversão CSV ainda utiliza o servidor XML-RPC.

```powershell
python client/xmlrpc/client_convert.py <caminho_csv> [--generate-schema]
```

### Exemplo
```powershell
# Converter Sales.csv completo com geração de XSD
python client/xmlrpc/client_convert.py data/datasets/Sales.csv --generate-schema
```

**Output:** Retorna o `XML ID` que será usado nos comandos gRPC seguintes.

---

## 3. Listar XMLs Armazenados

```powershell
python client/grpc/client_list.py
```

**Output:**
```
Total: 3 ficheiro(s)

ID: 69238907fb662cc0e919c437
Nome: Sales.xml
Data: 2025-11-23T22:21:59.620000
------------------------------------------------------------
```

---

## 4. Consultas XPath

### Sintaxe
```powershell
python client/grpc/client_query.py <xml_id> "<xpath_expression>"
```

### Exemplos Básicos

```powershell
# Contar total de registos
python client/grpc/client_query.py 69238907fb662cc0e919c437 "count(//record)"

# Primeira data
python client/grpc/client_query.py 69238907fb662cc0e919c437 "//record[1]/date/text()"

# Última data
python client/grpc/client_query.py 69238907fb662cc0e919c437 "//record[last()]/date/text()"
```

### Exemplos com Filtros

```powershell
# Vendas por país (ex: Canada) - contar
python client/grpc/client_query.py 69238907fb662cc0e919c437 "count(//record[country='Canada'])"

# Vendas por país - listar primeiros 5 países
python client/grpc/client_query.py 69238907fb662cc0e919c437 "//record[position() <= 5]/country/text()"

# Vendas por categoria de produto - contar
python client/grpc/client_query.py 69238907fb662cc0e919c437 "count(//record[product_category='Bikes'])"

# Listar primeiros 5 produtos da categoria Bikes
python client/grpc/client_query.py 69238907fb662cc0e919c437 "//record[product_category='Bikes'][position() <= 5]/product/text()"

# Vendas por género - contar
python client/grpc/client_query.py 69238907fb662cc0e919c437 "count(//record[customer_gender='F'])"

# Listar idades das primeiras 10 clientes femininas
python client/grpc/client_query.py 69238907fb662cc0e919c437 "//record[customer_gender='F'][position() <= 10]/customer_age/text()"

# Filtros combinados - contar
python client/grpc/client_query.py 69238907fb662cc0e919c437 "count(//record[country='Canada' and product_category='Bikes'])"

# Listar produtos vendidos no Canada na categoria Bikes (primeiros 5)
python client/grpc/client_query.py 69238907fb662cc0e919c437 "//record[country='Canada' and product_category='Bikes'][position() <= 5]/product/text()"
```

### Exemplos com Agregações

```powershell
# Soma total de revenue
python client/grpc/client_query.py 69238907fb662cc0e919c437 "sum(//record/revenue)"

# Soma total de profit
python client/grpc/client_query.py 69238907fb662cc0e919c437 "sum(//record/profit)"

# Média de idade dos clientes
python client/grpc/client_query.py 69238907fb662cc0e919c437 "sum(//record/customer_age) div count(//record)"

# Revenue de vendas femininas
python client/grpc/client_query.py 69238907fb662cc0e919c437 "sum(//record[customer_gender='F']/revenue)"
```

### Campos Disponíveis (Sales.csv)

- `date`, `day`, `month`, `year`
- `customer_age`, `age_group`, `customer_gender`
- `country`, `state`
- `product_category`, `sub_category`, `product`
- `order_quantity`, `unit_cost`, `unit_price`
- `profit`, `cost`, `revenue`

**Nota:** Os nomes dos campos são convertidos para lowercase com underscores.

---

## 5. Converter XML para JSON

### Sintaxe
```powershell
python client/grpc/client_to_json.py <xml_id> [output_file.json]
```

### Exemplos

```powershell
# Mostrar JSON no terminal
python client/grpc/client_to_json.py 69238907fb662cc0e919c437

# Guardar em ficheiro
python client/grpc/client_to_json.py 69238907fb662cc0e919c437 sales_grpc.json
```

---

## 6. Obter XML Armazenado

### Sintaxe
```powershell
python client/grpc/client_get_xml.py <xml_id> [output_file.xml]
```

### Exemplos

```powershell
# Mostrar preview do XML (primeiros 500 caracteres)
python client/grpc/client_get_xml.py 69238907fb662cc0e919c437

# Guardar XML completo em ficheiro
python client/grpc/client_get_xml.py 69238907fb662cc0e919c437 sales_grpc.xml
```

**Atenção:** Para ficheiros grandes (>15MB GridFS), o preview mostrará apenas os primeiros 500 caracteres.

---

## 7. Validar XML

### Sintaxe
```powershell
python client/grpc/client_validate.py <xml_id> [schema.xsd]
```

### Exemplos

```powershell
# Validar XML bem formado (sem schema)
python client/grpc/client_validate.py 69238907fb662cc0e919c437

# Validar contra schema XSD gerado
python client/grpc/client_validate.py 69238907fb662cc0e919c437 data/xml_schemas/Sales.xsd
```

**Output:**
```
✓ XML válido: XML bem formado
```

---

## Workflow Completo - Sales.csv

```powershell
# 1. Converter CSV para XML (via XML-RPC)
python client/xmlrpc/client_convert.py data/datasets/Sales.csv --generate-schema

# 2. Verificar servidor gRPC
python client/grpc/client_status.py

# 3. Listar XMLs disponíveis
python client/grpc/client_list.py

# 4. Consultas XPath (usar ID retornado no passo 1)
python client/grpc/client_query.py 69238907fb662cc0e919c437 "count(//record)"
python client/grpc/client_query.py 69238907fb662cc0e919c437 "sum(//record/revenue)"

# 5. Converter para JSON
python client/grpc/client_to_json.py 69238907fb662cc0e919c437 sales_output.json

# 6. Validar XML
python client/grpc/client_validate.py 69238907fb662cc0e919c437 data/xml_schemas/Sales.xsd
```

---

## Diferenças vs XML-RPC

| Aspecto | XML-RPC | gRPC |
|---------|---------|------|
| **Porta** | 8000 | 50051 |
| **Protocolo** | XML sobre HTTP | Protocol Buffers sobre HTTP/2 |
| **Performance** | Mais lento | Mais rápido |
| **Path** | `client/xmlrpc/` | `client/grpc/` |
| **Conversão CSV** | Suportada | Via XML-RPC |

---

## Troubleshooting

### Erro: "No module named 'grpc'"
```powershell
python -m pip install grpcio grpcio-tools
```

### Erro: "failed to connect to all addresses"
Verificar se o servidor gRPC está a correr:
```powershell
docker-compose ps grpc_server
docker-compose logs grpc_server
```

Reiniciar se necessário:
```powershell
docker-compose restart grpc_server
```

### Servidor não arranca após alterações no .proto
Rebuild do container:
```powershell
docker-compose stop grpc_server
docker-compose build grpc_server
docker-compose up -d grpc_server
```
