import socket
import threading
import time
from move import move

HOST = "192.168.3.49"  # Raspberry Pi IP
PORT = 8080
SEND_INTERVAL = 0.1

def parseMsg(data):
    cmd = data.decode().split(" ")
    if cmd[0] == "mov":
        match cmd[1]:
            case "1":
                move.forward()
            case "2":
                move.backward()
            case "3":
                move.rTurn()
            case "4":
                move.lTurn()

def parse_loop(client):
    """Continuously receive and parse messages from the client."""
    try:
        while True:
            data = client.recv(1024)
            if not data:
                print("Client disconnected (parse loop)")
                break
            print("Received:", data)
            parseMsg(data)
            client.sendall(data)  # Echo back if needed
    except (ConnectionResetError, BrokenPipeError):
        print("Connection error in parse loop")
    finally:
        client.close()

def update_loop(client):
    """Periodically send status updates to the client."""
    try:
        while True:
            time.sleep(SEND_INTERVAL)
            msg = "sts "
            msg += "100 "  # TODO: replace with actual battery
            msg += str(move.orientation) + " "
            msg += "1" if move.turning else "0"
            client.sendall(msg.encode())
    except (ConnectionResetError, BrokenPipeError):
        print("Connection error in update loop")
    finally:
        client.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        client, clientInfo = s.accept()
        print("Client connected:", clientInfo)

        # Start parse and update in separate threads
        parse_thread = threading.Thread(target=parse_loop, args=(client,), daemon=True)
        update_thread = threading.Thread(target=update_loop, args=(client,), daemon=True)

        parse_thread.start()
        update_thread.start()

        # Keep main thread alive until both end
        parse_thread.join()
        update_thread.join()

        print("Client disconnected. Server shutting down.")

if __name__ == "__main__":
    main()
