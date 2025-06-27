from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    return client["uiautomator_db"]

def insert_modules(module_list):
    db = get_db()
    db.modules.drop()  # optional: clears old list
    db.modules.insert_one({"modules": module_list})

def fetch_modules():
    db = get_db()
    result = db.modules.find_one()
    return result["modules"] if result else []
