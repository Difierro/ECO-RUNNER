from scripts.database.connection import DatabaseConnection
from scripts.database.user_DAO import UserDAO

print("=" * 50)
print("🔧 TESTE DE CONEXÃO COM POSTGRESQL")
print("=" * 50)

try:
    # Testa inicialização do pool
    print("\n1️⃣ Inicializando pool de conexões...")
    DatabaseConnection.initialize_pool()
    print("✅ Pool inicializado com sucesso!")
    
    # Testa obtenção de conexão
    print("\n2️⃣ Obtendo conexão do pool...")
    conn = DatabaseConnection.get_connection()
    print("✅ Conexão obtida com sucesso!")
    
    # Testa query simples
    print("\n3️⃣ Testando query no banco...")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]
    print(f"✅ Query executada! Total de usuários: {total_usuarios}")
    
    # Retorna conexão
    DatabaseConnection.return_connection(conn)
    print("\n4️⃣ Conexão retornada ao pool")
    
    print("\n" + "=" * 50)
    print("✨ TODOS OS TESTES PASSARAM!")
    print("=" * 50)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print("\nVerifique:")
    print("  1. PostgreSQL está rodando?")
    print("  2. Arquivo .env está configurado?")
    print("  3. Banco 'eco_runner' foi criado?")
    print("  4. Credenciais estão corretas?")

finally:
    DatabaseConnection.close_all_connections()
