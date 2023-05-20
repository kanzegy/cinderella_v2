import serial, time
import csv
import pandas as pd
import numpy as np
from pysnmp.hlapi import *

class Entradas():
    def __init__(self):

        self.slope = 1000
        self.offset = 0
        self.entrada = 0
        self.lineaDatos = 0
        self.modulo = 0
        self.valoresSalida = 0
        self.epg = ""
        self.csvConf = ""
                
    def Leer_serial(self, modulo):

        serialMicro = serial.Serial('COM4',9600, timeout=1)  #establece la comunicación por el puerto serial
        time.sleep(.2)

        serialMicro.write(modulo.encode("ascii")) 
        time.sleep(.2)

        while self.lineaDatos == 0:
            self.lineaDatos = serialMicro.readline().decode("ascii", errors="ignore")
            self.lineaDatos = self.lineaDatos.split(',')  # convierte la entrada en lista

        print(self.lineaDatos)
        time.sleep(.1)

    def valor_real(self, csvConf):
        result = {'data': [], 'alertas': []}

        lineaDatos = self.lineaDatos
        for i in range(len(lineaDatos)):
            with open(csvConf, newline='') as File:
                listaEntradas = csv.reader(File)

                for rowEnt in listaEntradas:   # lee cada linea del archivo conf_entradas.csv
                    if rowEnt[1] == "si" and i == int(rowEnt[0]) and lineaDatos[i] != "END\n":
                        #verifica si la linea (alarma) esta siendo usada,
                        #de lo contrario no se calcula su valor

                        #0. epgID_	1. usada_	2. epgLabel_	3. convVolts_	4. offset_	5. slope_	6. tipo_
                        epg = str(rowEnt[0])
                        slope = float(rowEnt[5])
                        offset = float(rowEnt[4])
                        nameEnt = str(rowEnt[2])
                        valorEnt = (float(lineaDatos[i]))/float(rowEnt[3])  # row[3] es para convertir a 0-5 vcd

                        #asigna los valores de ajuste en la tabla conf_entradas.csv 
                        valor = (float(valorEnt)-float(offset))/float(slope)
                        # print("ENT_ABR: ",nameEnt," VALOR: ",valor)
                        result["data"].append({'nameEnt': nameEnt, 'valor': valor}); 
                        time.sleep(.01)

                        with open('conf_alarmas.csv', newline='') as File:
                            confAlarmas = csv.reader(File)

                            #0.nombreAlarma	 1.usado  2.textoLargo  3.limite  4.logica  5.oid_set  6.oid_clear  7.origen_  8.clave
                            for rowAlm in confAlarmas:
                                #logAnt = rowAlm[4]
                                #estadoRegistro = rowAlm[5]
                                alarma = rowAlm[0]
                                clave = rowAlm[8]

                                if rowAlm[1] == 'si' and rowAlm[7] == nameEnt:

                                    if (valor > float(rowAlm[3]) and rowAlm[4] == 'NA') or (valor < float(rowAlm[3]) and rowAlm[4] == 'NC'):
                                        estadoActual = 'ACTIVA'
                                        almOid = rowAlm[5]

                                    else:
                                        estadoActual = 'NORMAL'
                                        almOid = rowAlm[6]

                                    df = pd.read_csv('registroAlm.csv')
                                    time.sleep(.1)

                                    # 0.clave  1.alarmaReg  2.estatusRegistro  3.horaReg
                                    estadoRegistro = df.loc[int(clave),'2.estatusRegistro']
                                    if estadoRegistro != estadoActual:
                                        # print(rowAlm[0],' cambio a ',estadoActual)
                                        result["alertas"].append(rowAlm[0],' cambio a ',estadoActual); 

                                        self.enviarTraps(df,estadoActual,alarma,clave,almOid,'100.124.64.237')
                                        time.sleep(.1)
                                        self.enviarTraps(df,estadoActual,alarma,clave,almOid,'10.128.41.5')
                                        time.sleep(.1)
        return result

    def enviarTraps(self,df,estadoActual,alarma,clave,almOid,snmpServidor):
        # https://www.geeksforgeeks.org/update-column-value-of-csv-in-python/
        df.loc[int(clave), '2.estatusRegistro'] = estadoActual
        df.to_csv('registroAlm.csv',index = False)
        #--------------------------------------
        iterator = sendNotification(
            SnmpEngine(),
            CommunityData('public', mpModel=0),
            UdpTransportTarget((snmpServidor, 162)),
            ContextData(),
            'trap',
            NotificationType(
                ObjectIdentity(almOid)
            ).addVarBinds(
                ('1.3.6.1.6.3.1.1.4.3.0', '1.3.6.1.4.1.20408.4.1.1.2'),
                ('1.3.6.1.2.1.1.1.0', OctetString(alarma))
            ).loadMibs(
                'SNMPv2-MIB'
            )
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:
            print(errorIndication)

    def obtener_entradas():
        # *****   objeto verEntradas para ver entradas analógicas
        verControl = Entradas()
        verControl.Leer_serial('#200\r')  # ejecuta la función Leer_serial de la clase Entradas vinculada al objeto verEntrada
        result = verControl.valor_real('conf_entradas.csv')   # instancia la funcion valor real al objeto ver entrada.

        return result



    def obtener_Control():
        # *****   objeto verControl para ver entradas del control de AA
        verControl = Entradas()
        verControl.Leer_serial('#400\r')
        result = verControl.valor_real('conf_ctlaa.csv')   # instancia la funcion valor real al objeto ver entrada.

        return result
