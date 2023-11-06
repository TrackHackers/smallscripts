import subprocess
from concurrent.futures import ThreadPoolExecutor
import argparse

def run_smbmap(username, domain, host):
    # Test for empty password
    print(f"\nTesting user {username} with empty password")
    subprocess.run(["smbmap", "-u", username, "-p", "", "-d", domain, "-H", host])
    
    # Test for password same as username
    print(f"\nTesting user {username} with password as username")
    subprocess.run(["smbmap", "-u", username, "-p", username.lower(), "-d", domain, "-H", host])

    #Test for weak Passwords
    print(f"\nTesting user {username} with password \"password\"")
    subprocess.run(["smbmap", "-u", username, "-p", "password", "-d", domain, "-H", host])


def main():
    parser = argparse.ArgumentParser(description='Run smbmap against a list of users.')
    parser.add_argument('-f', '--file', required=True, help='Path to the file containing usernames.')
    parser.add_argument('-d', '--domain', required=True, help='Domain name.')
    parser.add_argument('-H', '--host', required=True, help='Host IP address.')
    
    args = parser.parse_args()
    
    with open(args.file, 'r') as f:
        usernames = f.read().splitlines()
        
    with ThreadPoolExecutor() as executor:
        for username in usernames:
            executor.submit(run_smbmap, username, args.domain, args.host)

if __name__ == "__main__":
    main()
