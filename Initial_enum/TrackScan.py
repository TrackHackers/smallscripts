import subprocess
import re
import argparse

def run_command(command, title, verbose):
    ports = {}
    print(f"[*] Running {title}...")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    print(f"[*] {title} results:")
    while True:
        output = process.stdout.readline()
        if output:
            line = output.strip()
            if verbose:
                print(f"    {line}")
            match = re.search(r"(\d+)/(tcp|udp)\s+(\w+)", line)
            if match:
                port, protocol, state = match.groups()
                ports[f"{port}/{protocol}"] = state
        if process.poll() is not None:
            break

    if ports:
        print("PORT       STATE")
        for port, state in ports.items():
            print(f"{port.ljust(9)} {state}")

    return ",".join([port.split("/")[0] for port in ports.keys() if ports[port] == 'open'])

def quick_scan(target, pn_flag, verbose):
    return run_command(f"nmap -F {'-Pn' if pn_flag else ''} {target}", "quick scan", verbose)

def full_tcp_scan(target, pn_flag, verbose):
    return run_command(f"nmap -p- --min-rate=1000 --max-retries=1 {'-Pn' if pn_flag else ''} {target}", "full TCP scan", verbose)

def full_udp_scan(target, pn_flag, verbose):
    return run_command(f"nmap -sU --top-ports 20 {'-Pn' if pn_flag else ''} {target}", "full UDP scan", verbose)

def detailed_scan(target, open_ports, pn_flag, verbose):
    print(f"[*] Running detailed scan on open ports: {open_ports}...")
    detailed_scan_command = f"nmap -p {open_ports} -sC -sV {'-Pn' if pn_flag else ''} {target}"
    process = subprocess.Popen(detailed_scan_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    
    print("[*] Detailed scan results:")
    while True:
        output = process.stdout.readline()
        if output:
            line = output.strip()
            print(f"    {line}")
        if process.poll() is not None:
            break


def main(target, pn_flag, verbose):
    quick_ports = quick_scan(target, pn_flag, verbose)
    
    if quick_ports:
        detailed_scan(target, quick_ports, pn_flag, verbose)
    
    full_tcp_ports = full_tcp_scan(target, pn_flag, verbose)
    full_udp_ports = full_udp_scan(target, pn_flag, verbose)
    
    if full_tcp_ports:
        detailed_scan(target, full_tcp_ports, pn_flag, verbose)
    
    if full_udp_ports:
        print(f"[*] Full UDP scan found open ports: {full_udp_ports}")
        # Add additional actions for UDP ports if needed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automated Nmap Scanning')
    parser.add_argument('-t', '--target', required=True, help='Target IP address')
    parser.add_argument('-Pn', '--no-ping', action='store_true', help='No ping, treats all hosts as online')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    main(args.target, args.no_ping, args.verbose)
