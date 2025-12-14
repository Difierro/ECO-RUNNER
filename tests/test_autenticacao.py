"""
Testes de Autenticação - Eco Runner
Caso de Teste: CT-RF01-01 - Login com credenciais válidas
"""
import pytest
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.database.user_DAO import UserDAO
from scripts.database.game_DAO import GameDAO
from scripts.database.connection import DatabaseConnection


class TestLoginCredenciaisValidas:
    """
    CT-RF01-01: Login com credenciais válidas
    
    Requisito: RF01 - Autenticação de usuário
    Objetivo: Validar autenticação, carregamento de progresso e início do jogo
    
    Pré-condições:
    - Banco de dados PostgreSQL configurado
    - Usuário cadastrado com progresso salvo
    
    Resultado Esperado:
    - Login bem-sucedido
    - Progresso carregado corretamente
    - Dados do jogo inicializados
    """
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """
        Setup: Criar usuário de teste com progresso
        Teardown: Limpar dados de teste do banco
        """
        # ==================== SETUP ====================
        self.usuario_teste = {
            'nickname': 'ct_rf01_01',
            'senha': 'senha_teste_123'
        }
        
        # Cadastrar usuário de teste
        print(f"\nSetup: Criando usuário de teste '{self.usuario_teste['nickname']}'...")
        sucesso, mensagem = UserDAO.cadastrar_usuario(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        if not sucesso:
            pytest.skip(f"Não foi possível criar usuário de teste: {mensagem}")
        
        # Buscar ID do usuário criado
        sucesso_login, resultado_login = UserDAO.verificar_login(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        if not sucesso_login:
            pytest.skip("Não foi possível obter ID do usuário criado")
            
        self.user_id = resultado_login['id']
        print(f"Usuário criado com ID: {self.user_id}")
        
        # Salvar progresso inicial
        print("Salvando progresso inicial...")
        GameDAO.salvar_progresso_fase1(
            self.user_id,
            itens_papel=2,
            itens_plastico=1,
            itens_vidro=0,
            itens_metal=1,
            vidas=3,
            fase_completa=False
        )
        print("Progresso salvo: Vidas=3, Papel=2, Plástico=1, Metal=1\n")
        
        yield  # Executa o teste
        
        # ==================== TEARDOWN ====================
        print("\nTeardown: Limpando dados de teste...")
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Deletar progresso
            cursor.execute("DELETE FROM fase1 WHERE usuario_id = %s", (self.user_id,))
            cursor.execute("DELETE FROM fase2 WHERE usuario_id = %s", (self.user_id,))
            cursor.execute("DELETE FROM fase3 WHERE usuario_id = %s", (self.user_id,))
            # Deletar usuário
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (self.user_id,))
            
            connection.commit()
            cursor.close()
            DatabaseConnection.return_connection(connection)
            print("Dados de teste removidos do banco\n")
        except Exception as e:
            print(f"Erro ao limpar dados: {e}\n")
    
    def test_ct_rf01_01_login_com_credenciais_validas(self):
        """
        CT-RF01-01: Login com credenciais válidas
        
        Passos do Teste:
        1. Autenticar usuário com credenciais válidas
        2. Verificar se login foi bem-sucedido
        3. Carregar progresso do banco de dados
        4. Validar dados do progresso
        5. Simular inicialização do jogo
        
        Critérios de Aceitação:
        - Login retorna dados do usuário
        - Progresso carregado contém todos os campos
        - Valores correspondem ao esperado
        - Sistema está pronto para iniciar o jogo
        """
        print("\n" + "="*70)
        print("EXECUTANDO CT-RF01-01: Login com Credenciais Válidas")
        print("="*70 + "\n")
        
        # ==================== PASSO 1: AUTENTICAÇÃO ====================
        print("PASSO 1: Autenticar usuário")
        print(f"   Login: {self.usuario_teste['nickname']}")
        print(f"   Senha: {'*' * len(self.usuario_teste['senha'])}")
        
        sucesso, resultado_login = UserDAO.verificar_login(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        # ==================== VALIDAÇÃO 1: LOGIN BEM-SUCEDIDO ====================
        assert sucesso is True, \
            "FALHOU: Login não retornou sucesso"
        
        assert resultado_login is not None, \
            "FALHOU: Login retornou None (esperava dados do usuário)"
        
        assert 'id' in resultado_login, \
            "FALHOU: ID do usuário não retornado"
        
        assert 'nickname' in resultado_login, \
            "FALHOU: Nickname não retornado"
        
        assert resultado_login['nickname'] == self.usuario_teste['nickname'], \
            f"FALHOU: Nickname incorreto (esperado: {self.usuario_teste['nickname']}, obtido: {resultado_login['nickname']})"
        
        print(f"PASSOU: Login bem-sucedido")
        print(f"   ID do Usuário: {resultado_login['id']}")
        print(f"   Nickname: {resultado_login['nickname']}\n")
        
        # ==================== PASSO 2: CARREGAR PROGRESSO ====================
        print("PASSO 2: Carregar progresso do banco de dados")
        
        progresso = GameDAO.carregar_progresso_fase1(resultado_login['id'])
        
        # ==================== VALIDAÇÃO 2: PROGRESSO CARREGADO ====================
        assert progresso is not None, \
            "FALHOU: Progresso não foi carregado (retornou None)"
        
        assert isinstance(progresso, dict), \
            f"FALHOU: Progresso não é dicionário (tipo: {type(progresso)})"
        
        print("PASSOU: Progresso carregado com sucesso\n")
        
        # ==================== PASSO 3: VALIDAR ESTRUTURA DO PROGRESSO ====================
        print("PASSO 3: Validar estrutura dos dados do progresso")
        
        campos_obrigatorios = [
            'vidas', 'itens_papel', 'itens_plastico', 
            'itens_vidro', 'itens_metal', 'fase_completa'
        ]
        
        for campo in campos_obrigatorios:
            assert campo in progresso, \
                f"FALHOU: Campo '{campo}' ausente no progresso"
        
        print("PASSOU: Todos os campos obrigatórios presentes\n")
        
        # ==================== PASSO 4: VALIDAR VALORES DO PROGRESSO ====================
        print("PASSO 4: Validar valores do progresso")
        
        # Vidas
        assert progresso['vidas'] == 3, \
            f"FALHOU: Vidas incorretas (esperado: 3, obtido: {progresso['vidas']})"
        print(f"   Vidas: {progresso['vidas']} (correto)")
        
        # Papel
        assert progresso['itens_papel'] == 2, \
            f"FALHOU: Itens papel incorretos (esperado: 2, obtido: {progresso['itens_papel']})"
        print(f"   Papel: {progresso['itens_papel']}/5 (correto)")
        
        # Plástico
        assert progresso['itens_plastico'] == 1, \
            f"FALHOU: Itens plástico incorretos (esperado: 1, obtido: {progresso['itens_plastico']})"
        print(f"   Plástico: {progresso['itens_plastico']}/5 (correto)")
        
        # Vidro
        assert progresso['itens_vidro'] == 0, \
            f"FALHOU: Itens vidro incorretos (esperado: 0, obtido: {progresso['itens_vidro']})"
        print(f"   Vidro: {progresso['itens_vidro']}/5 (correto)")
        
        # Metal
        assert progresso['itens_metal'] == 1, \
            f"FALHOU: Itens metal incorretos (esperado: 1, obtido: {progresso['itens_metal']})"
        print(f"   Metal: {progresso['itens_metal']}/5 (correto)")
        
        # Fase completa
        assert progresso['fase_completa'] is False, \
            "FALHOU: Fase não deveria estar marcada como completa"
        print(f"   Fase completa: {progresso['fase_completa']} (correto)\n")
        
        # ==================== PASSO 5: VALIDAR ESTADO DO JOGO ====================
        print("PASSO 5: Validar estado do jogo para inicialização")
        
        # Verificar se usuário pode jogar (tem vidas)
        assert progresso['vidas'] > 0, \
            "FALHOU: Usuário sem vidas (não pode iniciar o jogo)"
        print(f"   Usuário pode jogar (vidas > 0)")
        
        # Calcular total de itens coletados
        total_itens = (
            progresso['itens_papel'] +
            progresso['itens_plastico'] +
            progresso['itens_vidro'] +
            progresso['itens_metal']
        )
        
        assert total_itens >= 0 and total_itens <= 20, \
            f"FALHOU: Total de itens fora do intervalo válido (0-20): {total_itens}"
        print(f"   Total de itens: {total_itens}/20 (válido)")
        
        # Verificar limites individuais
        assert progresso['itens_papel'] <= 5, "FALHOU: Papel excede limite (5)"
        assert progresso['itens_plastico'] <= 5, "FALHOU: Plástico excede limite (5)"
        assert progresso['itens_vidro'] <= 5, "FALHOU: Vidro excede limite (5)"
        assert progresso['itens_metal'] <= 5, "FALHOU: Metal excede limite (5)"
        print(f"   Todos os itens dentro dos limites (max 5/tipo)\n")
        
        # ==================== RESULTADO FINAL ====================
        print("="*70)
        print("RESUMO DO ESTADO DO JOGO")
        print("="*70)
        print(f"Usuário: {resultado_login['nickname']} (ID: {resultado_login['id']})")
        print(f"Vidas: {progresso['vidas']}/5")
        print(f"Itens Coletados: {total_itens}/20")
        print(f"   Papel: {progresso['itens_papel']}/5")
        print(f"   Plástico: {progresso['itens_plastico']}/5")
        print(f"   Vidro: {progresso['itens_vidro']}/5")
        print(f"   Metal: {progresso['itens_metal']}/5")
        print(f"Fase Completa: {progresso['fase_completa']}")
        print("="*70)
        print("TESTE CT-RF01-01 PASSOU COM SUCESSO!")
        print("="*70 + "\n")


class TestCasosErroAutenticacao:
    """
    Testes adicionais de autenticação para validar casos de erro
    """
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Criar usuário válido para testes de erro."""
        self.usuario_valido = {
            'nickname': 'user_valido',
            'senha': 'senha_correta_123'
        }
        
        sucesso, mensagem = UserDAO.cadastrar_usuario(
            self.usuario_valido['nickname'],
            self.usuario_valido['senha']
        )
        
        if sucesso:
            resultado = UserDAO.verificar_login(
                self.usuario_valido['nickname'],
                self.usuario_valido['senha']
            )
            if resultado[0]:
                self.user_id = resultado[1]['id']
            else:
                pytest.skip("Não foi possível obter ID do usuário")
        else:
            pytest.skip("Não foi possível criar usuário para testes")
        
        yield
        
        # Cleanup
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM fase1 WHERE usuario_id = %s", (self.user_id,))
            cursor.execute("DELETE FROM fase2 WHERE usuario_id = %s", (self.user_id,))
            cursor.execute("DELETE FROM fase3 WHERE usuario_id = %s", (self.user_id,))
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (self.user_id,))
            connection.commit()
            cursor.close()
            DatabaseConnection.return_connection(connection)
        except Exception as e:
            print(f"Erro ao limpar: {e}")
    
    def test_login_senha_incorreta(self):
        """
        Teste: Login com senha incorreta deve falhar
        """
        print("\nTestando: Login com senha incorreta")
        
        sucesso, resultado = UserDAO.verificar_login(
            self.usuario_valido['nickname'],
            'senha_errada_123'
        )
        
        assert sucesso is False, \
            "FALHOU: Login deveria retornar False com senha incorreta"
        
        print("PASSOU: Senha incorreta rejeitada corretamente\n")
    
    def test_login_usuario_inexistente(self):
        """
        Teste: Login com usuário inexistente deve falhar
        """
        print("\nTestando: Login com usuário inexistente")
        
        sucesso, resultado = UserDAO.verificar_login(
            'usuario_que_nao_existe_xyz',
            'qualquer_senha'
        )
        
        assert sucesso is False, \
            "FALHOU: Login deveria retornar False com usuário inexistente"
        
        print("PASSOU: Usuário inexistente rejeitado corretamente\n")


class TestCadastroLimiteMinimo:
    """
    CT-RF02-01: Cadastro de jogador com valores no limite mínimo
    
    Requisito: RF02 - Cadastro de jogador
    Objetivo: Validar que o cadastro funciona usando nickname e senha no tamanho mínimo permitido
    
    Pré-condições:
    - Banco de dados PostgreSQL configurado
    - Nickname escolhido ainda não existir no banco
    
    Dados de Teste:
    - Nickname: 3 caracteres (limite mínimo)
    - Senha: 8 caracteres (limite mínimo)
    
    Resultado Esperado:
    - Jogador criado com sucesso
    - Registro persistido no banco de dados
    """
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """
        Setup: Preparar ambiente de teste
        Teardown: Limpar dados de teste do banco
        """
        # ==================== SETUP ====================
        self.usuario_teste = {
            'nickname': 'abc',  # 3 caracteres - limite mínimo
            'senha': '12345678'  # 8 caracteres - limite mínimo
        }
        
        self.user_id = None
        
        # Garantir que usuário não existe antes do teste
        print(f"\nSetup: Verificando se usuário '{self.usuario_teste['nickname']}' não existe...")
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id FROM usuarios WHERE nick_name = %s",
                (self.usuario_teste['nickname'],)
            )
            resultado = cursor.fetchone()
            
            if resultado:
                # Se existir, deletar antes do teste
                user_id_existente = resultado[0]
                cursor.execute("DELETE FROM fase1 WHERE usuario_id = %s", (user_id_existente,))
                cursor.execute("DELETE FROM fase2 WHERE usuario_id = %s", (user_id_existente,))
                cursor.execute("DELETE FROM fase3 WHERE usuario_id = %s", (user_id_existente,))
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id_existente,))
                connection.commit()
                print(f"Usuário existente removido (cleanup pré-teste)")
            
            cursor.close()
            DatabaseConnection.return_connection(connection)
        except Exception as e:
            print(f"Erro no setup: {e}")
            pytest.skip(f"Erro ao preparar ambiente de teste: {e}")
        
        yield  # Executa o teste
        
        # ==================== TEARDOWN ====================
        print("\nTeardown: Limpando dados de teste...")
        if self.user_id:
            try:
                connection = DatabaseConnection.get_connection()
                cursor = connection.cursor()
                
                # Deletar progresso
                cursor.execute("DELETE FROM fase1 WHERE usuario_id = %s", (self.user_id,))
                cursor.execute("DELETE FROM fase2 WHERE usuario_id = %s", (self.user_id,))
                cursor.execute("DELETE FROM fase3 WHERE usuario_id = %s", (self.user_id,))
                # Deletar usuário
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (self.user_id,))
                
                connection.commit()
                cursor.close()
                DatabaseConnection.return_connection(connection)
                print("Dados de teste removidos do banco\n")
            except Exception as e:
                print(f"Erro ao limpar dados: {e}\n")
    
    def test_ct_rf02_01_cadastro_valores_limite_minimo(self):
        """
        CT-RF02-01: Cadastro com valores no limite mínimo
        
        Passos do Teste:
        1. Abrir tela de cadastro (simular)
        2. Informar nickname no tamanho mínimo permitido (3 caracteres)
        3. Informar senha no tamanho mínimo permitido (8 caracteres)
        4. Confirmar cadastro
        5. Verificar se jogador foi criado com sucesso
        6. Validar persistência no banco de dados
        
        Critérios de Aceitação:
        - Cadastro aceita nickname com 3 caracteres
        - Cadastro aceita senha com 8 caracteres
        - Registro criado no banco de dados
        - Registro possui todas as fases inicializadas
        """
        print("\n" + "="*70)
        print("EXECUTANDO CT-RF02-01: Cadastro com Valores no Limite Mínimo")
        print("="*70 + "\n")
        
        # ==================== PASSO 1: ABRIR TELA DE CADASTRO ====================
        print("PASSO 1: Abrir tela de cadastro (simulado)")
        print("   Tela de cadastro pronta para receber dados\n")
        
        # ==================== PASSO 2-3: INFORMAR DADOS ====================
        print("PASSO 2-3: Informar dados no limite mínimo")
        print(f"   Nickname: '{self.usuario_teste['nickname']}' ({len(self.usuario_teste['nickname'])} caracteres)")
        print(f"   Senha: {'*' * len(self.usuario_teste['senha'])} ({len(self.usuario_teste['senha'])} caracteres)\n")
        
        # ==================== VALIDAÇÃO 1: TAMANHOS CORRETOS ====================
        assert len(self.usuario_teste['nickname']) == 3, \
            f"FALHOU: Nickname deve ter 3 caracteres (tem {len(self.usuario_teste['nickname'])})"
        
        assert len(self.usuario_teste['senha']) == 8, \
            f"FALHOU: Senha deve ter 8 caracteres (tem {len(self.usuario_teste['senha'])})"
        
        print("PASSOU: Dados estão no limite mínimo permitido\n")
        
        # ==================== PASSO 4: CONFIRMAR CADASTRO ====================
        print("PASSO 4: Confirmar cadastro")
        
        sucesso, mensagem = UserDAO.cadastrar_usuario(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        # ==================== VALIDAÇÃO 2: CADASTRO BEM-SUCEDIDO ====================
        assert sucesso is True, \
            f"FALHOU: Cadastro não foi bem-sucedido. Mensagem: {mensagem}"
        
        assert mensagem == "Usuário cadastrado com sucesso", \
            f"FALHOU: Mensagem incorreta (obtido: {mensagem})"
        
        print(f"PASSOU: Cadastro realizado com sucesso")
        print(f"   Mensagem: {mensagem}\n")
        
        # ==================== PASSO 5: VERIFICAR CRIAÇÃO DO JOGADOR ====================
        print("PASSO 5: Verificar se jogador foi criado com sucesso")
        
        # Tentar fazer login para verificar
        sucesso_login, dados_usuario = UserDAO.verificar_login(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        assert sucesso_login is True, \
            "FALHOU: Login falhou após cadastro (usuário não foi criado corretamente)"
        
        assert dados_usuario is not None, \
            "FALHOU: Dados do usuário não retornados"
        
        assert 'id' in dados_usuario, \
            "FALHOU: ID do usuário não retornado"
        
        self.user_id = dados_usuario['id']
        
        print(f"PASSOU: Jogador criado e autenticado com sucesso")
        print(f"   ID do Usuário: {self.user_id}")
        print(f"   Nickname: {dados_usuario['nickname']}\n")
        
        # ==================== PASSO 6: VALIDAR PERSISTÊNCIA NO BANCO ====================
        print("PASSO 6: Validar persistência no banco de dados")
        
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Verificar registro na tabela usuarios
            cursor.execute(
                "SELECT id, nick_name, senha, salt FROM usuarios WHERE id = %s",
                (self.user_id,)
            )
            
            usuario_db = cursor.fetchone()
            
            assert usuario_db is not None, \
                "FALHOU: Registro não encontrado na tabela usuarios"
            
            user_id_db, nickname_db, senha_hash_db, salt_db = usuario_db
            
            assert nickname_db == self.usuario_teste['nickname'], \
                f"FALHOU: Nickname incorreto no banco (esperado: {self.usuario_teste['nickname']}, obtido: {nickname_db})"
            
            assert senha_hash_db is not None and len(senha_hash_db) == 64, \
                "FALHOU: Hash da senha não foi armazenado corretamente (SHA-256 deve ter 64 caracteres)"
            
            assert salt_db is not None and len(salt_db) == 64, \
                "FALHOU: Salt não foi armazenado corretamente (deve ter 64 caracteres)"
            
            print(f"PASSOU: Registro encontrado na tabela usuarios")
            print(f"   ID: {user_id_db}")
            print(f"   Nickname: {nickname_db}")
            print(f"   Hash senha: {senha_hash_db[:16]}... (SHA-256)")
            print(f"   Salt: {salt_db[:16]}... (64 caracteres)\n")
            
            # Verificar inicialização das fases
            cursor.execute(
                "SELECT usuario_id, vidas, fase_completa FROM fase1 WHERE usuario_id = %s",
                (self.user_id,)
            )
            fase1_db = cursor.fetchone()
            
            assert fase1_db is not None, \
                "FALHOU: Registro não encontrado na tabela fase1"
            
            cursor.execute(
                "SELECT usuario_id, fase_completa FROM fase2 WHERE usuario_id = %s",
                (self.user_id,)
            )
            fase2_db = cursor.fetchone()
            
            assert fase2_db is not None, \
                "FALHOU: Registro não encontrado na tabela fase2"
            
            cursor.execute(
                "SELECT usuario_id, derrotar_yluh FROM fase3 WHERE usuario_id = %s",
                (self.user_id,)
            )
            fase3_db = cursor.fetchone()
            
            assert fase3_db is not None, \
                "FALHOU: Registro não encontrado na tabela fase3"
            
            print(f"PASSOU: Todas as fases inicializadas corretamente")
            print(f"   Fase 1: Vidas={fase1_db[1]}, Completa={fase1_db[2]}")
            print(f"   Fase 2: Completa={fase2_db[1]}")
            print(f"   Fase 3: Yluh derrotado={fase3_db[1]}\n")
            
            cursor.close()
            DatabaseConnection.return_connection(connection)
            
        except Exception as e:
            pytest.fail(f"FALHOU: Erro ao validar persistência no banco: {e}")
        
        # ==================== RESULTADO FINAL ====================
        print("="*70)
        print("RESUMO DO CADASTRO")
        print("="*70)
        print(f"Nickname: {self.usuario_teste['nickname']} (3 caracteres - mínimo)")
        print(f"Senha: {'*' * len(self.usuario_teste['senha'])} (8 caracteres - mínimo)")
        print(f"ID gerado: {self.user_id}")
        print(f"Status: CADASTRADO COM SUCESSO")
        print(f"Persistência: VALIDADA")
        print(f"Fases inicializadas: 3/3")
        print("="*70)
        print("TESTE CT-RF02-01 PASSOU COM SUCESSO!")
        print("="*70 + "\n")


class TestSalvarCarregarProgresso:
    """
    CT-RF06-01: Pausar, salvar e carregar progresso (fluxo básico)
    
    Requisito: RF06 - Salvar e carregar progresso
    Objetivo: Confirmar que o jogo salva o progresso e, ao reabrir, carrega corretamente
    
    Pré-condições:
    - Banco de dados PostgreSQL configurado
    - Usuário logado
    - Jogo em andamento em uma fase conhecida com número conhecido de vidas
    
    Dados de Teste:
    - Fase atual: Fase 1
    - Vidas atuais: 3
    - Itens coletados: Papel=2, Plástico=1, Vidro=0, Metal=1
    - Fase completa: False
    
    Resultado Esperado:
    - Estado restaurado corretamente
    - Fase e vidas iguais às salvas
    - Itens coletados preservados
    """
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """
        Setup: Criar usuário e simular jogo em andamento
        Teardown: Limpar dados de teste do banco
        """
        # ==================== SETUP ====================
        self.usuario_teste = {
            'nickname': 'player_rf06',
            'senha': 'senha_rf06_123'
        }
        
        # Estado inicial do jogo (antes do salvamento)
        self.estado_jogo_inicial = {
            'fase': 1,
            'vidas': 3,
            'itens_papel': 2,
            'itens_plastico': 1,
            'itens_vidro': 0,
            'itens_metal': 1,
            'fase_completa': False
        }
        
        print(f"\nSetup: Criando usuário '{self.usuario_teste['nickname']}' e simulando jogo em andamento...")
        
        # Cadastrar usuário
        sucesso, mensagem = UserDAO.cadastrar_usuario(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        if not sucesso:
            pytest.skip(f"Não foi possível criar usuário de teste: {mensagem}")
        
        # Fazer login para obter ID
        sucesso_login, resultado_login = UserDAO.verificar_login(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        if not sucesso_login:
            pytest.skip("Não foi possível fazer login com usuário criado")
        
        self.user_id = resultado_login['id']
        print(f"Usuário criado com ID: {self.user_id}")
        
        # Simular estado de jogo em andamento (modificar progresso inicial)
        print(f"Simulando jogo em andamento: Fase {self.estado_jogo_inicial['fase']}, Vidas {self.estado_jogo_inicial['vidas']}")
        GameDAO.salvar_progresso_fase1(
            self.user_id,
            itens_papel=self.estado_jogo_inicial['itens_papel'],
            itens_plastico=self.estado_jogo_inicial['itens_plastico'],
            itens_vidro=self.estado_jogo_inicial['itens_vidro'],
            itens_metal=self.estado_jogo_inicial['itens_metal'],
            vidas=self.estado_jogo_inicial['vidas'],
            fase_completa=self.estado_jogo_inicial['fase_completa']
        )
        print(f"Estado inicial configurado no banco\n")
        
        yield  # Executa o teste
        
        # ==================== TEARDOWN ====================
        print("\nTeardown: Limpando dados de teste...")
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Deletar progresso
            cursor.execute("DELETE FROM fase1 WHERE usuario_id = %s", (self.user_id,))
            cursor.execute("DELETE FROM fase2 WHERE usuario_id = %s", (self.user_id,))
            cursor.execute("DELETE FROM fase3 WHERE usuario_id = %s", (self.user_id,))
            # Deletar usuário
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (self.user_id,))
            
            connection.commit()
            cursor.close()
            DatabaseConnection.return_connection(connection)
            print("Dados de teste removidos do banco\n")
        except Exception as e:
            print(f"Erro ao limpar dados: {e}\n")
    
    def test_ct_rf06_01_pausar_salvar_carregar_progresso(self):
        """
        CT-RF06-01: Pausar, salvar e carregar progresso
        
        Passos do Teste:
        1. Durante o jogo, acionar pausar (simulado)
        2. Acionar salvar progresso
        3. Encerrar a sessão (fechar o jogo - simulado)
        4. Abrir o jogo novamente e realizar login
        5. Acionar carregar progresso
        6. Validar que estado foi restaurado corretamente
        
        Critérios de Aceitação:
        - Progresso salvo com sucesso
        - Dados persistidos no banco
        - Carregamento retorna estado correto
        - Fase igual à salva
        - Vidas iguais às salvas
        - Itens coletados preservados
        """
        print("\n" + "="*70)
        print("EXECUTANDO CT-RF06-01: Pausar, Salvar e Carregar Progresso")
        print("="*70 + "\n")
        
        # ==================== PASSO 1: PAUSAR JOGO ====================
        print("PASSO 1: Durante o jogo, acionar pausar")
        print("   Jogo pausado (simulado)")
        print(f"   Estado atual: Fase {self.estado_jogo_inicial['fase']}, Vidas {self.estado_jogo_inicial['vidas']}\n")
        
        # ==================== PASSO 2: SALVAR PROGRESSO ====================
        print("PASSO 2: Acionar salvar progresso")
        
        # Modificar estado antes de salvar (simular progresso adicional)
        estado_modificado = {
            'vidas': 2,  # Perdeu 1 vida
            'itens_papel': 3,  # Coletou mais 1 papel
            'itens_plastico': 2,  # Coletou mais 1 plástico
            'itens_vidro': 1,  # Coletou 1 vidro
            'itens_metal': 1,  # Metal continua igual
            'fase_completa': False
        }
        
        print(f"   Estado modificado durante jogo:")
        print(f"   - Vidas: {self.estado_jogo_inicial['vidas']} -> {estado_modificado['vidas']} (perdeu 1 vida)")
        print(f"   - Papel: {self.estado_jogo_inicial['itens_papel']} -> {estado_modificado['itens_papel']} (coletou +1)")
        print(f"   - Plástico: {self.estado_jogo_inicial['itens_plastico']} -> {estado_modificado['itens_plastico']} (coletou +1)")
        print(f"   - Vidro: {self.estado_jogo_inicial['itens_vidro']} -> {estado_modificado['itens_vidro']} (coletou +1)\n")
        
        # Salvar progresso modificado
        try:
            GameDAO.salvar_progresso_fase1(
                self.user_id,
                itens_papel=estado_modificado['itens_papel'],
                itens_plastico=estado_modificado['itens_plastico'],
                itens_vidro=estado_modificado['itens_vidro'],
                itens_metal=estado_modificado['itens_metal'],
                vidas=estado_modificado['vidas'],
                fase_completa=estado_modificado['fase_completa']
            )
            print("PASSOU: Progresso salvo com sucesso\n")
        except Exception as e:
            pytest.fail(f"FALHOU: Erro ao salvar progresso: {e}")
        
        # ==================== VALIDAÇÃO 1: VERIFICAR PERSISTÊNCIA ====================
        print("VALIDAÇÃO 1: Verificar persistência no banco de dados")
        
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                SELECT vidas, itens_papel, itens_plastico, itens_vidro, 
                       itens_metal, fase_completa, game_over
                FROM fase1 
                WHERE usuario_id = %s
                """,
                (self.user_id,)
            )
            
            resultado_db = cursor.fetchone()
            
            assert resultado_db is not None, \
                "FALHOU: Registro não encontrado no banco após salvar"
            
            vidas_db, papel_db, plastico_db, vidro_db, metal_db, completa_db, game_over_db = resultado_db
            
            assert vidas_db == estado_modificado['vidas'], \
                f"FALHOU: Vidas no banco incorretas (esperado: {estado_modificado['vidas']}, obtido: {vidas_db})"
            
            assert papel_db == estado_modificado['itens_papel'], \
                f"FALHOU: Papel no banco incorreto (esperado: {estado_modificado['itens_papel']}, obtido: {papel_db})"
            
            assert plastico_db == estado_modificado['itens_plastico'], \
                f"FALHOU: Plástico no banco incorreto (esperado: {estado_modificado['itens_plastico']}, obtido: {plastico_db})"
            
            assert vidro_db == estado_modificado['itens_vidro'], \
                f"FALHOU: Vidro no banco incorreto (esperado: {estado_modificado['itens_vidro']}, obtido: {vidro_db})"
            
            print("PASSOU: Dados persistidos corretamente no banco")
            print(f"   Vidas: {vidas_db}")
            print(f"   Papel: {papel_db}/5")
            print(f"   Plástico: {plastico_db}/5")
            print(f"   Vidro: {vidro_db}/5")
            print(f"   Metal: {metal_db}/5")
            print(f"   Game Over: {game_over_db}\n")
            
            cursor.close()
            DatabaseConnection.return_connection(connection)
            
        except Exception as e:
            pytest.fail(f"FALHOU: Erro ao verificar persistência: {e}")
        
        # ==================== PASSO 3: ENCERRAR SESSÃO ====================
        print("PASSO 3: Encerrar a sessão (fechar o jogo)")
        print("   Jogo fechado (simulado)")
        print("   Conexão encerrada\n")
        
        # Simular fechamento limpando variáveis da sessão
        estado_sessao_encerrada = None
        print("   Estado da sessão: ENCERRADO\n")
        
        # ==================== PASSO 4: REABRIR JOGO E FAZER LOGIN ====================
        print("PASSO 4: Abrir o jogo novamente e realizar login")
        
        sucesso_login, dados_usuario = UserDAO.verificar_login(
            self.usuario_teste['nickname'],
            self.usuario_teste['senha']
        )
        
        assert sucesso_login is True, \
            "FALHOU: Login falhou ao reabrir o jogo"
        
        assert dados_usuario['id'] == self.user_id, \
            "FALHOU: ID do usuário diferente após relogin"
        
        print(f"PASSOU: Login realizado com sucesso")
        print(f"   Usuário: {dados_usuario['nickname']}")
        print(f"   ID: {dados_usuario['id']}\n")
        
        # ==================== PASSO 5: CARREGAR PROGRESSO ====================
        print("PASSO 5: Acionar carregar progresso")
        
        progresso_carregado = GameDAO.carregar_progresso_fase1(self.user_id)
        
        assert progresso_carregado is not None, \
            "FALHOU: Carregamento de progresso retornou None"
        
        assert isinstance(progresso_carregado, dict), \
            f"FALHOU: Carregamento não retornou dicionário (tipo: {type(progresso_carregado)})"
        
        print("PASSOU: Progresso carregado com sucesso\n")
        
        # ==================== PASSO 6: VALIDAR ESTADO RESTAURADO ====================
        print("PASSO 6: Validar que estado foi restaurado corretamente")
        
        # Validar vidas
        assert progresso_carregado['vidas'] == estado_modificado['vidas'], \
            f"FALHOU: Vidas não restauradas corretamente (esperado: {estado_modificado['vidas']}, obtido: {progresso_carregado['vidas']})"
        print(f"   Vidas: {progresso_carregado['vidas']} (correto)")
        
        # Validar papel
        assert progresso_carregado['itens_papel'] == estado_modificado['itens_papel'], \
            f"FALHOU: Papel não restaurado corretamente (esperado: {estado_modificado['itens_papel']}, obtido: {progresso_carregado['itens_papel']})"
        print(f"   Papel: {progresso_carregado['itens_papel']}/5 (correto)")
        
        # Validar plástico
        assert progresso_carregado['itens_plastico'] == estado_modificado['itens_plastico'], \
            f"FALHOU: Plástico não restaurado corretamente (esperado: {estado_modificado['itens_plastico']}, obtido: {progresso_carregado['itens_plastico']})"
        print(f"   Plástico: {progresso_carregado['itens_plastico']}/5 (correto)")
        
        # Validar vidro
        assert progresso_carregado['itens_vidro'] == estado_modificado['itens_vidro'], \
            f"FALHOU: Vidro não restaurado corretamente (esperado: {estado_modificado['itens_vidro']}, obtido: {progresso_carregado['itens_vidro']})"
        print(f"   Vidro: {progresso_carregado['itens_vidro']}/5 (correto)")
        
        # Validar metal
        assert progresso_carregado['itens_metal'] == estado_modificado['itens_metal'], \
            f"FALHOU: Metal não restaurado corretamente (esperado: {estado_modificado['itens_metal']}, obtido: {progresso_carregado['itens_metal']})"
        print(f"   Metal: {progresso_carregado['itens_metal']}/5 (correto)")
        
        # Validar fase completa
        assert progresso_carregado['fase_completa'] == estado_modificado['fase_completa'], \
            f"FALHOU: Status da fase incorreto (esperado: {estado_modificado['fase_completa']}, obtido: {progresso_carregado['fase_completa']})"
        print(f"   Fase completa: {progresso_carregado['fase_completa']} (correto)\n")
        
        # ==================== VALIDAÇÃO FINAL: COMPARAÇÃO COMPLETA ====================
        print("VALIDAÇÃO FINAL: Comparação estado salvo vs carregado")
        
        total_itens_salvos = (
            estado_modificado['itens_papel'] + 
            estado_modificado['itens_plastico'] + 
            estado_modificado['itens_vidro'] + 
            estado_modificado['itens_metal']
        )
        
        total_itens_carregados = (
            progresso_carregado['itens_papel'] + 
            progresso_carregado['itens_plastico'] + 
            progresso_carregado['itens_vidro'] + 
            progresso_carregado['itens_metal']
        )
        
        assert total_itens_salvos == total_itens_carregados, \
            f"FALHOU: Total de itens divergente (salvo: {total_itens_salvos}, carregado: {total_itens_carregados})"
        
        print(f"   Total de itens: {total_itens_carregados}/20 (correto)")
        print(f"   Estado 100% restaurado\n")
        
        # ==================== RESULTADO FINAL ====================
        print("="*70)
        print("RESUMO DO TESTE DE SALVAMENTO/CARREGAMENTO")
        print("="*70)
        print(f"Usuário: {self.usuario_teste['nickname']}")
        print(f"Fase: 1")
        print("\nEstado Salvo:")
        print(f"  Vidas: {estado_modificado['vidas']}")
        print(f"  Papel: {estado_modificado['itens_papel']}/5")
        print(f"  Plástico: {estado_modificado['itens_plastico']}/5")
        print(f"  Vidro: {estado_modificado['itens_vidro']}/5")
        print(f"  Metal: {estado_modificado['itens_metal']}/5")
        print("\nEstado Carregado:")
        print(f"  Vidas: {progresso_carregado['vidas']}")
        print(f"  Papel: {progresso_carregado['itens_papel']}/5")
        print(f"  Plástico: {progresso_carregado['itens_plastico']}/5")
        print(f"  Vidro: {progresso_carregado['itens_vidro']}/5")
        print(f"  Metal: {progresso_carregado['itens_metal']}/5")
        print(f"\nStatus: ESTADOS IDÊNTICOS")
        print(f"Persistência: VALIDADA")
        print(f"Carregamento: FUNCIONANDO CORRETAMENTE")
        print("="*70)
        print("TESTE CT-RF06-01 PASSOU COM SUCESSO!")
        print("="*70 + "\n")
