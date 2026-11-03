#!/usr/bin/env python3
"""Detecta llaves, contraseñas y archivos sensibles ANTES de que lleguen a GitHub.

Modos:
    python adminExe/escanear_secretos.py --staged     # lo que vas a commitear (lo usa el hook pre-commit)
    python adminExe/escanear_secretos.py --todo       # todo lo que git subiría (versionado + nuevo no ignorado)
    python adminExe/escanear_secretos.py --historial  # cada línea agregada en TODA la historia de git

Sale con código 1 si encuentra algo. Los valores se muestran enmascarados.
Para aceptar una línea a propósito (p. ej. contraseña de prueba), agrega al final:  secretos: permitido
Solo biblioteca estándar.
"""
import argparse
import re
import subprocess
import sys
from pathlib import PurePosixPath

PERMITIDO = "secretos: permitido"

# Archivos que nunca deben versionarse (se comparan por nombre o patrón).
ARCHIVOS_PROHIBIDOS = [
    (re.compile(r"(^|/)\.env(\.[^/]*)?$"), "archivo .env con variables reales"),
    (re.compile(r"\.(pem|key|p12|pfx|jks|keystore|ppk)$", re.I), "llave o certificado privado"),
    (re.compile(r"(^|/)id_(rsa|dsa|ecdsa|ed25519)$"), "llave SSH privada"),
    (re.compile(r"\.sqlite3?$|\.db$", re.I), "base de datos (puede tener usuarios y contraseñas)"),
    (re.compile(r"(^|/)(SuperUser|User)\.txt$", re.I), "notas de credenciales"),
    (re.compile(r"(^|/)(credentials|secrets?)(\.[a-z]+)?$", re.I), "archivo de credenciales"),
]
EXCEPCIONES_ARCHIVO = re.compile(r"(^|/)\.env\.example$")

REGLAS = [
    ("Llave privada", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("AWS Access Key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Token de GitHub", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b")),
    ("Llave de Anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("Llave de OpenAI", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}")),
    ("Llave de Google", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Token de Slack", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("Llave de Stripe", re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{20,}")),
    ("URL con contraseña", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@'\"]+:([^\s/@'\"]{3,})@[^\s'\"]+", re.I)),
    ("SECRET_KEY de Django", re.compile(
        r"SECRET_KEY\s*[:=]\s*['\"]?(?!django-insecure)(?!cambiar)(?!ci-solo)([A-Za-z0-9!@#$%^&*()_+\-=]{40,})")),
    ("Contraseña escrita en código", re.compile(
        r"(?i)\b(?:password|passwd|contrase(?:ñ|n)a|db_password|clave)\b['\"]?\s*[:=]\s*(?:env\.\w+\([^)]*default\s*=\s*)?"
        r"['\"]([^'\"\s]{6,})['\"]")),
]
# Valores que son marcadores obvios, no secretos reales.
MARCADORES = re.compile(r"(?i)^(changeme|cambiar.*|tu[-_].*|your[-_].*|example.*|ejemplo.*|x{3,}|\*{3,}|<.*>|\$\{.*\}|placeholder)$")

EXTENSIONES_BINARIAS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".exe", ".zip", ".whl", ".deb", ".gz",
                        ".pdf", ".woff", ".woff2", ".ttf", ".pyc", ".mp4", ".sqlite3"}


def git(*args, binario=False):
    r = subprocess.run(["git", *args], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} falló: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binario else r.stdout.decode("utf-8", errors="replace")


def enmascarar(v):
    v = str(v)
    return v[:3] + "…" + "*" * 6 if len(v) > 6 else "******"


def revisar_texto(ruta, texto, hallazgos, numeros=None):
    lineas = texto.splitlines()
    for i, linea in enumerate(lineas):
        if PERMITIDO in linea:
            continue
        for nombre, regla in REGLAS:
            m = regla.search(linea)
            if not m:
                continue
            valor = m.group(1) if m.groups() else m.group(0)
            if MARCADORES.match(valor or ""):
                continue
            n = numeros[i] if numeros else i + 1
            hallazgos.append((ruta, n, nombre, enmascarar(valor)))


def revisar_nombre(ruta, hallazgos, etiqueta=None):
    if EXCEPCIONES_ARCHIVO.search(ruta):
        return
    for regla, motivo in ARCHIVOS_PROHIBIDOS:
        if regla.search(ruta):
            hallazgos.append((etiqueta or ruta, 0, "Archivo sensible", motivo))
            return


def es_binario(ruta, datos):
    return PurePosixPath(ruta).suffix.lower() in EXTENSIONES_BINARIAS or b"\0" in datos[:8000]


def modo_archivos(rutas, leer):
    hallazgos = []
    for ruta in rutas:
        revisar_nombre(ruta, hallazgos)
        datos = leer(ruta)
        if datos is None or es_binario(ruta, datos):
            continue
        revisar_texto(ruta, datos.decode("utf-8", errors="replace"), hallazgos)
    return hallazgos


def modo_historial():
    """Revisa solo las líneas AGREGADAS en cada commit (lo que realmente llegó al historial)."""
    hallazgos, ruta, linea_nueva = [], None, 0
    salida = git("log", "--all", "-p", "--no-color", "--unified=0", "--format=COMMIT %h")
    commit = "?"
    for linea in salida.splitlines():
        if linea.startswith("COMMIT "):
            commit = linea.split()[1]
        elif linea.startswith("+++ "):
            ruta = linea[6:] if linea.startswith("+++ b/") else None
            if ruta:
                revisar_nombre(ruta, hallazgos, etiqueta=f"{ruta} (commit {commit})")
        elif linea.startswith("@@"):
            m = re.search(r"\+(\d+)", linea)
            linea_nueva = int(m.group(1)) if m else 0
        elif linea.startswith("+") and ruta and PurePosixPath(ruta).suffix.lower() not in EXTENSIONES_BINARIAS:
            revisar_texto(f"{ruta} (commit {commit})", linea[1:], hallazgos, numeros=[linea_nueva])
            linea_nueva += 1
    return hallazgos


def main(argv=None):
    for flujo in (sys.stdout, sys.stderr):  # la consola de Windows usa cp1252
        if hasattr(flujo, 'reconfigure'):
            flujo.reconfigure(encoding='utf-8', errors='replace')
    p = argparse.ArgumentParser(description="Busca secretos antes de subir a GitHub.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--staged", action="store_true", help="archivos preparados para commit (predeterminado)")
    g.add_argument("--todo", action="store_true", help="todo lo que se subiría al repositorio")
    g.add_argument("--historial", action="store_true", help="toda la historia de git")
    a = p.parse_args(argv)

    if a.historial:
        hallazgos = modo_historial()
        alcance = "historial completo"
    elif a.todo:
        rutas = [r for r in git("ls-files", "-co", "--exclude-standard", "-z").split("\0") if r]
        hallazgos = modo_archivos(rutas, lambda r: _leer_disco(r))
        alcance = f"{len(rutas)} archivos"
    else:
        rutas = [r for r in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0") if r]
        hallazgos = modo_archivos(rutas, lambda r: git("show", f":{r}", binario=True))
        alcance = f"{len(rutas)} archivos preparados"

    if not hallazgos:
        print(f"✓ Sin secretos detectados ({alcance}).")
        return 0
    print(f"✗ Se encontraron {len(hallazgos)} posibles secretos ({alcance}):\n")
    for ruta, n, regla, detalle in hallazgos:
        print(f"  {ruta}{f':{n}' if n else ''}  →  {regla}: {detalle}")
    print("\nQuita el secreto (muévelo a .env) o, si es intencional y seguro, agrega al final de la línea:"
          f"  # {PERMITIDO}")
    return 1


def _leer_disco(ruta):
    try:
        with open(ruta, "rb") as f:
            return f.read()
    except OSError:
        return None


if __name__ == "__main__":
    sys.exit(main())
