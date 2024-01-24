from requests.auth import HTTPBasicAuth
import requests

# Teste par ver se api esta pegando (nao esqueça de ligar o servidor: api_main)
class Auth_basic_login:
    def __init__(self):
        self.login = "joao"
        self.senha = "123@456"
        url = "http://localhost:12129/login"
        self.resultado = requests.get(url, auth=(self.login, self.senha))

    def liberar_acesso_token(self, url="http://localhost:12129/autores"):
        resultado_autores = requests.get(
            url,
            headers={"x-access-token": self.resultado.json()["token"]},
        )
        return print(resultado_autores.json())

teste = Auth_basic_login()
teste.liberar_acesso_token()