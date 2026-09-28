#!/usr/bin/env python3
"""
Publica Hervor: commit + push a GitHub (inhumario/hervor) y redeploy en EasyPanel (travelia/hervor).

Uso:
  python3 scripts/deploy_easypanel.py            # primera vez: repo, servicio, dominio, DNS y deploy
  python3 scripts/deploy_easypanel.py deploy     # lo normal tras cambiar contenido: push + redeploy

El push a main NO redespliega solo: hay que ejecutar esto. Token de GitHub en Infisical `github`
(cuenta de usuario inhumario: repos nuevos por POST /user/repos), EasyPanel en easypanel.env,
DNS con el token de Cloudflare (solo permisos de DNS).
"""
import json
import os
import secrets
import string
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.config/aromas"))
from infisical_get import get_secrets  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
PROJECT, SERVICE, REPO = "travelia", "hervor", "inhumario/hervor"
HOST = "hervor.inhumario.com"
ZONA_INHUMARIO = "1e0d6a02e9584299ad53dba4bdb79699"
IP_EASYPANEL = "46.202.168.58"


def cargar_env(ruta):
    valores = {}
    for linea in open(os.path.expanduser(ruta)):
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            k, v = linea.split("=", 1)
            valores[k] = v.strip('"')
    return valores


EP = cargar_env("~/.config/aromas/easypanel.env")


def http(url, payload=None, headers=None, method="POST"):
    req = urllib.request.Request(url, data=json.dumps(payload).encode() if payload is not None else None,
                                 headers={"Content-Type": "application/json", **(headers or {})}, method=method)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read() or b"{}")


def trpc(procedure, payload):
    return http(f"{EP['EASYPANEL_API_BASE']}/{procedure}", {"json": payload},
                {"Authorization": f"Bearer {EP['EASYPANEL_TOKEN']}"})


def git(*args):
    return subprocess.run(["git", "-C", str(RAIZ), *args], check=True, capture_output=True, text=True).stdout


def token_github():
    s = get_secrets("github")
    return next(v for k, v in s.items() if "TOKEN" in k.upper())


def push():
    tok = token_github()
    if not (RAIZ / ".git").exists():
        git("init", "-b", "main")
    git("-c", "user.name=Mario Cuadrado", "-c", "user.email=hola@inhumario.com", "add", "-A")
    if git("status", "--porcelain").strip():
        msg = sys.argv[2] if len(sys.argv) > 2 else "Actualiza contenido"
        git("-c", "user.name=Mario Cuadrado", "-c", "user.email=hola@inhumario.com", "commit", "-q", "-m", msg)
    git("push", "-q", f"https://x-access-token:{tok}@github.com/{REPO}.git", "main")
    print("git: push OK")


def preparar():
    tok = token_github()
    try:
        http("https://api.github.com/user/repos",
             {"name": "hervor", "private": False, "description": "Hervor — café y té en casa (web estática)"},
             {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"})
        print("github: repo creado")
    except urllib.error.HTTPError as e:
        if e.code != 422:
            raise
        print("github: el repo ya existía")
    push()

    try:
        trpc("services.app.createService", {"projectName": PROJECT, "serviceName": SERVICE})
        print("easypanel: servicio creado")
    except urllib.error.HTTPError:
        print("easypanel: el servicio ya existía")
    trpc("services.app.updateSourceGit", {"projectName": PROJECT, "serviceName": SERVICE,
                                          "repo": f"https://github.com/{REPO}.git", "ref": "main", "path": "/"})
    trpc("services.app.updateBuild", {"projectName": PROJECT, "serviceName": SERVICE,
                                      "build": {"type": "dockerfile", "file": "Dockerfile"}})
    # DNS antes que el dominio: si EasyPanel pide el certificado sin DNS, se queda con el autofirmado
    cf = get_secrets("cloudflare")["CLOUDFLARE_API_TOKEN"]
    base = f"https://api.cloudflare.com/client/v4/zones/{ZONA_INHUMARIO}/dns_records"
    auth = {"Authorization": f"Bearer {cf}"}
    existentes = http(f"{base}?name={HOST}", headers=auth, method="GET")["result"]
    cuerpo = {"type": "A", "name": "hervor", "content": IP_EASYPANEL, "proxied": False, "ttl": 300,
              "comment": "Hervor (web de afiliados) en EasyPanel travelia/hervor"}
    if existentes:
        http(f"{base}/{existentes[0]['id']}", cuerpo, auth, "PUT")
    else:
        http(base, cuerpo, auth)
    print(f"dns: {HOST} -> {IP_EASYPANEL}")
    dominios = trpc("domains.listDomains", {"projectName": PROJECT, "serviceName": SERVICE})["json"]
    if not any(d.get("host") == HOST for d in dominios):
        trpc("domains.createDomain", {
            "id": "c" + "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(24)),
            "destinationType": "service", "host": HOST, "https": True, "path": "/", "middlewares": [],
            "certificateResolver": "letsencrypt", "wildcard": False,
            "serviceDestination": {"protocol": "http", "port": 80, "projectName": PROJECT, "serviceName": SERVICE}})
        print(f"easypanel: dominio {HOST}")



def main():
    if len(sys.argv) > 1 and sys.argv[1] == "deploy":
        push()
    else:
        preparar()
    trpc("services.app.deployService", {"projectName": PROJECT, "serviceName": SERVICE})
    print("easypanel: deploy lanzado")


if __name__ == "__main__":
    main()
