import base64


class BelvoService:
    def __init__(self, config):
        self.base_url = config.get("base_url")
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")

    def generate_auth_token(self):
        return base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

    def get_auth_header(self):
        return {"Authorization": f"Basic {self.generate_auth_token()}"}
