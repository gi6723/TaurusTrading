import os
from dotenv import load_dotenv
load_dotenv()
username = os.getenv("FINVIZ_USERNAME")
password = os.getenv("FINVIZ_PASSWORD")
print(f"Username: {username}, Password: {password}")