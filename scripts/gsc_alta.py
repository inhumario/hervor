#!/usr/bin/env python3
"""Alta de puntodeinfusion.inhumario.com en Search Console (propiedad de dominio verificada por TXT) y envío del sitemap.
Token OAuth de Mario en ~/.config/aromas/google_token.json (scopes webmasters + siteverification)."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
sys.path.insert(0, str(Path.home() / '.config/aromas'))
from infisical_get import get_secrets

HOST = 'puntodeinfusion.inhumario.com'; SITE = f'sc-domain:{HOST}'; ZONA = '1e0d6a02e9584299ad53dba4bdb79699'
c = Credentials.from_authorized_user_info(json.load(open(Path.home() / '.config/aromas/google_token.json'))); c.refresh(Request())

def g(url, data=None, method=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data is not None else None, method=method,
                                 headers={'Authorization': 'Bearer ' + c.token, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        b = r.read(); return json.loads(b) if b else {}

tok = g('https://www.googleapis.com/siteVerification/v1/token',
        {'site': {'type': 'INET_DOMAIN', 'identifier': HOST}, 'verificationMethod': 'DNS_TXT'})['token']
cf = get_secrets('cloudflare')['CLOUDFLARE_API_TOKEN']
def cfapi(m, p, d=None):
    req = urllib.request.Request('https://api.cloudflare.com/client/v4/zones/' + ZONA + p, method=m,
                                 data=json.dumps(d).encode() if d else None, headers={'Authorization': 'Bearer ' + cf, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r: return json.load(r)['result']
if not any(r['content'].strip('"') == tok for r in cfapi('GET', f'/dns_records?type=TXT&name={HOST}')):
    cfapi('POST', '/dns_records', {'type': 'TXT', 'name': HOST.split('.')[0], 'content': tok, 'ttl': 300, 'comment': 'Verificación Search Console Punto de Infusión'})
    print('TXT creado; esperando propagación'); time.sleep(45)
for intento in range(6):
    try:
        g('https://www.googleapis.com/siteVerification/v1/webResource?verificationMethod=DNS_TXT',
          {'site': {'type': 'INET_DOMAIN', 'identifier': HOST}}); print('verificado'); break
    except urllib.error.HTTPError as e:
        print('aún no verifica', e.code); time.sleep(30)
q = urllib.parse.quote(SITE, safe='')
g(f'https://www.googleapis.com/webmasters/v3/sites/{q}', method='PUT'); print('propiedad añadida:', SITE)
g(f'https://www.googleapis.com/webmasters/v3/sites/{q}/sitemaps/' + urllib.parse.quote(f'https://{HOST}/sitemap.xml', safe=''), method='PUT')
print('sitemap enviado')
