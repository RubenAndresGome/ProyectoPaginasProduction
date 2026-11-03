# adminExe — herramientas del proyecto y protección de secretos

## 1. Descargar herramientas (Windows y Linux)

Las herramientas externas (Tailwind CSS, uv) **no se suben a GitHub**: se descargan de su fuente oficial
según [`requirements-tools.txt`](requirements-tools.txt), y cada archivo se verifica con su **SHA-256**.
Si un hash no coincide, el archivo se borra y el proceso se detiene.

```bash
python adminExe/descargar_tools.py                     # solo la plataforma actual
python adminExe/descargar_tools.py --plataforma todas  # Windows + Linux (desde cualquier sistema)
python adminExe/descargar_tools.py --python 3.12       # además instala Python 3.12 con uv
python adminExe/descargar_tools.py --verificar         # comprueba que nada se haya alterado
```

Resultado:

```
adminExe/dist/
├── toolsForWindows/          tailwindcss.exe, uv.exe, uvx.exe, uvw.exe
│   ├── SHA256SUMS.txt
│   └── herramientas.json
└── toolsForLinux/
    ├── bin/                  tailwindcss, uv, uvx
    ├── mathmaster-tools_<versión>_amd64.deb
    ├── SHA256SUMS.txt
    └── herramientas.json
```

**Linux:** instala el paquete y abre una terminal nueva:

```bash
sudo apt install ./adminExe/dist/toolsForLinux/mathmaster-tools_*.deb
tailwindcss --help        # quedan en /opt/mathmaster-tools/bin
sudo apt remove mathmaster-tools   # para quitarlo
```

El paquete agrega su carpeta **al final** del `PATH`, así que no reemplaza versiones que ya tengas instaladas.

**Windows:** usa los `.exe` directamente o deja que `run_windows.bat` los encuentre solo.

### Actualizar una herramienta

Edita la línea en `requirements-tools.txt` cambiando **versión, fuente y sha256 juntos**.
El hash de una wheel de PyPI aparece en `https://pypi.org/pypi/<nombre>/<versión>/json`;
el de un binario de GitHub, calculándolo tú (`sha256sum archivo` / `Get-FileHash archivo`)
y comparándolo con el publicado por el proyecto.

Solo usa la biblioteca estándar de Python ≥ 3.8, así que funciona antes de instalar el Python del proyecto.
El `.deb` se arma en Python puro: no necesitas `dpkg-deb` ni Linux para generarlo.

## 2. Evitar que se filtren llaves

`escanear_secretos.py` busca llaves privadas, tokens (GitHub, AWS, Google, OpenAI, Anthropic, Slack, Stripe),
`SECRET_KEY` reales, contraseñas escritas en código, URLs con contraseña y archivos que nunca deben subirse
(`.env`, bases de datos, `*.pem`, `*.key`, `SuperUser.txt`…).

```bash
git config core.hooksPath adminExe/hooks           # una vez: revisa antes de cada commit
python adminExe/escanear_secretos.py --todo        # todo lo que se subiría
python adminExe/escanear_secretos.py --historial   # toda la historia de git
```

Si una línea es intencional y segura (p. ej. una contraseña de prueba), agrega al final
`# secretos: permitido`. El mismo escaneo corre en GitHub Actions en cada push.
