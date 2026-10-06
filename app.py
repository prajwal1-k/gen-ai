from flask import Flask, render_template, request, jsonify
from chatbot import VeridionChatbot
import os


app = Flask(__name__)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2"
)

chatbot = VeridionChatbot(
    model=OLLAMA_MODEL
)


# --------------------------------------------------
# Home Page
# --------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# --------------------------------------------------
# Chat API
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error": "Request body is required."
            }), 400

        message = data.get("message", "").strip()

        if not message:

            return jsonify({
                "success": False,
                "error": "Message cannot be empty."
            }), 400

        response = chatbot.chat(message)

        return jsonify({
            "success": True,
            "response": response
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():

    status = chatbot.get_status()

    return jsonify({
        "success": True,
        "status": status
    })


# --------------------------------------------------
# Ollama Models
# --------------------------------------------------

@app.route("/api/models", methods=["GET"])
def models():

    models = chatbot.get_models()

    return jsonify({
        "success": True,
        "models": models
    })


# --------------------------------------------------
# Clear Chat
# --------------------------------------------------

@app.route("/api/clear", methods=["POST"])
def clear_chat():

    chatbot.clear_history()

    return jsonify({
        "success": True,
        "message": "Conversation cleared."
    })


# --------------------------------------------------
# Run Application
# --------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("VERIDION AI")
    print("Document Intelligence & Forensics Assistant")
    print("=" * 60)

    print(f"Ollama Model: {OLLAMA_MODEL}")

    if chatbot.check_ollama():

        print("Ollama: ONLINE")

        models = chatbot.get_models()

        print("Available models:")

        for model in models:
            print(f"  - {model}")

    else:

        print("Ollama: OFFLINE")
        print("Start Ollama using: ollama serve")

    print("=" * 60)
    print("Server: http://127.0.0.1:5001")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )