from concurrent.futures import process
from operator import truth
from re import T
import socket
from threading import Thread
import time

HOST = socket.gethostbyname(socket.gethostname())  # Standard loopback interface address (localhost)
PORT_RONNIE = 30000  # Port to listen on (non-privileged ports are > 1023)
PORT_PHONE = 30001
PORT_HEARTBEAT = 30002

ronnie_connected = False
phone_connected = False

def receive_and_send_thread(input_soc, output_soc, from_phone):     # from_phone is boolean
    global ronnie_connected, phone_connected
    try:
        while True:
            input_data = input_soc.recv(1024)
            if input_data != b'':
                if from_phone:
                    input_data = input_data[2:]
                else:
                    print(input_data.decode())
                output_soc.sendall(input_data)
            else:
                if from_phone:
                    print("phone disconnected")
                    phone_connected = False
                else:
                    print("ronnie disconnected")
                    ronnie_connected = False
                break
    except:
        
        if from_phone:
            print("phone disconnected")
            phone_connected = False
        else:
            print("ronnie disconnected")
            ronnie_connected = False
        return

def heartbeat_func(hb_soc):
    try:
        while True:
            hb_soc.sendall("ping".encode())
            time.sleep(1)
    except:
        return

while True:
    print("Server IP: " + HOST)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as heartbeat_soc:
        heartbeat_soc.bind((HOST, PORT_HEARTBEAT))
        heartbeat_soc.listen()
        conn_hb, addr_hb = heartbeat_soc.accept()
        conn_hb.settimeout(5)
        heartbeat_thread = Thread(target=heartbeat_func, args=(conn_hb,))
        heartbeat_thread.start()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ronnie_soc:
            ronnie_soc.bind((HOST, PORT_RONNIE))
            print("Waiting for Ronnie...")
            ronnie_soc.listen()
            conn_ronnie, addr_ronnie = ronnie_soc.accept()
            print(f"Ronnie is at {addr_ronnie}")
            ronnie_connected = True
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as phone_soc:
                phone_soc.bind((HOST, PORT_PHONE))
                print("Waiting for phone...")
                phone_soc.listen(5)
                conn_phone, addr_phone = phone_soc.accept()
                print(f"Phone is at {addr_phone}")
                phone_connected = True
                conn_ronnie.settimeout(5)
                ronnie_to_phone_thread = Thread(target=receive_and_send_thread, args=(conn_ronnie, conn_phone, False))
                phone_to_ronnie_thread = Thread(target=receive_and_send_thread, args=(conn_phone, conn_ronnie, True))
                ronnie_to_phone_thread.start()
                phone_to_ronnie_thread.start()
                while ronnie_connected and phone_connected:
                    time.sleep(0.01)
                conn_hb.close()
                if ronnie_connected:
                    conn_ronnie.close()
                if phone_connected:
                    conn_phone.sendall("reset".encode())
                    conn_phone.close()