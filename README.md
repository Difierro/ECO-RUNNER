# Eco Runner 🎮🌱

Eco Runner é um jogo educativo desenvolvido em Python (Pygame) com integração ao banco de dados PostgreSQL. O projeto combina entretenimento, tecnologia e conscientização ambiental, promovendo a coleta seletiva, reciclagem e combate à poluição.
O jogo está alinhado aos Objetivos de Desenvolvimento Sustentável (ODS), em especial:

- ODS5  – Igualdade de Gênero
- ODS 12 – Consumo e Produção Responsáveis
- ODS 13 – Ação Contra a Mudança Global do Clima

## 📌 Definição do Projeto

A narrativa apresenta Yluh, o Monstro da Poluição, que ameaça encobrir as cidades com fumaça e destruição. Para enfrentá-lo, surge uma guardiã ambiental, cuja missão é coletar, separar e transformar resíduos em armas contra o inimigo.

A jogabilidade está dividida em três fases principais:

- **Fase 1** – A Coleta: em estilo plataforma 2D, o jogador deve coletar 20 materiais recicláveis, desviando de obstáculos como fumaça tóxica e lixo radioativo.
- **Fase 2** – A Separação: o jogador deve classificar corretamente os itens coletados nas lixeiras de coleta seletiva (azul, vermelha, verde e amarela). O sistema impede erros, mantendo o item na tela até que seja feita a escolha correta. Ao concluir, o jogador recebe a arma reciclada e suas vidas são restauradas.
- **Fase 3** – O Desafio Final: a protagonista utiliza a arma reciclada para enfrentar Yluh em uma batalha decisiva, reduzindo sua vida até a vitória.

O Eco Runner proporciona diversão e aprendizado, transmitindo valores de responsabilidade ambiental e incentivando a reflexão sobre os impactos da poluição nas cidades.


## 📂 Estrutura do Projeto

Este repositório será desenvolvido ao longo de três unidades.
Na **Unidade 1**, entregamos:

-   ✅ [Definição do projeto](docs/Definição%20do%20Projeto.pdf)
-   ✅ [Requisitos funcionais e não funcionais](docs/Documento%20de%20Requisitos.pdf)
-   ✅ [Diagramas de classes](docs/Diagrama%20de%20Classes.pdf)
-   ✅ [Diagramas de casos de uso](docs/Diagrama%20de%20Casos%20de%20Uso.pdf)
-   ✅ [Plano de testes](docs/Plano%20de%20Testes.pdf)
-   ✅ [Plano de especificação formal](docs/Plano%20de%20especificacao%20formal.pdf)

O desenvolvimento do código (mecânicas do jogo, banco de dados e
integração) será realizado nas próximas unidades.


## 🛠 Tecnologias e Ferramentas Utilizadas

-   **Linguagem:** Python
-   **Biblioteca de Jogo:** Pygame
-   **Banco de Dados:** PostgreSQL 

## 📋 Requisitos

### Requisitos Funcionais

-   **RF01:** Login de Usuário
-   **RF02:** Cadastrar Jogador
-   **RF03:** Coletar materiais recicláveis 
-   **RF04:** Classificar itens recicláveis
-   **RF05:** Combater Yluh
-   **RF06:** Gerenciar jogo: pausar, salvar e carregar progresso


### Requisitos Não Funcionais

-   **RNF01:** Tempo de resposta
-   **RNF02:** Consistência e Legibilidade da Interface
-   **RNF03:** Compatibilidade com Windows/Linux
-   **RNF04:** Integridade e resiliência dos dados salvos


## 📊 Plano de Testes

Os testes planejados para a primeira entrega incluem:

- **Teste Funcional:** login, coleta, classificação de itens, bloqueio de itens errados e salvamento de progresso.
- **Teste de Integração:** comunicação entre jogo e banco de dados.
- **Teste de Usabilidade:** alertas adequados em erros de classificação de itens.
- **Teste de Desempenho:** medição de resposta em tempo de execução.

## 📐 Especificação Formal

A especificação formal dos requisitos foi desenvolvida utilizando duas abordagens complementares para garantir a corretude do sistema:

- **Notação Z:** Utilizada para modelar a estrutura de dados, estados e operações críticas.
- **Redes de Petri:** Utilizadas para a modelagem de estados dinâmicos e fluxos de transição.
Os esquemas descrevem:

- Estados e invariantes (vidas do jogador, itens, progresso salvo, vidas de Yluh).
- Operações formais (login, cadastro, coleta, classificação, combate, pausa, salvar e carregar).
- Garantia de consistência lógica e prevenção de erros durante a execução do jogo.

## 🤝 Colaboradores
<table align="center">
  <tr>    
    <td align="center">
      <a href="https://github.com/Difierro">
        <img src="https://avatars.githubusercontent.com/u/113316680?v=4" width="120px;" alt="Foto de Gustavo Rodrigues"/><br>
        Gustavo Rodrigues
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/KaueCarvalho11">
        <img src="https://avatars.githubusercontent.com/u/147278152?v=4" width="120px;" alt="Foto de Kauê Valentim"/><br>
        Kauê Valentim
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/M-Aparecida">
        <img src="https://avatars.githubusercontent.com/u/143430124?v=4" width="120px;" alt="Foto de 
        Maria Aparecida"/><br>
        Maria Aparecida
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/euduar-da">
        <img src="https://avatars.githubusercontent.com/u/114101163?v=4" width="120px;" alt="Foto de Maria Eduarda"/><br>
        Maria Eduarda
      </a>
    </td>
     <td align="center">
      <a href="https://github.com/alexrbss">
        <img src="https://avatars.githubusercontent.com/u/143243497?v=4" width="120px;" alt="Foto de Rubens Alexandre"/><br>
        Rubens Alexandre
      </a>
    </td>
  </tr>
</table>
