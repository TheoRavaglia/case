# Marketing Analytics Dashboard - Frontend

Frontend da aplicação de analytics de marketing desenvolvido em React + TypeScript + Vite.

## 🚀 Funcionalidades

- ✅ **Sistema de Login** com autenticação por email/senha
- ✅ **Exibição de dados** em formato tabular responsivo
- ✅ **Filtros por data** (início e fim) 
- ✅ **Ordenação por coluna** (clique nos cabeçalhos)
- ✅ **Controle de acesso** - coluna `cost_micros` visível apenas para admins
- ✅ **Interface responsiva** com CSS profissional

## 🛠️ Tecnologias

- **React 19** - Biblioteca de componentes
- **TypeScript** - Tipagem estática
- **Vite** - Build tool e dev server
- **CSS3** - Estilização responsiva
- **ESLint** - Linting e qualidade de código

## 🏃 Como executar

```bash
# Instalar dependências
npm install

# Executar em modo desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview
```

## 📁 Estrutura do projeto

```
src/
├── components/          # Componentes React
│   ├── LoginForm.tsx   # Formulário de login
│   └── MetricsTable.tsx # Tabela com métricas
├── services/           # Camada de serviços
│   └── api.ts         # Cliente da API
├── types/             # Definições TypeScript
│   └── index.ts       # Interfaces e tipos
├── App.tsx            # Componente principal
├── App.css            # Estilos principais
└── main.tsx          # Ponto de entrada
```

## 🔗 Integração

Este frontend foi desenvolvido para consumir uma API Python (FastAPI) que deve estar rodando na porta 8080.
