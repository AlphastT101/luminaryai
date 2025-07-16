def api_start(client):
    db = client["tokens"]
    bot_collection = db["bot"]
    api_collection = db["api"]

    openr_doc = api_collection.find_one({"key": "api_token"})
    bot_token_doc = bot_collection.find_one({"key": "bot_token"})
    jwt_token_doc = api_collection.find_one({"key": "jwt_token"})
    poli_token_doc = api_collection.find_one({"key": "polinations"})
    verify_email_doc = api_collection.find_one({"key": "verify_email"})
    action_password_doc = api_collection.find_one({"key": "action_password"})

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

    if action_password_doc is None:
        action_password = input("Enter password for the API(when you take an action): ")
        api_collection.insert_one({"key": "action_password", "value": action_password})
    else: action_password = action_password_doc['value']

    if openr_doc is None:
        openr = input("Enter openrouter token for the API: ")
        api_collection.insert_one({"key": "api_token", "value": openr})
    else: openr = openr_doc['value']

    if poli_token_doc is None:
        poli_token = input("Polinations token is not found in MongoDB, Please enter a new poli token: ")
        api_collection.insert_one({"key": "polinations", "value": poli_token})
    else:
        poli_token = poli_token_doc["value"]

    return bot_token, jwt_token, verify_email, action_password, openr, poli_token