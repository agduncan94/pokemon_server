import socket
import threading
import subprocess
import json

HOST = '127.0.0.1'  # localhost
PORT = 65431        # arbitrary non-privileged port

def _():
    ...

def get_disk_usage():
    lines = subprocess.run(['df','--si'], capture_output=True, text=True).stdout.splitlines()
    tot=0
    usage=0
    for line in lines:
        vals = line.split()
        partition_of_interest=False
        for v in vals:
            if 'T' in v: 
                partition_of_interest=True
        if partition_of_interest:
            #print(vals[1],vals[4])
            tot=tot+float(vals[1][:-1])
            usage=usage+ 0.01*float(vals[4][:-1])*float(vals[1][:-1])
    
    return {
        "usedDiskSize": usage,
        "totalDiskSize": tot
    }
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
