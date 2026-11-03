#!/usr/bin/env python3
"""Descarga y empaqueta las herramientas externas del proyecto para Windows y Linux.

Lee adminExe/requirements-tools.txt y, para cada plataforma pedida:

  * windows -> adminExe/dist/toolsForWindows/   (tailwindcss.exe, uv.exe, uvx.exe)
  * linux   -> adminExe/dist/toolsForLinux/     (bin/ + paquete mathmaster-tools_*.deb)

Seguridad: cada descarga se verifica contra el SHA-256 del manifiesto (y, para PyPI,
también contra el hash que publica PyPI). Si no coincide, el archivo se borra y se aborta.

Solo usa la biblioteca estándar (Python >= 3.8): funciona antes de instalar el
Python del proyecto. El .deb se arma en Python puro, así que también se puede
generar desde Windows.

Uso:
    python adminExe/descargar_tools.py                    # plataforma actual
    python adminExe/descargar_tools.py --plataforma todas  # Windows + Linux
    python adminExe/descargar_tools.py --python 3.12       # además instala Python con uv
    python adminExe/descargar_tools.py --verificar         # solo comprueba lo ya descargado
"""
import argparse
import gzip
import hashlib
import io
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import urllib.request
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
MANIFIESTO = RAIZ / "requirements-tools.txt"
DIST = RAIZ / "dist"
CARPETAS = {"windows": "toolsForWindows", "linux": "toolsForLinux"}
PAQUETE_DEB = "mathmaster-tools"
PREFIJO_DEB = "opt/mathmaster-tools"
MANTENEDOR = "Ruben Andres Gomez Molina <RubenAndresGome@users.noreply.github.com>"
AGENTE = "mathmaster-descargar-tools/1.0"


# ----------------------------------------------------------------------------- utilidades
def log(msg, nivel="·"):
    print(f" {nivel} {msg}", flush=True)


def sha256_de(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def plataforma_actual():
    s = platform.system().lower()
    if s == "windows":
        return "windows"
    if s == "linux":
        return "linux"
    sys.exit(f"Plataforma no soportada: {platform.system()} (solo Windows y Linux x86_64).")


class ErrorHerramienta(Exception):
    pass


# ----------------------------------------------------------------------------- manifiesto
def leer_manifiesto(ruta=MANIFIESTO):
    """Devuelve (herramientas, deb_depends). herramientas: lista de dicts."""
    herramientas, depends = [], ""
    for n, linea in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        linea = linea.split("#", 1)[0].strip()
        if not linea:
            continue
        partes = [p.strip() for p in linea.split(";")]
        if partes[0] == "deb-depends":
            if len(partes) != 3:
                raise ErrorHerramienta(f"línea {n}: deb-depends ; linux ; paquete1, paquete2")
            depends = partes[2]
            continue
        if len(partes) != 4 or "==" not in partes[0] or not partes[3].startswith("sha256="):
            raise ErrorHerramienta(f"línea {n}: formato esperado 'nombre==versión ; plataforma ; fuente ; sha256=…'")
        nombre, version = partes[0].split("==", 1)
        sha = partes[3][len("sha256="):].lower()
        if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
            raise ErrorHerramienta(f"línea {n}: sha256 inválido")
        if partes[1] not in CARPETAS:
            raise ErrorHerramienta(f"línea {n}: plataforma '{partes[1]}' (usa windows o linux)")
        fuente = partes[2]
        if not (fuente.startswith("https://") or fuente.startswith("pypi:")):
            raise ErrorHerramienta(f"línea {n}: la fuente debe ser https:// o pypi:")
        herramientas.append({"nombre": nombre.strip(), "version": version.strip(), "plataforma": partes[1],
                             "fuente": fuente, "sha256": sha})
    return herramientas, depends


# ----------------------------------------------------------------------------- descargas
def _abrir(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    return urllib.request.urlopen(req, timeout=60)


def resolver_pypi(h):
    """pypi:<archivo> -> URL real, comprobando que PyPI publica el mismo hash."""
    archivo = h["fuente"][len("pypi:"):]
    with _abrir(f"https://pypi.org/pypi/{h['nombre']}/{h['version']}/json") as r:
        datos = json.load(r)
    for f in datos.get("urls", []):
        if f["filename"] == archivo:
            if f["digests"]["sha256"] != h["sha256"]:
                raise ErrorHerramienta(f"{archivo}: el hash del manifiesto no coincide con el que publica PyPI")
            return f["url"]
    raise ErrorHerramienta(f"{archivo} no existe en PyPI para {h['nombre']}=={h['version']}")


def descargar(h, cache):
    """Descarga (o reutiliza de la caché) y verifica el SHA-256. Devuelve la ruta."""
    cache.mkdir(parents=True, exist_ok=True)
    destino = cache / h["sha256"]
    if destino.exists() and sha256_de(destino) == h["sha256"]:
        log(f"{h['nombre']} {h['version']} ({h['plataforma']}): en caché, hash correcto", "✓")
        return destino
    url = resolver_pypi(h) if h["fuente"].startswith("pypi:") else h["fuente"]
    temporal = destino.with_suffix(".parcial")
    log(f"Descargando {h['nombre']} {h['version']} ({h['plataforma']})…")
    inicio, total = time.time(), 0
    with _abrir(url) as r, open(temporal, "wb") as f:
        for bloque in iter(lambda: r.read(1 << 20), b""):
            f.write(bloque)
            total += len(bloque)
    obtenido = sha256_de(temporal)
    if obtenido != h["sha256"]:
        temporal.unlink()
        raise ErrorHerramienta(f"{h['nombre']} ({h['plataforma']}): SHA-256 NO coincide. "
                               f"Esperado {h['sha256'][:16]}…, obtenido {obtenido[:16]}…. Archivo descartado.")
    temporal.replace(destino)
    log(f"{total / 1e6:.1f} MB en {time.time() - inicio:.1f}s · SHA-256 verificado", "✓")
    return destino


def extraer(h, archivo, carpeta_bin):
    """Copia el binario (o los scripts de una wheel) a carpeta_bin. Devuelve los nombres creados."""
    carpeta_bin.mkdir(parents=True, exist_ok=True)
    exe = ".exe" if h["plataforma"] == "windows" else ""
    creados = []
    if h["fuente"].startswith("pypi:"):
        with zipfile.ZipFile(archivo) as z:
            for miembro in z.namelist():
                partes = miembro.split("/")
                if len(partes) == 3 and partes[0].endswith(".data") and partes[1] == "scripts" and partes[2]:
                    nombre = partes[2]
                    with z.open(miembro) as src, open(carpeta_bin / nombre, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    creados.append(nombre)
        if not creados:
            raise ErrorHerramienta(f"{archivo.name}: la wheel no contiene ejecutables en *.data/scripts/")
    else:
        nombre = h["nombre"] + exe
        shutil.copyfile(archivo, carpeta_bin / nombre)
        creados.append(nombre)
    if h["plataforma"] == "linux":
        for n in creados:
            p = carpeta_bin / n
            p.chmod(p.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return creados


# ----------------------------------------------------------------------------- .deb (Python puro)
def _ar_miembro(nombre, datos, mtime):
    cab = (f"{nombre:<16}{mtime:<12}{0:<6}{0:<6}{'100644':<8}{len(datos):<10}`\n").encode("ascii")
    assert len(cab) == 60
    return cab + datos + (b"\n" if len(datos) % 2 else b"")


def _tar_gz(entradas, mtime):
    """entradas: lista de (ruta_en_tar, bytes|None para directorio, modo)."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=mtime) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tar:
            for ruta, datos, modo in entradas:
                info = tarfile.TarInfo(ruta)
                info.mtime, info.uid, info.gid, info.uname, info.gname = mtime, 0, 0, "root", "root"
                info.mode = modo
                if datos is None:
                    info.type = tarfile.DIRTYPE
                    tar.addfile(info)
                else:
                    info.size = len(datos)
                    tar.addfile(info, io.BytesIO(datos))
    return buf.getvalue()


def construir_deb(carpeta_bin, versiones, depends, salida):
    """Arma mathmaster-tools_<ver>_amd64.deb con los binarios en /opt/mathmaster-tools/bin."""
    mtime = int(os.environ.get("SOURCE_DATE_EPOCH", "1700000000"))  # reproducible
    version = "1.0+" + ".".join(f"{n}{v}" for n, v in sorted(versiones.items())) + "-1"
    binarios = sorted(p for p in carpeta_bin.iterdir() if p.is_file())
    perfil = (f'# Añadido por {PAQUETE_DEB}: herramientas del proyecto MathMaster\n'
              f'case ":$PATH:" in *":/{PREFIJO_DEB}/bin:"*) ;; *) PATH="$PATH:/{PREFIJO_DEB}/bin" ;; esac\n'
              'export PATH\n').encode()
    data = [("./", None, 0o755), ("./opt/", None, 0o755), (f"./{PREFIJO_DEB}/", None, 0o755),
            (f"./{PREFIJO_DEB}/bin/", None, 0o755)]
    data += [(f"./{PREFIJO_DEB}/bin/{b.name}", b.read_bytes(), 0o755) for b in binarios]
    data += [("./etc/", None, 0o755), ("./etc/profile.d/", None, 0o755),
             (f"./etc/profile.d/{PAQUETE_DEB}.sh", perfil, 0o644)]
    md5 = "".join(f"{hashlib.md5(d).hexdigest()}  {r[2:]}\n" for r, d, _ in data if d is not None)
    kib = sum(len(d) for _, d, _ in data if d is not None) // 1024 + 1
    control = (f"Package: {PAQUETE_DEB}\nVersion: {version}\nArchitecture: amd64\nMaintainer: {MANTENEDOR}\n"
               f"Installed-Size: {kib}\nDepends: {depends}\nSection: devel\nPriority: optional\n"
               "Homepage: https://github.com/RubenAndresGome/ProyectoPaginasProduction\n"
               "Description: Herramientas de desarrollo del proyecto MathMaster (Django)\n"
               f" Incluye {', '.join(f'{n} {v}' for n, v in sorted(versiones.items()))} en /{PREFIJO_DEB}/bin\n"
               " y lo agrega al PATH mediante /etc/profile.d.\n").encode()
    control_tar = _tar_gz([("./", None, 0o755), ("./control", control, 0o644), ("./md5sums", md5.encode(), 0o644),
                           ("./conffiles", f"/etc/profile.d/{PAQUETE_DEB}.sh\n".encode(), 0o644)], mtime)
    data_tar = _tar_gz(data, mtime)
    salida.parent.mkdir(parents=True, exist_ok=True)
    nombre = salida / f"{PAQUETE_DEB}_{version}_amd64.deb"
    for viejo in salida.glob(f"{PAQUETE_DEB}_*.deb"):
        viejo.unlink()
    with open(nombre, "wb") as f:
        f.write(b"!<arch>\n")
        f.write(_ar_miembro("debian-binary", b"2.0\n", mtime))
        f.write(_ar_miembro("control.tar.gz", control_tar, mtime))
        f.write(_ar_miembro("data.tar.gz", data_tar, mtime))
    return nombre


# ----------------------------------------------------------------------------- orquestación
def preparar(plat, herramientas, depends, dist, con_deb=True):
    destino = dist / CARPETAS[plat]
    carpeta_bin = destino / "bin" if plat == "linux" else destino
    cache = dist / ".cache"
    log(f"Plataforma {plat} → {destino}", "▶")
    instaladas, versiones = [], {}
    for h in [x for x in herramientas if x["plataforma"] == plat]:
        archivo = descargar(h, cache)
        for nombre in extraer(h, archivo, carpeta_bin):
            instaladas.append({"archivo": nombre, "herramienta": h["nombre"], "version": h["version"],
                               "sha256": sha256_de(carpeta_bin / nombre)})
        versiones[h["nombre"]] = h["version"]
    if plat == "linux" and con_deb:
        deb = construir_deb(carpeta_bin, versiones, depends, destino)
        log(f"Paquete: {deb.name}  (sudo apt install ./{deb.name})", "✓")
        instaladas.append({"archivo": deb.name, "herramienta": "paquete-deb", "version": deb.name.split("_")[1],
                           "sha256": sha256_de(deb)})
    sumas = "".join(f"{i['sha256']}  {i['archivo']}\n" for i in instaladas)
    (destino / "SHA256SUMS.txt").write_text(sumas, encoding="utf-8")
    (destino / "herramientas.json").write_text(json.dumps(
        {"plataforma": plat, "generado": time.strftime("%Y-%m-%dT%H:%M:%S"), "herramientas": instaladas},
        indent=2, ensure_ascii=False), encoding="utf-8")
    return destino, carpeta_bin


def verificar(plat, dist):
    destino = dist / CARPETAS[plat]
    sumas = destino / "SHA256SUMS.txt"
    if not sumas.exists():
        log(f"{plat}: no hay herramientas descargadas todavía", "✗")
        return False
    ok = True
    for linea in sumas.read_text(encoding="utf-8").splitlines():
        sha, nombre = linea.split("  ", 1)
        ruta = destino / ("bin/" + nombre if plat == "linux" and not nombre.endswith(".deb") else nombre)
        bien = ruta.exists() and sha256_de(ruta) == sha
        ok &= bien
        log(f"{plat}/{nombre}: {'correcto' if bien else 'FALTA o ALTERADO'}", "✓" if bien else "✗")
    return ok


def instalar_python(carpeta_bin, version, plat):
    uv = carpeta_bin / ("uv.exe" if plat == "windows" else "uv")
    destino = carpeta_bin.parent / "python" if plat == "linux" else carpeta_bin / "python"
    env = dict(os.environ, UV_PYTHON_INSTALL_DIR=str(destino), UV_CACHE_DIR=str(DIST / ".cache" / "uv"))
    log(f"Instalando Python {version} con uv en {destino}…", "▶")
    subprocess.run([str(uv), "python", "install", version], check=True, env=env)


def main(argv=None):
    for flujo in (sys.stdout, sys.stderr):  # la consola de Windows usa cp1252
        if hasattr(flujo, 'reconfigure'):
            flujo.reconfigure(encoding='utf-8', errors='replace')
    p = argparse.ArgumentParser(description="Descarga las herramientas del proyecto (Windows y Linux).")
    p.add_argument("--plataforma", choices=["auto", "windows", "linux", "todas"], default="auto")
    p.add_argument("--manifiesto", type=Path, default=MANIFIESTO)
    p.add_argument("--dist", type=Path, default=DIST)
    p.add_argument("--sin-deb", action="store_true", help="en Linux, no construir el .deb")
    p.add_argument("--python", metavar="VERSION", help="instalar también Python con uv (solo plataforma actual)")
    p.add_argument("--verificar", action="store_true", help="solo comprobar lo ya descargado")
    a = p.parse_args(argv)

    plats = ["windows", "linux"] if a.plataforma == "todas" else (
        [plataforma_actual()] if a.plataforma == "auto" else [a.plataforma])
    if a.verificar:
        return 0 if all([verificar(x, a.dist) for x in plats]) else 1
    try:
        herramientas, depends = leer_manifiesto(a.manifiesto)
        for plat in plats:
            _, carpeta_bin = preparar(plat, herramientas, depends, a.dist, con_deb=not a.sin_deb)
            if a.python:
                if plat != plataforma_actual():
                    log(f"--python se omite para {plat}: solo se puede en la plataforma actual", "!")
                else:
                    instalar_python(carpeta_bin, a.python, plat)
    except (ErrorHerramienta, OSError, subprocess.CalledProcessError) as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        return 1
    log("Listo.", "✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
