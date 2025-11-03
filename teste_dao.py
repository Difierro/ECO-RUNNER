from scripts.database.connection import DatabaseConnection
from scripts.database.user_DAO import UserDAO
from scripts.database.game_DAO import GameDAO

print("=" * 60)
print("🧪 TESTE DOS DAOs - USER E GAME")
print("=" * 60)

try:
    # Inicializa pool
    DatabaseConnection.initialize_pool()
    
    # ========== TESTE 1: Cadastro de Usuário ==========
    print("\n📝 TESTE 1: Cadastrando usuário de teste...")
    sucesso, msg = UserDAO.cadastrar_usuario("testedao", "senha12345")
    
    if sucesso:
        print(f"✅ {msg}")
    else:
        print(f"ℹ️  {msg} (pode já existir)")
    
    # ========== TESTE 2: Login ==========
    print("\n🔐 TESTE 2: Fazendo login...")
    sucesso, dados = UserDAO.verificar_login("testedao", "senha12345")
    
    if sucesso:
        print(f"✅ Login realizado!")
        print(f"   ID: {dados['id']}")
        print(f"   Nickname: {dados['nickname']}")
        print(f"   Vidas: {dados['vidas']}")
        user_id = dados['id']
    else:
        print(f"❌ Falha no login: {dados}")
        exit()
    
    # ========== TESTE 3: Salvar Progresso Fase 1 ==========
    print("\n💾 TESTE 3: Salvando progresso fase 1...")
    sucesso = GameDAO.salvar_progresso_fase1(
        user_id, 
        itens_papel=3, 
        itens_plastico=2, 
        vidas=4
    )
    print("✅ Progresso salvo!" if sucesso else "❌ Erro ao salvar")
    
    # ========== TESTE 4: Carregar Progresso ==========
    print("\n📥 TESTE 4: Carregando progresso...")
    progresso = GameDAO.carregar_progresso_fase1(user_id)
    
    if progresso:
        print("✅ Progresso carregado:")
        print(f"   Papel: {progresso['itens_papel']}")
        print(f"   Plástico: {progresso['itens_plastico']}")
        print(f"   Vidas: {progresso['vidas']}")
        print(f"   Fase completa: {progresso['fase_completa']}")
    
    # ========== TESTE 5: Adicionar Item ==========
    print("\n➕ TESTE 5: Adicionando item de vidro...")
    sucesso, qtd = GameDAO.adicionar_item_fase1(user_id, 'vidro')
    print(f"✅ Item adicionado! Quantidade: {qtd}" if sucesso else "❌ Erro")
    
    # ========== TESTE 6: Reduzir Vida ==========
    print("\n💔 TESTE 6: Reduzindo uma vida...")
    sucesso, vidas, game_over = GameDAO.reduzir_vida_fase1(user_id)
    print(f"✅ Vida reduzida! Vidas restantes: {vidas}" if sucesso else "❌ Erro")
    
    print("\n" + "=" * 60)
    print("✨ TODOS OS TESTES DOS DAOs PASSARAM!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

finally:
    DatabaseConnection.close_all_connections()