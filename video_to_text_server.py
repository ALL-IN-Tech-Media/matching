import sys
import os
import json
from matching.video_to_text import video_to_text
from flask import Flask, request, jsonify

def load_prompts():
    """Load prompts from JSON file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'prompts.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: prompts.json not found, using default prompt")
        return {"0": {"name": "Default", "prompt": "Please analyze this video and provide a description."}}

def get_prompt(prompt_id="0"):
    """Get prompt by ID from JSON file"""
    prompts = load_prompts()
    return prompts.get(str(prompt_id), prompts["0"])["prompt"]

app = Flask(__name__)

@app.route("/video_to_text", methods=["POST"])
def handle_video_to_text():
    data = request.get_json()
    video_path = data.get("video_path")
    prompt_id = data.get("prompt_id", "3")
    custom_prompt = data.get("prompt")  # 允许自定义prompt
    max_new_tokens = int(data.get("max_new_tokens", 1024))
    
    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "video_path is required and must exist."}), 400
    
    # 使用自定义prompt或从JSON文件获取prompt
    if custom_prompt:
        prompt = custom_prompt
    else:
        prompt = get_prompt(prompt_id)
    
    # print(prompt)
    
    try:
        result = video_to_text(video_path, prompt=prompt, max_new_tokens=max_new_tokens)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/prompts", methods=["GET"])
def list_prompts():
    """List all available prompts"""
    prompts = load_prompts()
    return jsonify(prompts)

if __name__ == "__main__":
    print("[Model loaded. HTTP server running on http://0.0.0.0:5000 . POST to /video_to_text]")
    app.run(host="0.0.0.0", port=5000) 