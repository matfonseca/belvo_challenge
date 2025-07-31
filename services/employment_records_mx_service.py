import requests
from services.belvo_service import BelvoService

class EmploymentRecordsMXService(BelvoService):
    def __init__(self, config):
        super().__init__(config)

    def get_employment_records(self, link_id, page=1, page_size=100):
        endpoint = f"/api/employment-records/?page={page}&link={link_id}&page_size={page_size}"
        response = requests.get(f"{self.base_url}{endpoint}", headers=self.get_auth_header())
        return response.json()
    
    def get_employment_records_details(self, record_id):
        endpoint = f"/api/employment-records/{record_id}/"
        response = requests.get(f"{self.base_url}{endpoint}", headers=self.get_auth_header())
        return response.json()
