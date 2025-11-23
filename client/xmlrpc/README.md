# Cliente XML-RPC - Guia de Comandos

Comandos para interagir com o servidor XML-RPC (porta 8000).

## Pré-requisitos

Certifica-te que os servidores estão a correr:
```powershell
docker-compose up -d
```

---

## 1. Verificar Status do Servidor

```powershell
python client/xmlrpc/client_status.py
```

**Output esperado:**
```
Ping: pong
Status: ativo
Database: conectado
```

---

## 2. Converter CSV para XML e Armazenar

### Sintaxe
```powershell
python client/xmlrpc/client_convert.py <caminho_csv> [--generate-schema]
```

### Exemplos
```powershell
# Converter Sales.csv completo com geração de XSD
python client/xmlrpc/client_convert.py data/datasets/Sales.csv --generate-schema

# Converter sales_data.csv
python client/xmlrpc/client_convert.py data/datasets/sales_data.csv --generate-schema
```

**Output:** Retorna o `XML ID` que será usado nos comandos seguintes.

**Nota:** Ficheiros grandes (>15MB) são automaticamente armazenados em GridFS.

---

## 3. Listar XMLs Armazenados

```powershell
python client/xmlrpc/client_list.py
```

**Output:**
```
Total: 3 ficheiro(s)

ID: 69238907fb662cc0e919c437
Nome: Sales.xml
Data: 2025-11-23T22:21:59.620000
Tamanho: 75443600 bytes
Armazenamento: GridFS
------------------------------------------------------------
```

---

## 4. Consultas XPath

### Sintaxe
```powershell
python client/xmlrpc/client_query.py <xml_id> "<xpath_expression>"
```

### Exemplos Básicos

```powershell
# Contar total de registos
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "count(//record)"

# Primeira data
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "//record[1]/date/text()"

# Última data
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "//record[last()]/date/text()"
```

### Exemplos com Filtros

```powershell
# Vendas por país (ex: Portugal)
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "count(//record[country='Portugal'])"

# Vendas por categoria de produto
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "count(//record[product_category='Bikes'])"

# Vendas por género
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "count(//record[customer_gender='F'])"

# Filtros combinados
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "count(//record[country='Portugal' and product_category='Bikes'])"
```

### Exemplos com Agregações

```powershell
# Soma total de revenue
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "sum(//record/revenue)"

# Soma total de profit
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "sum(//record/profit)"

# Média de idade dos clientes
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "sum(//record/customer_age) div count(//record)"

# Revenue de vendas femininas
python client/xmlrpc/client_query.py 69238907fb662cc0e919c437 "sum(//record[customer_gender='F']/revenue)"
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
python client/xmlrpc/client_to_json.py <xml_id> [output_file.json]
```

### Exemplos

```powershell
# Mostrar JSON no terminal
python client/xmlrpc/client_to_json.py 69238907fb662cc0e919c437

# Guardar em ficheiro
python client/xmlrpc/client_to_json.py 69238907fb662cc0e919c437 sales_output.json
```

---

## 6. Obter XML Armazenado

### Sintaxe
```powershell
python client/xmlrpc/client_get_xml.py <xml_id> [output_file.xml]
```

### Exemplos

```powershell
# Mostrar preview do XML (primeiros 500 caracteres)
python client/xmlrpc/client_get_xml.py 69238907fb662cc0e919c437

# Guardar XML completo em ficheiro
python client/xmlrpc/client_get_xml.py 69238907fb662cc0e919c437 sales_output.xml
```

**Atenção:** Para ficheiros grandes (>15MB), recomenda-se guardar em ficheiro.

---

## 7. Validar XML

### Sintaxe
```powershell
python client/xmlrpc/client_validate.py <xml_id> <schema.xsd>
```

### Exemplo

```powershell
# Validar contra schema XSD gerado
python client/xmlrpc/client_validate.py 69238907fb662cc0e919c437 Sales.xsd
```