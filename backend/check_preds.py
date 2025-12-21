from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['Chronic_Kidney_Disease']

print("All predictions and their user_ids:\n")
for p in db.hybrid_predictions.find():
    print(f"ID: {p['_id']}")
    print(f"user_id: {p.get('user_id')}")
    print(f"timestamp: {p.get('timestamp')}")
    print()
