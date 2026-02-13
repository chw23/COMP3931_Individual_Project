import logging
from langchain_ollama import ChatOllama

logging.basicConfig(level=logging.INFO)

model = ChatOllama(
    model="llama3.1:8b",
    temperature=0.7,
    num_predict=256,
    base_url="http://localhost:11434"
)

try:
    response = model.invoke("Hello from vscode!")
    logging.info(f"Received response: {response.content}")
except Exception as e:
    logging.error(f"Error invoking model: {str(e)}")
