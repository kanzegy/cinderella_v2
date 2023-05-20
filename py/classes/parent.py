from pymongo import MongoClient
from bson import ObjectId

class Parent():
    def __init__(self, db, collection):
        self.M_URI = "mongodb://localhost"
        self.client = MongoClient(self.M_URI)
        self.db = self.client[db]
        self.collection = self.db[collection]
        self.dbObject = {}
        self._id = "0"

    def ConvertirDeFormASimpleObj(self, formData, dbKeys):
        for dbKey in dbKeys["inputsConvert"]:
            if dbKey in formData:
                self.dbObject[dbKey] = formData[dbKey]

        for dbKey in dbKeys["arrays"]:
            if dbKey in formData:
                self.dbObject[dbKey] = formData.getlist(dbKey)

        for obj in dbKeys["objects"]:
            self.dbObject[obj["name"]] = []

            requestLists = {}
            for value in obj["values"]:
                requestLists[value] = formData.getlist((obj["name"] +"[" + value + "]"))

            element1 = obj["values"][0]
            for i in range(len(requestLists[element1])):
                alarmaObj = {}
                for value in obj["values"]:
                    alarmaObj[value] = requestLists[value][i]
                
                self.dbObject[obj["name"]].append(alarmaObj)


        if "_id" in formData:
            self._id = formData["_id"]

    def _obtenerColeccionObjSimple(self, dbKeys, filter1):
        result = []
        for MongoObj in self.collection.find(filter1):
            obj = {}
            for dbKey in dbKeys["inputsSelectDb"]:
                if dbKey in MongoObj:
                    if dbKey in dbKeys["ObjectIds"]:
                        obj[dbKey] = str(MongoObj[dbKey])
                    else:
                        obj[dbKey] = MongoObj[dbKey]
            result.append(obj)
        return result; 

    def _guardaDatos(self, dbKeys):
        objToInsert = {}
        for input in dbKeys["inputsInsertDb"]:
            if input in self.dbObject:
                objToInsert[input] = self.dbObject[input]


        if(self._id != "" and self._id != "0"):
            self.collection.update_one({"_id" : ObjectId(self._id)}, {"$set" : objToInsert})
        else:
            self.collection.insert_one(objToInsert)
            self.dbObject["_id"] = objToInsert["_id"]