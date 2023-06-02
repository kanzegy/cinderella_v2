import serial, time
from pysnmp.hlapi import *
from py.classes.dbController import dbController
from py.classes.alarmas import Alarma
from bson.timestamp import Timestamp
from datetime import datetime
import datetime as dt



class ConexionTarjeta():
    def __init__(self, codigo):
        db = dbController("cinderella").getDb()
        self.tarjetaDb = db["tarjetas"].find_one({"codigo" : codigo})
        self.alarmasDb = Alarma().obtenerColeccion({"tarjeta_id" : self.tarjetaDb["_id"], "usado" : "si"})
        self.codigo = codigo + "\r"
        self.lineaDatos = 0

    
    def obtenerDatosDeTarjetaFisica(self, conexion_real = False):

        if conexion_real == False:
            self.lineaDatos = ["121", "32", "73", "64", "55", "76","74", "86", "49","104","101","112"]
            return
            
        serialMicro = serial.Serial(self.tarjetaDb["nombrePuerto"],9600, timeout=1)  #establece la comunicación por el puerto serial
        time.sleep(.2)

        serialMicro.write(self.codigo.encode("ascii")) 
        time.sleep(.2)

        while self.lineaDatos == 0:
            self.lineaDatos = serialMicro.readline().decode("ascii", errors="ignore")
            self.lineaDatos = self.lineaDatos.split(',')  # convierte la entrada en lista
        time.sleep(.1)
        

    def cumpleCondiciones(self, limite, logica, valor):
        result = {
            "status": "OK",
            "limite_NA" : False,
            "limite_NC" : False
        }
        if logica == 'NA'and valor > limite:
            result["limite_NA"] = True
            result["status"] = "ALERT"

        if logica == 'NC' and valor < limite:
            result["limite_NC"] = True
            result["status"] = "ALERT"
        
        return result

    def chequeoDeAlarmas(self):
        db = dbController("cinderella").getDb()
        result = {'infoAlarmas': [], 'Alertas': []}
        
        for i, datoSp in enumerate(self.lineaDatos):
            for alarma in self.alarmasDb:
                if i == int(alarma["epgID"]) and datoSp != "END\n":
                    slope = float(alarma["slope"])
                    offset = float(alarma["offset"])
                    valorEnt = (float(datoSp))/float(alarma["convVolts"])

                    valor = (float(valorEnt)-float(offset))/float(slope)
                    alarma_conf = db["conf_alarmas"].find_one({"usado" : "si", "origen" : alarma["epgLabel"]})
                    result["infoAlarmas"].append({'epgLabel': alarma["epgLabel"], 'valor': valor, "unidad" : alarma["unidad"], "texto_largo" : alarma_conf["texto_largo"]})
                    
                    if self.cumpleCondiciones(float(alarma_conf["limite"]), alarma_conf["logica"], valor):
                        statusActual = 'ACTIVA'
                        almOid = alarma_conf["oid_set"]

                    else:
                        statusActual = 'NORMAL'
                        almOid = alarma_conf["oid_clear"]

                    statusAnterior = db["registro_alarmas"].find_one({"clave" : alarma_conf["clave"]})
                    if statusAnterior:
                        if statusAnterior["estatusRegistro"] != statusActual:
                            for trapIp in self.tarjetaDb["trapsIp"]:
                                self.enviaTrap(alarma, almOid, trapIp)
                                
                        db["registro_alarmas"].update_one({"clave" : alarma_conf["clave"]} , {"$set" : {"estatusRegistro" : statusActual}})
                    else:
                        objInsert = {
                            "clave" : alarma_conf["clave"],
                            "alarmaReg":alarma_conf["nombreAlarma"],
                            "estatusRegistro":statusActual,
                            "texto_largo": alarma_conf["texto_largo"],
                            "horaReg": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                        }
                        result["Alertas"].append(objInsert)
                        db["registro_alarmas"].insert_one(objInsert)

        return result

    def enviaTrap(self, alarma, almOid, snmpServidor):
        iterator = sendNotification(
            SnmpEngine(), 
            CommunityData('public', mpModel=0),
            UdpTransportTarget((snmpServidor, 162)),
		    ContextData(),
		    'trap',
		    NotificationType(ObjectIdentity(almOid)).addVarBinds(
                ('1.3.6.1.6.3.1.1.4.3.0', '1.3.6.1.4.1.20408.4.1.1.2'),
                ('1.3.6.1.2.1.1.1.0', OctetString(alarma))).loadMibs('SNMPv2-MIB'))

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(errorIndication)
