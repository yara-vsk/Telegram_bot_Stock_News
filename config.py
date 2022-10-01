import os
from database import DBcomand
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")


db = DBcomand()