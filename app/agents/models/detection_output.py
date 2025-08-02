from typing import List

from pydantic import BaseModel, Field

from app.agents.models.invoice_type_output import InvoiceType


class Anomaly(BaseModel):
    date: str = Field(description="Date of the transaction")
    total_amount: float = Field(description="Total amount of the transaction")
    invoice_type: InvoiceType = Field(description="Type of the invoice")
    reason: str = Field(description="Reason of the anomaly")

    class Config:
        use_enum_values = True


class DetectionOutput(BaseModel):
    anomalies: List[Anomaly] = Field(description="List of anomalies")

    class Config:
        use_enum_values = True
