import socket
import threading
import subprocess
import json
import sys
import os

HOST = '127.0.0.1'  # localhost
PORT = 65431        # arbitrary non-privileged port
HOME_DIRS = ["/home"]
if os.path.exists("/valr"):
    HOME_DIRS.append("/valr")

def get_home_users():
    """Return users, defined by folders at `HOME_DIRS`."""
    user_names = []
    for home_dir in HOME_DIRS:
        user_names += [name for name in os.listdir(home_dir) if os.path.isdir(os.path.join(home_dir, name))]
    return list(set(user_names)) # remove dups

def get_cpu_info(user_names): 
    """
    Return cpu info as a dictionary looking like:
    ```
    [
        {
            "userName": # user name
            "cpuUsage": # %CPU usage
            "memUsage": # ?? MEM usage
        }
    ]
    ```
    """
    cpu_info = {}
    for line_no, line in enumerate(os.popen("top -n 1 -b")): 
        if line_no > 6: 
            x = line.split() 
            user_name = x[1]
            if user_name not in user_names: 
                continue
            cpu_use = float(x[8])
            mem_use = float(x[9])
            if user_name not in cpu_info:
                cpu_info[user_name] = {
                    "cpuUsage": 0,
                    "memUsage": 0
                }
            cpu_info[user_name]["cpuUsage"] += cpu_use
            cpu_info[user_name]["memUsage"] += mem_use
    return [{"userName": name, **entry} for name, entry in cpu_info.items() if float(entry["cpuUsage"]) > 0 or float(entry["memUsage"]) > 0]

def get_gpu_info():
    """
    Returns two things:
      - Per-user GPU usage:
        [
            {
                "userName": # user name 
                "gpusUsed": [{
                    "gpuID": # uuid for gpu
                    "gpuName": # human readable gpu name
                    "gpuMemUsage": # %mem I think
                }]
            }
        ]
      - Per-GPU cumulative usage: 
        [
            {
                "gpuID": # uuid for gpu
                "gpuName": # human readable gpu name
                "gpuCumulativeUsage": # total %mem
            }
        ]
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
        cmd = ['ps', '-o', 'user=', '-p', str(pid)]
        try:
            user_name = subprocess.run(cmd,
                                        capture_output=True, text=True).stdout.strip()
            if not user_name:
                continue
            if (entry := user_gpu_usage.get(user_name)) is None:
                user_gpu_usage[user_name] = entry = {}
            if gpu not in entry:
                entry[gpu] = 0
            entry[gpu] += mem
            if gpu not in gpu_total_usage:
                gpu_total_usage[gpu] = 0
            gpu_total_usage[gpu] += mem
        except Exception as e:
            print("bad process command ({}): {}".format(cmd, e), file=sys.stderr)
            continue

    per_user_output = [{'userName': user, 'gpusUsed': [{'gpuID': gpu, 'gpuName': gpu_names[gpu], 'gpuMemUsage': mem} for gpu, mem in jobs.items()]} for user, jobs in user_gpu_usage.items()]
    per_gpu_output = [{'gpuID': gpu, 'gpuName': gpu_names[gpu], 'gpuCumulativeUsage': mem} for gpu, mem in gpu_total_usage.items()]
    return per_user_output, per_gpu_output


def get_disk_usage():
    """Returns disk usage of all partitions with `T` in them."""
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
    """Do handler work."""
    print(f"[+] Connected by {addr}", file=sys.stderr)
    with conn:
        home_users = get_home_users()
        cpu_info = get_cpu_info(home_users)
        per_user_nvidia, per_gpu_nvidia = get_gpu_info()
        df_info = get_disk_usage()
        payload = json.dumps({
            "diskInfo": df_info,
            "cpuInfo": cpu_info,
            "gpuInfoPerUser": per_user_nvidia,
            "gpuInfoPerNvidia": per_gpu_nvidia
        })
        conn.sendall(payload.encode())
    print(f"[-] Disconnected from {addr}", file=sys.stderr)

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
