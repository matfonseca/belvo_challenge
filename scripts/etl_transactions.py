import os
import re
import sys

import pandas as pd
from dotenv import load_dotenv

# Add parent directory to Python path to find services module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ofda_service import OFDAService  # noqa: E402

load_dotenv()

config = {
    "base_url": os.getenv("BASE_URL"),
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
}


def get_page(url):
    """
    Devuelve el número de página de una URL.
    """
    match = re.search(r"page=(\d+)", url)
    if match:
        return int(match.group(1))


ofda_service = OFDAService(config)
all_transactions = []
link_id = "e0f02811-39f3-4c08-be2d-b65476e13ff5"

page = 1

while page:
    transactions = ofda_service.get_transactions(link_id, page)
    all_transactions.extend(transactions["results"])
    page = get_page(transactions["next"]) if transactions["next"] else None


df = pd.DataFrame(all_transactions)

df = df.dropna(axis=1, how="any").copy()  # Elimina columnas con valores nulos

df.to_csv("./data/transactions.csv", index=False)
