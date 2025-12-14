"""
Configurações globais para os testes do Eco Runner
"""
import pytest
import sys
import os

# Adicionar diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Configuração global executada uma vez antes de todos os testes.
    """
    print("\n" + "="*70)
    print("INICIANDO BATERIA DE TESTES - ECO RUNNER")
    print("="*70)
    print("Suíte de Testes de Autenticação e Integração")
    print("Banco de Dados: PostgreSQL")
    print("Python: 3.14.0")
    print("="*70 + "\n")
    
    yield
    
    print("\n" + "="*70)
    print("BATERIA DE TESTES FINALIZADA")
    print("="*70 + "\n")


@pytest.fixture
def limpar_usuario_teste():
    """
    Fixture para garantir limpeza de usuários de teste após cada teste.
    """
    usuarios_criados = []
    
    def registrar_usuario(user_id):
        """Registra ID de usuário criado para limpeza posterior."""
        usuarios_criados.append(user_id)
    
    yield registrar_usuario
    
    # Cleanup: deletar todos os usuários de teste criados
    if usuarios_criados:
        from scripts.database.connection import DatabaseConnection
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            for user_id in usuarios_criados:
                # Deletar progresso
                cursor.execute("DELETE FROM fase1 WHERE usuario_id = %s", (user_id,))
                cursor.execute("DELETE FROM fase2 WHERE usuario_id = %s", (user_id,))
                cursor.execute("DELETE FROM fase3 WHERE usuario_id = %s", (user_id,))
                # Deletar usuário
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            
            connection.commit()
            cursor.close()
            DatabaseConnection.return_connection(connection)
            print(f"Limpeza: {len(usuarios_criados)} usuário(s) de teste removido(s)")
        except Exception as e:
            print(f"Erro na limpeza: {e}")
