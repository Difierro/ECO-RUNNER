import psycopg2
import hashlib
import secrets
from scripts.database.connection import DatabaseConnection

class UserDAO:
    """
    DAO para gerenciar usuários e autenticação.
    """
    
    @staticmethod
    def _hash_password(password, salt=None):
        """
        Gera hash seguro da senha usando SHA-256 com salt.
        
        Args:
            password: Senha em texto plano
            salt: Salt opcional (se None, gera novo)
        
        Returns:
            tuple: (hash_senha, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)  # Gera salt aleatório de 64 caracteres
        
        # Combina senha + salt e gera hash
        senha_salt = (password + salt).encode('utf-8')
        hash_senha = hashlib.sha256(senha_salt).hexdigest()
        
        return hash_senha, salt
    
    @staticmethod
    def cadastrar_usuario(nickname, senha):
        """
        Cadastra novo usuário com senha hasheada.
        
        Args:
            nickname: Nome de usuário (3-12 caracteres)
            senha: Senha em texto plano (8-64 caracteres)
        
        Returns:
            tuple: (sucesso, mensagem)
        """
        # Validações
        if len(nickname) < 3 or len(nickname) > 12:
            return False, "Nickname deve ter entre 3 e 12 caracteres"
        
        if len(senha) < 8 or len(senha) > 64:
            return False, "Senha deve ter entre 8 e 64 caracteres"
        
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Verifica se usuário já existe
            cursor.execute(
                "SELECT id FROM usuarios WHERE nick_name = %s",
                (nickname,)
            )
            
            if cursor.fetchone():
                return False, "Nome de usuário já existe"
            
            # Gera hash e salt
            senha_hash, salt = UserDAO._hash_password(senha)
            
            # Insere usuário usando prepared statement (proteção contra SQL injection)
            cursor.execute(
                """
                INSERT INTO usuarios (nick_name, senha, salt)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (nickname, senha_hash, salt)
            )
            
            user_id = cursor.fetchone()[0]
            
            # Inicializa registros nas 3 fases para o novo usuário
            cursor.execute(
                "INSERT INTO fase1 (usuario_id) VALUES (%s)",
                (user_id,)
            )
            
            cursor.execute(
                "INSERT INTO fase2 (usuario_id) VALUES (%s)",
                (user_id,)
            )
            
            cursor.execute(
                "INSERT INTO fase3 (usuario_id) VALUES (%s)",
                (user_id,)
            )
            
            connection.commit()
            print(f"Usuário '{nickname}' cadastrado com sucesso!")
            return True, "Usuário cadastrado com sucesso"
            
        except psycopg2.IntegrityError:
            if connection:
                connection.rollback()
            return False, "Nome de usuário já existe"
        
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao cadastrar usuário: {e}")
            return False, "Erro ao cadastrar usuário"
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def verificar_login(nickname, senha):
        """
        Verifica credenciais do usuário.
        
        Args:
            nickname: Nome de usuário
            senha: Senha em texto plano
        
        Returns:
            tuple: (sucesso, dados_usuario ou mensagem_erro)
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Busca usuário usando prepared statement
            cursor.execute(
                """
                SELECT u.id, u.nick_name, u.senha, u.salt,
                       f1.fase_completa as fase1_completa,
                       f2.fase_completa as fase2_completa,
                       f3.derrotar_yluh as fase3_completa,
                       f1.vidas as vidas_fase1,
                       f1.game_over as game_over_fase1
                FROM usuarios u
                LEFT JOIN fase1 f1 ON u.id = f1.usuario_id
                LEFT JOIN fase2 f2 ON u.id = f2.usuario_id
                LEFT JOIN fase3 f3 ON u.id = f3.usuario_id
                WHERE u.nick_name = %s
                """,
                (nickname,)
            )
            
            resultado = cursor.fetchone()
            
            if not resultado:
                return False, "Usuário não encontrado"
            
            user_id, nickname_db, senha_hash_db, salt, fase1_completa, fase2_completa, fase3_completa, vidas_fase1, game_over_fase1 = resultado
            
            # Verifica senha
            senha_hash_input, _ = UserDAO._hash_password(senha, salt)
            
            if senha_hash_input != senha_hash_db:
                return False, "Senha incorreta"
            
            # Retorna dados do usuário
            dados_usuario = {
                'id': user_id,
                'nickname': nickname_db,
                'fase1_completa': fase1_completa or False,
                'fase2_completa': fase2_completa or False,
                'fase3_completa': fase3_completa or False,
                'vidas': vidas_fase1 or 5,#ver se precisa
                'game_over': game_over_fase1 or False #ver se precisa
            }
            
            print(f"Login bem-sucedido: {nickname_db}")
            return True, dados_usuario
            
        except psycopg2.Error as e:
            print(f"Erro ao verificar login: {e}")
            return False, "Erro ao processar login"
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def obter_progresso_completo(user_id):#ver necessidade
        """
        Obtém o progresso completo do usuário em todas as fases.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            dict: Dicionário com progresso de todas as fases ou None se erro
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Busca dados da fase 1
            cursor.execute(
                """
                SELECT itens_papel, itens_plastico, itens_vidro, itens_metal,
                       fase_completa, vidas, game_over
                FROM fase1
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            fase1 = cursor.fetchone()
            
            # Busca dados da fase 2
            cursor.execute(
                """
                SELECT lixeira_papel, lixeira_plastico, lixeira_vidro, lixeira_metal,
                       fase_completa
                FROM fase2
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            fase2 = cursor.fetchone()
            
            # Busca dados da fase 3
            cursor.execute(
                """
                SELECT derrotar_yluh, vidas, game_over
                FROM fase3
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            fase3 = cursor.fetchone()
            
            return {
                'fase1': {
                    'itens_papel': fase1[0] if fase1 else 0,
                    'itens_plastico': fase1[1] if fase1 else 0,
                    'itens_vidro': fase1[2] if fase1 else 0,
                    'itens_metal': fase1[3] if fase1 else 0,
                    'fase_completa': fase1[4] if fase1 else False,
                    'vidas': fase1[5] if fase1 else 5,
                    'game_over': fase1[6] if fase1 else False
                },
                'fase2': {
                    'lixeira_papel': fase2[0] if fase2 else 0,
                    'lixeira_plastico': fase2[1] if fase2 else 0,
                    'lixeira_vidro': fase2[2] if fase2 else 0,
                    'lixeira_metal': fase2[3] if fase2 else 0,
                    'fase_completa': fase2[4] if fase2 else False
                },
                'fase3': {
                    'derrotar_yluh': fase3[0] if fase3 else False,
                    'vidas': fase3[1] if fase3 else 5,
                    'game_over': fase3[2] if fase3 else False
                }
            }
            
        except psycopg2.Error as e:
            print(f"Erro ao obter progresso: {e}")
            return None
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)