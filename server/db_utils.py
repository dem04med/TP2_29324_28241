import psycopg2
import os
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgres://user:password@localhost:5432/xmlrpc_db')
        self.connection = None
    
    def connect(self):
        """Estabelece conexão com a base de dados PostgreSQL"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            logger.info("Conexão com a base de dados estabelecida com sucesso")
            return True
        except psycopg2.Error as e:
            logger.error(f"Erro ao conectar com a base de dados: {e}")
            return False
    
    def disconnect(self):
        """Fecha a conexão com a base de dados"""
        if self.connection:
            self.connection.close()
            logger.info("Conexão com a base de dados fechada")
    
    def execute_query(self, query, params=None):
        """Executa uma query SQL"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT') or 'RETURNING' in query.upper():
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except psycopg2.Error as e:
            logger.error(f"Erro ao executar query: {e}")
            self.connection.rollback()
            raise e
    
    def create_tables(self):
        """Cria as tabelas necessárias na base de dados"""
        create_xml_data_table = """
        CREATE TABLE IF NOT EXISTS xml_data (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_conversion_log_table = """
        CREATE TABLE IF NOT EXISTS conversion_log (
            id SERIAL PRIMARY KEY,
            xml_data_id INTEGER REFERENCES xml_data(id),
            conversion_type VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            self.execute_query(create_xml_data_table)
            self.execute_query(create_conversion_log_table)
            logger.info("Tabelas criadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise e

def get_db_connection():
    """Função utilitária para obter uma conexão com a base de dados"""
    db = DatabaseConnection()
    if db.connect():
        return db
    return None