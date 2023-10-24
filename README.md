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

