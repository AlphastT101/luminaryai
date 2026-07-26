async def insertdb(dbname, id, mongodb):
    if dbname == "blist-servers":
        collection = mongodb["blacklisted"]["servers"]
        result = collection.find_one({"server_id": int(id)})
        if result:
            return "already blacklisted"
        collection.insert_one({"server_id": id})
        return "blacklisted"

    if dbname == "blist-users":
        collection = mongodb["blacklisted"]["users"]
        result = collection.find_one({"user_id": int(id)})
        if result:
            return "already blacklisted"
        collection.insert_one({"user_id": id})
        return "blacklisted"


async def deletedb(dbname, id, mongodb):
    if dbname == "blist-servers":
        collection = mongodb["blacklisted"]["servers"]
        result = collection.find_one({"server_id": int(id)})
        if result:
            collection.delete_one({"server_id": int(id)})
            return "unblacklisted"
        return "not blacklisted"

    if dbname == "blist-users":
        collection = mongodb["blacklisted"]["users"]
        result = collection.find_one({"user_id": int(id)})
        if result:
            collection.delete_one({"user_id": int(id)})
            return "unblacklisted"
        return "not blacklisted"


async def check_blist(ctx, mongodb):
    collection = mongodb["blacklisted"]["servers"]
    result = collection.find_one({"server_id": int(ctx.guild.id)})
    server_blist = bool(result)

    collection = mongodb["blacklisted"]["users"]
    result = collection.find_one({"user_id": int(ctx.user.id)})
    user_blist = bool(result)

    return user_blist or server_blist


async def check_blist_msg(message, mongodb):
    server_blist = False
    if message.guild is not None:
        collection = mongodb["blacklisted"]["servers"]
        result = collection.find_one({"server_id": int(message.guild.id)})
        server_blist = bool(result)

    collection = mongodb["blacklisted"]["users"]
    result = collection.find_one({"user_id": int(message.author.id)})
    user_blist = bool(result)

    return user_blist or server_blist
