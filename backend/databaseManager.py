import firebase_admin
from firebase_admin import db, credentials

class databaseManager:
    def __init__(self):
        self.credentials = credentials.Certificate('backend/credentials.json')
        firebase_admin.initialize_app(self.credentials)
        self.ref = db.reference('/')
    
   

    

    


