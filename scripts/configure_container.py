"""Create local container secrets without printing passwords or overwriting .env."""
from getpass import getpass
from pathlib import Path
import os
import secrets
from werkzeug.security import generate_password_hash


def main():
    target=Path('.env')
    if target.exists():
        raise SystemExit('.env already exists; edit it explicitly instead of overwriting.')
    password=getpass('Shared RADAR password: ')
    if not password:
        raise SystemExit('Password cannot be empty.')
    if getpass('Confirm password: ') != password:
        raise SystemExit('Passwords do not match.')
    content=(f"RADAR_PASSWORD_HASH='{generate_password_hash(password)}'\n"
             f"RADAR_SESSION_SECRET='{secrets.token_hex(32)}'\n"
             'RADAR_HTTPS=0\nRADAR_PORT=8051\n')
    descriptor=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(descriptor,'w') as stream:
        stream.write(content)
    print('Created .env for local HTTP on port 8051. Use RADAR_HTTPS=1 behind HTTPS.')


if __name__=='__main__':
    main()
