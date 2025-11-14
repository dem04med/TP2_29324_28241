"""
Servidor GraphQL para consultas avançadas sobre dados XML
Complementa o XML-RPC com interface moderna e flexível
"""
import graphene
from graphene import ObjectType, String, Int, List, Field, Argument, Boolean, DateTime, Float
from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS
import json
from datetime import datetime
import logging

from db_utils import get_db_connection
from xml_converter import XMLConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# TIPOS GRAPHQL
# ========================

class XMLFileType(ObjectType):
    """Tipo GraphQL para arquivos XML armazenados"""
    id = Int(required=True, description="ID único do arquivo XML")
    filename = String(required=True, description="Nome do arquivo")
    content = String(description="Conteúdo XML completo")
    created_at = DateTime(description="Data de criação")
    updated_at = DateTime(description="Data de atualização")
    record_count = Int(description="Número de registos no XML")
    file_size = Int(description="Tamanho do arquivo em bytes")

class XMLElementType(ObjectType):
    """Tipo GraphQL para elementos XML individuais"""
    tag = String(required=True, description="Nome do elemento XML")
    text = String(description="Conteúdo de texto do elemento")
    attributes = String(description="Atributos do elemento (JSON)")
    xml_content = String(description="XML completo do elemento")

class XPathResultType(ObjectType):
    """Tipo GraphQL para resultados de consultas XPath"""
    xpath_expression = String(required=True, description="Expressão XPath executada")
    result_count = Int(required=True, description="Número de resultados encontrados")
    elements = List(XMLElementType, description="Elementos encontrados")
    execution_time = Float(description="Tempo de execução em segundos")

class ValidationResultType(ObjectType):
    """Tipo GraphQL para resultados de validação"""
    is_valid = Boolean(required=True, description="Se o XML é válido")
    errors = List(String, description="Lista de erros de validação")
    warnings = List(String, description="Lista de avisos")
    schema_used = String(description="Schema XSD utilizado")

class ConversionResultType(ObjectType):
    """Tipo GraphQL para resultados de conversões"""
    success = Boolean(required=True, description="Se a conversão foi bem-sucedida")
    result_content = String(description="Conteúdo resultante da conversão")
    format_from = String(description="Formato de origem")
    format_to = String(description="Formato de destino")
    record_count = Int(description="Número de registos processados")

class CSVAnalysisType(ObjectType):
    """Tipo GraphQL para análise de CSV"""
    total_columns = Int(description="Total de colunas")
    total_rows = Int(description="Total de linhas")
    column_names = List(String, description="Nomes das colunas")
    column_types = String(description="Tipos de dados das colunas (JSON)")
    sample_data = String(description="Dados de exemplo (JSON)")

class XMLExplorationResultType(ObjectType):
    """Tipo GraphQL para resultado de exploração XML (Desafio 2)"""
    root_tag = String(description="Tag do elemento raiz")
    total_elements = Int(description="Total de elementos no XML")
    total_records = Int(description="Total de registos encontrados")
    record_element = String(description="Elemento identificado como record")
    max_depth = Int(description="Profundidade máxima da árvore XML")
    element_types_count = Int(description="Número de tipos diferentes de elementos")
    attributes_count = Int(description="Número de atributos diferentes encontrados")
    text_statistics = String(description="Estatísticas de texto (JSON)")
    average_text_length = Float(description="Comprimento médio do texto")

class StreamingValidationResultType(ObjectType):
    """Tipo GraphQL para validação streaming (Desafio 2)"""
    valid = Boolean(description="XML é válido")
    message = String(description="Mensagem de resultado")
    method = String(description="Método de validação usado")
    total_errors = Int(description="Total de erros encontrados")
    errors = List(String, description="Lista de erros")

class XMLSubsetResultType(ObjectType):
    """Tipo GraphQL para resultado de subset XML (Desafio 2)"""
    xml_content = String(description="Conteúdo XML do subset")
    original_records = Int(description="Total de registos no XML original")
    filtered_records = Int(description="Total de registos no subset")
    filter_applied = String(description="Filtro XPath aplicado")
    max_records_limit = String(description="Limite máximo de registos aplicado")

# ========================
# QUERIES GRAPHQL
# ========================

class Query(ObjectType):
    """Queries GraphQL principais"""
    
    # Query básica de teste
    hello = String(description="Mensagem de teste")
    server_status = String(description="Status do servidor GraphQL")
    
    # Queries de arquivos XML
    xml_files = List(XMLFileType, description="Lista todos os arquivos XML")
    xml_file = Field(XMLFileType, 
                     xml_id=Argument(Int, required=True),
                     description="Obter arquivo XML por ID")
    
    # Queries de pesquisa e filtragem
    search_xml_files = List(XMLFileType,
                           filename_contains=Argument(String),
                           created_after=Argument(DateTime),
                           created_before=Argument(DateTime),
                           min_records=Argument(Int),
                           max_records=Argument(Int),
                           description="Pesquisar arquivos XML com filtros")
    
    # Queries XPath avançadas
    query_xpath = Field(XPathResultType,
                       xml_id=Argument(Int, required=True),
                       xpath=Argument(String, required=True),
                       description="Executar consulta XPath sobre XML")
    
    # Análise e estatísticas
    xml_statistics = String(xml_id=Argument(Int, required=True),
                           description="Estatísticas detalhadas do XML (JSON)")
    
    # Validação
    validate_xml = Field(ValidationResultType,
                        xml_id=Argument(Int, required=True),
                        schema_name=Argument(String),
                        description="Validar XML contra schema")
    
    # Métodos avançados (Desafio 2)
    validate_xml_streaming = Field(StreamingValidationResultType,
                                   xml_id=Argument(Int, required=True),
                                   xsd_id=Argument(Int),
                                   description="Validação streaming para arquivos grandes (Desafio 2)")
    
    explore_xml_structure = Field(XMLExplorationResultType,
                                  xml_id=Argument(Int, required=True),
                                  description="Exploração avançada de estrutura XML (Desafio 2)")
    
    generate_xml_subset = Field(XMLSubsetResultType,
                               xml_id=Argument(Int, required=True),
                               filter_xpath=Argument(String),
                               max_records=Argument(Int),
                               description="Gerar subset de XML com filtros (Desafio 2)")

    # ========================
    # RESOLVERS
    # ========================
    
    def resolve_hello(self, info):
        return "GraphQL Server para XML Processing está ativo! 🚀"
    
    def resolve_server_status(self, info):
        status = {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "graphql_version": "1.0",
            "endpoints_available": ["xml_files", "query_xpath", "search_xml_files", "validate_xml"]
        }
        return json.dumps(status, indent=2)
    
    def resolve_xml_files(self, info):
        """Lista todos os arquivos XML"""
        try:
            db = get_db_connection()
            if not db:
                return []
            
            query = """
                SELECT id, filename, content, created_at, updated_at,
                       length(content) as file_size
                FROM xml_data 
                ORDER BY created_at DESC
            """
            results = db.execute_query(query)
            
            xml_files = []
            for row in results:
                # Contar registos no XML
                record_count = 0
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(row['content'])
                    # Tentar diferentes padrões de elementos
                    record_count = len(root.findall('.//record')) or len(root.findall('.//employee')) or len(list(root))
                except:
                    record_count = 0
                
                xml_files.append(XMLFileType(
                    id=row['id'],
                    filename=row['filename'],
                    content=row['content'][:1000] + "..." if len(row['content']) > 1000 else row['content'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    file_size=row['file_size'],
                    record_count=record_count
                ))
            
            return xml_files
            
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos XML: {e}")
            return []
    
    def resolve_xml_file(self, info, xml_id):
        """Obter arquivo XML específico"""
        try:
            db = get_db_connection()
            if not db:
                return None
            
            query = "SELECT * FROM xml_data WHERE id = %s"
            results = db.execute_query(query, (xml_id,))
            
            if not results:
                return None
            
            row = results[0]
            
            # Contar registos
            record_count = 0
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(row['content'])
                record_count = len(root.findall('.//record')) or len(root.findall('.//employee')) or len(list(root))
            except:
                record_count = 0
            
            return XMLFileType(
                id=row['id'],
                filename=row['filename'],
                content=row['content'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                file_size=len(row['content']),
                record_count=record_count
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar arquivo XML {xml_id}: {e}")
            return None
    
    def resolve_search_xml_files(self, info, filename_contains=None, created_after=None, 
                                created_before=None, min_records=None, max_records=None):
        """Pesquisa avançada de arquivos XML"""
        try:
            db = get_db_connection()
            if not db:
                return []
            
            # Construir query dinâmica
            conditions = []
            params = []
            
            if filename_contains:
                conditions.append("filename ILIKE %s")
                params.append(f"%{filename_contains}%")
            
            if created_after:
                conditions.append("created_at >= %s")
                params.append(created_after)
            
            if created_before:
                conditions.append("created_at <= %s")
                params.append(created_before)
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            query = f"""
                SELECT id, filename, content, created_at, updated_at,
                       length(content) as file_size
                FROM xml_data 
                {where_clause}
                ORDER BY created_at DESC
            """
            
            results = db.execute_query(query, params)
            
            xml_files = []
            for row in results:
                # Contar registos e aplicar filtros de contagem
                record_count = 0
                try:
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(row['content'])
                    record_count = len(root.findall('.//record')) or len(root.findall('.//employee')) or len(list(root))
                except:
                    record_count = 0
                
                # Aplicar filtros de contagem de registos
                if min_records is not None and record_count < min_records:
                    continue
                if max_records is not None and record_count > max_records:
                    continue
                
                xml_files.append(XMLFileType(
                    id=row['id'],
                    filename=row['filename'],
                    content=row['content'][:500] + "..." if len(row['content']) > 500 else row['content'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    file_size=row['file_size'],
                    record_count=record_count
                ))
            
            return xml_files
            
        except Exception as e:
            logger.error(f"Erro na pesquisa XML: {e}")
            return []
    
    def resolve_query_xpath(self, info, xml_id, xpath):
        """Executar consulta XPath"""
        try:
            start_time = datetime.now()
            
            db = get_db_connection()
            if not db:
                return None
            
            # Obter XML
            query = "SELECT content FROM xml_data WHERE id = %s"
            results = db.execute_query(query, (xml_id,))
            
            if not results:
                return None
            
            xml_content = results[0]['content']
            
            # Executar XPath usando xml_converter
            converter = XMLConverter()
            success, result = converter.query_xml_xpath(xml_content, xpath)
            
            if not success:
                return XPathResultType(
                    xpath_expression=xpath,
                    result_count=0,
                    elements=[],
                    execution_time=0
                )
            
            # Converter resultados para GraphQL types
            elements = []
            for item in result['results']:
                if isinstance(item, dict) and 'tag' in item:
                    elements.append(XMLElementType(
                        tag=item['tag'],
                        text=item.get('text', ''),
                        attributes=json.dumps(item.get('attributes', {})),
                        xml_content=item.get('xml', '')
                    ))
                else:
                    # Resultado simples (texto)
                    elements.append(XMLElementType(
                        tag="text_result",
                        text=str(item),
                        attributes="{}",
                        xml_content=str(item)
                    ))
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return XPathResultType(
                xpath_expression=xpath,
                result_count=len(elements),
                elements=elements,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Erro na consulta XPath: {e}")
            return None
    
    def resolve_xml_statistics(self, info, xml_id):
        """Gerar estatísticas detalhadas do XML"""
        try:
            db = get_db_connection()
            if not db:
                return "{}"
            
            query = "SELECT filename, content, created_at FROM xml_data WHERE id = %s"
            results = db.execute_query(query, (xml_id,))
            
            if not results:
                return "{}"
            
            row = results[0]
            xml_content = row['content']
            
            # Análise detalhada
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            stats = {
                "file_info": {
                    "filename": row['filename'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "file_size_bytes": len(xml_content),
                    "file_size_mb": round(len(xml_content) / (1024 * 1024), 2)
                },
                "xml_structure": {
                    "root_element": root.tag,
                    "total_elements": len(list(root.iter())),
                    "max_depth": self._get_xml_depth(root),
                    "unique_tags": len(set(elem.tag for elem in root.iter()))
                },
                "data_analysis": {
                    "record_elements": len(root.findall('.//record')),
                    "text_elements": len([elem for elem in root.iter() if elem.text and elem.text.strip()]),
                    "elements_with_attributes": len([elem for elem in root.iter() if elem.attrib])
                }
            }
            
            return json.dumps(stats, indent=2)
            
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {e}")
            return "{}"
    
    def resolve_validate_xml(self, info, xml_id, schema_name=None):
        """Validar XML contra schema"""
        try:
            db = get_db_connection()
            if not db:
                return None
            
            query = "SELECT content FROM xml_data WHERE id = %s"
            results = db.execute_query(query, (xml_id,))
            
            if not results:
                return None
            
            xml_content = results[0]['content']
            
            # Usar xml_converter para validação
            converter = XMLConverter()
            schema_path = None  # Por agora sem schema específico
            
            is_valid, validation_result = converter.validate_xml(xml_content, schema_path)
            
            if isinstance(validation_result, list):
                errors = validation_result
                warnings = []
            else:
                errors = [] if is_valid else [str(validation_result)]
                warnings = []
            
            return ValidationResultType(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                schema_used=schema_name or "Built-in XML validation"
            )
            
        except Exception as e:
            logger.error(f"Erro na validação XML: {e}")
            return None
    
    def _get_xml_depth(self, element, depth=0):
        """Calcula profundidade máxima do XML"""
        if not list(element):
            return depth
        return max(self._get_xml_depth(child, depth + 1) for child in element)
    
    def resolve_validate_xml_streaming(self, info, xml_id, xsd_id=None):
        """Validação streaming (Desafio 2)"""
        try:
            db = get_db_connection()
            if not db:
                return None
            
            # Buscar XML
            query = "SELECT content FROM xml_data WHERE id = %s"
            results = db.execute_query(query, (xml_id,))
            if not results:
                return None
            
            xml_content = results[0]['content']
            
            # Buscar XSD se fornecido
            xsd_content = None
            if xsd_id:
                xsd_results = db.execute_query(query, (xsd_id,))
                if xsd_results:
                    xsd_content = xsd_results[0]['content']
            
            # Executar validação streaming
            converter = XMLConverter()
            success, result = converter.validate_xml_streaming(xml_content, xsd_content)
            
            if success:
                return StreamingValidationResultType(
                    valid=result.get('valid', False),
                    message=result.get('message', ''),
                    method=result.get('method', 'streaming'),
                    total_errors=result.get('total_errors', 0),
                    errors=result.get('errors', [])
                )
            else:
                return StreamingValidationResultType(
                    valid=False,
                    message=str(result),
                    method='streaming_error',
                    total_errors=1,
                    errors=[str(result)]
                )
                
        except Exception as e:
            logger.error(f"Erro na validação streaming: {e}")
            return None
    
    def resolve_explore_xml_structure(self, info, xml_id):
        """Exploração XML (Desafio 2)"""
        try:
            db = get_db_connection()
            if not db:
                return None
            
            query = "SELECT content FROM xml_data WHERE id = %s"
            results = db.execute_query(query, (xml_id,))
            if not results:
                return None
            
            xml_content = results[0]['content']
            
            # Executar exploração
            converter = XMLConverter()
            success, result = converter.explore_xml(xml_content)
            
            if success:
                import json
                return XMLExplorationResultType(
                    root_tag=result.get('root_tag', ''),
                    total_elements=result.get('total_elements', 0),
                    total_records=result.get('total_records', 0),
                    record_element=result.get('record_element', ''),
                    max_depth=result.get('max_depth', 0),
                    element_types_count=result.get('element_types_count', 0),
                    attributes_count=result.get('attributes_count', 0),
                    text_statistics=json.dumps(result.get('text_statistics', {})),
                    average_text_length=result.get('average_text_length', 0.0)
                )
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro na exploração XML: {e}")
            return None
    
    def resolve_generate_xml_subset(self, info, xml_id, filter_xpath=None, max_records=None):
        """Gerar subset XML (Desafio 2)"""
        try:
            db = get_db_connection()
            if not db:
                return None
            
            query = "SELECT content FROM xml_data WHERE id = %s"
            results = db.execute_query(query, (xml_id,))
            if not results:
                return None
            
            xml_content = results[0]['content']
            
            # Executar geração de subset
            converter = XMLConverter()
            success, result = converter.generate_xml_subset(xml_content, filter_xpath, max_records)
            
            if success:
                return XMLSubsetResultType(
                    xml_content=result.get('xml_content', ''),
                    original_records=result.get('original_records', 0),
                    filtered_records=result.get('filtered_records', 0),
                    filter_applied=result.get('filter_applied', 'none'),
                    max_records_limit=str(result.get('max_records_limit', 'none'))
                )
            else:
                return None
                
        except Exception as e:
            logger.error(f"Erro ao gerar subset XML: {e}")
            return None

# ========================
# MUTATIONS GRAPHQL
# ========================

class XMLMutation(graphene.Mutation):
    """Mutation para armazenar XML"""
    
    class Arguments:
        filename = String(required=True)
        xml_content = String(required=True)
    
    success = Boolean()
    message = String()
    xml_id = Int()
    
    def mutate(self, info, filename, xml_content):
        try:
            # Usar XML-RPC server handler para consistência
            from xmlrpc_server import XMLRPCServerHandler
            handler = XMLRPCServerHandler()
            result = handler.store_xml(filename, xml_content)
            
            return XMLMutation(
                success=result["success"],
                message=result.get("message", ""),
                xml_id=result.get("xml_id")
            )
        except Exception as e:
            return XMLMutation(
                success=False,
                message=f"Erro: {str(e)}",
                xml_id=None
            )

class CSVToXMLMutation(graphene.Mutation):
    """Mutation para converter CSV para XML"""
    
    class Arguments:
        csv_content = String(required=True)
        filename = String(required=True)
        root_element = String(default_value="dataset")
        row_element = String(default_value="record")
    
    success = Boolean()
    xml_content = String()
    message = String()
    xml_id = Int()
    
    def mutate(self, info, csv_content, filename, root_element="dataset", row_element="record"):
        try:
            # Converter CSV para XML
            from xmlrpc_server import XMLRPCServerHandler
            handler = XMLRPCServerHandler()
            
            # Converter
            convert_result = handler.convert_csv_to_xml(csv_content, root_element, row_element)
            
            if not convert_result["success"]:
                return CSVToXMLMutation(
                    success=False,
                    message=convert_result.get("error", "Erro na conversão"),
                    xml_content="",
                    xml_id=None
                )
            
            xml_content = convert_result["xml_content"]
            
            # Armazenar XML gerado
            store_result = handler.store_xml(filename, xml_content)
            
            return CSVToXMLMutation(
                success=True,
                xml_content=xml_content,
                message="CSV convertido e armazenado com sucesso",
                xml_id=store_result.get("xml_id")
            )
            
        except Exception as e:
            return CSVToXMLMutation(
                success=False,
                message=f"Erro: {str(e)}",
                xml_content="",
                xml_id=None
            )

class Mutation(ObjectType):
    """Mutations GraphQL principais"""
    store_xml = XMLMutation.Field()
    convert_csv_to_xml = CSVToXMLMutation.Field()

# ========================
# SERVIDOR GRAPHQL
# ========================

def create_graphql_app():
    """Cria aplicação Flask com GraphQL"""
    app = Flask(__name__)
    CORS(app)  # Permite CORS para desenvolvimento
    
    # Schema GraphQL
    schema = graphene.Schema(query=Query, mutation=Mutation)
    
    # Endpoint GraphQL
    app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql',
            schema=schema,
            graphiql=True  # Interface GraphiQL para desenvolvimento
        )
    )
    
    # Endpoint de saúde
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "GraphQL XML Server"}
    
    # Endpoint de informação do schema
    @app.route('/schema')
    def schema_info():
        return {
            "schema_version": "2.0 - Desafio 2 Complete",
            "types": [
                "XMLFileType", "XPathResultType", "ValidationResultType",
                "XMLExplorationResultType", "StreamingValidationResultType", "XMLSubsetResultType"
            ],
            "queries": [
                "xml_files", "xml_file", "search_xml_files", "query_xpath", "validate_xml",
                "validate_xml_streaming", "explore_xml_structure", "generate_xml_subset"
            ],
            "mutations": ["store_xml", "convert_csv_to_xml"],
            "graphiql_url": "/graphql",
            "advanced_features": [
                "Streaming validation for large files (>50MB)",
                "Deep XML structure exploration",
                "XML subset generation with XPath filters"
            ]
        }
    
    return app

if __name__ == "__main__":
    app = create_graphql_app()
    logger.info("Servidor GraphQL iniciado em http://localhost:5000/graphql")
    logger.info("Interface GraphiQL disponível em: http://localhost:5000/graphql")
    app.run(host="0.0.0.0", port=5000, debug=True)