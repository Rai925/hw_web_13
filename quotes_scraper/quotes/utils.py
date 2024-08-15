from pymongo import MongoClient

def get_mongodb():
    """

    :rtype: object
    """
    client = MongoClient("mongodb://localhost")

    db = client.homework
    return db