import subprocess
import re
import argparse
import platform
import socket

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
    return run_command(f"nmap -p- {'-Pn' if pn_flag else ''} {target}", "full TCP scan", verbose)

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

def edit_hosts_file(target, boxname):
    try:
        host_ip = socket.gethostbyname(target)
        existing_entry = None

        # Read /etc/hosts file to check for existing entries
        with open('/etc/hosts', 'r') as hosts_file:
            lines = hosts_file.readlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == host_ip and parts[-1] == boxname:
                    existing_entry = line.strip()

        # Check if the existing entry already matches the correct format
        if existing_entry == f"{host_ip}\t{boxname}":
            print(f"[*] {boxname} is already resolving to the correct IP: {host_ip}")
        else:
            # Remove any existing entry for the target before adding the new entry
            if existing_entry:
                sudo_remove_command = f"sudo sed -i '/{target}/d' /etc/hosts"
                subprocess.run(sudo_remove_command, shell=True, check=True)
            
            # Add the new entry to /etc/hosts using sudo if the IP isn't present
            if not existing_entry:
                sudo_command = f"echo '{host_ip}\t{boxname}' | sudo tee -a /etc/hosts"
                subprocess.run(sudo_command, shell=True, check=True)
                print(f"[*] Added {boxname} to /etc/hosts associated with IP {host_ip}")
            else:
                print(f"[*] The IP {host_ip} for {target} is already in /etc/hosts with a different entry")

    except socket.gaierror:
        print("[!] Error: Unable to resolve the target IP to add to /etc/hosts")

def check_os(target):
    try:
        # Ping with a packet size of 32 bytes for Windows
        windows_ping = subprocess.Popen(["ping", "-n", "1", "-l", "32", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        windows_ping.communicate(timeout=5)  # Adjust the timeout as needed

        if windows_ping.returncode == 0:
            print(f"[*] Target OS identified as: Windows")
            return 'windows'
    except subprocess.TimeoutExpired:
        pass

    try:
        # Ping with a packet size of 64 bytes for Linux
        linux_ping = subprocess.Popen(["ping", "-c", "1", "-s", "64", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        linux_ping.communicate(timeout=5)  # Adjust the timeout as needed

        if linux_ping.returncode == 0:
            print(f"[*] Target OS identified as: Linux")
            return 'linux'
    except subprocess.TimeoutExpired:
        pass

    print("[*] Unable to determine the target OS")
    return 'unknown'

def main(target, pn_flag, verbose, boxname):
 # OS identification
    current_os = platform.system()
    print(f"[*] Running on {current_os}")

    # DNS resolution setup
    if current_os.lower() == 'linux':
        edit_hosts_file(target, boxname)
    else:
        print("[!] OS not supported for DNS resolution setup")

    os_type = check_os(target)

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
    parser.add_argument('-b', '--boxname', required=True, help='Specify boxname for local DNS resolution')
    args = parser.parse_args()

    main(args.target, args.no_ping, args.verbose, args.boxname)
