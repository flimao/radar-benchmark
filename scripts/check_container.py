"""HTTP smoke check plus persistent-volume recreation check. Requires Docker Compose."""
from getpass import getpass
from http.cookiejar import CookieJar
import json
import re
import subprocess
import urllib.request
import urllib.parse
import uuid


def main():
    port=input('Published port [8051]: ').strip() or '8051'
    base='http://127.0.0.1:'+str(int(port))
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    assert json.load(opener.open(base+'/health',timeout=10))=={'status':'ok'}
    assert opener.open(base+'/export',timeout=10).geturl().endswith('/login'), 'Anonymous export was not denied'
    page=opener.open(base+'/login',timeout=10).read().decode()
    csrf=re.search(r'name="csrf" value="([^"]+)"',page).group(1)
    body=urllib.parse.urlencode({'csrf':csrf,'password':getpass('Shared RADAR password: ')}).encode()
    assert not opener.open(base+'/login',body,timeout=10).geturl().endswith('/login'), 'Login failed'
    assert opener.open(base+'/export',timeout=10).headers.get_content_type()=='text/csv'
    marker='container-check-'+uuid.uuid4().hex
    code=f"from pathlib import Path; p=Path('/var/lib/radar/evidence/{marker}'); p.write_text('{marker}')"
    subprocess.run(['docker','compose','exec','-T','radar','python','-c',code],check=True)
    subprocess.run(['docker','compose','up','-d','--force-recreate','--wait','radar'],check=True)
    code=f"from pathlib import Path; p=Path('/var/lib/radar/evidence/{marker}'); assert p.read_text()=='{marker}'; p.unlink()"
    subprocess.run(['docker','compose','exec','-T','radar','python','-c',code],check=True)
    assert opener.open(base+'/export',timeout=10).headers.get_content_type()=='text/csv', 'Session did not survive recreation'
    print('Passed: health, authentication, CSV export, volume and session persistence.')


if __name__=='__main__':
    main()
