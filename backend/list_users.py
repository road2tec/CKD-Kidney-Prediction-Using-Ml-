from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

db = MongoClient(MONGO_URI)[DATABASE_NAME]
print('Current DB:', DATABASE_NAME)
print()
print('All users in this database:')
for u in db.users.find():
    print(f"  - {u.get('email')}: {u.get('name', 'NO NAME')} ({u.get('role', 'no role')})")
