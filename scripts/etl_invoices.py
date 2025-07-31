import os
import re
import sys
import pandas as pd

from dotenv import load_dotenv

# Add parent directory to Python path to find services module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.fiscal_mx_service import FiscalMXService



load_dotenv()

config = {
    "base_url": os.getenv("BASE_URL"),
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET")
}

fiscal_mx_service = FiscalMXService(config)
all_invoices = []
link_id = 'c4432b21-b248-4bff-ab46-05ec06a22da1'

def get_page(url):
    """
    Devuelve el número de página de una URL.
    """
    match = re.search(r'page=(\d+)', url)
    if match:
        return int(match.group(1))

page= 1

while page:
    invoices = fiscal_mx_service.get_invoices(link_id,page)
    all_invoices.extend(invoices['results'])
    page = get_page(invoices['next']) if invoices['next'] else None

df = pd.DataFrame(all_invoices)

df = df.dropna(axis=1, how='any').copy() # Elimina columnas con valores nulos

df.to_csv('./data/invoices.csv', index=False)
