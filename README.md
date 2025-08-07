Configuracion proyecto demo 2025

Sino puede instalar python por restricciones se puede instalar por CMD de forma silenciosa sin permisos de administrador
```bash
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.4/python-3.13.4-amd64.msi' -OutFile 'python-3.13.4-amd64.msi'; Start-Process msiexec.exe -ArgumentList '/i python-3.13.4-amd64.msi /quiet InstallAllUsers=0 PrependPath=1' -Wait"
```
Instalar extensiones de Python sin tener permisos de administrador desde CMD:
```bash
code --install-extension ms-python.python
```

Quitar restriccion desde la terminal VS code de powerShell

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Configurar en VSC en preferenecias Usuario JSON, variable global PYTHON
```bash
"python.pythonPath": "C:\\Users\\ESTUDIANTE\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "C:\\Users\\ESTUDIANTE\\AppData\\Local\\Programs\\Python\\Python313"
```bash



markdown

# Instrucciones para Configurar el Proyecto, y si gustas puedes crear un archivo bash que con un solo clic te lo ejecute todo

1. Clona el repositorio:
```bash
    cd tu_proyecto
   git clone https://gitlab.com/maestro763129/proyecto-demo.git
```


2. Crea un entorno virtual:

```bash
python3 -m venv env
```

3. Activa el entorno virtual:

    En Linux/macOS:

```bash
source env/bin/activate
```

En Windows:

```bash
    env\Scripts\activate
```
4. Instala las dependencias:

```bash

Pip install flask
Pip install flask-mysqldb
```

5. Ejecuta tu aplicación:

```bash
python app.py
```

```bash
python3 app.py
```