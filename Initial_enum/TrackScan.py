import subprocess
import re
import argparse

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, _ = process.communicate()
    return stdout.decode('utf-8')

def get_open_ports(nmap_output):
    open_ports = []
    lines = nmap_output.strip().split("\n")
    for line in lines:
        match = re.search(r"(\d+)/tcp\s+open", line)
        if match:
            open_ports.append(match.group(1))
    return ",".join(open_ports)

def main(target):
    # Initial full port scan
    print("[*] Running initial port scan...")
    initial_scan_command = f"nmap -p- --min-rate=1000 --max-retries=1 {target}"
    initial_scan_output = run_command(initial_scan_command)

    # Parsing the initial output to get the open ports
    print("[*] Parsing initial scan output...")
    open_ports = get_open_ports(initial_scan_output)
    if not open_ports:
        print("[!] No open ports found. Exiting.")
        return

    # Running a detailed scan on the open ports
    print(f"[*] Running detailed scan on open ports: {open_ports}...")
    detailed_scan_command = f"nmap -p {open_ports} -sC -sV {target}"
    detailed_scan_output = run_command(detailed_scan_command)

    print("[*] Detailed scan results:")
    print(detailed_scan_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automated Nmap Scanning')
    parser.add_argument('-t', '--target', required=True, help='Target IP address')
    args = parser.parse_args()

    main(args.target)
