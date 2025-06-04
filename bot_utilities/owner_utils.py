async def insertdb(dbname, id ,mongodb):

    if dbname == 'blist-servers':
        collection = mongodb["blacklisted"]['servers']

        result = collection.find_one({"server_id": int(id)})

        if result: return "already blacklisted"
        else:
            collection.insert_one({"server_id": id})
            return "blacklisted"
        
    if dbname == 'blist-users':
        collection = mongodb["blacklisted"]['users']
        result = collection.find_one({"user_id": int(id)})

        if result: return "already blacklisted"
        else:
            collection.insert_one({"user_id": id})
            return "blacklisted"

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
        db = mongodb['blacklisted']['users']
        result = collection.find_one({"user_id": int(id)})

        if result:
            collection.delete_one({"user_id": int(id)})
            return "unblacklisted"
        else: return "not blacklisted"

async def check_blist(ctx, mongodb):

    collection = mongodb['blacklisted']['servers']
    result = collection.find_one({"server_id": int(ctx.guild.id)})
    if result: server_blist = True
    else: server_blist = False

    collection = mongodb['blacklisted']['users']
    result = collection.find_one({"user_id": int(ctx.user.id)})
    if result: user_blist = True
    else: user_blist = False

    if user_blist or server_blist: return True
    else: return False

    
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