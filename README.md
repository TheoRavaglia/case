# Marketing Analytics Dashboard

Uma aplicação web para visualização de dados de performance de campanhas de marketing digital, desenvolvida como case técnico.

## 🏗️ Arquitetura

- **Backend**: FastAPI (Python) com autenticação JWT
- **Frontend**: React com Vite
- **Dados**: CSV files (users.csv, metrics.csv)
- **Testes**: pytest para testes automatizados

## 📋 Funcionalidades

### ✅ Implementadas
- ✅ Sistema de login por email e senha
- ✅ Autenticação JWT com tokens seguros
- ✅ Exibição de dados em formato tabular
- ✅ Filtros por data (início e fim)
- ✅ Ordenação por qualquer coluna (clicável)
- ✅ Busca por nome de campanha
- ✅ Coluna "cost_micros" visível apenas para admins
- ✅ Controle de permissões baseado em role
- ✅ API RESTful com FastAPI
- ✅ Interface React responsiva
- ✅ Testes automatizados completos

### 👥 Usuários de Teste
- **Admin**: admin@company.com / admin123 (vê custos)
- **User**: user@company.com / user123 (não vê custos)

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8+
- Node.js 16+
- npm ou yarn

### Backend (FastAPI)

```bash
# Entre no diretório do backend
cd backend

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure os usuários iniciais (execute uma vez)
python utils.py

# Execute o servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: http://localhost:8000

### Frontend (React)

```bash
# Em um novo terminal, entre no diretório do frontend
cd frontend

# Instale as dependências
npm install

# Execute o servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em: http://localhost:3000

## 🧪 Executando Testes

```bash
# No diretório raiz do projeto
cd tests

# Execute todos os testes
pytest -v

# Execute testes específicos
pytest test_auth.py -v
pytest test_permissions.py -v
pytest test_routes.py -v

# Execute com cobertura
pytest --cov=../backend --cov-report=html
```

## 📁 Estrutura do Projeto

```
project/
├── backend/                 # API Python (FastAPI)
│   ├── main.py             # Ponto de entrada da aplicação
│   ├── auth.py             # Autenticação JWT e validação
│   ├── models.py           # Modelos Pydantic (schemas)
│   ├── routes.py           # Rotas da API REST
│   ├── services.py         # Lógica de negócio e filtros
│   ├── utils.py            # Funções auxiliares
│   ├── requirements.txt    # Dependências Python
│   ├── users.csv          # Base de usuários
│   └── metrics.csv        # Base de métricas
│
├── frontend/               # Interface React
│   ├── src/
│   │   ├── App.jsx        # Componente principal
│   │   ├── components/
│   │   │   ├── LoginForm.jsx      # Formulário de login
│   │   │   └── MetricsTable.jsx   # Tabela de métricas
│   │   └── services/
│   │       └── api.js     # Cliente HTTP (Axios)
│   ├── public/index.html  # HTML + CSS embutido
│   ├── package.json       # Dependências Node.js
│   └── vite.config.js     # Configuração Vite
│
├── tests/                  # Testes automatizados
│   ├── test_auth.py       # Testes de autenticação
│   ├── test_permissions.py # Testes de permissões
│   └── test_routes.py     # Testes de rotas e filtros
│
├── .flake8               # Configuração linter
├── pyproject.toml        # Configuração Black
└── README.md             # Esta documentação
```

## 🔐 Autenticação e Segurança

- **JWT Tokens**: Tokens seguros com expiração configurável
- **Bcrypt**: Hash seguro de senhas
- **Role-based Access**: Controle granular de permissões
- **CORS**: Configurado para desenvolvimento local
- **Validação**: Pydantic para validação de entrada

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e performático
- **JWT**: Autenticação stateless
- **Pandas**: Manipulação eficiente de dados CSV
- **Pydantic**: Validação e serialização de dados
- **Pytest**: Framework de testes robusto
- **Uvicorn**: Servidor ASGI de alta performance

### Frontend
- **React 18**: Biblioteca UI reativa
- **Vite**: Build tool rápido e moderno
- **Axios**: Cliente HTTP para API calls
- **CSS Vanilla**: Estilização responsiva sem frameworks

### Qualidade de Código
- **Black**: Formatação automática de código
- **Flake8**: Linting e análise estática
- **Pytest**: Cobertura de testes abrangente

## 📊 API Endpoints

### Autenticação
- `POST /api/login` - Login de usuário
- `GET /api/me` - Informações do usuário atual

### Métricas
- `POST /api/metrics` - Busca métricas com filtros

### Exemplo de Filtros
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "search": "campaign name",
  "sort_by": "impressions",
  "sort_order": "desc"
}
```

## 🎯 Características Técnicas

### Performance
- **Lazy Loading**: Dados carregados sob demanda
- **Filtros Eficientes**: Pandas para manipulação rápida
- **Tokens JWT**: Autenticação stateless escalável

### Usabilidade
- **Ordenação Clicável**: Interface intuitiva
- **Filtros Dinâmicos**: Busca em tempo real
- **Feedback Visual**: Estados de loading e erro
- **Responsivo**: Funciona em diferentes tamanhos de tela

### Segurança
- **Permissões Granulares**: Coluna sensível apenas para admins
- **Validação Robusta**: Entrada sanitizada
- **Tokens Seguros**: Expiração automática

## 🔧 Desenvolvimento

### Code Style
O projeto segue os padrões da Monks:
- **Black** para formatação Python
- **Flake8** para linting
- **Convenções React** modernas
- **Clean Code** principles

### Testes
- **Cobertura Completa**: Auth, permissões, rotas
- **Testes Unitários**: Funções isoladas
- **Testes de Integração**: Endpoints completos
- **Fixtures**: Dados de teste consistentes

## 📝 Próximos Passos (Melhorias Futuras)

- [ ] Paginação para grandes datasets
- [ ] Cache Redis para performance
- [ ] Logs estruturados
- [ ] Métricas de monitoramento
- [ ] Deploy containerizado (Docker)
- [ ] CI/CD pipeline
- [ ] Backup automático dos CSVs

## 👨‍💻 Desenvolvedor

Case técnico desenvolvido seguindo as melhores práticas de:
- **Clean Code**: Código limpo e legível
- **Testing**: Cobertura abrangente
- **Security**: Autenticação robusta
- **Performance**: Otimizações aplicadas
- **Documentation**: Documentação completa