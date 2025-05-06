import socket
import threading

HOST = '127.0.0.1'  # localhost
PORT = 65432        # arbitrary non-privileged port

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)  # Echo back the received data
    print(f"[-] Disconnected from {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Echo server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    main()
