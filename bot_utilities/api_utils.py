import google.generativeai as gemini
from openai import OpenAI
from bot_utilities.api_prompt import prompt
import random
import string
import requests


gemini.configure(api_key="AIzaSyBiXYuuTUgD5m42TF49_7AmDqCF6QxU2zk")

model = gemini.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=prompt)

def poli(prompt):
    # response = openai_client.images.generate(
    #     model="playground-v2.5",
    #     prompt=prompt,
    #     n=1,  # images count
    #     size="4096x4096"
    # )
    # return response.data[0].url
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    response = requests.get(image_url)
    return response.url


def gen_text(prompt):
    response = model.generate_content(
        contents=prompt
    )
    return {"generated_text": response.text}

async def generate_api_key(prefix='luminary'):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    api_key = f'{prefix}-{random_string}'
    return api_key


def check_token(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]

    result = collection.find_one({"apitoken": token})
    if result: return True
    else: return False

async def check_user(mongodb, userid):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    result = collection.find_one({"userid": userid})
    if result: return True
    else: return False

async def insert_token(mongodb, userid):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    key = await generate_api_key()
    collection.insert_one({"apitoken": key, "userid": userid})
    return key

def get_id(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    id_doc = collection.find_one({"apitoken": token})
    user_id = id_doc["userid"]
    return user_id