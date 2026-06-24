import secrets
import hashlib
from cryptography.fernet import Fernet

def generate_secure_token():
    """Gera o token limpo (string) e seu respectivo hash SHA-256 (string)."""
    token_limpo = f"tkn_{secrets.token_urlsafe(32)}"
    token_hash = hashlib.sha256(token_limpo.encode('utf-8')).hexdigest()
    return str(token_limpo), str(token_hash)

class VaultCrypto:
    def __init__(self, master_key: str):
        # Garante de forma estrita que a chave seja convertida para bytes
        if isinstance(master_key, str):
            self.fernet = Fernet(master_key.encode('utf-8'))
        else:
            self.fernet = Fernet(master_key)

    def encrypt_secret(self, plain_text: str) -> str:
        """Criptografa uma string de texto limpo de forma segura."""
        try:
            # Força o dado de entrada a ser uma string normal antes do encode
            raw_text = str(plain_text)
            encrypted_bytes = self.fernet.encrypt(raw_text.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            # Captura qualquer erro interno de tipo e lança com clareza
            raise ValueError(f"Erro interno na criptografia: {str(e)}")

    def decrypt_secret(self, encrypted_text: str) -> str:
        """Descriptografa o texto e retorna a string original."""
        try:
            raw_encrypted = str(encrypted_text)
            decrypted_bytes = self.fernet.decrypt(raw_encrypted.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Erro interno na descriptografia: {str(e)}")