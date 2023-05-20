from pymongo import MongoClient

class dbController():
    def __init__(self, db):
        self.M_URI = "mongodb://localhost"
        self.client = MongoClient(self.M_URI)
        self.db = self.client[db]
    
    def getDb(self):
        return self.db
    

#tarjetas_coll.insert_one({"nombre":"test3"})
#tarjetas_coll.find_one({"nombre":"test3"})
#tarjetas_coll.delete_one({"nombre":"test3"})
#tarjetas_coll.update_one({"nombre":"test3"}, {"$set":{"nombre": "updateado"}})
#tarjetas_coll.update_one({"nombre":"test3"}, {"$inc":{"precio": 10}}) #le suma 10 a la cantidad 

#tarjetas_coll.count_documents({"nombre":"test3"})

# for tc in tarjetas_coll.find():
#     print(tc)

