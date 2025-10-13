import socket
import time
import readchar 

HOST = "DC:A6:32:80:7D:87" # The address of Raspberry PI Bluetooth adapter on the server.
PORT = 1

with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
    s.connect((HOST, PORT))
    s.settimeout(5.0)
    print(f"Connected to server {HOST}:{PORT}")

    try:
        while True:
            data = s.recv(1024)
            if not data:
                print("Server closed connection.")
                break
            print("from server:", data.decode("utf-8"))
            time.sleep(0.1)
            key = readchar.readkey()
            key = key.lower()
            s.sendall(key)

    except KeyboardInterrupt:
        print("\nClient exiting...")
    except socket.timeout:
        print("Timed out waiting for data.")
    finally:
        s.close()