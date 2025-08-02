import requests

from services.belvo_service import BelvoService


class OFDAService(BelvoService):
    def __init__(self, config):
        super().__init__(config)

    def get_transactions(self, link_id, page=1, page_size=100):
        endpoint = (
            f"/api/transactions/?page={page}&link={link_id}&page_size={page_size}"
        )
        response = requests.get(
            f"{self.base_url}{endpoint}", headers=self.get_auth_header()
        )
        return response.json()
