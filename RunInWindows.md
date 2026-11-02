# Guía de Portabilidad e Instalación: Matemáticas Remediales en Windows

Esta guía está diseñada para que cualquier desarrollador o agente de IA pueda portar, instalar, depurar y ejecutar el proyecto Django + Tailwind de forma idéntica en entornos de **Windows** que en **Linux**, solucionando los típicos cuellos de botella de compatibilidad.

---

## 1. Diagnóstico de Diferencias Linux vs. Windows

El proyecto utiliza tecnologías que tienen dependencias de sistema específicas que difieren entre ambos entornos:

| Componente | Comportamiento en Linux (Actual) | Comportamiento en Windows (Gotchas) | Solución en Windows |
| :--- | :--- | :--- | :--- |
| **Entorno Virtual** | `source venv/bin/activate` | `venv\Scripts\activate` | Script de activación de PowerShell o CMD |
| **Base de Datos** | `mysqlclient` (compila nativo) | Fallo al instalar `mysqlclient` vía pip | Ruedas precompiladas (.whl) o SQLite de desarrollo |
| **Tailwind CSS** | Binario standalone `tailwindcss` (Linux) | Ejecutable Linux no compatible | Descargar binario `.exe` o usar compilador npm |
| **Separadores de Ruta** | Usa `/` en cadenas | Usa `\` en rutas de disco | Usar `os.path` o `pathlib` en Django |
| **Variables de Entorno** | Carga directa desde `.env` | Requiere seteo CMD/PowerShell | `.env` administrado con `django-environ` o `python-dotenv` |

---

## 2. Configuración Paso a Paso en Windows

### Paso 1: Inicialización del Entorno Virtual de Python
En Windows PowerShell, abre la carpeta del proyecto y ejecuta:
```powershell
# Crear el entorno virtual si no existe
python -m venv env_win

# Activar el entorno virtual en PowerShell
.\env_win\Scripts\Activate.ps1

# (Si PowerShell da error de políticas de ejecución):
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Paso 2: Instalación Exitosa de `mysqlclient` en Windows
El instalador `pip install mysqlclient` suele fallar en Windows debido a la falta de compiladores C++. Para solucionarlo de forma inmediata:

1. **Opción A (Recomendada para Desarrollo Rápido):**
   Si no necesitas MySQL localmente, puedes indicarle a Django en `settings.py` que use el SQLite existente (`db.sqlite3`), el cual funciona de forma nativa en Windows sin instalar ninguna dependencia extra.
2. **Opción B (Instalación Nativa con MySQL):**
   Descarga la "rueda" (wheel) precompilada correspondiente a tu versión de Python y arquitectura desde el repositorio de Cristoph Gohlke o similares:
   - Sitio de descarga: `pip install pipwin` o descargar directamente el archivo `.whl` compatible de `mysqlclient`.
   - Ejecuta: `pip install nombre_del_archivo_descargado.whl`
   - O bien, instala las herramientas de compilación oficiales: **Microsoft C++ Build Tools** antes de correr `pip install -r requirements.txt`.

### Paso 3: Sincronización y Ejecución de Tailwind CSS
El archivo `tailwindcss` en la raíz es un binario Linux ELF de 42MB. Ejecutarlo en Windows dará un error de compatibilidad.

**Solución 1: Usar Node.js y npm (Estándar e Infalible):**
1. Instala Node.js en Windows.
2. Ejecuta en el directorio del proyecto:
   ```bash
   npm install -g tailwindcss
   ```
3. Para compilar y vigilar cambios, corre:
   ```bash
   npx tailwindcss -i ./static/css/estilosPersonalizados.css -o ./static/css/modern_styles.css --watch
   ```

**Solución 2: Binario Standalone para Windows (.exe):**
1. Descarga el ejecutable para Windows de Tailwind desde su repositorio oficial de lanzamientos: `tailwindcss-windows-x64.exe`.
2. Renómbralo a `tailwindcss.exe` y colócalo en la raíz del proyecto.
3. Ejecútalo mediante:
   ```cmd
   .\tailwindcss.exe -i ./static/css/estilosPersonalizados.css -o ./static/css/modern_styles.css --watch
   ```

---

## 3. Depuración de Rutas de Archivos en Windows
Asegúrate de que en `settings.py` y cualquier lógica de guardado no se utilicen barras `/` estáticas para directorios.
- **Incorrecto:** `BASE_DIR + '/theme/templates/'`
- **Correcto:** `os.path.join(BASE_DIR, 'theme', 'templates')` o el uso de la librería estándar `pathlib`: `BASE_DIR / 'theme' / 'templates'`.

---

## 4. Script de Automatización: Ejecución con Un Clic (`run_windows.bat`)

Para evitar tener que ejecutar comandos repetitivos, crea un archivo llamado `run_windows.bat` en la raíz del proyecto con la siguiente estructura automatizada. Este script detecta las dependencias, activa el entorno y levanta tanto el servidor Django como la compilación de Tailwind CSS:

```batch
@echo off
title Servidor de Desarrollo - Matematicas Remediales ITESS
echo ==========================================================
echo       INICIANDO PROYECTO REMEDIAL EN WINDOWS
echo ==========================================================

:: 1. Activar entorno virtual
if exist env_win\Scripts\activate.bat (
    echo [OK] Activando entorno env_win...
    call env_win\Scripts\activate.bat
) else (
    echo [ALERTA] No se encontro env_win. Creando entorno virtual...
    python -m venv env_win
    call env_win\Scripts\activate.bat
    echo [OK] Entorno virtual creado. Instalando dependencias básicas...
    pip install -r requirements.txt
)

:: 2. Sincronizar Base de Datos
echo [OK] Verificando consistencia de Base de Datos...
python manage.py migrate

:: 3. Iniciar Tailwind CSS en segundo plano (si existe npm o binario)
echo [OK] Levantando compitador de Tailwind CSS...
start "Tailwind Compiler" cmd /c "npx tailwindcss -i ./static/css/estilosPersonalizados.css -o ./static/css/modern_styles.css --watch"

:: 4. Levantar servidor de Django
echo [OK] Levantando servidor local de Django en http://127.0.0.1:8000/
python manage.py runserver
pause
```

---

## 5. El Salvavidas Definitivo: WSL (Windows Subsystem for Linux)

Si el entorno de Windows sigue arrojando problemas insalvables con librerías compiladas, la mejor práctica de Ingeniería de Software es usar **WSL2** (Ubuntu para Windows):

1. Abre PowerShell como administrador e instala WSL:
   ```powershell
   wsl --install
   ```
2. Reinicia la computadora, abre la terminal de Ubuntu y clona/abre la carpeta del proyecto.
3. Al ejecutarse dentro del subsistema Linux, **todos los comandos, binarios (incluyendo el ejecutable standalone de Tailwind) y dependencias de MySQL del proyecto actual funcionarán de forma 100% nativa e inmediata**, eliminando la fricción de Windows por completo.
