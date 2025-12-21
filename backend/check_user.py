from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Check sagar user
user = db.users.find_one({'email': 'sagar@gmail.com'})
if user:
    print('User found!')
    print('Name:', user.get('name', 'NO NAME FIELD'))
    print('Email:', user.get('email'))
    print('Role:', user.get('role'))
    print('All keys:', list(user.keys()))
else:
    print('User NOT found!')
    
# Check all users
print('\nAll users:')
for u in db.users.find().limit(5):
    print(f"  - {u.get('email')}: {u.get('name', 'NO NAME')}")
