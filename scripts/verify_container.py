"""Disposable production-image check; never uses existing containers or app data."""
import argparse
from http.cookiejar import CookieJar
from pathlib import Path
import json
import re
import secrets
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request
import uuid
from werkzeug.security import generate_password_hash


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--docker',default='docker')
    args=parser.parse_args()
    name='radar-verification-'+uuid.uuid4().hex[:12]
    volume=name+'-data'
    def docker(*arguments):
        return subprocess.check_output([args.docker,*arguments],text=True).strip()
    def ready():
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            if docker('inspect','--format','{{.State.Health.Status}}',name)=='healthy': return
            time.sleep(1)
        raise RuntimeError('Container did not become healthy: '+docker('logs',name))
    with tempfile.TemporaryDirectory(prefix='radar-container-check-') as directory:
        password=secrets.token_urlsafe(32)
        envfile=Path(directory)/'runtime.env'
        envfile.write_text('RADAR_PASSWORD_HASH='+generate_password_hash(password)+'\nRADAR_SESSION_SECRET='+secrets.token_hex(32)+'\nRADAR_HTTPS=0\n')
        envfile.chmod(0o600)
        try:
            def start():
                docker('run','-d','--name',name,'--env-file',str(envfile),'-p','127.0.0.1::8050','-v',volume+':/var/lib/radar','radar:local')
                ready()
            start()
            port=docker('port',name,'8050/tcp').split(':')[-1]
            base='http://127.0.0.1:'+port
            opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
            assert json.load(opener.open(base+'/health',timeout=10))=={'status':'ok'}
            assert opener.open(base+'/export',timeout=10).geturl().endswith('/login')
            page=opener.open(base+'/login',timeout=10).read().decode()
            csrf=re.search(r'name="csrf" value="([^"]+)"',page).group(1)
            wrong=urllib.parse.urlencode({'csrf':csrf,'password':'invalid'}).encode()
            assert opener.open(base+'/login',wrong,timeout=10).geturl().endswith('/login')
            body=urllib.parse.urlencode({'csrf':csrf,'password':password}).encode()
            assert not opener.open(base+'/login',body,timeout=10).geturl().endswith('/login')
            exported=opener.open(base+'/export',timeout=10).read()
            assert b'TotalEnergies' in exported
            assert b'Equinor' not in exported
            assert opener.open(base+'/assets/style.css',timeout=10).status==200
            assert opener.open(base+'/_dash-layout',timeout=10).status==200
            code="from radar import data; data.preserve(b'%PDF-verification','probe.pdf','TotalEnergies','2025Q4','https://example.org/report','p.1')"
            docker('exec',name,'python','-c',code)
            docker('rm','-f',name)
            start()
            code="from radar import data; import hashlib; h=hashlib.sha256(b'%PDF-verification').hexdigest(); assert (data.ROOT/'data/original'/h).read_bytes()==b'%PDF-verification'; assert len(data.documents())==1; assert 'TotalEnergies' in set(data.facts().company)"
            docker('exec',name,'python','-c',code)
            print('PASS: production startup, health, authentication, static assets, Dash layout, active-peer CSV, original document and DuckDB persistence after container recreation.')
        finally:
            subprocess.run([args.docker,'rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            subprocess.run([args.docker,'volume','rm',volume],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)


if __name__=='__main__': main()
