import json
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import socket
import time

# Function to run FFUF
def run_ffuf(target, wordlist, is_subdomain=False):
    try:
        fuzz_param = 'FUZZ'
        if is_subdomain:
            fuzz_param = 'FUZZ.' + target
        else:
            fuzz_param = target + '/FUZZ'
            
        # Execute FFUF command and capture the output
        completed_process = subprocess.run(f"ffuf -u http://{fuzz_param} -w {wordlist} -of csv -o temp.csv", shell=True, capture_output=True, text=True)
        
        # Read FFUF output and filter it (for DNS)
        if is_subdomain:
            with open('temp.csv', 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    subdomain = line.split(',')[1].strip()
                    try:
                        resolved_ip = socket.gethostbyname(subdomain)
                        if not resolved_ip.startswith('192.168'):  # Filter out local/reserved IPs
                            print(f"Legitimate subdomain found: {subdomain}")
                    except:
                        pass
        return completed_process.returncode
    except subprocess.TimeoutExpired:
        print(f"FFUF timed out for target: {target}, wordlist: {wordlist}")
        return 1
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

# Prepare list of tasks
tasks = []
for directory_wordlist in config['directory_wordlists']:
    tasks.append((args.ip, directory_wordlist, False))

for subdomain_wordlist in config['subdomain_wordlists']:
    tasks.append((args.dns, subdomain_wordlist, True))

# Run FFUF concurrently and monitor progress
with ThreadPoolExecutor() as executor:
    results = list(tqdm(executor.map(lambda p: run_ffuf(*p), tasks), total=len(tasks)))

# Output results (could be extended to multiple formats)
print(f"Completed. {results.count(0)} tasks succeeded, {results.count(1)} tasks failed.")

