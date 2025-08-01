from enum import Enum

class InvoiceType(Enum):
    EGRESO = 'Egreso'
    INGRESO = 'Ingreso'
    NOMINA = 'Nómina'
    PAGO = 'Pago'
    TRASLADO = 'Traslado'