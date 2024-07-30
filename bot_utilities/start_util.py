def start(client):
    db = client["tokens"]
    bot_collection = db["bot"]
    api_collection = db["api"]

    bot_token_doc = bot_collection.find_one({"key": "bot_token"})
    api_token_doc = api_collection.find_one({"key": "api_token"})

    if bot_token_doc is None:
        bot_token = input("Bot token is not found in MongoDB, Please enter a new bot token: ")
        bot_collection.insert_one({"key": "bot_token", "value": bot_token})
    else:
        bot_token = bot_token_doc["value"]

    if api_token_doc is None:
        api_token = input("AI API token is not found in MongoDB, Please enter a new API token: ")
        api_collection.insert_one({"key": "api_token", "value": api_token})
    else:
        api_token = api_token_doc["value"]

    return bot_token, api_token
