import requests
from typing import Any, Dict, Optional, List


class VeridionChatbot:
    def __init__(
            self,
            model: str = "llama3.2",
            ollama_url: str = "http://localhost:11434",
            timeout: int = 300
    ):
        self.model = model
        self.ollama_url = ollama_url.strip("/")
        self.timeout = timeout
        self.system_prompt = """You are Veridion AI, an intelligent AI assistant developed for
document authenticity, document forensics, tampering detection,
OCR verification, and AI-assisted document analysis.

Your main areas of expertise are:

1. Document tampering detection
2. Image manipulation detection
3. OCR verification
4. Document metadata analysis
5. Visual evidence analysis
6. Semantic consistency analysis
7. AI-generated document detection
8. Suspicious text and character substitution detection
9. Document risk assessment
10. OCR-to-LLM pipeline integrity
11. Evidence fusion
12. Explainable AI

When answering:

- Be technically accurate.
- Explain complex concepts clearly.
- Do not claim that a document is fraudulent without actual evidence.
- Distinguish between evidence, suspicion, and conclusion.
- Explain what additional evidence would be required.
- When discussing document detection, consider multiple evidence sources.
- Prefer a multimodal evidence-fusion approach.
- Explain limitations and uncertainty.
- Never invent document analysis results when no document has been provided.

A typical Veridion AI document analysis pipeline contains:

Input Document
    ↓
File Validation
    ↓
Document Preprocessing
    ↓
Image/Visual Analysis
    ↓
OCR Extraction
    ↓
OCR Quality Analysis
    ↓
Text/Language Analysis
    ↓
Metadata Analysis
    ↓
Layout Analysis
    ↓
Cross-Modal Consistency Analysis
    ↓
Evidence Fusion
    ↓
Risk Scoring
    ↓
Explainable Detection Report

If the user asks about implementation, provide practical
Python, Flask, API, machine-learning, computer-vision,
OCR, or system architecture guidance where appropriate.

You are currently operating as the conversational intelligence
layer of Veridion AI. Actual forensic detection requires the
appropriate document, OCR, computer-vision, and evidence-fusion
modules.
"""
        self.conversation: List[Dict[str, str]] = []


    def check_ollama(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags",timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_models(self) -> Optional[List[str]]:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return [model.get("name", "") for model in models if isinstance(model, dict)]
            return None
        except requests.RequestException:
            return None

    def ask_ollama(self, message: str, temperature: float = 0.2) -> str:
        url = f"{self.ollama_url}/api/chat"

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]

        messages.extend(self.conversation)

        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 500,
            },
        }

        try:
            response = requests.post(url, json=payload, timeout=(5, self.timeout))

            if response.status_code == 404:
                error_detail = response.json().get("error", "")
                if "model" in error_detail.lower() and "not found" in error_detail.lower():
                    return (
                        f"Ollama model '{self.model}' is not installed.\n\n"
                        f"Run this in your terminal:\n"
                        f"ollama pull {self.model}"
                    )

            response.raise_for_status()
            data = response.json()
            answer = data.get("message", {}).get("content", "")
            self.conversation.append({"role": "user", "content": message})
            self.conversation.append({"role": "assistant", "content": answer})
            return answer
        except requests.exceptions.HTTPError as e:
            response = e.response
            try:
                detail = response.json().get("error", response.text)
            except ValueError:
                detail = response.text
            return f"Ollama API returned HTTP {response.status_code}: {detail}"
        except requests.exceptions.ConnectionError as e:
            return f"Error communicating with Ollama API: {e}"
        except requests.exceptions.Timeout as e:
            return f"Request to Ollama API timed out: {e}"
        except requests.exceptions.RequestException as e:
            return f"An error occurred while communicating with Ollama API: {e}"


        
    def chat(self, message: str) -> str:
        if not message.strip():

            return "Please enter a message."

        if not self.check_ollama():

            return (
                "Ollama is not running.\n\n"
                "Start Ollama using:\n"
                "ollama serve"
            )

        return self.ask_ollama(message)

    def clear_history(self):
        self.conversation.clear()

    def get_status(self):
        self.conversation = []

        ollama_running = self.check_ollama()
        models = self.get_models() if ollama_running else []

        return {
            "ollama_running": ollama_running,
            "models": self.model,
            "available_models": models,
            "conversation_messages": len(self.conversation)
        }
