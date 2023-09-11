import bcrypt
from supabase.client import create_client, Client
from app.models import User
from dotenv import dotenv_values

config = dotenv_values(".env")

url: str = config["SUPABASE_URL"]
key: str = config["SUPABASE_KEY"]
supa: Client = create_client(url, key)
