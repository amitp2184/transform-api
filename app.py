from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException
import re
from langdetect import detect,LangDetectException

app = Flask(__name__)

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(405)
def handle_405(e):
    return jsonify({"error": "Method Not Allowed"}), 405

@app.errorhandler(413)
def handle_413(e):
    return jsonify({"error": "Payload Too Large"}), 413

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500


@app.route("/transform", methods=["POST"])
def transform():
    if not request.is_json or not (raw := request.data) or not raw.strip():
        return jsonify({"error": "Request must be json and body cannot be empoty"}),400
    
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("text"),str):
        return jsonify({"error": "Inavlid JSON or missing text"}),400
    
    text = data["text"]
    
    if len(text) > 1000000:
        return jsonify({"error": "text must be at most 1000000 characters"}),400
    is_spanish = None
    lang = data.get("language", "")
    
    if isinstance(lang, str) and lang.strip().lower() == "spanish":
        try:
            is_spanish = detect(text) == "es"
        except LangDetectException:
            is_spanish = None
    
    tokens = [t.lower() for t in text.split() if t.strip()]
    
    response = {
        "tokens": tokens,
        "count": len(tokens),
        "has_numbers": bool(re.search(r"\d", text)),    
    }
    
    if is_spanish is not None:
        response["is_spanish"] = is_spanish
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)