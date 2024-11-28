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

# def spotify_token(client):
#     db = client["tokens"]
#     bot_collection = db["bot"]

#     spotify_id = bot_collection.find_one({"key": "spotify_id"})
#     spotify_secret = bot_collection.find_one({"key": "spotify_secret"})

#     if spotify_id is None:
#         spotify_id = input("Spotify ID is not found in MongoDB, Please enter a new ID: ")
#         bot_collection.insert_one({"key": "spotify_id", "value": spotify_id})
#     else:
#         spotify_id = spotify_id["value"]

#     if spotify_secret is None:
#         spotify_secret = input("Spotify secret is not found in MongoDB, Please enter a new secret token: ")
#         bot_collection.insert_one({"key": "spotify_secret", "value": spotify_secret})
#     else:
#         spotify_secret = spotify_secret["value"]

#     return spotify_id, spotify_secret