import socket
import threading
import subprocess
import json
import os

HOST = '127.0.0.1'  # localhost
PORT = 65431        # arbitrary non-privileged port

def list_home_users():
    """Return a list of usernames in /home."""
    try:
        return sorted(entry for entry in os.listdir('/home') if os.path.isdir(os.path.join('/home', entry)))
    except Exception as e:
        return [f"Error: {e}"]

def get_gpu_info():
    """
    Returns:
      - Per-user GPU usage: list of dicts {username, [{gpuID, gpuMemUsage}]}
      - Per-GPU cumulative usage: list of dicts [{gpuID, gpuCumulativeUsage}]
    """
    result = subprocess.run(
        ['nvidia-smi', '--query-compute-apps=pid,gpu_uuid,gpu_name,used_memory', '--format=csv,noheader,nounits'],
        capture_output=True,
        text=True,
        check=True
    )
    lines = result.stdout.strip().splitlines()

    # Mapping: pid -> (gpu_uuid, used_memory)
    pid_gpu_mem = {}
    gpu_names = {}
    for line in lines:
        parts = [x.strip() for x in line.split(',')]
        if len(parts) != 4:
            continue
        pid, gpu_uuid, gpu_name, mem = parts
        gpu_names[gpu_uuid] = gpu_name
        pid_gpu_mem[int(pid)] = (gpu_uuid, int(mem))

    # Get usernames from PIDs
    user_gpu_usage = {}  # username -> list of (gpuID, mem)
    gpu_total_usage = {} # gpuID -> total mem

    for pid, (gpu, mem) in pid_gpu_mem.items():
        try:
            username = subprocess.run(['ps', '-o', 'user=', '-p', str(pid)],
                                        capture_output=True, text=True).stdout.strip()
            if username:
                if username not in user_gpu_usage:
                    user_gpu_usage[username] = []
                user_gpu_usage[username].append({'gpuID': gpu, 'gpuName': gpu_names[gpu], 'gpuMemUsage': mem})
                if gpu not in gpu_total_usage:
                    gpu_total_usage[gpu] = 0
                gpu_total_usage[gpu] += mem
        except Exception:
            continue

    per_user_output = [{'username': user, 'jobs': jobs} for user, jobs in user_gpu_usage.items()]
    per_gpu_output = [{'gpuID': gpu, 'gpuName': gpu_names[gpu], 'gpuCumulativeUsage': mem} for gpu, mem in gpu_total_usage.items()]
    return per_user_output, per_gpu_output


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
        per_user_nvidia, per_gpu_nvidia = get_gpu_info()
        df_info = get_disk_usage()
        payload = json.dumps({
            "diskInfo": df_info,
            "gpuInfoPerUser": per_user_nvidia,
            "gpuInfoPerNvidia": per_gpu_nvidia
        })
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
