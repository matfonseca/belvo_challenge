from typing import Annotated, Any, Dict, TypedDict

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.agents.models.invoice_type_input import InvoiceType
from app.extractors.invoices_extractor import InvoicesExtractor


class FinancialAnalysisAgent:
    MODEL_NAME = "gpt-4o-mini"

    class State(TypedDict):
        messages: Annotated[list, add_messages]
        anomaly: Dict[str, Any]

    @tool
    def extract_invoices(date: str, invoice_type: InvoiceType):
        """
        Extract invoices for a given date and invoice type.

        Args:
            date (str): The date for which to extract invoices (format: YYYY-MM-DD).
            invoice_type (str): The type of invoice to extract (INFLOW or OUTFLOW).

        Returns:
            str: A JSON string containing the extracted invoices for the specified date and type.
        """
        try:
            extractor = InvoicesExtractor()
            df = extractor.get_invoices(date, invoice_type)
            return df.to_json(orient="records", date_format="iso")
        except Exception as e:
            return f"Error extracting invoices: {str(e)}"

    def __init__(self):
        self.tools = [self.extract_invoices]
        self.tool_node = ToolNode(self.tools)
        self.model = ChatOpenAI(model=self.MODEL_NAME, temperature=0).bind_tools(
            self.tools
        )
        self.graph = self._build_graph()

    def chatbot(self, state: State):
        """Main chatbot function."""
        return {"messages": [self.model.invoke(state["messages"])]}

    def should_continue(self, state: State):
        """Determine whether to continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def _build_graph(self):
        graph_builder = StateGraph(self.State)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("tools", self.tool_node)
        graph_builder.add_conditional_edges(
            "chatbot", self.should_continue, {"tools": "tools", END: END}
        )
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.set_entry_point("chatbot")
        return graph_builder.compile()

    def run(self, anomaly_data, invoices_type):
        """
        Run the financial analysis agent on a single anomaly.

        Args:
            anomaly_data: Anomaly dictionary from your detection system

        Returns:
            dict: The final state containing the analysis
        """
        initial_message = f"""You are a financial analyst. You have access to tools to extract invoice data.

Your task is to analyze the following anomaly:

{anomaly_data}

1. Use the extract_invoices with param type {invoices_type} to get the invoice data for the anomaly date
2. Analyze the data to understand why it's anomalous
3. Provide insights and recommendations

Please start by extracting the invoice data for the anomaly date."""
        final_state = self.graph.invoke(
            {"messages": [("human", initial_message)], "anomaly": anomaly_data}
        )
        return final_state
