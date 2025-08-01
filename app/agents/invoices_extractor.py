import pandas as pd
from app.agents.models.invoice_type_input import InvoiceType

class InvoicesExtractor:
    def __init__(self):
        pass
    
    def extract(self, from_date: str, to_date: str, invoice_type: InvoiceType) -> pd.DataFrame:
        data = pd.read_csv('../data/invoices.csv')
        data = self._filter_data(data, from_date, to_date, invoice_type)
        data = data.groupby(['invoice_date', 'invoice_type'], as_index=False)['total_amount'].sum()
        
        data.rename(columns={'invoice_date': 'date', 'invoice_type': 'invoice_type', 'total_amount': 'total_amount'}, inplace=True)
        return data
    
    def _filter_data(self, data: pd.DataFrame, from_date: str, to_date: str, invoice_type: InvoiceType):
        data['invoice_date'] = pd.to_datetime(data['invoice_date']).dt.date
        
        data = data[(data['invoice_date'] >= pd.to_datetime(from_date).date()) & (data['invoice_date'] <= pd.to_datetime(to_date).date()) & (data['type'] == invoice_type.value)]
        return data
    
    def get_invoices(self, date, invoice_type) -> pd.DataFrame:
        data = pd.read_csv('../data/invoices.csv')
        data = self._filter_data(data, date, date, invoice_type)
        return data