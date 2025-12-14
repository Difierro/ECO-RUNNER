# Relatório de Teste - CT-RF01-01

## Identificação do Teste

| Campo | Valor |
|-------|-------|
| **ID do Teste** | CT-RF01-01 |
| **Requisito Funcional** | RF01 - Autenticação de usuário |
| **Objetivo** | Validar login com credenciais válidas, carregamento de progresso do banco de dados e inicialização do jogo |
| **Data de Execução** | 14 de dezembro de 2024 |
| **Testador** | Alexandre |
| **Versão do Sistema** | 1.0.0 |
| **Ambiente** | PostgreSQL 16.0, Python 3.14.0, macOS |

---

## Objetivo do Teste

Confirmar que um usuário com credenciais válidas consegue:
1. Realizar login no sistema
2. Ter seu progresso carregado do banco de dados
3. Iniciar o jogo com o estado correto (vidas, itens coletados, fase)

---

## Pré-condições

- Banco de dados PostgreSQL configurado e acessível
- Tabelas `usuarios` e `fase1` criadas
- Pool de conexões ativo
- Usuário de teste cadastrado (`ct_rf01_01_user`)
- Progresso salvo no banco:
  - Vidas: 3
  - Papel: 2/5
  - Plástico: 1/5
  - Vidro: 0/5
  - Metal: 1/5
  - Fase completa: Não

---

## Dados de Teste

| Campo | Valor |
|-------|-------|
| **Nickname** | `ct_rf01_01_user` |
| **Senha** | `senha_teste_123` |
| **Progresso Inicial** | Vidas: 3, Papel: 2, Plástico: 1, Metal: 1 |

---

## Passos Executados

### **Passo 1: Autenticar usuário**
- **Ação:** Chamar `UserDAO.verificar_login()` com credenciais válidas
- **Entrada:** Nickname: `ct_rf01_01_user`, Senha: `senha_teste_123`
- **Resultado:** Login bem-sucedido, retornou ID do usuário

### **Passo 2: Carregar progresso**
- **Ação:** Chamar `GameDAO.carregar_progresso_fase1(user_id)`
- **Resultado:** Progresso carregado com sucesso do banco

### **Passo 3: Validar estrutura dos dados**
- **Ação:** Verificar presença de campos obrigatórios
- **Campos validados:** `vidas`, `itens_papel`, `itens_plastico`, `itens_vidro`, `itens_metal`, `fase_completa`
- **Resultado:** Todos os campos presentes

### **Passo 4: Validar valores do progresso**
- **Ação:** Comparar valores retornados com valores esperados
- **Resultado:** Todos os valores conferem

| Campo | Esperado | Obtido | Status |
|-------|----------|--------|--------|
| Vidas | 3 | 3 | OK |
| Papel | 2 | 2 | OK |
| Plástico | 1 | 1 | OK |
| Vidro | 0 | 0 | OK |
| Metal | 1 | 1 | OK |
| Fase Completa | False | False | OK |

### **Passo 5: Validar estado do jogo**
- **Ação:** Verificar se dados são válidos para iniciar jogo
- **Validações:**
  - Vidas > 0 (pode jogar)
  - Total de itens: 4/20 (válido)
  - Todos os itens dentro dos limites (0-5)
- **Resultado:** Estado do jogo validado

---

## Resultado Obtido

### **TESTE PASSOU COM SUCESSO**

Todos os critérios de aceitação foram atendidos:

1. Login realizado com sucesso
2. Progresso carregado corretamente do banco
3. Todos os dados correspondem ao esperado
4. Sistema pronto para iniciar o jogo

### Estado Final do Jogo

```
Usuário: ct_rf01_01_user (ID: 5)
Vidas: 3/5
Itens Coletados: 4/20
   Papel: 2/5
   Plástico: 1/5
   Vidro: 0/5
   Metal: 1/5
Fase Completa: False
```

---

## Evidências (Log de Execução)

```
EXECUTANDO CT-RF01-01: Login com Credenciais Válidas
======================================================================

PASSO 1: Autenticar usuário
   Login: ct_rf01_01_user
   Senha: ****************
PASSOU: Login bem-sucedido
   ID do Usuário: 5
   Nickname: ct_rf01_01_user

PASSO 2: Carregar progresso do banco de dados
PASSOU: Progresso carregado com sucesso

PASSO 3: Validar estrutura dos dados do progresso
PASSOU: Todos os campos obrigatórios presentes

PASSO 4: Validar valores do progresso
   Vidas: 3 (correto)
   Papel: 2/5 (correto)
   Plástico: 1/5 (correto)
   Vidro: 0/5 (correto)
   Metal: 1/5 (correto)
   Fase completa: False (correto)

PASSO 5: Validar estado do jogo para inicialização
   Usuário pode jogar (vidas > 0)
   Total de itens: 4/20 (válido)
   Todos os itens dentro dos limites (max 5/tipo)

======================================================================
TESTE CT-RF01-01 PASSOU COM SUCESSO!
======================================================================
```

---

## Testes Adicionais Executados

### Teste: Login com senha incorreta
- **Entrada:** Usuário válido, senha incorreta
- **Resultado:** PASSOU - Login rejeitado corretamente

### Teste: Login com usuário inexistente
- **Entrada:** Usuário não cadastrado
- **Resultado:** PASSOU - Login rejeitado corretamente

---

## Status Final

| Critério | Status |
|----------|--------|
| **Autenticação** | APROVADO |
| **Carregamento de Progresso** | APROVADO |
| **Validação de Dados** | APROVADO |
| **Inicialização do Jogo** | APROVADO |
| **Testes de Erro** | APROVADO |

### **REQUISITO RF01: APROVADO**

O sistema de autenticação está funcionando corretamente e atende todos os requisitos especificados.

---

## Observações

1. **Automação:** Teste totalmente automatizado com pytest
2. **Limpeza:** Dados de teste criados e removidos automaticamente
3. **Integração:** Banco de dados PostgreSQL funcionando corretamente
4. **Segurança:** Senhas armazenadas com hash SHA-256 + salt
5. **Performance:** Tempo de execução: ~0.5s por teste

---

## Validações de Segurança

- Senhas não são retornadas nas consultas
- Hash SHA-256 funcionando corretamente
- Salt único por usuário
- Verificação de senha case-sensitive

---

## Próximos Passos

1. Implementar testes para RF02 (Cadastro de usuário)
2. Implementar testes para RF03 (Salvamento de progresso)
3. Implementar testes de interface (Pygame)
4. Implementar testes de performance

---

**Testador:** Alexandre  
**Data:** 14/12/2024  
**Assinatura Digital:** Teste Aprovado
