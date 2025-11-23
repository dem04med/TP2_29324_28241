from xmlrpc.server import SimpleXMLRPCServer
import logging
import os
from datetime import datetime
import json
import time

from db_utils import get_db_connection, DatabaseConnection
from xml_converter import XMLConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XMLRPCServerHandler:
    def __init__(self):
        self.xml_converter = XMLConverter()
        self.db = None
        self.init_database()
    
    def init_database(self):
        """Inicializa a conexão com a base de dados MongoDB e cria índices"""
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.db = get_db_connection()
                if self.db:
                    self.db.create_indexes()
                    logger.info("Base de dados MongoDB inicializada com sucesso")
                    return
                else:
                    logger.warning(f"Tentativa {attempt + 1} de conexão falhou")
            except Exception as e:
                logger.error(f"Erro na tentativa {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Aguardando {retry_delay} segundos antes da próxima tentativa...")
                time.sleep(retry_delay)
        
        logger.error("Não foi possível estabelecer conexão com a base de dados")
    
    def ping(self):
        """Método para testar se o servidor está ativo"""
        return "pong"
    
    def get_server_status(self):
        """Retorna o status do servidor"""
        db_status = "conectado" if self.db and self.db.client else "desconectado"
        return {
            "status": "ativo",
            "timestamp": datetime.now().isoformat(),
            "database": db_status
        }
    
    def store_xml(self, filename, xml_content):
        """Armazena XML na base de dados"""
        try:
            if not self.db:
                return {"success": False, "error": "Conexão com base de dados não disponível"}
            
            # Validar XML
            is_valid, validation_result = self.xml_converter.validate_xml(xml_content)
            if not is_valid:
                return {
                    "success": False, 
                    "error": f"XML inválido: {validation_result}"
                }
            
            # Inserir na base de dados MongoDB
            xml_id = self.db.insert_xml(filename, xml_content)
            
            if xml_id:
                logger.info(f"XML armazenado com ID: {xml_id}")
                return {
                    "success": True, 
                    "message": f"XML armazenado com sucesso",
                    "xml_id": xml_id
                }
            else:
                return {"success": False, "error": "Erro ao inserir na base de dados"}
                
        except Exception as e:
            logger.error(f"Erro ao armazenar XML: {e}")
            return {"success": False, "error": str(e)}
    
    def retrieve_xml(self, xml_id):
        """Recupera XML da base de dados MongoDB pelo ID"""
        try:
            if not self.db:
                return {"success": False, "error": "Conexão com base de dados não disponível"}
            
            document = self.db.retrieve_xml(xml_id)
            
            if document:
                return {
                    "success": True,
                    "data": document
                }
            else:
                return {"success": False, "error": f"XML com ID {xml_id} não encontrado"}
                
        except Exception as e:
            logger.error(f"Erro ao recuperar XML: {e}")
            return {"success": False, "error": str(e)}
    
    def list_xml_files(self):
        """Lista todos os arquivos XML armazenados no MongoDB"""
        try:
            if not self.db:
                return {"success": False, "error": "Conexão com base de dados não disponível"}
            
            files = self.db.list_xml_files()
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
                
        except Exception as e:
            logger.error(f"Erro ao listar arquivos XML: {e}")
            return {"success": False, "error": str(e)}
    
    def convert_xml_to_json(self, xml_id):
        """Converte XML armazenado para JSON"""
        try:
            # Recuperar XML
            xml_result = self.retrieve_xml(xml_id)
            if not xml_result["success"]:
                return xml_result
            
            xml_content = xml_result["data"]["content"]
            
            # Converter para JSON
            success, result = self.xml_converter.xml_to_json(xml_content)
            
            if success:
                # Log da conversão
                self._log_conversion(xml_id, "xml_to_json", "success")
                
                return {
                    "success": True,
                    "json_content": result,
                    "message": "Conversão para JSON realizada com sucesso"
                }
            else:
                # Log do erro
                self._log_conversion(xml_id, "xml_to_json", "error", result)
                
                return {
                    "success": False,
                    "error": f"Erro na conversão: {result}"
                }
                
        except Exception as e:
            logger.error(f"Erro no processo de conversão XML para JSON: {e}")
            return {"success": False, "error": str(e)}
    
    def convert_json_to_xml(self, json_content, root_element="root"):
        """Converte JSON para XML"""
        try:
            success, result = self.xml_converter.json_to_xml(json_content, root_element)
            
            if success:
                return {
                    "success": True,
                    "xml_content": result,
                    "message": "Conversão para XML realizada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro na conversão: {result}"
                }
                
        except Exception as e:
            logger.error(f"Erro no processo de conversão JSON para XML: {e}")
            return {"success": False, "error": str(e)}
    
    def validate_xml_content(self, xml_content, schema_filename=None):
        """Valida conteúdo XML"""
        try:
            schema_path = None
            if schema_filename:
                schema_path = os.path.join(self.xml_converter.xml_schemas_path, schema_filename)
            
            is_valid, validation_result = self.xml_converter.validate_xml(xml_content, schema_path)
            
            return {
                "success": True,
                "is_valid": is_valid,
                "validation_result": validation_result
            }
                
        except Exception as e:
            logger.error(f"Erro na validação XML: {e}")
            return {"success": False, "error": str(e)}
    
    def convert_csv_to_xml(self, csv_content, root_element="dataset", row_element="record"):
        """Converte dados CSV (estilo Kaggle) para XML"""
        try:
            success, result = self.xml_converter.csv_to_xml(csv_content, root_element, row_element)
            
            if success:
                return {
                    "success": True,
                    "xml_content": result,
                    "message": "Conversão CSV para XML realizada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro na conversão: {result}"
                }
                
        except Exception as e:
            logger.error(f"Erro no processo de conversão CSV para XML: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_xsd_schema(self, xml_content, target_namespace="http://kaggle-data.local"):
        """Gera schema XSD a partir de XML"""
        try:
            success, result = self.xml_converter.generate_xsd_from_xml(xml_content, target_namespace)
            
            if success:
                return {
                    "success": True,
                    "xsd_content": result,
                    "message": "Schema XSD gerado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": f"Erro na geração XSD: {result}"
                }
                
        except Exception as e:
            logger.error(f"Erro no processo de geração XSD: {e}")
            return {"success": False, "error": str(e)}
    
    def query_xml_xpath(self, xml_id, xpath_expression):
        """Executa consulta XPath sobre XML armazenado"""
        try:
            # Recuperar XML
            xml_result = self.retrieve_xml(xml_id)
            if not xml_result["success"]:
                return xml_result
            
            xml_content = xml_result["data"]["content"]
            
            # Executar XPath
            success, result = self.xml_converter.query_xml_xpath(xml_content, xpath_expression)
            
            if success:
                # Log da consulta
                self._log_conversion(xml_id, "xpath_query", "success")
                
                return {
                    "success": True,
                    "query_result": result,
                    "message": "Consulta XPath executada com sucesso"
                }
            else:
                # Log do erro
                self._log_conversion(xml_id, "xpath_query", "error", result)
                
                return {
                    "success": False,
                    "error": f"Erro na consulta XPath: {result}"
                }
                
        except Exception as e:
            logger.error(f"Erro no processo de consulta XPath: {e}")
            return {"success": False, "error": str(e)}
    
    def query_xml_xquery(self, xml_id, xquery_expression):
        """Executa consulta XQuery sobre XML armazenado"""
        try:
            # Recuperar XML
            xml_result = self.retrieve_xml(xml_id)
            if not xml_result["success"]:
                return xml_result
            
            xml_content = xml_result["data"]["content"]
            
            # Executar XQuery
            success, result = self.xml_converter.query_xml_xquery(xml_content, xquery_expression)
            
            if success:
                # Log da consulta
                self._log_conversion(xml_id, "xquery_query", "success")
                
                return {
                    "success": True,
                    "query_result": result,
                    "message": "Consulta XQuery executada com sucesso"
                }
            else:
                # Log do erro
                self._log_conversion(xml_id, "xquery_query", "error", result)
                
                return {
                    "success": False,
                    "error": f"Erro na consulta XQuery: {result}"
                }
                
        except Exception as e:
            logger.error(f"Erro no processo de consulta XQuery: {e}")
            return {"success": False, "error": str(e)}
    
    def _log_conversion(self, xml_data_id, conversion_type, status, error_message=None):
        """Registra log de conversão no MongoDB"""
        try:
            if self.db:
                self.db.log_conversion(xml_data_id, conversion_type, status, error_message)
                
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")

def create_server():
    """Cria e configura o servidor XML-RPC"""
    server_host = "0.0.0.0"
    server_port = 8000
    
    server = SimpleXMLRPCServer((server_host, server_port), allow_none=True)
    server.register_introspection_functions()
    
    # Registrar handler
    handler = XMLRPCServerHandler()
    
    # Registrar métodos
    server.register_function(handler.ping, "ping")
    server.register_function(handler.get_server_status, "get_server_status")
    server.register_function(handler.store_xml, "store_xml")
    server.register_function(handler.retrieve_xml, "retrieve_xml")
    server.register_function(handler.list_xml_files, "list_xml_files")
    server.register_function(handler.convert_xml_to_json, "convert_xml_to_json")
    server.register_function(handler.convert_json_to_xml, "convert_json_to_xml")
    server.register_function(handler.validate_xml_content, "validate_xml_content")
    # Novos métodos do pipeline completo
    server.register_function(handler.convert_csv_to_xml, "convert_csv_to_xml")
    server.register_function(handler.generate_xsd_schema, "generate_xsd_schema")
    server.register_function(handler.query_xml_xpath, "query_xml_xpath")
    server.register_function(handler.query_xml_xquery, "query_xml_xquery")
    
    return server

if __name__ == "__main__":
    logger.info("Iniciando servidor XML-RPC...")
    
    server = create_server()
    
    logger.info("Servidor XML-RPC iniciado em http://0.0.0.0:8000")
    logger.info("Pressione Ctrl+C para parar o servidor")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo utilizador")
    except Exception as e:
        logger.error(f"Erro no servidor: {e}")
    finally:
        logger.info("Servidor XML-RPC parado")