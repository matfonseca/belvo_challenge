import pandas as pd
from langchain_openai import ChatOpenAI
from app.agents.models.detection_output import DetectionOutput

class Summarizer:
    MODEL_NAME = "gpt-4.1-nano"
    PROMPT = """
    You are a financial analyst.
    
    Your task is to summarize the data provided and explain the anomalies.
    You receive a list of days which were detected as anomalies.
    You can access to the invoices of the day to understand the reason of the anomaly.
    
    Anomalies:
    {anomalies}
    
    Plan:
    1. Extract the invoices for each anomaly day.
    2. Analyze the invoices to understand the reason of the anomaly.
    3. Generate a markdown report with the summary.
    """
    def __init__(self, tools):
        self.model = ChatOpenAI(model=self.MODEL_NAME, temperature=0)
        self.model.bind_tools(tools)
        
    def summarize(self, anomalies: DetectionOutput) -> str:
        prompt = self.PROMPT.format(anomalies=anomalies.model_dump()['anomalies'])
        return self.model.invoke(prompt)
        