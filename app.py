import streamlit as st
import requests
import pandas as pd

# Configuração da página do Streamlit
st.set_page_config(page_title="ForteKnox Vault", page_icon="🔒", layout="wide")

BASE_URL = "http://127.0.0.1:8000/api/v1"

st.title("🔒 ForteKnox Vault — Painel de Controle")
st.markdown("---")

# Painel Lateral para Autenticação Geral
st.sidebar.header("🔑 Autenticação")
token_usuario = st.sidebar.text_input("Insira seu X-Vault-Token", type="password", help="Cole o token gerado pela sua aplicação para gerenciar os segredos.")

headers = {"X-Vault-Token": token_usuario} if token_usuario else {}

# Criação das abas principais na tela
tab_apps, tab_secrets, tab_logs = st.tabs(["🚀 Registrar App", "💼 Meus Segredos", "📜 Trilha de Auditoria"])

# --- ABA 1: REGISTRO DE APLICAÇÕES ---
with tab_apps:
    st.header("Registrar Nova Aplicação")
    st.write("Crie uma credencial de acesso isolada para um novo sistema.")
    
    novo_app_nome = st.text_input("Nome da Aplicação", placeholder="ex: app-ecommerce-prod")
    
    if st.button("Gerar Acesso", type="primary"):
        if novo_app_nome:
            try:
                response = requests.post(f"{BASE_URL}/apps", json={"name": novo_app_nome})
                if response.status_code == 201:
                    dados = response.json()
                    st.success(f"🔥 Aplicação '{dados['name']}' registrada com sucesso!")
                    st.code(dados['token'], language="text")
                    st.warning("⚠️ Guarde este token em um local seguro! Você precisará dele no painel lateral para acessar as demais funções.")
                elif response.status_code == 400:
                    st.error("❌ Esse nome de aplicação já está em uso.")
                else:
                    st.error(f"❌ Erro no servidor: {response.text}")
            except Exception as e:
                st.error(f"Não foi possível conectar à API: {e}")
        else:
            st.warning("Por favor, digite um nome para a aplicação.")

# --- ABA 2: GERENCIAMENTO DE SEGREDOS ---
with tab_secrets:
    st.header("Gerenciador de Credenciais Criptografadas")
    
    if not token_usuario:
        st.info("💡 Insira o token da sua aplicação no menu lateral para liberar esta seção.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 Adicionar / Atualizar Segredo")
            chave = st.text_input("Nome da Chave (Key Name)", placeholder="ex: STRIPE_API_KEY")
            valor = st.text_input("Valor do Segredo (Value)", type="password", placeholder="ex: sk_live_...")
            
            if st.button("Criptografar e Salvar"):
                if chave and valor:
                    res = requests.post(f"{BASE_URL}/secrets", json={"key_name": chave, "value": valor}, headers=headers)
                    if res.status_code == 201:
                        st.success(f"✅ Segredo '{chave}' armazenado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Falha ao salvar segredo. Verifique seu token.")
                else:
                    st.warning("Preencha ambos os campos.")
                    
        with col2:
            st.subheader("📤 Consultar Segredo Existente")
            
            # Busca as chaves disponíveis para facilitar a seleção do usuário
            try:
                res_keys = requests.get(f"{BASE_URL}/secrets", headers=headers)
                if res_keys.status_code == 200:
                    lista_chaves = res_keys.json().get("keys", [])
                    
                    if lista_chaves:
                        chave_selecionada = st.selectbox("Selecione a chave para descriptografar:", lista_chaves)
                        
                        if st.button("Revelar Valor"):
                            res_val = requests.get(f"{BASE_URL}/secrets/{chave_selecionada}", headers=headers)
                            if res_val.status_code == 200:
                                st.success(f"Chave: {chave_selecionada}")
                                st.code(res_val.json()["value"], language="text")
                            else:
                                st.error("Erro ao buscar o valor.")
                                
                        if st.button("🗑️ Deletar Chave Permanentemente", type="secondary"):
                            res_del = requests.delete(f"{BASE_URL}/secrets/{chave_selecionada}", headers=headers)
                            if res_del.status_code == 200:
                                st.success(f"Segredo '{chave_selecionada}' removido.")
                                st.rerun()
                    else:
                        st.write("Nenhum segredo salvo para esta aplicação ainda.")
                else:
                    st.error("Token inválido ou expirado.")
            except Exception as e:
                st.error(f"Erro ao listar chaves: {e}")

# --- ABA 3: TRILHA DE AUDITORIA ---
with tab_logs:
    st.header("Histórico de Operações (Audit Logs)")
    st.write("Monitore em tempo real todos os acessos, leituras e escritas desta credencial.")
    
    if not token_usuario:
        st.info("💡 Insira o token da sua aplicação no menu lateral para visualizar os logs de segurança.")
    else:
        try:
            res_logs = requests.get(f"{BASE_URL}/logs", headers=headers)
            if res_logs.status_code == 200:
                dados_logs = res_logs.json()
                if dados_logs:
                    # Converte os logs recebidos da API em uma tabela elegante do Pandas
                    df = pd.DataFrame(dados_logs)
                    df.columns = ["Ação", "Detalhes", "Data/Hora"]
                    st.dataframe(df, use_container_width=True)
                else:
                    st.write("Nenhuma atividade registrada para esta aplicação.")
            else:
                st.error("Erro ao recuperar logs de auditoria.")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")