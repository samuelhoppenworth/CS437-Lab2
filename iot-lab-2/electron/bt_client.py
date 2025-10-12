import bluetooth
import time

host = "DC:A6:32:80:7D:87" # The address of Raspberry PI Bluetooth adapter on the server.
port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((host, port))
sock.settimeout(5.0)

try:
    while 1:
        data = sock.recv(1024)
        print("from server: ", data)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nClient exiting...")
except socket.timeout:
    print("Timed out waiting for data.")
finally:
    sock.close()


