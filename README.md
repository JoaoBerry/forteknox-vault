# 🔒 ForteKnox Vault

O **ForteKnox Vault** é um ecossistema seguro de gerenciamento de credenciais e segredos (API e Dashboard). Ele foi projetado para permitir que aplicações registrem acessos via tokens isolados e armazenem suas chaves de configuração (como strings de conexão de bancos de dados ou chaves de API externas) de forma totalmente criptografada.

## 🚀 Funcionalidades Principais

* **Isolamento por Aplicação:** Cada sistema possui seu próprio token de acesso (`X-Vault-Token`) e hash SHA-256 persistido no banco de dados.
* **Criptografia Simétrica Forte:** Os segredos são transformados em bytes e criptografados em tempo de execução usando o algoritmo Fernet (AES-128 em modo CBC com assinatura HMAC).
* **Trilha de Auditoria Completa:** Cada operação de escrita (`WRITE_SECRET`), leitura (`READ_SECRET`) ou exclusão grava um rastro imutável com data/hora para fins de segurança e conformidade.
* **Interface Gráfica Integrada:** Painel visual moderno e intuitivo construído em Streamlit para gerenciamento ágil sem necessidade de chamadas cURL ou Swagger manuais.

## 🛠️ Tecnologias Utilizadas

* **FastAPI:** Framework web moderno e de alta performance para a construção da API.
* **Streamlit:** Interface gráfica do usuário (Front-end) desenvolvida puramente em Python.
* **SQLAlchemy & SQLite:** ORM para mapeamento e persistência de dados localmente.
* **Cryptography (Fernet):** Biblioteca robusta para garantia da segurança e confidencialidade dos dados.
* **Pydantic:** Validação de esquemas e contratos de dados das requisições.

## 📂 Estrutura do Projeto

* `main.py`: Ponto de entrada da API FastAPI contendo todas as rotas de gerenciamento.
* `models.py`: Definição das tabelas de banco de dados (Applications, Secrets e AuditLogs).
* `database.py`: Configuração da sessão do SQLAlchemy e inicialização do arquivo SQLite.
* `crypto.py`: Lógicas de geração de tokens seguros e wrapper de criptografia/descriptografia.
* `app.py`: Código do dashboard visual interativo em Streamlit.
* `client.py`: Script automatizado para simulação de consumo do cofre via terminal.

## 🔧 Como Executar o Projeto

### 1. Clonar o repositório e configurar o ambiente:
```bash
git clone [https://github.com/SEU_USUARIO/forteknox-vault.git](https://github.com/SEU_USUARIO/forteknox-vault.git)
cd forteknox-vault
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt

![Painel do ForteKnox Vault](dashboard.PNG)