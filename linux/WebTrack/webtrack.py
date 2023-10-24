import json
import subprocess
import argparse

# Function to run FFUF
def run_ffuf(target, wordlist, is_subdomain=False):
    fuzz_param = 'FUZZ'
    if is_subdomain:
        fuzz_param = 'FUZZ.' + target
    else:
        fuzz_param = target + '/FUZZ'
    subprocess.run(f"ffuf -u http://{fuzz_param} -w {wordlist}", shell=True)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Web Enumeration Tool')
parser.add_argument('-i', '--ip', required=True, help='Target IP Address')
parser.add_argument('-d', '--dns', required=True, help='Target DNS Name')
args = parser.parse_args()

# Read config file
with open('config.json', 'r') as f:
    config = json.load(f)

# Run FFUF for directory bruteforcing using multiple wordlists
for directory_wordlist in config['directory_wordlists']:
    run_ffuf(args.ip, directory_wordlist)

# Run FFUF for subdomain bruteforcing using multiple wordlists
for subdomain_wordlist in config['subdomain_wordlists']:
    run_ffuf(args.dns, subdomain_wordlist, is_subdomain=True)
