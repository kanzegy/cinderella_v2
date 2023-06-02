from flask import Flask, request, jsonify, render_template, redirect, copy_current_request_context
from flask_socketio import SocketIO, emit
from py.classes.entradas import Entradas
from py.classes.dbController import dbController
from py.classes.tarjetas import Tarjeta
from py.classes.alarmas import Alarma
from py.classes.alarmasconfig import AlarmaConfig
from py.classes.conexionPuertoSerial import ConexionTarjeta
from pymongo import MongoClient
from bson import ObjectId
import serial.tools.list_ports
import threading
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config["secret"] = "secret!123"
socketio = SocketIO(app, cors_allowed_origins = "*")

#threading ================================================================================

def ejecutar_cada_5_segundos():
    while True:
        result = obtenerDatosDeTarjetasYConexiones() 
        
        print("pasamo por el 5 segundo: ")
        socketio.emit("listenerData", result)   
        time.sleep(5)

threading.Thread(target=ejecutar_cada_5_segundos).start()



# @app.route("/<var_par>")
# def WParameter(var_par):
#     return render_template("temp_var.html", temp_var = var_par)

# @app.route("/vistaDatos")
# def vistaDatos():
#     return render_template("vistaDatos.html")

# @app.get("/getEntradas")
# def getEntradas():
#     resultEnt = Entradas.obtener_entradas()
#     return jsonify(resultEnt)

# @app.get("/getControl")
# def getControl():
#     resultCont = Entradas.obtener_Control()
#     return jsonify(resultCont)



@socketio.on("message")
def handle_message(message):
    print("recivido: " + message)
    emit("chat", message, broadcast=True)


@app.route("/simpleChat")
def simpleChat():
    return render_template("simpleChat.html")

@app.route("/")
def inicio():
    return redirect("/s_tarjeta200", code=302)

# #Conexion Puerto Serial ===============================================================
@app.get("/ObtenerDatosDeTarjetas")
def ObtenerDatosDeTarjetas():
    result = obtenerDatosDeTarjetasYConexiones()
    return jsonify(result)

#Bases de datos ========================================================================
@app.route("/GuardaTarjeta", methods=['POST'])
def GuardaTarjeta():
    tObj = Tarjeta()
    tObj.initForm(request.form)
    tObj.guarda()

    for alarma in tObj.dbObject["alarmas"]:
        alObj = Alarma()
        alObj.initForm(alarma)
        alObj.dbObject["tarjeta_id"] = tObj.dbObject["_id"]
        alObj.guarda()
    
    return redirect("/Conexiones", code=302)

@app.route("/guardaConfAlarma", methods=['POST'])
def guardaConfAlarma():
    confAl = AlarmaConfig()
    confAl.initForm(request.form)
    confAl.guarda()

    return jsonify({"success": "true", "req" : request.form})
    
#vistas ================================================================================
@app.route("/AgregarTarjeta")
def AgregarTarjeta():
    
    result = []
    puertos_disponibles = serial.tools.list_ports.comports()
    for puerto in puertos_disponibles:
        result.append(puerto.device)

    return render_template("configuracionTarjeta.html", puertos =  result)
    
@app.route("/configAlarmas")
def configAlarmas():
    confAl = AlarmaConfig()
    result = confAl.obtenerColeccion({})
    return render_template("configAlarmas.html", configAlarmas = result)

@app.route("/Conexiones")
def Conexiones():
    result = obtenerDatosDeTarjetasYConexiones()    
    return render_template("Conexiones.html", TarjetaData = result)

@app.route("/s_tarjeta200")
def s_tarjeta200():
    result = obtenerDatosDeTarjetasYConexiones()  
    return render_template("simple_tarjeta200.html", TarjetaData = result)


def obtenerDatosDeTarjetasYConexiones():
    result = []
    alObj = Alarma()
    taObj = Tarjeta()

    tarjetas = taObj.obtenerColeccion({})

    for tarjeta in tarjetas:
        conexionObj = ConexionTarjeta(tarjeta["codigo"])
        conexionObj.obtenerDatosDeTarjetaFisica()
        res = conexionObj.chequeoDeAlarmas()
        tarjeta["alarmas"] = alObj.obtenerColeccion({"tarjeta_id" : ObjectId(tarjeta["_id"])})
        res["tarjeta"] = tarjeta
        result.append(res)

    return result


#==========================================================================================

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
    socketio.run(app, host="localhost", port=5000)

    

