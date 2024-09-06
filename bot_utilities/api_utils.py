from openai import OpenAI
import random
import string
import requests

system_prompt = {
    "gpt-4": "I am GPT-4. I am not GPT-4-Turbo rather I am a normal GPT-4 powered by OpenAI.",
    "gpt-4-turbo": "I am GPT-4-Turbo, powered by OpenAI. I am not GPT-4.",
    "gpt-3.5": "I am GPT-3.5. I Always try to act as a GPT-3.5. I am a normal version of GPT-3.5 means I am not the turbo edition. Plus, I am not GPT-4 or GPT-4-turbo.",
    "gpt-3.5-turbo": "I am GPT-3.5-turbo, I am not GPT-4-turbo. I am powered by OpenAI"
}

spml = ["gpt-4", "gpt-4-turbo", "gpt-3.5", "gpt-3.5-turbo"]
models_dict = {
    "gpt-4":"openchat/openchat-7b:free",
    "gpt-4-turbo":"openchat/openchat-7b:free",
    "gpt-3.5":"openchat/openchat-7b:free",
    "gpt-3.5-turbo":"openchat/openchat-7b:free",

    "mistral":"mistralai/mistral-7b-instruct:free",
    "llama-3":"meta-llama/llama-3-8b-instruct:free",
    "llama-3.1":"meta-llama/llama-3.1-8b-instruct:free",
    "gemma-2": "google/gemma-2-9b-it:free",

    # "gemma":"google/gemma-7b-it:free",
    # "qwen-2":"qwen/qwen-2-7b-instruct:free",
    # "phi-3-mini":"microsoft/phi-3-mini-128k-instruct:free",
    # "phi-3-medium":"microsoft/phi-3-medium-128k-instruct:free",
    # "nous-capybara":"nousresearch/nous-capybara-7b:free",
    # "mythomist":"gryphe/mythomist-7b:free",
    # "toppy-m":"undi95/toppy-m-7b:free",
    # "zephyr-beta":"huggingfaceh4/zephyr-7b-beta:free",

    "gpt-4o":"1t",
}

available = [
'gpt-4', 'gpt-4-turbo', 'gpt-3.5', 'gpt-3.5-turbo',
'llama-3','llama-3.1', 'gemma-2', 'mistral', 'gpt-4o',
'command-r-plus-online'
]

def poli(prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    response = requests.get(image_url)
    return response.url

async def generate_api_key(prefix='luminary'):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    api_key = f'{prefix}-{random_string}'
    return api_key


def check_token(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]

    result = collection.find_one({"apitoken": token})
    return result

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

async def delete_token(mongodb, userid):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    key = collection.delete_one({"userid": userid})
    return "deleted" if key else None

def get_id(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    id_doc = collection.find_one({"apitoken": token})
    user_id = "None" if not id_doc["userid"] else id_doc["userid"]
    return user_id


def gen_text(api_key, msg_history, model):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_ = msg_history[0]["role"]
    if system_ == "system" and model in spml:
        msg_history.insert(0, {"role": "system", "name": model , "content": f"{system_prompt[model]} {system_}"})
    elif system_ != "system" and model in spml:
        msg_history.insert(0, {"role": "system","name": model, "content": system_prompt[model]})

    completion = client.chat.completions.create(
        model=models_dict[model],
        messages=msg_history,
    )
    return completion.choices[0].message.content