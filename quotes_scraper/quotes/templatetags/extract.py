from django import template
from bson.objectid import ObjectId
from ..utils import get_mongodb
import logging

register = template.Library()


def get_author(id_):
    db = get_mongodb()
    try:
        object_id = ObjectId(id_)
    except Exception as e:
        logging.error(f"Invalid ObjectId: {id_} - {e}")
        return "Unknown"

    author = db.authors.find_one({'_id': object_id})

    if author is None:
        logging.warning(f"Author not found for id: {id_}")
        return "Unknown"

    fullname = author.get('fullname', 'Unknown')
    if fullname == 'Unknown':
        logging.warning(f"No 'fullname' field for author id: {id_}")

    return fullname


register.filter('author', get_author)
