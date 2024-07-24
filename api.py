from flask import Flask, render_template, request, send_file, jsonify, send_from_directory
import requests
import io
from PIL import Image
from bot_utilities.api_utils import poli, gen_text, check_token
from bot_utilities.start_util import api_start
from bot_utilities.api_models import models
import random
import string
import yaml
from pymongo.mongo_client import MongoClient
import os
import time
from collections import defaultdict


ratelimits = defaultdict(list)
with open("config.yml", "r") as config_file: config = yaml.safe_load(config_file)
mongodb = config["bot"]["mongodb"]
flask_port = str(config["flask"]["port"])
guild_id = str(config["flask"]["guild_id"])
send_req = str(config["flask"]["send_req_channel"])
client = MongoClient(mongodb)
bot_token = api_start(client)
cache_folder = os.path.join(os.getcwd(), 'cache')
os.makedirs(cache_folder, exist_ok=True)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# OpenAI-compatible image generation endpoint
@app.route('/v1/images/generations', methods=['POST'])
def image():
    if 'Authorization' in request.headers: token = request.headers['Authorization'].split()[1]
    else: return jsonify({"error": "Auth failed, API token not found."}), 401

    result = check_token(client, token)
    if not result: return jsonify({"error": "Inavalid API token!, check your API token and try again. Support: https://discord.gg/hmMBe8YyJ4"}), 401

    # Rate limiting logic
    if token.startswith("luminary"):
        current_time = time.time()
        if token in ratelimits:
            ratelimits[token] = [timestamp for timestamp in ratelimits[token] if current_time - timestamp < 60]
            if len(ratelimits[token]) >= 10:
                return jsonify({"error": "Rate limit exceeded, you can only make 10 requests per minute."}), 429
        ratelimits[token].append(current_time)

    data = request.get_json()
    try: prompt = data['prompt']
    except KeyError: return jsonify({"error": "Invalid request, you MUST include a 'prompt' in the json."}), 400
    try: engine = data['model']
    except KeyError: return jsonify({"error": "Invalid request, you MUST include a 'model' in the json."}), 400

    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(12))

    if engine == "poli":
        img_url = poli(prompt)

    elif engine == "lumage-1":
        headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}

        res = requests.post(f"https://discord.com/api/v9/guilds/{guild_id}/channels", json={"name": f"api-{random_string}", "permission_overwrites": [], "type": 0}, headers=headers)
        channel_info = res.json()
        channel_id = channel_info['id']
        res = requests.post(f"https://discord.com/api/v9/channels/{send_req}/messages", json={"content": f"a!reqapi {channel_id} {prompt}"}, headers=headers)

        while True:
            res = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers)
            messages = res.json()
            do_break = False
            for message in messages:
                if message['content'].startswith("https://"):
                    img_url = message['content']
                    do_break = True

            if do_break: break
            else: time.sleep(3)
        requests.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
    else: return jsonify({"error": "Unknown engine, available engines are: 'poli', 'lumage-1'."}), 400

    img_response = requests.get(img_url)
    img = Image.open(io.BytesIO(img_response.content))
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    os.makedirs('cache', exist_ok=True)
    file_path = os.path.join('cache', f'{random_string}.png')
    with open(file_path, 'wb') as f:
        f.write(img_io.getbuffer())

    response = requests.get('https://api.ipify.org?format=json')
    response.raise_for_status()


    ip_info = response.json()
    return jsonify({
        "data": [
            {"url": f"http://{ip_info['ip']}:{flask_port}/cache/{random_string}.png"},
            {"localhost": f"http://127.0.0.1:{flask_port}/cache/{random_string}.png"},
            {"serveo": f"https://luminary.serveo.net/cache/{random_string}.png"}
        ]
    })


# OpenAI-compatible model list endpoint
@app.route('/v1/models', methods=['GET'])
def model_list():
    return jsonify(models)

@app.route('/cache/<filename>')
def serve_file(filename):
    return send_from_directory(cache_folder, filename)

@app.route('/text', methods=['POST'])
def text():
    data = request.get_json()
    try:
        prompt = data['prompt']
    except KeyError:
        return jsonify({"error": "Invalid request, you MUST include a 'prompt' in the json."}), 400
    except Exception as e:
        return "Ouch! An error occured, this is probably our fault. Please report this issue.", 1

    response_data = gen_text(prompt)
    return jsonify(response_data)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", flask_port))
    app.run(host='0.0.0.0', port=port, debug=True)