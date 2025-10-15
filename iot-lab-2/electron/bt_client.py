import socket
import time
import readchar
import threading

HOST = '88:a2:9e:03:ef:5d'
PORT = 11

def recv_thread(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Server closed connection.")
                break
            print("from server:", data.decode("utf-8"))
        except Exception as e:
            print("Receive error:", e)
            break

with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as s:
    s.connect((HOST, PORT))
    print(f"Connected to server {HOST}:{PORT}")

    threading.Thread(target=recv_thread, args=(s,), daemon=True).start()

    keycode_map = {'w': 87, 's': 83, 'a': 65, 'd': 68}

    try:
        while True:
            key = readchar.readkey().lower()
            if key in keycode_map:
                keycode = keycode_map[key]
                s.sendall(str(keycode).encode())
            elif key == 'q':  # optional quit key
                print("Quitting...")
                break
    except KeyboardInterrupt:
        print("\nClient exiting...")
    finally:
        s.close()
