import os
import sys

print("=" * 60)
print("🔍 DIAGNÓSTICO DE ESTRUTURA DO PROJETO ECO-RUNNER")
print("=" * 60)

# Diretório raiz do projeto
raiz = "/Users/alexandre/Documents/GitHub/ECO-RUNNER"
os.chdir(raiz)

# Arquivos críticos para verificar
arquivos_criticos = {
    "Credenciais (.env)": ".env",
    "Auth Principal": "scripts/Auth.py",
    "Conexão DB": "scripts/database/connection.py",
    "User DAO": "scripts/database/user_DAO.py",
    "Game DAO": "scripts/database/game_DAO.py",
    "Scripts __init__": "scripts/__init__.py",
    "Database __init__": "scripts/database/__init__.py",
    "Game Principal": "game.py",
    "Fonte": "assets/fonts/PressStart2P-Regular.ttf",
}

print("\n📋 Verificando arquivos críticos:\n")

todos_ok = True
for nome, caminho in arquivos_criticos.items():
    existe = os.path.exists(caminho)
    status = "✅" if existe else "❌"
    print(f"{status} {nome:25} → {caminho}")
    if not existe:
        todos_ok = False

print("\n" + "=" * 60)

# Verificar imports
print("\n🔧 Testando imports:\n")

try:
    from scripts.database.connection import DatabaseConnection
    print("✅ DatabaseConnection importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar DatabaseConnection: {e}")
    todos_ok = False

try:
    from scripts.database.user_DAO import UserDAO
    print("✅ UserDAO importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar UserDAO: {e}")
    todos_ok = False

try:
    from scripts.database.game_DAO import GameDAO
    print("✅ GameDAO importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar GameDAO: {e}")
    todos_ok = False

# Verificar .env
print("\n" + "=" * 60)
print("\n🔐 Verificando credenciais (.env):\n")

if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        db_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        for var in db_vars:
            valor = os.getenv(var)
            if valor:
                # Ofuscar senha
                if var == 'DB_PASSWORD' and valor:
                    valor = '*' * len(valor)
                print(f"✅ {var:15} = {valor}")
            else:
                print(f"⚠️  {var:15} = (não definido)")
                todos_ok = False
    except ImportError:
        print("❌ python-dotenv não instalado")
        print("   Execute: pip install python-dotenv")
        todos_ok = False
else:
    print("❌ Arquivo .env não encontrado na raiz")
    print("   Crie o arquivo .env com as credenciais do banco")
    todos_ok = False

# Resultado final
print("\n" + "=" * 60)
if todos_ok:
    print("\n✅ ESTRUTURA OK! Projeto pronto para executar.")
    print("\n🚀 Próximos passos:")
    print("   1. python test_connection.py  (testar conexão)")
    print("   2. python scripts/Auth.py     (executar sistema)")
else:
    print("\n⚠️  PROBLEMAS ENCONTRADOS!")
    print("   Corrija os itens marcados com ❌ acima")
print("=" * 60)