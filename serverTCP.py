from datetime import datetime
import socket
import os
import threading
import time
import hashlib

SERVER_HOST = "192.168.10.27"
SERVER_PORT = 5001
BUFFER_SIZE = 4096


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((SERVER_HOST, SERVER_PORT))

lock = threading.Lock()

s.listen(25)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

def handle_client(conn,addr,filename, barrera, nombreLog):
    exito = False
    hasher = hashlib.sha256()
    print(f"[+] {addr} is connected.")
    while True:
        received = conn.recv(BUFFER_SIZE).decode()
        print(received)
        if not received:
            break
        if received=="Listo":
            barrera.wait()
            with open(filename, "rb") as f:
                start = time.time()
                while True:
                    bytes_read = f.read(BUFFER_SIZE)           
                    if not bytes_read:
                        print("Archivo enviado")
                        conn.send(hasher.digest())
                        integridad = conn.recv(BUFFER_SIZE).decode()
                        if integridad == "Correcto":
                            exito = True
                        break
                    #print("Se esta enviando el archivo")
                    hasher.update(bytes_read)
                    conn.sendall(bytes_read)
                end = time.time()
            tiempo = end-start
            log(addr, exito, tiempo, nombreLog) 


def log(cliente, exito, tiempo, nombreLog):
    texto = ["Conexion del cliente: " + str(cliente) + "\n", "\tEstado de exito: " + str(exito) + "\n", "\tTiempo de transferencia: " + str(tiempo) + "\n"]
    lock.acquire()
    with open("Logs/"+nombreLog, "a") as f:
        f.writelines(texto)
        f.close()
    lock.release()

def main():
    nombreLog = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    numClientes = input("Numero clientes\n")
    filename = input("Nombre del archivo a enviar\n")
    filesize = os.path.getsize(filename)
    barrera = threading.Barrier(int(numClientes))
    texto = ["Archivo enviado: " + filename + "\n", "Tamaño del archivo: " + str(filesize) + "\n"]
    with open("Logs/"+nombreLog, "w") as f:
        f.writelines(texto)
        f.close()
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, filename, barrera, nombreLog))
        thread.start()

if __name__ == "__main__":
    main()
