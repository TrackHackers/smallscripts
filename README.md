# smallscripts
A repository for small scripts to help speed up the Hacking process in HTB

This Repository will be divided into Windows and Linux hacking scripts.

## Windows

### smb_tester.py
This script is a simple python tool that will spray easy passwords for users on smb shares. the ones we regularly see on HackTheBox.

when to use this tool?
you have: 
- valid usernames
- an open port 445 with smb shares available
- no passwords

this tool will try empty passwords as well as the same password as the username.

```bash
python3 smbmap_tester.py -f users.txt -d MANAGER -H manager.htb
```

## Linux

### WebTrack: Web Enumeration Tool by Trackhackers
WebTrack is a Python-based web enumeration tool designed to automate the process of web service enumeration. It uses FFUF (Fuzz Faster U Fool) under the hood to perform directory and subdomain bruteforcing. The tool is highly configurable, allowing for multiple wordlists and providing real-time progress monitoring.

#### Prerequisites
Python 3.x
FFUF
tqdm Python library (pip install tqdm)

#### Usage
1. Configuration: Place your wordlists' paths in the config.json file. Multiple wordlists can be specified.
```json
{
  "directory_wordlists": ["/path/to/directory-wordlist1.txt", "/path/to/directory-wordlist2.txt"],
  "subdomain_wordlists": ["/path/to/subdomain-wordlist.txt"]
}
```
2. Command Line Arguments: The tool requires the target IP and DNS name to be passed as command-line arguments.
```bash
python main.py -i 192.168.1.1 -d example.com
```
3. Run: Execute the script. A progress bar will display the status in real-time.
4. 
