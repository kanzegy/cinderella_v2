import serial.tools.list_ports

puertos_disponibles = serial.tools.list_ports.comports()

print("Puertos disponibles:")
for puerto in puertos_disponibles:
    print(puerto.device)