async def insertdb(dbname, id ,mongodb):

    if dbname == 'blist-servers':
        db = mongodb["blacklisted"]
        collection = db['servers']

        doc = {
            "server_id": id
        }
        result = collection.find_one({"server_id": int(id)})

        if result:
            return "already blacklisted"
        else:
            collection.insert_one(doc)
            return "blacklisted"
        
    if dbname == 'blist-users':
        db = mongodb["blacklisted"]
        collection = db['users']

        doc ={
            "user_id": id
        }
        result = collection.find_one({"user_id": int(id)})

        if result:
            return "already blacklisted"
        else:
            collection.insert_one(doc)
            return "blacklisted"

    if dbname == 'ai-channels':
        db = mongodb["ai"]
        collection = db['channels']

        doc ={
            "ai_channels": id
        }
        result = collection.find_one({"ai_channels": int(id)})

        if result:
            return "already set"
        else:
            collection.insert_one(doc)
            return "success"

async def getdb(dbname, id, mongodb):

    if dbname == 'blist-servers':
        db = mongodb["blacklisted"]
        collection = db['servers']
        result = collection.find_one({"server_id": int(id)})
        if result:
            return "blacklisted"
        else:
            return "not blacklisted"
        
    if dbname == 'blist-users':
        db = mongodb["blacklisted"]
        collection = db['users']

        result = collection.find_one({"user_id": int(id)})
        if result:
            return "blacklisted"
        else:
            return "not blacklisted"
        
    if dbname == 'ai-channels':
        db = mongodb["ai"]
        collection = db['channels']

        result = collection.find_one({"ai_channels": int(id)})
        if result:
            return "found"
        else:
            return "not found"

async def deletedb(dbname, id, mongodb):

    if dbname == 'blist-servers':
        db = mongodb['blacklisted']
        collection = db['servers']

        result = collection.find_one({"server_id": int(id)})
        if result:
            collection.delete_one({"server_id": int(id)})
            return "unblacklisted"
        else:
            return "not blacklisted"
        
    if dbname == 'blist-users':
        db = mongodb['blacklisted']
        collection = db['users']

        result = collection.find_one({"user_id": int(id)})
        if result:
            collection.delete_one({"user_id": int(id)})
            return "unblacklisted"
        else:
            return "not blacklisted"

    if dbname == 'ai-channels':
        db = mongodb['ai']
        collection = db['channels']

        result = collection.find_one({"ai_channels": int(id)})
        if result:
            collection.delete_one({"ai_channels": int(id)})
            return "success"
        else:
            return "not found"

async def check_blist(ctx, mongodb):

    if ctx.guild is not None:
        db = mongodb['blacklisted']
        collection = db['servers']
        result = collection.find_one({"server_id": int(ctx.guild.id)})
        if result:
            server_blist = True
        else:
            server_blist = False

    db = mongodb['blacklisted']
    collection = db['users']
    result = collection.find_one({"user_id": int(ctx.user.id)})
    if result:
        user_blist = True
    else:
        user_blist = False

    if user_blist or server_blist:
        return True
    else:
        return False
    
    
async def check_blist_msg(message, mongodb):

    if message.guild is not None:
        db = mongodb['blacklisted']
        collection = db['servers']
        result = collection.find_one({"server_id": int(message.guild.id)})
        if result:
            server_blist = True
        else:
            server_blist = False

    db = mongodb['blacklisted']
    collection = db['users']
    result = collection.find_one({"user_id": int(message.author.id)})
    if result:
        user_blist = True
    else:
        user_blist = False

    if user_blist or server_blist:
        return True
    else:
        return False