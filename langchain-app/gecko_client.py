import requests

class GECOClient:
    def __init__(self, username: str, password: str):
        self.token_url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/get-token"
        self.username = username
        self.password = password
        self.token = None

    def get_token(self):
        payload = {
            'username': self.username,
            'password': self.password
        }

        response = requests.post(self.token_url, data=payload)

        if response.status_code == 200:
            self.token = response.json().get('token')
            print("Token received:", self.token)
            return self.token
        else:
            raise Exception(f"Failed to get token. Status: {response.status_code}, Response: {response.text}")

    def make_authorized_request(self, url: str):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        return requests.get(url, headers=headers)


    def list_corpus(self):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")
        url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        return requests.get(url, headers=headers)

    def corpus_metadata(self, corpus_id: str):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")
        url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/meta"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        return requests.get(url, headers=headers)

    def list_corpus_documents(self, corpus_id: str):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")
        url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        return requests.get(url, headers=headers)

    def list_corpus_applications(self, corpus_id: str):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")

        url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/apps/" + corpus_id + "/aplicaciones"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        return requests.get(url, headers=headers)
    
    def list_corpus_files(self, corpus_id: str, documents_id: str):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")

        url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/" + documents_id + "/adjuntos"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        return requests.get(url, headers=headers)

    def get_corpus_file(self, corpus_id: str, documents_id):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")

        url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/" + documents_id + "/" + '544'
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        return requests.get(url, headers=headers)

    def get_corpus_text(self, corpus_id: str, documents_id):
        if not self.token:
            raise Exception("No token available. Call get_token() first.")

        url = "http://devsys.iingen.unam.mx/geco4/proyectos/apidocs/corpus/" + corpus_id + "/" + documents_id
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.token}"
        }
        response = requests.get(url, headers=headers)
        return response.json()
