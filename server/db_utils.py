from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.mongo_host = os.getenv('MONGO_HOST', 'localhost')
        self.mongo_user = os.getenv('MONGO_USER', 'user')
        self.mongo_pass = os.getenv('MONGO_PASS', 'password')
        self.mongo_db = os.getenv('MONGO_DB', 'xmlrpc_db')
        
        self.client = None
        self.db = None
    
    def connect(self):
        """Estabelece conexão com a base de dados MongoDB"""
        try:
            connection_string = f"mongodb://{self.mongo_user}:{self.mongo_pass}@{self.mongo_host}:27017/"
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Testa a conexão
            self.client.admin.command('ping')
            
            self.db = self.client[self.mongo_db]
            logger.info("Conexão com MongoDB estabelecida com sucesso")
            return True
        except ConnectionFailure as e:
            logger.error(f"Erro ao conectar com MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao conectar: {e}")
            return False
    
    def disconnect(self):
        """Fecha a conexão com a base de dados"""
        if self.client:
            self.client.close()
            logger.info("Conexão com MongoDB fechada")
    
    def get_collection(self, collection_name):
        """Retorna uma coleção do MongoDB"""
        if self.db is None:
            raise Exception("Conexão não estabelecida. Execute connect() primeiro.")
        return self.db[collection_name]
    
    def insert_xml(self, filename, content):
        """Insere documento XML na coleção"""
        try:
            collection = self.get_collection('xml_data')
            document = {
                'filename': filename,
                'content': content,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            result = collection.insert_one(document)
            logger.info(f"Documento XML inserido com ID: {result.inserted_id}")
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Erro ao inserir XML: {e}")
            raise e
    
    def retrieve_xml(self, xml_id):
        """Recupera documento XML pelo ID"""
        try:
            from bson.objectid import ObjectId
            collection = self.get_collection('xml_data')
            document = collection.find_one({'_id': ObjectId(xml_id)})
            
            if document:
                # Converte ObjectId para string para serialização
                document['_id'] = str(document['_id'])
                document['created_at'] = document['created_at'].isoformat() if 'created_at' in document else None
                document['updated_at'] = document['updated_at'].isoformat() if 'updated_at' in document else None
            
            return document
        except Exception as e:
            logger.error(f"Erro ao recuperar XML: {e}")
            raise e
    
    def list_xml_files(self):
        """Lista todos os documentos XML armazenados"""
        try:
            collection = self.get_collection('xml_data')
            documents = list(collection.find({}, {'filename': 1, 'created_at': 1}))
            
            # Converte ObjectId para string
            for doc in documents:
                doc['_id'] = str(doc['_id'])
                if 'created_at' in doc:
                    doc['created_at'] = doc['created_at'].isoformat()
            
            return documents
        except PyMongoError as e:
            logger.error(f"Erro ao listar XMLs: {e}")
            raise e
    
    def update_xml(self, xml_id, content):
        """Atualiza conteúdo de um documento XML"""
        try:
            from bson.objectid import ObjectId
            collection = self.get_collection('xml_data')
            result = collection.update_one(
                {'_id': ObjectId(xml_id)},
                {'$set': {'content': content, 'updated_at': datetime.now()}}
            )
            return result.modified_count
        except Exception as e:
            logger.error(f"Erro ao atualizar XML: {e}")
            raise e
    
    def delete_xml(self, xml_id):
        """Remove documento XML"""
        try:
            from bson.objectid import ObjectId
            collection = self.get_collection('xml_data')
            result = collection.delete_one({'_id': ObjectId(xml_id)})
            return result.deleted_count
        except Exception as e:
            logger.error(f"Erro ao deletar XML: {e}")
            raise e
    
    def log_conversion(self, xml_id, conversion_type, status, error_message=None):
        """Registra log de conversão"""
        try:
            collection = self.get_collection('conversion_log')
            log_entry = {
                'xml_id': xml_id,
                'conversion_type': conversion_type,
                'status': status,
                'error_message': error_message,
                'created_at': datetime.now()
            }
            result = collection.insert_one(log_entry)
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Erro ao registrar log: {e}")
            raise e
    
    def create_indexes(self):
        """Cria índices para melhor performance"""
        try:
            xml_collection = self.get_collection('xml_data')
            xml_collection.create_index('filename')
            xml_collection.create_index('created_at')
            
            log_collection = self.get_collection('conversion_log')
            log_collection.create_index('xml_id')
            log_collection.create_index('conversion_type')
            
            logger.info("Índices criados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar índices: {e}")
            raise e

def get_db_connection():
    """Função utilitária para obter uma conexão com a base de dados"""
    db = DatabaseConnection()
    if db.connect():
        return db
    return None