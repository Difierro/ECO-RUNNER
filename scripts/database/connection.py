import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    """
    Gerenciador de conexões com PostgreSQL usando pool de conexões.
    """
    _connection_pool = None
    
    @classmethod
    def initialize_pool(cls):
        """Inicializa o pool de conexões"""
        if cls._connection_pool is None:
            try:
                cls._connection_pool = pool.SimpleConnectionPool(
                    1,
                    10,
                    host=os.getenv('DB_HOST'),
                    port=os.getenv('DB_PORT'),
                    database=os.getenv('DB_NAME'),
                    user=os.getenv('DB_USER'),
                    password=os.getenv('DB_PASSWORD')
                )
                print("Pool de conexões criado com sucesso")
            except psycopg2.Error as e:
                print(f"Erro ao criar pool de conexões: {e}")
                raise
    
    @classmethod
    def get_connection(cls):
        """Retorna uma conexão do pool"""
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, connection):
        """Retorna a conexão ao pool"""
        if cls._connection_pool:
            cls._connection_pool.putconn(connection)
    
    @classmethod
    def close_all_connections(cls):
        """Fecha todas as conexões do pool"""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            print("Pool de conexões fechado")