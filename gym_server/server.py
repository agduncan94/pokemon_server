import socket
import threading
import subprocess
import json

HOST = '127.0.0.1'  # localhost
PORT = 65432        # arbitrary non-privileged port

def get_disk_usage():
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')[1:]  # skip header
    usage_info = []

    for line in lines:
        parts = line.split()
        if len(parts) >= 6:
            partition, size, used = parts[0], parts[1], parts[2]
            usage_info.append({'partition': partition, 'total': size, 'used': used})
    return usage_info

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")
    with conn:
        # top_info = get_top_info()
        # nvidia_info = get_nvidia_info()
        df_info = get_disk_usage()
        payload = json.dumps(df_info)
        conn.sendall(payload.encode())
    print(f"[-] Disconnected from {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Gym server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    main()
