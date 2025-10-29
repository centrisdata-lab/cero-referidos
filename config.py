"""
Configuración del proyecto Cero Referidos
"""
import os
from pathlib import Path

# Rutas
BASE_DIR = Path(__file__).resolve().parent
SERVICE_ACCOUNT_FILE = BASE_DIR / "service_account.json"

# Configuración de Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ID del Google Sheet (se debe configurar después de crear la plantilla)
# Para obtener el ID: ejecuta crear_plantilla.py y copia el ID que te muestra
SPREADSHEET_ID = "1H9WAG5t6rDYPym1VraZR0Cci6tVTScA1V9DPAOrUCo8"

# Nombre de las hojas
SHEET_NAMES = {
    'DATOS': 'Datos',
    'RESUMEN': 'Resumen'
}

# Columnas de la hoja de datos
COLUMNAS = {
    'IGLESIA': 0,
    'MUNICIPIO': 1,
    'CEDULA': 2,
    'NOMBRE': 3,
    'CELULAR': 4,
    'CONTACTADO': 5,
    'FECHA_CONTACTO': 6,
    'OBSERVACIONES': 7,
    'ESTA_EN_INFOMIRA': 8,
    'REFERIDOS_ACTIVOS': 9,
    'REFERIDOS_INACTIVOS': 10
}