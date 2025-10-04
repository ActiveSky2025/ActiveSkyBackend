# ActiveSkyBackend

# 1. Navegar al proyecto
cd /c/Users/josec/Code/ACTIVESKY/Back

# 2. Activar entorno virtual
source venv/Scripts/activate

# 3. Verificar Python
python --version

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Iniciar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

Si da error de importacion de fastapi hacer lo siguiente:

# 1. Presiona en VSCode:
Ctrl + Shift + P

# 2. Escribe:
Python: Select Interpreter

# 3. Selecciona:
.\venv\Scripts\python.exe

# O la ruta completa:
C:\Users\josec\Code\ACTIVESKY\Back\venv\Scripts\python.exe