"""
Gestión de Google Sheets para Cero Referidos
"""
import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SCOPES, SPREADSHEET_ID
import pandas as pd


class SheetsManager:
    def __init__(self):
        """Inicializa la conexión con Google Sheets"""
        self.creds = Credentials.from_service_account_file(
            str(SERVICE_ACCOUNT_FILE),
            scopes=SCOPES
        )
        self.client = gspread.authorize(self.creds)
        self.spreadsheet = None

    def conectar_sheet(self, spreadsheet_id=None):
        """Conecta con un Google Sheet específico"""
        sheet_id = spreadsheet_id or SPREADSHEET_ID
        if not sheet_id:
            raise ValueError("Debe proporcionar un SPREADSHEET_ID")
        self.spreadsheet = self.client.open_by_key(sheet_id)
        return self.spreadsheet

    def crear_plantilla(self, nombre_archivo="Cero Referidos - Plantilla"):
        """Crea una plantilla de Google Sheets con la estructura necesaria"""
        # Crear nuevo spreadsheet
        spreadsheet = self.client.create(nombre_archivo)

        # Hoja de Datos
        worksheet_datos = spreadsheet.get_worksheet(0)
        worksheet_datos.update_title("Datos")

        # Encabezados
        headers = [
            "Iglesia",
            "Municipio",
            "Cédula",
            "Nombre",
            "Celular",
            "Contactado",
            "Fecha Contacto",
            "Observaciones",
            "¿Está en InfoMIRA?",
            "Referidos Activos",
            "Referidos Inactivos"
        ]

        worksheet_datos.update('A1:K1', [headers])

        # Formato de encabezados
        worksheet_datos.format('A1:K1', {
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
            'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'horizontalAlignment': 'CENTER'
        })

        # Crear hoja de Resumen
        worksheet_resumen = spreadsheet.add_worksheet(title="Resumen", rows=100, cols=10)

        print(f"Plantilla creada exitosamente!")
        print(f"URL: {spreadsheet.url}")
        print(f"ID: {spreadsheet.id}")

        return spreadsheet

    def leer_datos(self, hoja="Datos"):
        """Lee todos los datos de una hoja"""
        if not self.spreadsheet:
            raise ValueError("Primero debe conectar con un spreadsheet")

        worksheet = self.spreadsheet.worksheet(hoja)
        datos = worksheet.get_all_records()
        df = pd.DataFrame(datos)
        return df

    def agregar_persona(self, datos, hoja="Datos"):
        """Agrega una nueva persona al sheet"""
        if not self.spreadsheet:
            raise ValueError("Primero debe conectar con un spreadsheet")

        worksheet = self.spreadsheet.worksheet(hoja)

        # Preparar fila
        fila = [
            datos.get('iglesia', ''),
            datos.get('municipio', ''),
            datos.get('cedula', ''),
            datos.get('nombre', ''),
            datos.get('celular', ''),
            datos.get('contactado', 'NO'),
            datos.get('fecha_contacto', ''),
            datos.get('observaciones', ''),
            datos.get('esta_en_infomira', 'NO'),
            datos.get('referidos_activos', 0),
            datos.get('referidos_inactivos', 0)
        ]

        worksheet.append_row(fila)
        return True

    def actualizar_persona(self, cedula, datos, hoja="Datos"):
        """Actualiza los datos de una persona existente"""
        if not self.spreadsheet:
            raise ValueError("Primero debe conectar con un spreadsheet")

        worksheet = self.spreadsheet.worksheet(hoja)

        # Buscar la cédula
        cell = worksheet.find(str(cedula))
        if cell:
            fila = cell.row
            # Actualizar campos específicos
            if 'contactado' in datos:
                worksheet.update_cell(fila, 6, datos['contactado'])
            if 'fecha_contacto' in datos:
                worksheet.update_cell(fila, 7, datos['fecha_contacto'])
            if 'observaciones' in datos:
                worksheet.update_cell(fila, 8, datos['observaciones'])
            if 'esta_en_infomira' in datos:
                worksheet.update_cell(fila, 9, datos['esta_en_infomira'])
            if 'referidos_activos' in datos:
                worksheet.update_cell(fila, 10, datos['referidos_activos'])
            if 'referidos_inactivos' in datos:
                worksheet.update_cell(fila, 11, datos['referidos_inactivos'])
            return True
        return False

    def obtener_estadisticas(self):
        """Obtiene estadísticas generales y por iglesia"""
        df = self.leer_datos()
        return self.obtener_estadisticas_de_dataframe(df)

    def obtener_estadisticas_de_dataframe(self, df):
        """Calcula estadísticas de cualquier dataframe (filtrado o completo)"""
        if df.empty:
            return None

        # Asegurar que columnas numéricas sean realmente numéricas
        df_copy = df.copy()
        df_copy['Referidos Activos'] = pd.to_numeric(df_copy['Referidos Activos'], errors='coerce').fillna(0)
        df_copy['Referidos Inactivos'] = pd.to_numeric(df_copy['Referidos Inactivos'], errors='coerce').fillna(0)

        # Estadísticas generales
        total_personas = len(df_copy)
        total_contactados = len(df_copy[df_copy['Contactado'].str.upper() == 'SI'])
        total_no_contactados = total_personas - total_contactados
        total_en_infomira = len(df_copy[df_copy['¿Está en InfoMIRA?'].str.upper() == 'SI'])

        # Estadísticas por iglesia
        stats_por_iglesia = df_copy.groupby('Iglesia').agg({
            'Cédula': 'count',
            'Contactado': lambda x: (x.str.upper() == 'SI').sum(),
            '¿Está en InfoMIRA?': lambda x: (x.str.upper() == 'SI').sum(),
            'Referidos Activos': 'sum',
            'Referidos Inactivos': 'sum'
        }).reset_index()

        stats_por_iglesia.columns = [
            'Iglesia',
            'Total Personas',
            'Contactados',
            'En InfoMIRA',
            'Referidos Activos',
            'Referidos Inactivos'
        ]

        stats_por_iglesia['No Contactados'] = stats_por_iglesia['Total Personas'] - stats_por_iglesia['Contactados']
        stats_por_iglesia['Total Referidos'] = stats_por_iglesia['Referidos Activos'] + stats_por_iglesia['Referidos Inactivos']

        return {
            'general': {
                'total_personas': total_personas,
                'contactados': total_contactados,
                'no_contactados': total_no_contactados,
                'en_infomira': total_en_infomira,
                'referidos_activos': int(df_copy['Referidos Activos'].sum()),
                'referidos_inactivos': int(df_copy['Referidos Inactivos'].sum()),
                'total_referidos': int(df_copy['Referidos Activos'].sum() + df_copy['Referidos Inactivos'].sum())
            },
            'por_iglesia': stats_por_iglesia
        }