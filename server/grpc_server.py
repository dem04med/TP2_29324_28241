import grpc
from concurrent import futures
import logging
import time
import os

# Importar classes do projeto
from db_utils import get_db_connection
from xml_converter import XMLConverter

# Importar código gerado do protobuf (será gerado depois)
import xml_service_pb2 as pb2
import xml_service_pb2_grpc as pb2_grpc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XMLServiceServicer(pb2_grpc.XMLServiceServicer):
    """Implementação do serviço gRPC para operações XML"""
    
    def __init__(self):
        self.xml_converter = XMLConverter()
        self.db = None
        self.init_database()
    
    def init_database(self):
        """Inicializa conexão com MongoDB"""
        max_retries = 10
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.db = get_db_connection()
                if self.db:
                    self.db.create_indexes()
                    logger.info("gRPC: Conexão MongoDB estabelecida")
                    return
                else:
                    logger.warning(f"gRPC: Tentativa {attempt + 1} de conexão falhou")
            except Exception as e:
                logger.error(f"gRPC: Erro na tentativa {attempt + 1}: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Aguardando {retry_delay}s antes da próxima tentativa...")
                time.sleep(retry_delay)
        
        logger.error("gRPC: Não foi possível conectar ao MongoDB")
    
    def Ping(self, request, context):
        """Testa conectividade do servidor"""
        return pb2.XMLResponse(
            success=True,
            filename="",
            xml_content="",
            message="pong"
        )
    
    def StoreXML(self, request, context):
        """Armazena documento XML no MongoDB"""
        try:
            if not self.db:
                return pb2.StoreXMLResponse(
                    success=False,
                    message="Conexão com MongoDB não disponível",
                    xml_id=""
                )
            
            # Validar XML
            is_valid, validation_result = self.xml_converter.validate_xml(request.xml_content)
            if not is_valid:
                return pb2.StoreXMLResponse(
                    success=False,
                    message=f"XML inválido: {validation_result}",
                    xml_id=""
                )
            
            # Inserir no MongoDB
            xml_id = self.db.insert_xml(request.filename, request.xml_content)
            
            logger.info(f"gRPC: XML armazenado com ID {xml_id}")
            return pb2.StoreXMLResponse(
                success=True,
                message="XML armazenado com sucesso",
                xml_id=xml_id
            )
            
        except Exception as e:
            logger.error(f"gRPC: Erro ao armazenar XML: {e}")
            return pb2.StoreXMLResponse(
                success=False,
                message=str(e),
                xml_id=""
            )
    
    def GetXML(self, request, context):
        """Recupera documento XML do MongoDB"""
        try:
            if not self.db:
                return pb2.XMLResponse(
                    success=False,
                    filename="",
                    xml_content="",
                    message="Conexão com MongoDB não disponível"
                )
            
            document = self.db.retrieve_xml(request.xml_id)
            
            if document:
                return pb2.XMLResponse(
                    success=True,
                    filename=document['filename'],
                    xml_content=document['content'],
                    message="XML recuperado com sucesso"
                )
            else:
                return pb2.XMLResponse(
                    success=False,
                    filename="",
                    xml_content="",
                    message=f"XML com ID {request.xml_id} não encontrado"
                )
                
        except Exception as e:
            logger.error(f"gRPC: Erro ao recuperar XML: {e}")
            return pb2.XMLResponse(
                success=False,
                filename="",
                xml_content="",
                message=str(e)
            )
    
    def ListXMLs(self, request, context):
        """Lista todos os XMLs armazenados"""
        try:
            if not self.db:
                return pb2.ListXMLResponse(
                    success=False,
                    files=[],
                    count=0
                )
            
            documents = self.db.list_xml_files()
            
            files = []
            for doc in documents:
                files.append(pb2.XMLFileInfo(
                    xml_id=doc['_id'],
                    filename=doc['filename'],
                    created_at=doc.get('created_at', '')
                ))
            
            return pb2.ListXMLResponse(
                success=True,
                files=files,
                count=len(files)
            )
            
        except Exception as e:
            logger.error(f"gRPC: Erro ao listar XMLs: {e}")
            return pb2.ListXMLResponse(
                success=False,
                files=[],
                count=0
            )
    
    def QueryXPath(self, request, context):
        """Executa consulta XPath sobre XML armazenado"""
        try:
            if not self.db:
                return pb2.XPathResponse(
                    success=False,
                    results=[],
                    message="Conexão com MongoDB não disponível"
                )
            
            # Recuperar XML
            document = self.db.retrieve_xml(request.xml_id)
            if not document:
                return pb2.XPathResponse(
                    success=False,
                    results=[],
                    message=f"XML com ID {request.xml_id} não encontrado"
                )
            
            # Executar XPath
            success, result = self.xml_converter.query_xml_xpath(
                document['content'],
                request.expression
            )
            
            if success:
                # Converter resultado para lista de strings
                results = []
                if isinstance(result, dict) and 'results' in result:
                    for item in result['results']:
                        results.append(str(item))
                
                # Log da consulta
                self.db.log_conversion(request.xml_id, "xpath_query", "success")
                
                return pb2.XPathResponse(
                    success=True,
                    results=results,
                    message="Consulta XPath executada com sucesso"
                )
            else:
                self.db.log_conversion(request.xml_id, "xpath_query", "error", result)
                return pb2.XPathResponse(
                    success=False,
                    results=[],
                    message=f"Erro na consulta XPath: {result}"
                )
                
        except Exception as e:
            logger.error(f"gRPC: Erro na consulta XPath: {e}")
            return pb2.XPathResponse(
                success=False,
                results=[],
                message=str(e)
            )
    
    def ConvertToJSON(self, request, context):
        """Converte XML armazenado para JSON"""
        try:
            if not self.db:
                return pb2.ConvertToJSONResponse(
                    success=False,
                    json_content="",
                    message="Conexão com MongoDB não disponível"
                )
            
            # Recuperar XML
            document = self.db.retrieve_xml(request.xml_id)
            if not document:
                return pb2.ConvertToJSONResponse(
                    success=False,
                    json_content="",
                    message=f"XML com ID {request.xml_id} não encontrado"
                )
            
            # Converter para JSON
            success, result = self.xml_converter.xml_to_json(document['content'])
            
            if success:
                self.db.log_conversion(request.xml_id, "xml_to_json", "success")
                return pb2.ConvertToJSONResponse(
                    success=True,
                    json_content=result,
                    message="Conversão para JSON realizada com sucesso"
                )
            else:
                self.db.log_conversion(request.xml_id, "xml_to_json", "error", result)
                return pb2.ConvertToJSONResponse(
                    success=False,
                    json_content="",
                    message=f"Erro na conversão: {result}"
                )
                
        except Exception as e:
            logger.error(f"gRPC: Erro na conversão para JSON: {e}")
            return pb2.ConvertToJSONResponse(
                success=False,
                json_content="",
                message=str(e)
            )
    
    def ValidateXML(self, request, context):
        """Valida XML contra schema XSD"""
        try:
            if not self.db:
                return pb2.ValidateXMLResponse(
                    success=False,
                    is_valid=False,
                    validation_result="",
                    message="Conexão com MongoDB não disponível"
                )
            
            # Recuperar XML
            document = self.db.retrieve_xml(request.xml_id)
            if not document:
                return pb2.ValidateXMLResponse(
                    success=False,
                    is_valid=False,
                    validation_result="",
                    message=f"XML com ID {request.xml_id} não encontrado"
                )
            
            # Validar XML
            schema_path = request.schema_path if request.schema_path else None
            is_valid, validation_result = self.xml_converter.validate_xml(
                document['content'], 
                schema_path
            )
            
            return pb2.ValidateXMLResponse(
                success=True,
                is_valid=is_valid,
                validation_result=str(validation_result),
                message="Validação realizada com sucesso"
            )
                
        except Exception as e:
            logger.error(f"gRPC: Erro na validação XML: {e}")
            return pb2.ValidateXMLResponse(
                success=False,
                is_valid=False,
                validation_result="",
                message=str(e)
            )
def serve():
    """Inicia o servidor gRPC"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_XMLServiceServicer_to_server(XMLServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    
    logger.info("Servidor gRPC iniciado na porta 50051")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
