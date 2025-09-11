# Cross-Platform Setup Guide

Este proyecto incluye scripts específicos para cada sistema operativo.

## 🐧 **Mac/Linux - usando Makefile**

### Prerrequisitos
- Docker y Docker Compose
- Python 3.9+
- make (incluido en macOS y la mayoría de distribuciones Linux)

### Comandos disponibles
```bash
# Ver todos los comandos
make help

# Instalar dependencias
make install

# Levantar servicios
make run

# Ver logs
make logs

# Parar servicios
make down

# Limpiar todo
make clean

# Ejecutar tests
make test
make check  # Suite completa

# Desarrollo
make dev
```

### Flujo típico
```bash
# Primera vez
make install && make run

# Verificar que funciona
curl http://localhost:8000/health

# Ver logs si es necesario
make logs

# Parar al final del día
make down
```

## 🪟 **Windows - usando PowerShell**

### Prerrequisitos
- Docker Desktop
- Python 3.9+
- PowerShell (incluido en Windows 10+)

### Comandos disponibles
```powershell
# Ver todos los comandos
.\make.ps1 help

# Instalar dependencias
.\make.ps1 install

# Levantar servicios
.\make.ps1 run

# Ver logs
.\make.ps1 logs

# Parar servicios
.\make.ps1 down

# Limpiar todo
.\make.ps1 clean

# Ejecutar tests
.\make.ps1 test
.\make.ps1 check  # Suite completa

# Desarrollo
.\make.ps1 dev
```

### Configuración inicial Windows
```powershell
# 1. Permitir ejecución de scripts (una sola vez)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. Instalar dependencias
.\make.ps1 install

# 3. Levantar servicios
.\make.ps1 run

# 4. Verificar que funciona
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

## 🔧 **Comandos equivalentes por sistema**

| Función | Mac/Linux | Windows |
|---------|-----------|---------|
| Ver ayuda | `make help` | `.\make.ps1 help` |
| Instalar | `make install` | `.\make.ps1 install` |
| Levantar | `make run` | `.\make.ps1 run` |
| Ver logs | `make logs` | `.\make.ps1 logs` |
| Parar | `make down` | `.\make.ps1 down` |
| Limpiar | `make clean` | `.\make.ps1 clean` |
| Tests | `make test` | `.\make.ps1 test` |
| Suite completa | `make check` | `.\make.ps1 check` |
| Desarrollo | `make dev` | `.\make.ps1 dev` |

## 🚀 **Comandos universales (sin scripts)**

Si prefieres ejecutar comandos directamente:

```bash
# Instalar dependencias
pip3 install -r requirements.txt  # Mac/Linux
pip install -r requirements.txt   # Windows

# Crear archivo de configuración
cp .env.example .env              # Mac/Linux
Copy-Item .env.example .env       # Windows PowerShell

# Levantar servicios
docker-compose up --build -d      # Todos los sistemas
# O en versiones nuevas:
docker compose up --build -d      # Todos los sistemas

# Ver logs
docker-compose logs -f            # Todos los sistemas

# Parar servicios
docker-compose down               # Todos los sistemas
```

## 🛠️ **Solución de problemas**

### Mac/Linux
```bash
# Si make no está disponible
sudo apt-get install make        # Ubuntu/Debian
brew install make                # macOS con Homebrew

# Si pip3 no funciona
python3 -m pip install -r requirements.txt

# Verificar Docker
docker --version
docker-compose --version
```

### Windows
```powershell
# Si hay problemas de permisos
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Si python no se encuentra
python --version
python3 --version

# Verificar Docker
docker --version
docker compose version
```

## 📁 **Estructura del proyecto**

```
kopi-chatbot/
├── Makefile                    # ← Para Mac/Linux
├── make.ps1                    # ← Para Windows
├── CROSS-PLATFORM.md          # ← Este archivo
├── app/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🎯 **Recomendaciones**

- **Mac/Linux**: Usar `make` (más estándar en desarrollo)
- **Windows**: Usar `.\make.ps1` (nativo de PowerShell)
- **CI/CD**: Usar comandos universales de Docker
- **Equipos mixtos**: Documentar ambas opciones

## ✅ **Verificación rápida**

Independientemente del sistema:

```bash
# Verificar que la API funciona
curl http://localhost:8000/health

# O en Windows PowerShell:
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

Deberías ver una respuesta JSON con `"status": "healthy"` y `"redis_status": "connected"`.