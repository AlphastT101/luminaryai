import io
import os
import yaml
import time
import random
import string
import logging
import warnings
import requests
from PIL import Image
from flask_cors import CORS
from flask_limiter import Limiter
from collections import defaultdict
from pymongo.mongo_client import MongoClient
from flask_limiter.util import get_remote_address
from flask import Flask, render_template, request, jsonify, send_from_directory

from bot_utilities.start_util import start
from bot_utilities.api_models import models
from bot_utilities.api_utils import poli, gen_text, check_token, get_id, available, models_dict, get_t_sbot


# only show errors
log = logging.getLogger('werkzeug')
warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)
# Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per minute"]  # Default global rate limit for IP
)

# Load configuration
with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)
mongodb = config["bot"]["mongodb"]
flask_port = str(config["flask"]["port"])
guild_id = str(config["flask"]["guild_id"])
guild_id_verify = str(config["flask"]["guild_id_verify"])
send_req = str(config["flask"]["send_req_channel"])
webhook = str(config["bot"]["webhook_images"])
client = MongoClient(mongodb)
sbot = get_t_sbot(client)
bot_token, open_r = start(client)
cache_folder = os.path.join(os.getcwd(), 'cache')
os.makedirs(cache_folder, exist_ok=True)

# Rate limit dictionaries
token_rate_limits = defaultdict(list)

@app.route('/')
def index():
    return "hi, what are you doing here?"

@app.route('/v1/images/generations', methods=['POST'])
@limiter.limit("200 per minute")  # Rate limit by IP address
def image():
    # Extract and validate token
    token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
    if not token:
        return jsonify({"error": "Auth failed, API token not found."}), 401

    # Check token validity
    result = check_token(client, token)
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
    sheader = {'Authorization': sbot}
    if not result:
        return jsonify({"error": "Invalid API token! Check your API token and try again. Support: https://discord.gg/hmMBe8YyJ4"}), 401

    user_id = str(get_id(client, token))
    if not user_id.startswith('owner'):
        response = requests.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/roles/1279261339574861895", headers=headers)
        member_response = requests.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/members/{user_id}", headers=headers)
        member_data = member_response.json()
        user_roles = member_data.get('roles', [])
        if "1279261339574861895" not in user_roles:
            return jsonify({"error": "Your account is not verified, please verify yourself in our XET discord server."}), 401

    # Rate limiting by token
    current_time = time.time()
    if token.startswith("luminary"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 200:
            return jsonify({"error": "Rate limit exceeded for this API token, you can only make 10 requests per minute."}), 429
        token_rate_limits[token].append(current_time)

    # Handle request and generate image
    data = request.get_json()
    try:
        prompt = data['prompt']
        engine = data['model']
    except KeyError:
        return jsonify({"error": "Invalid request, you MUST include a 'prompt' and 'model' in the JSON."}), 400

    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(12))

    if engine == "poli":
        img_url = poli(prompt)
    elif engine in ["sdxl-turbo", "dalle3", "flux"]:
        res = requests.post(f"https://discord.com/api/v9/guilds/{guild_id}/channels", json={"name": f"api-{random_string}", "permission_overwrites": [], "type": 0}, headers=headers)
        channel_info = res.json()
        channel_id = channel_info['id']
        engine_id = "1254085308614709318" if engine == "dalle3" else "1265594684084981832" if engine == "sdxl-turbo" else "1280547383330996265"
        seconds = 0
        res = requests.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', json={"content": f"<@{engine_id}> Generate an image of {prompt}"}, headers=sheader)

        while True:
            res = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers)
            messages = res.json()
            do_break = False
            failed = False
            for message in messages:
                if message['content'].startswith("https://"):
                    img_url = message['content']
                    do_break = True
                    break
                elif message['content'] == "error":
                    failed = True

            if do_break: break
            elif failed: return jsonify({"error": "An internal server error occurred, we're working on it."}), 500
            elif seconds >= 120:
                return jsonify({"error": "An error occurred, this is probably our fault. Please share this error code with our developers: 'REQ_TIMEOUT/ENGINE_OFFLINE'"}), 520
            else:
                seconds += 3
                time.sleep(3)
        requests.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
    else:
        return jsonify({"error": "Unknown engine, available engines are: 'poli', 'dalle3', 'sdxl-turbo', 'flux'."}), 400

    img_response = requests.get(img_url)
    img = Image.open(io.BytesIO(img_response.content))
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    file_path = os.path.join('cache', f'{random_string}.png')
    os.makedirs('cache', exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(img_io.getbuffer())
    with open(file_path, 'rb') as f:
        response = requests.post(webhook, files={'file': f})
    response = response.json()
    discord_image_url = response['attachments'][0]['url']
    os.remove(file_path)
    return jsonify({
        "data": [
            {"url": discord_image_url},
            {"serveo": f"https://xet.serveo.net/cache/{random_string}.png"}
        ]
    })

@app.route('/v1/chat/completions', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit by IP address
def text():
    # Extract and validate token
    token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
    if not token:
        return jsonify({"error": "Auth failed, API token not found."}), 401

    # Check token validity
    result = check_token(client, token)
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
    if not result:
        return jsonify({"error": "Invalid API token! Check your API token and try again. Support: https://discord.gg/hmMBe8YyJ4"}), 401

    user_id = str(get_id(client, token))
    if not user_id.startswith('owner'):
        response = requests.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/roles/1279261339574861895", headers=headers)
        member_response = requests.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/members/{user_id}", headers=headers)
        member_data = member_response.json()
        user_roles = member_data.get('roles', [])

        if "1279261339574861895" not in user_roles:
            return jsonify({"error": "Your account is not verified, please verify yourself in our XET discord server."}), 401

    # Rate limiting by token
    current_time = time.time()
    if token.startswith("luminary"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 200:
            return jsonify({"error": "Rate limit exceeded for this API token, you can only make 10 requests per minute."}), 429
        token_rate_limits[token].append(current_time)

    # Handle request and generate response
    data = request.get_json()
    try:
        messages = data['messages']
        model = data['model']
    except KeyError:
        return jsonify({"error": "Invalid request, you MUST include 'messages' and 'model' in the JSON."}), 400

    if model not in available:
        return jsonify({"error": "The model you requested is not found. However, you can request this model to be added! support: https://discord.gg/hmMBe8YyJ4"})
    
    # if model == "gpt-4o":
    #     characters = string.ascii_letters + string.digits
    #     random_string = ''.join(random.choice(characters) for _ in range(12))
    #     res = requests.post(f"https://discord.com/api/v9/guilds/{guild_id}/channels", json={"name": f"api-{random_string}", "permission_overwrites": [], "type": 0}, headers=headers)
    #     channel_info = res.json()
    #     channel_id = channel_info['id']
    #     engine_id = models_dict[model]
    #     messagee = f"a!reqapi `{user_id}` {channel_id} {engine_id} {random_string}"
    #     seconds = 0
    #     file_path = os.path.join('cache', f'{random_string}.txt')
    #     os.makedirs('cache', exist_ok=True)
    #     with open(file_path, 'w') as f:
    #         f.write(f"{messages}")

    #     res = requests.post(f"https://discord.com/api/v9/channels/{send_req}/messages", json={"content": messagee}, headers=headers)

    #     while True:
    #         res = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers)
    #         messages = res.json()
    #         do_break = False
    #         for message in messages:
    #             if message['content'] == "error":
    #                 os.remove(file_path)
    #                 requests.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
    #                 return jsonify({"error": "An internal server error occurred, we're working on it."}), 500
    #             elif int(message['author']['id']) not in [1254815403553722401, 1212631443667423282]:
    #                 response = message['content']
    #                 do_break = True
    #                 break

    #         if do_break: break
    #         elif seconds >= 120:
    #             os.remove(file_path)
    #             requests.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
    #             return jsonify({"error": "An error occurred, this is probably our fault. Please share this error code with our developers: 'REQ_TIMEOUT/ENGINE_OFFLINE'"}), 520
    #         else:
    #             seconds += 3
    #             time.sleep(3)
    #     requests.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)

    response = gen_text(open_r, messages, model)

    return jsonify({"response": response})

# OpenAI-compatible model list endpoint
@app.route('/v1/models', methods=['GET'])
def model_list():
    return jsonify(models)

@app.route('/cache/<filename>')
def serve_file(filename):
    return send_from_directory(cache_folder, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", flask_port))
    app.run(host='0.0.0.0', port=port, debug=True)