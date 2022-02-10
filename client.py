import socket
from threading import Thread

HOST = '127.0.0.1'
PORT = 9009

def rceMsg(sock):
    while True:
        try :
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode())

        except:
            pass

def runChat():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
        sock.connect((HOST,PORT))
        t= Thread(target=rceMsg,args=(sock,))
        t.daemon = True
        t.start()

        while True:
            msg = input()
            if msg == '/quit':
                sock.send(msg.encode())
                break

            sock.send(msg.encode())
runChat()