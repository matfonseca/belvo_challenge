import pandas as pd
from langchain_openai import ChatOpenAI

from app.agents.models.detection_output import DetectionOutput


class AnomalyDetector:
    MODEL_NAME = "gpt-4.1-nano"
    PROMPT = """
    Detect anomalies in the total amount by day.

    Anomaly definition: The total amount increase significantly in comparison to the previous period with data.

    The input contains:
    - Date
    - Total amount
    - Invoice type (e.g. "Egreso", "Ingreso", "Nómina", "Pago", "Traslado")


    Data:
    {data}
    """

    def __init__(self):
        self.model = ChatOpenAI(
            model=self.MODEL_NAME, temperature=0
        ).with_structured_output(DetectionOutput)

    def detect(self, data: pd.DataFrame) -> DetectionOutput:
        prompt = self.PROMPT.format(data=data.to_markdown())
        return self.model.invoke(prompt)
