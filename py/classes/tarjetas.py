from py.classes.parent import Parent

class Tarjeta(Parent):
    def __init__(self):
        self.genericInit()

    def initForm(self, formData):
        self.genericInit()
        self.ConvertirDeFormASimpleObj(formData, self.dbKeys)

    def genericInit(self):
        super().__init__("cinderella", "tarjetas")
        self.dbKeys = {
            "inputsConvert" : ["alias", "codigo"],
            "arrays" : ["trapsIp"],
            "objects" : [{"name": "alarmas", "values": ["epgID", "usada", "epgLabel", "convVolts", "offset", "slope", "tipo", "unidad"]}],
            "inputsInsertDb" : ["alias", "codigo","trapsIp"],
            "inputsSelectDb" : ["_id", "alias", "codigo","trapsIp"],
            "ObjectIds": ["_id"]
        }
        
    
    def guarda(self):
        return self._guardaDatos(self.dbKeys)

    def obtenerColeccion(self, filter1):
        return super()._obtenerColeccionObjSimple(self.dbKeys, filter1)