import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"

def executar_fluxo_vault():
    print("🔒 [ForteKnox Client] Iniciando comunicação com o cofre...")
    
    # 1. Registrar uma nova aplicação via código
    app_nome = "app-cliente-automatico"
    print(f"\n1. Registrando a aplicação '{app_nome}'...")
    response_app = requests.post(f"{BASE_URL}/apps", json={"name": app_nome})
    
    if response_app.status_code == 201:
        token = response_app.json()["token"]
        print(f"   ✅ Sucesso! Token gerado: {token}")
    elif response_app.status_code == 400:
        # Se já existir, precisamos usar um token válido ou criar outro nome
        print("   ⚠️ Aplicação já cadastrada. Altere o 'app_nome' no script para gerar um novo token.")
        return
    else:
        print(f"   ❌ Erro ao registrar: {response_app.text}")
        return

    # O Header que usaremos para todas as próximas requisições protegidas
    headers = {"X-Vault-Token": token}

    # 2. Salvar um segredo criptografado
    chave = "API_KEY_PRODUCAO"
    valor = "live_9a8b7c6d5e4f3g2h1_secret_token"
    print(f"\n2. Salvando o segredo '{chave}'...")
    
    payload_secret = {"key_name": chave, "value": valor}
    response_save = requests.post(f"{BASE_URL}/secrets", json=payload_secret, headers=headers)
    print(f"   📬 Resposta do Servidor: {response_save.json()}")

    # 3. Recuperar e descriptografar o segredo
    print(f"\n3. Solicitando a chave '{chave}' de volta...")
    response_get = requests.get(f"{BASE_URL}/secrets/{chave}", headers=headers)
    
    if response_get.status_code == 200:
        dado_descriptografado = response_get.json()["value"]
        print(f"   🔓 Segredo descriptografado recebido: {dado_descriptografado}")
    
    # 4. Consultar o relatório de auditoria gerado pelas ações acima
    print("\n4. Coletando relatório de acessos (Audit Logs)...")
    response_logs = requests.get(f"{BASE_URL}/logs", headers=headers)
    
    if response_logs.status_code == 200:
        for log in response_logs.json():
            print(f"   🕒 [{log['timestamp']}] {log['action']} -> {log['details']}")

if __name__ == "__main__":
    # Certifique-se de instalar a biblioteca caso não tenha: pip install requests
    executar_fluxo_vault()