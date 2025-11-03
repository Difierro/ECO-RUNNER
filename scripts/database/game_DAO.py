import psycopg2
from scripts.database.connection import DatabaseConnection

class GameDAO:
    """
    DAO para gerenciar o progresso do jogador nas fases do jogo.
    Responsável por salvar e carregar dados de fase1, fase2 e fase3.
    """
    
    # ==================== FASE 1 - COLETA DE ITENS ====================
    
    @staticmethod
    def salvar_progresso_fase1(user_id, itens_papel=0, itens_plastico=0, 
                               itens_vidro=0, itens_metal=0, 
                               vidas=5, fase_completa=False):
        """
        Salva/atualiza o progresso da Fase 1 (coleta de itens).
        
        Args:
            user_id: ID do usuário
            itens_papel: Quantidade de papel coletado (0-5)
            itens_plastico: Quantidade de plástico coletado (0-5)
            itens_vidro: Quantidade de vidro coletado (0-5)
            itens_metal: Quantidade de metal coletado (0-5)
            vidas: Vidas restantes (0-5)
            fase_completa: Se a fase foi completada
        
        Returns:
            bool: Sucesso da operação
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                UPDATE fase1
                SET itens_papel = %s,
                    itens_plastico = %s,
                    itens_vidro = %s,
                    itens_metal = %s,
                    vidas = %s,
                    fase_completa = %s
                WHERE usuario_id = %s
                """,
                (itens_papel, itens_plastico, itens_vidro, itens_metal, 
                 vidas, fase_completa, user_id)
            )
            
            connection.commit()
            return True
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao salvar progresso fase1: {e}")
            return False
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def carregar_progresso_fase1(user_id):
        """
        Carrega o progresso da Fase 1.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            dict: Dicionário com progresso ou None se erro
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                SELECT itens_papel, itens_plastico, itens_vidro, itens_metal,
                       fase_completa, vidas, game_over
                FROM fase1
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'itens_papel': resultado[0],
                    'itens_plastico': resultado[1],
                    'itens_vidro': resultado[2],
                    'itens_metal': resultado[3],
                    'fase_completa': resultado[4],
                    'vidas': resultado[5],
                    'game_over': resultado[6]
                }
            return None
            
        except psycopg2.Error as e:
            print(f"Erro ao carregar progresso fase1: {e}")
            return None
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def adicionar_item_fase1(user_id, tipo_item):
        """
        Adiciona um item coletado na Fase 1.
        
        Args:
            user_id: ID do usuário
            tipo_item: 'papel', 'plastico', 'vidro' ou 'metal'
        
        Returns:
            tuple: (sucesso, quantidade_atual)
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Mapeia tipo de item para coluna
            colunas = {
                'papel': 'itens_papel',
                'plastico': 'itens_plastico',
                'vidro': 'itens_vidro',
                'metal': 'itens_metal'
            }
            
            if tipo_item not in colunas:
                return False, 0
            
            coluna = colunas[tipo_item]
            
            # Incrementa o item
            cursor.execute(
                f"""
                UPDATE fase1
                SET {coluna} = LEAST({coluna} + 1, 5)
                WHERE usuario_id = %s
                RETURNING {coluna}
                """,
                (user_id,)
            )
            
            quantidade = cursor.fetchone()[0]
            connection.commit()
            
            return True, quantidade
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao adicionar item fase1: {e}")
            return False, 0
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def reduzir_vida_fase1(user_id):
        """
        Reduz uma vida na Fase 1.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            tuple: (sucesso, vidas_restantes, game_over)
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                UPDATE fase1
                SET vidas = GREATEST(vidas - 1, 0)
                WHERE usuario_id = %s
                RETURNING vidas, game_over
                """,
                (user_id,)
            )
            
            vidas, game_over = cursor.fetchone()
            connection.commit()
            
            return True, vidas, game_over
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao reduzir vida fase1: {e}")
            return False, 0, False
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    # ==================== FASE 2 - SEPARAÇÃO NAS LIXEIRAS ====================
    
    @staticmethod
    def salvar_progresso_fase2(user_id, lixeira_papel=0, lixeira_plastico=0,
                               lixeira_vidro=0, lixeira_metal=0, fase_completa=False):
        """
        Salva/atualiza o progresso da Fase 2 (separação nas lixeiras).
        
        Args:
            user_id: ID do usuário
            lixeira_papel: Itens na lixeira de papel (0-5)
            lixeira_plastico: Itens na lixeira de plástico (0-5)
            lixeira_vidro: Itens na lixeira de vidro (0-5)
            lixeira_metal: Itens na lixeira de metal (0-5)
            fase_completa: Se a fase foi completada
        
        Returns:
            bool: Sucesso da operação
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                UPDATE fase2
                SET lixeira_papel = %s,
                    lixeira_plastico = %s,
                    lixeira_vidro = %s,
                    lixeira_metal = %s,
                    fase_completa = %s
                WHERE usuario_id = %s
                """,
                (lixeira_papel, lixeira_plastico, lixeira_vidro, 
                 lixeira_metal, fase_completa, user_id)
            )
            
            connection.commit()
            
            # Se fase foi completada, trigger vai restaurar vidas automaticamente
            if fase_completa:
                print("✅ Fase 2 completada! Vidas restauradas automaticamente pelo trigger.")
            
            return True
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao salvar progresso fase2: {e}")
            return False
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def carregar_progresso_fase2(user_id):
        """
        Carrega o progresso da Fase 2.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            dict: Dicionário com progresso ou None se erro
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                SELECT lixeira_papel, lixeira_plastico, lixeira_vidro, 
                       lixeira_metal, fase_completa
                FROM fase2
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'lixeira_papel': resultado[0],
                    'lixeira_plastico': resultado[1],
                    'lixeira_vidro': resultado[2],
                    'lixeira_metal': resultado[3],
                    'fase_completa': resultado[4]
                }
            return None
            
        except psycopg2.Error as e:
            print(f"Erro ao carregar progresso fase2: {e}")
            return None
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def adicionar_item_lixeira(user_id, tipo_lixeira):
        """
        Adiciona um item na lixeira correspondente.
        
        Args:
            user_id: ID do usuário
            tipo_lixeira: 'papel', 'plastico', 'vidro' ou 'metal'
        
        Returns:
            tuple: (sucesso, quantidade_atual)
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Mapeia tipo de lixeira para coluna
            colunas = {
                'papel': 'lixeira_papel',
                'plastico': 'lixeira_plastico',
                'vidro': 'lixeira_vidro',
                'metal': 'lixeira_metal'
            }
            
            if tipo_lixeira not in colunas:
                return False, 0
            
            coluna = colunas[tipo_lixeira]
            
            # Incrementa o item na lixeira
            cursor.execute(
                f"""
                UPDATE fase2
                SET {coluna} = LEAST({coluna} + 1, 5)
                WHERE usuario_id = %s
                RETURNING {coluna}
                """,
                (user_id,)
            )
            
            quantidade = cursor.fetchone()[0]
            connection.commit()
            
            return True, quantidade
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao adicionar item lixeira: {e}")
            return False, 0
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    # ==================== FASE 3 - DESAFIO FINAL ====================
    
    @staticmethod
    def salvar_progresso_fase3(user_id, vidas=5, derrotar_yluh=False):
        """
        Salva/atualiza o progresso da Fase 3 (desafio final).
        
        Args:
            user_id: ID do usuário
            vidas: Vidas restantes (0-5)
            derrotar_yluh: Se derrotou o chefe Yluh
        
        Returns:
            bool: Sucesso da operação
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                UPDATE fase3
                SET vidas = %s,
                    derrotar_yluh = %s
                WHERE usuario_id = %s
                """,
                (vidas, derrotar_yluh, user_id)
            )
            
            connection.commit()
            return True
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao salvar progresso fase3: {e}")
            return False
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def carregar_progresso_fase3(user_id):
        """
        Carrega o progresso da Fase 3.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            dict: Dicionário com progresso ou None se erro
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                SELECT derrotar_yluh, vidas, game_over
                FROM fase3
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'derrotar_yluh': resultado[0],
                    'vidas': resultado[1],
                    'game_over': resultado[2]
                }
            return None
            
        except psycopg2.Error as e:
            print(f"Erro ao carregar progresso fase3: {e}")
            return None
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def reduzir_vida_fase3(user_id):
        """
        Reduz uma vida na Fase 3.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            tuple: (sucesso, vidas_restantes, game_over)
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                UPDATE fase3
                SET vidas = GREATEST(vidas - 1, 0)
                WHERE usuario_id = %s
                RETURNING vidas, game_over
                """,
                (user_id,)
            )
            
            vidas, game_over = cursor.fetchone()
            connection.commit()
            
            return True, vidas, game_over
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao reduzir vida fase3: {e}")
            return False, 0, False
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    # ==================== MÉTODOS GERAIS ====================
    
    @staticmethod
    def resetar_progresso_usuario(user_id):
        """
        Reseta o progresso completo do usuário (todas as fases).
        
        Args:
            user_id: ID do usuário
        
        Returns:
            bool: Sucesso da operação
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            # Reset fase 1
            cursor.execute(
                """
                UPDATE fase1
                SET itens_papel = 0, itens_plastico = 0, itens_vidro = 0, itens_metal = 0,
                    fase_completa = FALSE, vidas = 5, game_over = FALSE
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            
            # Reset fase 2
            cursor.execute(
                """
                UPDATE fase2
                SET lixeira_papel = 0, lixeira_plastico = 0, lixeira_vidro = 0, lixeira_metal = 0,
                    fase_completa = FALSE
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            
            # Reset fase 3
            cursor.execute(
                """
                UPDATE fase3
                SET derrotar_yluh = FALSE, vidas = 5, game_over = FALSE
                WHERE usuario_id = %s
                """,
                (user_id,)
            )
            
            connection.commit()
            print("✅ Progresso resetado com sucesso!")
            return True
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            print(f"Erro ao resetar progresso: {e}")
            return False
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)
    
    @staticmethod
    def obter_estatisticas_usuario(user_id):
        """
        Obtém estatísticas gerais do usuário.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            dict: Estatísticas do usuário ou None se erro
        """
        connection = None
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(
                """
                SELECT 
                    u.nick_name,
                    f1.itens_papel + f1.itens_plastico + f1.itens_vidro + f1.itens_metal as total_coletado,
                    f1.fase_completa as fase1_completa,
                    f2.fase_completa as fase2_completa,
                    f3.derrotar_yluh as fase3_completa,
                    CASE 
                        WHEN f3.derrotar_yluh THEN 'Jogo Completado!'
                        WHEN f2.fase_completa THEN 'Fase 3'
                        WHEN f1.fase_completa THEN 'Fase 2'
                        ELSE 'Fase 1'
                    END as fase_atual
                FROM usuarios u
                LEFT JOIN fase1 f1 ON u.id = f1.usuario_id
                LEFT JOIN fase2 f2 ON u.id = f2.usuario_id
                LEFT JOIN fase3 f3 ON u.id = f3.usuario_id
                WHERE u.id = %s
                """,
                (user_id,)
            )
            
            resultado = cursor.fetchone()
            
            if resultado:
                return {
                    'nickname': resultado[0],
                    'total_itens_coletados': resultado[1],
                    'fase1_completa': resultado[2],
                    'fase2_completa': resultado[3],
                    'fase3_completa': resultado[4],
                    'fase_atual': resultado[5]
                }
            return None
            
        except psycopg2.Error as e:
            print(f"Erro ao obter estatísticas: {e}")
            return None
        
        finally:
            if connection:
                DatabaseConnection.return_connection(connection)