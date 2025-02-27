from flask import Flask, render_template, request, jsonify
import json, os, uuid
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

app = Flask(__name__)
CORS(app)

groq_api_key = "Enter api key here "

# Initialize Groq model
model = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=5,
    api_key=groq_api_key
)

# Provided reference text
context_text = """The 2017 ICC Champions Trophy final was a momentous occasion for Pakistan cricket. 
Facing arch-rivals India at The Oval, Pakistan posted a commanding 338/4, fueled by a century from Fakhar Zaman (114). 
India's chase faltered dramatically, restricted to 158 by Pakistan's bowlers. The 180-run victory secured Pakistan their first Champions Trophy title since the 1992 World Cup."""

# Prompt template
response_prompt = ChatPromptTemplate.from_messages([
    ("system", "You answer questions based on given text. If the question is not related to the provided text, respond with 'its not related to provided content'."),
    ("human", "Text: {text}\n\nQuestion: {question}\n\nAnswer:")
])

# Function to generate response
def get_groq_response(question):
    chain = response_prompt | model | StrOutputParser()
    response = chain.invoke({"text": context_text, "question": question}).strip()
    return response

HISTORY_FILE = "history.json"

def load_history():
    return json.load(open(HISTORY_FILE)) if os.path.exists(HISTORY_FILE) else []

def save_history(history):
    json.dump(history, open(HISTORY_FILE, "w"))

@app.route("/")
def index(): return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    conversation, chat_id = data.get("conversation", []), data.get("chat_id")
    history = load_history()

    if not chat_id:
        chat_id = str(uuid.uuid4())
        title = conversation[0]['content'][:15] + "..." if conversation else "New Chat"
        history.append({"id": chat_id, "title": title, "conversation": conversation})
    else:
        for chat in history:
            if chat["id"] == chat_id:
                chat["conversation"] = conversation
                break

    save_history(history)

    # Get AI response from Groq
    user_question = conversation[-1]['content'] if conversation else ""
    response = get_groq_response(user_question)

    for chat in history:
        if chat["id"] == chat_id:
            chat["conversation"].append({"role": "ai", "content": response})
            break
    save_history(history)

    return jsonify({"response": response, "chat_id": chat_id})

@app.route("/get_history")
def get_history():
    return jsonify(load_history())

@app.route("/get_chat/<chat_id>")
def get_chat(chat_id):
    history = load_history()
    for chat in history:
        if chat["id"] == chat_id:
            return jsonify({"conversation": chat["conversation"]})
    return jsonify({"conversation": []})

@app.route("/save_history", methods=["POST"])
def save_chat():
    data = request.get_json()
    chat_id, conversation = data.get("chat_id"), data.get("conversation", [])
    history = load_history()
    for chat in history:
        if chat["id"] == chat_id:
            chat["conversation"] = conversation
            break
    save_history(history)
    return jsonify({"status": "saved"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
