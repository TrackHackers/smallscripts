import json
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import socket
import time

# Function to check if port is open
def is_port_open(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        sock.connect((ip, port))
    except socket.error:
        return False
    return True

# Function to run FFUF
def run_ffuf(target, wordlist, is_subdomain=False, is_vhost=False):
    try:
        fuzz_param = 'FUZZ'
        if is_subdomain:
            fuzz_param = 'FUZZ.' + target
        elif is_vhost:
            fuzz_param = target
        else:
            fuzz_param = target + '/FUZZ'
            
        cmd = f"ffuf -u http://{fuzz_param} -w {wordlist}"
        if is_vhost:
            cmd += " -H 'Host: FUZZ'"
        
        completed_process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return completed_process.returncode
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1

# Parse command-line arguments
parser = argparse.ArgumentParser(description='WebTrack: Web Enumeration Tool by TrackHackers')
parser.add_argument('-i', '--ip', required=True, help='Target IP Address')
parser.add_argument('-d', '--dns', required=True, help='Target DNS Name')
args = parser.parse_args()

# Read config file
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Config file not found. Exiting.")
    exit(1)

# Check if port 80 is open, otherwise check other common HTTP ports
http_ports = [80, 8080, 8000, 8888]
open_port = None
for port in http_ports:
    if is_port_open(args.ip, port):
        open_port = port
        break

if open_port is None:
    print("No open HTTP ports found. Exiting.")
    exit(1)

# Run Nikto scan
print(f"Running Nikto scan on port {open_port}...")
subprocess.run(f"nikto -h {args.ip} -p {open_port}", shell=True)

# Fingerprint using curl
print("Fingerprinting the server...")
subprocess.run(f"curl -I http://{args.ip}:{open_port}", shell=True)

# Prepare list of tasks for FFUF
tasks = []
for directory_wordlist in config['directory_wordlists']:
    tasks.append((args.ip, directory_wordlist, False, False))

for subdomain_wordlist in config['subdomain_wordlists']:
    tasks.append((args.dns, subdomain_wordlist, True, False))

# Adding VHOST bruteforcing task
tasks.append((args.ip, config['vhost_wordlist'], False, True))

# Run FFUF concurrently and monitor progress
with ThreadPoolExecutor() as executor:
    results = list(tqdm(executor.map(lambda p: run_ffuf(*p), tasks), total=len(tasks)))

# Output results
print(f"Completed. {results.count(0)} tasks succeeded, {results.count(1)} tasks failed.")
