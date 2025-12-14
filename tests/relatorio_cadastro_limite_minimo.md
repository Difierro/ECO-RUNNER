# Relatório de Teste - CT-RF02-01

## Identificação do Teste

| Campo | Valor |
|-------|-------|
| **ID do Teste** | CT-RF02-01 |
| **Requisito Funcional** | RF02 - Cadastro de jogador |
| **Objetivo** | Validar que o cadastro funciona usando nickname e senha no tamanho mínimo permitido |
| **Data de Execução** | 14 de dezembro de 2024 |
| **Testador** | Alexandre |
| **Versão do Sistema** | 1.0.0 |
| **Ambiente** | PostgreSQL 16.0, Python 3.14.0, macOS |

---

## Objetivo do Teste

Confirmar que o sistema aceita cadastro de jogador com:
1. Nickname no tamanho mínimo (3 caracteres)
2. Senha no tamanho mínimo (8 caracteres)
3. Persistência correta no banco de dados
4. Inicialização automática das 3 fases

---

## Pré-condições

- Banco de dados PostgreSQL configurado e acessível
- Tabelas `usuarios`, `fase1`, `fase2` e `fase3` criadas
- Pool de conexões ativo
- Nickname escolhido (`abc`) não existir no banco

---

## Dados de Teste

| Campo | Valor | Observação |
|-------|-------|------------|
| **Nickname** | `abc` | 3 caracteres - limite mínimo |
| **Senha** | `12345678` | 8 caracteres - limite mínimo |

### Regras de Validação

- **Nickname:** 3-12 caracteres
- **Senha:** 8-64 caracteres

---

## Passos Executados

### **Passo 1: Abrir tela de cadastro**
- **Ação:** Simular abertura da tela de cadastro
- **Resultado:** Tela pronta para receber dados

### **Passo 2-3: Informar dados no limite mínimo**
- **Ação:** Fornecer nickname com 3 caracteres e senha com 8 caracteres
- **Entrada:** 
  - Nickname: `abc` (3 caracteres)
  - Senha: `12345678` (8 caracteres)
- **Resultado:** Dados validados e aceitos pelo sistema

### **Passo 4: Confirmar cadastro**
- **Ação:** Chamar `UserDAO.cadastrar_usuario(nickname, senha)`
- **Resultado:** Cadastro realizado com sucesso
- **Mensagem:** "Usuário cadastrado com sucesso"

### **Passo 5: Verificar criação do jogador**
- **Ação:** Tentar fazer login com as credenciais cadastradas
- **Resultado:** Login bem-sucedido, dados do usuário retornados
- **ID gerado:** 9
- **Nickname retornado:** `abc`

### **Passo 6: Validar persistência no banco de dados**
- **Ação:** Consultar tabelas do banco para verificar registros

#### Tabela `usuarios`
| Campo | Valor | Status |
|-------|-------|--------|
| ID | 9 | OK |
| Nickname | `abc` | OK |
| Hash SHA-256 | 64 caracteres | OK |
| Salt | 64 caracteres | OK |

#### Tabela `fase1`
| Campo | Valor | Status |
|-------|-------|--------|
| Usuario_ID | 9 | OK |
| Vidas | 5 | OK |
| Fase_Completa | False | OK |

#### Tabela `fase2`
| Campo | Valor | Status |
|-------|-------|--------|
| Usuario_ID | 9 | OK |
| Fase_Completa | False | OK |

#### Tabela `fase3`
| Campo | Valor | Status |
|-------|-------|--------|
| Usuario_ID | 9 | OK |
| Derrotar_Yluh | False | OK |

---

## Resultado Obtido

### **TESTE PASSOU COM SUCESSO**

Todos os critérios de aceitação foram atendidos:

1. Sistema aceitou nickname com 3 caracteres (limite mínimo)
2. Sistema aceitou senha com 8 caracteres (limite mínimo)
3. Cadastro realizado com sucesso
4. Registro criado na tabela `usuarios`
5. Senha armazenada com hash SHA-256 + salt
6. Todas as 3 fases inicializadas automaticamente
7. Login funciona com as credenciais cadastradas

### Resumo do Cadastro

```
Nickname: abc (3 caracteres - mínimo)
Senha: ******** (8 caracteres - mínimo)
ID gerado: 9
Status: CADASTRADO COM SUCESSO
Persistência: VALIDADA
Fases inicializadas: 3/3
```

---

## Evidências (Log de Execução)

```
======================================================================
EXECUTANDO CT-RF02-01: Cadastro com Valores no Limite Mínimo
======================================================================

PASSO 1: Abrir tela de cadastro (simulado)
   Tela de cadastro pronta para receber dados

PASSO 2-3: Informar dados no limite mínimo
   Nickname: 'abc' (3 caracteres)
   Senha: ******** (8 caracteres)

PASSOU: Dados estão no limite mínimo permitido

PASSO 4: Confirmar cadastro
Usuário 'abc' cadastrado com sucesso!
PASSOU: Cadastro realizado com sucesso
   Mensagem: Usuário cadastrado com sucesso

PASSO 5: Verificar se jogador foi criado com sucesso
Login bem-sucedido: abc
PASSOU: Jogador criado e autenticado com sucesso
   ID do Usuário: 9
   Nickname: abc

PASSO 6: Validar persistência no banco de dados
PASSOU: Registro encontrado na tabela usuarios
   ID: 9
   Nickname: abc
   Hash senha: f17c2f31e113ddcf... (SHA-256)
   Salt: 44c5b72c75941c48... (64 caracteres)

PASSOU: Todas as fases inicializadas corretamente
   Fase 1: Vidas=5, Completa=False
   Fase 2: Completa=False
   Fase 3: Yluh derrotado=False

======================================================================
TESTE CT-RF02-01 PASSOU COM SUCESSO!
======================================================================
```

---

## Validações Realizadas

### Validações de Tamanho
- Nickname com exatamente 3 caracteres aceito
- Senha com exatamente 8 caracteres aceita

### Validações de Persistência
- Registro criado na tabela `usuarios`
- Hash SHA-256 armazenado corretamente (64 caracteres)
- Salt único gerado e armazenado (64 caracteres)
- Fase 1 inicializada com 5 vidas
- Fase 2 inicializada
- Fase 3 inicializada

### Validações de Autenticação
- Login funciona após cadastro
- Senha verificada corretamente
- Dados do usuário retornados corretamente

---

## Status Final

| Critério | Status |
|----------|--------|
| **Aceitação de Nickname Mínimo** | APROVADO |
| **Aceitação de Senha Mínima** | APROVADO |
| **Cadastro no Banco** | APROVADO |
| **Hash de Senha** | APROVADO |
| **Inicialização de Fases** | APROVADO |
| **Autenticação Pós-Cadastro** | APROVADO |

### **REQUISITO RF02: APROVADO (Limite Mínimo)**

O sistema de cadastro está funcionando corretamente para valores no limite mínimo permitido.

---

## Observações

1. **Limite Mínimo:** Testado com exatamente 3 caracteres para nickname e 8 para senha
2. **Automação:** Teste totalmente automatizado com pytest
3. **Limpeza:** Dados de teste criados e removidos automaticamente
4. **Segurança:** Hash SHA-256 + salt único funcionando corretamente
5. **Performance:** Tempo de execução: ~0.08s
6. **Inicialização:** Todas as 3 fases criadas automaticamente no cadastro

---

## Validações de Segurança

- Senha nunca armazenada em texto plano
- Hash SHA-256 de 64 caracteres
- Salt único de 64 caracteres por usuário
- Prepared statements protegem contra SQL injection
- Verificação de nickname duplicado antes do cadastro

---

## Próximos Testes Sugeridos

1. **CT-RF02-02:** Cadastro com valores no limite máximo (nickname 12 chars, senha 64 chars)
2. **CT-RF02-03:** Cadastro com nickname abaixo do limite (2 caracteres) - deve falhar
3. **CT-RF02-04:** Cadastro com senha abaixo do limite (7 caracteres) - deve falhar
4. **CT-RF02-05:** Cadastro com nickname duplicado - deve falhar
5. **CT-RF02-06:** Cadastro com caracteres especiais válidos

---

**Testador:** Alexandre  
**Data:** 14/12/2024  
**Assinatura Digital:** Teste Aprovado
