import unittest
from crypto import VaultCrypto, generate_master_key

class TestVaultCrypto(unittest.TestCase):
    def setUp(self):
        """Esse método roda antes de cada teste para preparar o ambiente."""
        self.master_key = generate_master_key()
        self.crypto = VaultCrypto(self.master_key)

    def test_encrypt_and_decrypt_success(self):
        """Garante que um dado criptografado pode ser lido perfeitamente com a mesma chave."""
        texto_original = "minha_senha_super_secreta_123"
        
        # Criptografa
        texto_criptografado = self.crypto.encrypt_secret(texto_original)
        
        # Garante que o texto mudou (não está mais em texto limpo)
        self.assertNotEqual(texto_original, texto_criptografado)
        
        # Descriptografa
        texto_descriptografado = self.crypto.decrypt_secret(texto_criptografado)
        
        # Garante que o resultado final é exatamente igual ao texto original
        self.assertEqual(texto_original, texto_descriptografado)

    def test_decrypt_with_wrong_key_fails(self):
        """Garante que se alguém tentar usar uma chave errada, o sistema bloqueia e estoura um erro."""
        texto_original = "segredo_de_estado"
        texto_criptografado = self.crypto.encrypt_secret(texto_original)
        
        # Cria uma outra chave totalmente nova e incorreta
        outra_chave_errada = generate_master_key()
        instancia_errada = VaultCrypto(outra_chave_errada)
        
        # O teste passa se o código levantar um PermissionError (bloqueio)
        with self.assertRaises(PermissionError):
            instancia_errada.decrypt_secret(texto_criptografado)

if __name__ == "__main__":
    unittest.main()