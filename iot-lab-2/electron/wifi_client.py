import socket
import time

HOST = "10.0.0.218"  # Raspberry Pi IP
PORT = 65432          # Same port as server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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
    except KeyboardInterrupt:
        print("\nClient exiting...")
    except socket.timeout:
        print("Timed out waiting for data.")
    finally:
        s.close()
