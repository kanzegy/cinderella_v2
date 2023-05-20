from py.classes.parent import Parent

class AlarmaConfig(Parent):
    def __init__(self):
        self.genericInit()

    def initForm(self, formData):
        self.genericInit()
        self.ConvertirDeFormASimpleObj(formData, self.dbKeys)

    def genericInit(self):
        super().__init__("cinderella", "conf_alarmas")
        self.dbKeys = {
            "inputsConvert" : ["_id","nombreAlarma", "usado", "texto_largo", "limite", "logica", "oid_set", "oid_clear", "origen", "clave"],
            "arrays" : [],
            "objects" : [],
            "inputsInsertDb" : ["nombreAlarma", "usado", "texto_largo", "limite", "logica", "oid_set", "oid_clear", "origen", "clave"],
            "inputsSelectDb" : ["_id","nombreAlarma", "usado", "texto_largo", "limite", "logica", "oid_set", "oid_clear", "origen", "clave"],
            "ObjectIds": ["_id"]
        }
        
    
    def guarda(self):
        self._guardaDatos(self.dbKeys)

    def obtenerColeccion(self, filter1):
        return super()._obtenerColeccionObjSimple(self.dbKeys, filter1)
    