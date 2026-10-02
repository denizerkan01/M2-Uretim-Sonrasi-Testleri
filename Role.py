import serial.tools.list_ports
import time
import general_functions as fnc

def Role():

    ports = list(serial.tools.list_ports.comports())

    target_port = fnc.find_port("CH340", ports)

    #print(ports)
    #print(target_port)

    hex_open = "A0 01 01 A2"
    hex_close = "A0 01 00 A1"


    data_to_send_open = bytes.fromhex(hex_open)
    data_to_send_close = bytes.fromhex(hex_close)

    with serial.Serial(target_port, 9600) as ser:
        ser.write(data_to_send_open)
        #print(f"Sent {len(data_to_send_open)} bytes successfully.")
        time.sleep(1)
        ser.write(data_to_send_close)
        #print(f"Sent {len(data_to_send_close)} bytes successfully.")
