from flask import Blueprint, render_template, request, Response
import requests

ollama_bp = Blueprint('ollama', __name__, url_prefix='/ollama')

# Ollama 服务地址
OLLAMA_API = "http://110.40.188.181:11434/api/chat"

@ollama_bp.route('/')
def chat_index():
    return render_template('ollama/ai_chat.html')

@ollama_bp.route('/stream', methods=['POST'])
def chat_stream():
    user_input = request.json.get('message')
    history = request.json.get('history', [])

    history.append({"role": "user", "content": user_input})

    def generate():
        try:
            with requests.post(OLLAMA_API, json={
                "model": "deepseek-r1:7b",
                "messages": history,
                "stream": True
            }, stream=True) as r:
                full_response = ""
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        full_response += decoded
                        yield f"data: {decoded}\n\n"
                history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            yield f"data: 错误: {str(e)}\n\n"

    return Response(generate(), mimetype='text/event-stream')