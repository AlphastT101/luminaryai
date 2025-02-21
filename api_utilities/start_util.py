def api_start(client):
    db = client["tokens"]
    bot_collection = db["bot"]
    api_collection = db["api"]

    bot_token_doc = bot_collection.find_one({"key": "bot_token"})
    jwt_token_doc = api_collection.find_one({"key": "jwt_token"})
    verify_email_doc = api_collection.find_one({"key": "verify_email"})

    if bot_token_doc is None:
        bot_token = input("Bot token is not found in MongoDB, Please enter a new bot token: ")
        bot_collection.insert_one({"key": "bot_token", "value": bot_token})
    else: bot_token = bot_token_doc["value"]
    
    if jwt_token_doc is None:
        jwt_token = input("JWT token for API is not found in MongoDB, Please enter a new JWT token: ")
        api_collection.insert_one({"key": "jwt_token", "value": jwt_token})
    else: jwt_token = jwt_token_doc["value"]
    
    if verify_email_doc is None:
        verify_email = input("Password for verify email is not found in MongoDB, Please enter the password: ")
        api_collection.insert_one({"key": "verify_email", "value": verify_email})
    else: verify_email = verify_email_doc["value"]

    return bot_token, jwt_token, verify_email