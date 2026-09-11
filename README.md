# 🎮 RoboCode Challenge - Plataforma Gamificada de Aprendizado de Python

**RoboCode Challenge** é uma plataforma web completa e gamificada em estilo **Cyberpunk / Arcade Neon** projetada para ensinar programação em Python de forma prática, divertida e competitiva!

---

## 🌟 Principais Recursos

- 🔐 **Autenticação & Perfis Gamificados**: Cadastro e Login de alunos com escolha de Avatares Futuristas e geração de token seguro JWT.
- 🗺️ **Trilha de Fases (Roadmap RPG)**: Atividades divididas em fases progressivas (Hello World, Operações Matemáticas, Condicionais, Loops e Desafio Boss). Fases são desbloqueadas conforme o progresso!
- ⚡ **Arena de Código (IDE Interativa)**: Editor de código Python com destaque de sintaxe, suporte a entradas (`input()`), terminal de saída em tempo real e relatórios de execução em milissegundos.
- 🧪 **Avaliador de Código (Testes Automatizados)**: Execução segura em sandbox que valida o código do aluno contra casos de teste públicos e ocultos.
- 🏆 **Sistema de XP e Level Up**: Ganho de pontos (XP) ao concluir fases, com cálculo automático de níveis e modal de celebração com confetes.
- 🥇 **Hall da Fama (Ranking / Leaderboard)**: Pódio dos 3 melhores alunos e tabela de classificação global em tempo real por XP e nível.
- 🐘 **Suporte Total a PostgreSQL**: Integração nativa com banco de dados PostgreSQL (com fallback automático para SQLite em ambiente de desenvolvimento local).

---

## 🚀 Como Executar o Projeto

### Opção 1: Execução Direta (Sem Dependências de Instalação do PostgreSQL)

A aplicação possui um sistema inteligente de fallback: caso o PostgreSQL não esteja rodando no momento, ela utilizará automaticamente um banco SQLite local (`robocode.db`).

1. **Ative o ambiente virtual e execute o projeto:**
   ```bash
   .\venv\Scripts\python run.py
   ```
2. **Acesse no seu navegador:**
   - **Plataforma (Web UI):** [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Documentação da API (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Opção 2: Execução com Banco de Dados PostgreSQL (Recomendado)

Se você tiver o Docker/Docker Desktop instalado ou um banco PostgreSQL em execução:

1. **Inicie o PostgreSQL e o pgAdmin via Docker Compose:**
   ```bash
   docker compose up -d
   ```
   - **PostgreSQL Port:** `5432` (Usuário: `robocode`, Senha: `robocode_secret_pass`, Database: `robocode_db`)
   - **pgAdmin (Painel Web do Banco):** [http://localhost:8080](http://localhost:8080) (Email: `admin@robocode.com`, Senha: `admin`)

2. **Verifique ou configure o arquivo `.env`:**
   ```env
   DATABASE_URL=postgresql://robocode:robocode_secret_pass@localhost:5432/robocode_db
   SECRET_KEY=super_secret_jwt_key_robocode_2026_gamified
   ```

3. **Inicie a aplicação:**
   ```bash
   .\venv\Scripts\python run.py
   ```

---

## 📁 Estrutura do Projeto

```
RoboCode Challenge/
├── app/
│   ├── __init__.py
│   ├── main.py            # Servidor FastAPI com rotas de API, Auth, Execução e SPA
│   ├── config.py          # Configurações globais e variáveis de ambiente
│   ├── database.py        # Conexão SQLAlchemy (PostgreSQL + Fallback SQLite)
│   ├── models.py          # Tabelas: User, Activity, TestCase, Submission, UserProgress
│   ├── schemas.py         # Schemas Pydantic para requisições e respostas
│   ├── auth.py            # Hashing de senhas (bcrypt) e autenticação JWT
│   ├── evaluator.py       # Executor/Avaliador isolado de código Python
│   ├── seed_data.py       # Dados iniciais de fases e testes
│   ├── static/            # Arquivos estáticos
│   └── templates/
│       └── index.html     # Frontend React Gamified SPA (Tailwind + Ace + Confetti)
├── .env.example           # Modelo de variáveis de ambiente
├── docker-compose.yml     # Configuração do PostgreSQL + pgAdmin
├── requirements.txt       # Dependências Python
├── run.py                 # Script inicializador
└── README.md              # Documentação
```

---

## 🧪 Testando a Plataforma

1. Acesse `http://127.0.0.1:8000` no navegador.
2. Clique na aba **CADASTRAR**, informe seu nome, e-mail, senha e escolha um avatar futurista (ex: *Hacker Ninja*).
3. Na tela principal (**Mapa de Fases**), selecione a **Fase 1: O Despertar do Robô**.
4. Na **Arena de Código**, escreva a solução `print("Hello, RoboCode!")`.
5. Clique em **TESTAR EXECUÇÃO** para ver a saída no terminal.
6. Clique em **SUBMETER CÓDIGO** para receber sua pontuação (+50 XP), desbloquear a próxima fase e ver sua evolução no **Ranking**!
