from pymongo import MongoClient
from menu import Menu
import logging

logging.basicConfig(filename="store.log", level=logging.DEBUG, format='%(asctime)s :: %(message)s')
client = MongoClient()
db = client.get_database("store")

menu = Menu(db)
menu.welcome()