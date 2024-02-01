import firebase_admin
from firebase_admin import db, credentials

credentials = credentials.Certificate('backend/credentials.json')
firebase_admin.initialize_app(credentials, {"databaseURL":"https://taurustrading-c39b4-default-rtdb.firebaseio.com/"})  
ref = db.reference('/')

print(firebase_admin)

