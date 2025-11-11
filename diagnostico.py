import os
import sys

print("=" * 60)
print("DIAGNÓSTICO DE ESTRUTURA DO PROJETO ECO-RUNNER")
print("=" * 60)

# Diretório raiz do projeto
raiz = os.path.abspath('.')
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

print("\nVerificando arquivos críticos:\n")

todos_ok = True
for nome, caminho in arquivos_criticos.items():
    existe = os.path.exists(caminho)
    status = "OK - " if existe else "X - "
    print(f"{status} {nome:25} → {caminho}")
    if not existe:
        todos_ok = False

print("\n" + "=" * 60)

# Verificar .env
print("\n" + "=" * 60)
print("\n Verificando credenciais (.env):\n")

if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        db_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        for var in db_vars:
            valor = os.getenv(var)
            if valor:
                if var == 'DB_PASSWORD' and valor:
                    valor = '*' * len(valor)
                print(f"OK- {var:15} = {valor}")
            else:
                print(f"X  {var:15} = (não definido)")
                todos_ok = False
    except ImportError:
        print("X python-dotenv não instalado")
        print("     Execute: pip install python-dotenv")
        todos_ok = False
else:
    print("X Arquivo .env não encontrado na raiz")
    print("   Crie o arquivo .env com as credenciais do banco")
    todos_ok = False

# Resultado final
print("\n" + "=" * 60)
if todos_ok:
    print("\nESTRUTURA OK! Projeto pronto para executar.")
    print("\nPróximos passos:")
    print("   1. python test_connection.py  (testar conexão)")
    print("   2. python main.py     (executar sistema)")
else:
    print("\nPROBLEMAS ENCONTRADOS!")
    print("Corrija os itens marcados com X acima")
print("=" * 60)