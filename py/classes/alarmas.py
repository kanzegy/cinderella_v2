from py.classes.parent import Parent

class Alarma(Parent):
    def __init__(self):
        self.genericInit()

    def initForm(self, formData):
        self.genericInit()
        self.ConvertirDeFormASimpleObj(formData, self.dbKeys)

    def genericInit(self):
        super().__init__("cinderella", "alarmas")
        self.dbKeys = {
            "inputsConvert" : ["tarjeta_id","epgID", "usada", "epgLabel", "convVolts", "offset", "slope", "tipo", "unidad"],
            "arrays" : [],
            "objects" : [],
            "inputsInsertDb" : ["tarjeta_id", "epgID", "usada", "epgLabel", "convVolts", "offset", "slope", "tipo", "unidad"],
            "inputsSelectDb" : ["tarjeta_id", "_id", "epgID", "usada", "epgLabel", "convVolts", "offset", "slope", "tipo", "unidad"],
            "ObjectIds": ["tarjeta_id", "_id"]
        }
        
    
    def guarda(self):
        self._guardaDatos(self.dbKeys)

    def obtenerColeccion(self, filter1):
        return super()._obtenerColeccionObjSimple(self.dbKeys, filter1)
    