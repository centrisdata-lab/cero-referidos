"""
Dashboard visual para Cero Referidos
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sheets_manager import SheetsManager
from datetime import datetime
from config import SPREADSHEET_ID

# Configuración de la página
st.set_page_config(
    page_title="Cero Referidos - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Inicializar el gestor de sheets
def get_sheets_manager():
    return SheetsManager()

# Cargar datos
@st.cache_data(ttl=300)
def cargar_datos():
    """Carga los datos del Google Sheet"""
    try:
        manager = get_sheets_manager()
        manager.conectar_sheet()
        df = manager.leer_datos()

        # Convertir columnas numéricas a tipo numérico
        if not df.empty:
            df['Referidos Activos'] = pd.to_numeric(df['Referidos Activos'], errors='coerce').fillna(0)
            df['Referidos Inactivos'] = pd.to_numeric(df['Referidos Inactivos'], errors='coerce').fillna(0)

        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

def mostrar_vista_general_visual(stats, df):
    """Muestra la vista general con flujo visual del proceso"""

    # Título principal con estilo
    st.markdown("""
        <h1 style='text-align: center; color: #1E88E5; font-size: 2.2em; margin-bottom: 15px; margin-top: -10px;'>
            📊 Dashboard Cero Referidos
        </h1>
    """, unsafe_allow_html=True)

    # Calcular personas con referidos activados
    contactados = stats['general']['contactados']
    no_contactados = stats['general']['no_contactados']

    # CONTACTADOS: activaron referidos y total de referidos
    df_contactados = df[df['Contactado'].str.upper() == 'SI'].copy()
    # Convertir a numérico por si hay strings
    df_contactados['Referidos Activos'] = pd.to_numeric(df_contactados['Referidos Activos'], errors='coerce').fillna(0)
    df_contactados['Referidos Inactivos'] = pd.to_numeric(df_contactados['Referidos Inactivos'], errors='coerce').fillna(0)
    contactados_activaron = len(df_contactados[df_contactados['Referidos Activos'] > 0])
    contactados_total_refs = int(df_contactados['Referidos Activos'].sum())  # Solo activos
    contactados_refs_inactivos = int(df_contactados['Referidos Inactivos'].sum())

    # NO CONTACTADOS: activaron referidos y total de referidos
    df_no_contactados = df[df['Contactado'].str.upper() != 'SI'].copy()
    # Convertir a numérico por si hay strings
    df_no_contactados['Referidos Activos'] = pd.to_numeric(df_no_contactados['Referidos Activos'], errors='coerce').fillna(0)
    df_no_contactados['Referidos Inactivos'] = pd.to_numeric(df_no_contactados['Referidos Inactivos'], errors='coerce').fillna(0)
    no_contactados_activaron = len(df_no_contactados[df_no_contactados['Referidos Activos'] > 0])
    no_contactados_total_refs = int(df_no_contactados['Referidos Activos'].sum())  # Solo activos
    no_contactados_refs_inactivos = int(df_no_contactados['Referidos Inactivos'].sum())

    sin_activar = contactados - contactados_activaron if contactados > 0 else 0
    efectividad = (contactados_activaron / contactados * 100) if contactados > 0 else 0

    # Calcular porcentajes
    efectividad_total = (contactados_activaron / stats['general']['total_personas'] * 100) if stats['general']['total_personas'] > 0 else 0
    pct_contactados = (contactados/stats['general']['total_personas']*100) if stats['general']['total_personas'] > 0 else 0
    pct_no_contactados = (no_contactados/stats['general']['total_personas']*100) if stats['general']['total_personas'] > 0 else 0

    # PASO 1: Métricas principales del flujo
    col_lideres, col_contactados, col_no_contactados, col_activaron, col_total_refs, col_promedio = st.columns(6)

    with col_lideres:
        st.metric(
            label="🎯 Total de Líderes",
            value=stats['general']['total_personas']
        )

    with col_contactados:
        st.metric(
            label="📞 Contactados",
            value=contactados,
            delta=f"{pct_contactados:.1f}%"
        )

    with col_no_contactados:
        st.metric(
            label="❌ No Contactados",
            value=no_contactados,
            delta=f"{pct_no_contactados:.1f}%",
            delta_color="inverse"
        )

    with col_activaron:
        st.metric(
            label="✅ Activaron Referidos",
            value=contactados_activaron,
            delta=f"{efectividad_total:.1f}%"
        )

    with col_total_refs:
        st.metric(
            label="👥 Total Referidos",
            value=stats['general']['referidos_activos'],
            delta=f"{stats['general']['referidos_inactivos']} inactivos"
        )

    with col_promedio:
        promedio = stats['general']['referidos_activos'] / contactados_activaron if contactados_activaron > 0 else 0
        st.metric(
            label="📊 Promedio x Líder",
            value=f"{promedio:.1f}",
            delta="Solo activos"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Desglose por Contactados vs No Contactados
    st.markdown("""
        <h2 style='text-align: center; color: #424242; font-size: 1.5em; margin-bottom: 10px; margin-top: 5px;'>
            📊 Desglose: Contactados vs No Contactados
        </h2>
    """, unsafe_allow_html=True)

    col_desg1, col_desg2 = st.columns(2)

    with col_desg1:
        st.markdown("""
            <div style='text-align: center; padding: 10px; background-color: #e8f5e9; border-radius: 10px; margin-bottom: 10px;'>
                <h3 style='color: #2e7d32; margin: 0;'>📞 CONTACTADOS</h3>
            </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.metric("Total", contactados)
        with col_c2:
            st.metric("Activaron", contactados_activaron, delta=f"{(contactados_activaron/contactados*100 if contactados > 0 else 0):.1f}%")
        with col_c3:
            st.metric("Total Refs", contactados_total_refs, delta=f"{contactados_refs_inactivos} inactivos")

    with col_desg2:
        st.markdown("""
            <div style='text-align: center; padding: 10px; background-color: #ffebee; border-radius: 10px; margin-bottom: 10px;'>
                <h3 style='color: #c62828; margin: 0;'>❌ NO CONTACTADOS</h3>
            </div>
        """, unsafe_allow_html=True)

        col_nc1, col_nc2, col_nc3 = st.columns(3)
        with col_nc1:
            st.metric("Total", no_contactados)
        with col_nc2:
            st.metric("Activaron", no_contactados_activaron, delta=f"{(no_contactados_activaron/no_contactados*100 if no_contactados > 0 else 0):.1f}%")
        with col_nc3:
            st.metric("Total Refs", no_contactados_total_refs, delta=f"{no_contactados_refs_inactivos} inactivos")

def clasificar_iglesias_por_efectividad(df, stats_iglesia):
    """Clasifica iglesias según efectividad de gestión"""
    # Calcular efectividad por iglesia
    stats_iglesia['Efectividad'] = 0.0
    stats_iglesia['Con Referidos'] = 0

    for idx, row in stats_iglesia.iterrows():
        iglesia = row['Iglesia']
        df_iglesia = df[df['Iglesia'] == iglesia]

        # Personas contactadas que activaron referidos
        con_referidos = len(df_iglesia[(df_iglesia['Contactado'].str.upper() == 'SI') &
                                       (df_iglesia['Referidos Activos'] > 0)])
        contactados = row['Contactados']

        efectividad = (con_referidos / contactados * 100) if contactados > 0 else 0

        stats_iglesia.at[idx, 'Con Referidos'] = con_referidos
        stats_iglesia.at[idx, 'Efectividad'] = round(efectividad, 1)

    # Clasificar por nivel de atención
    def clasificar_nivel(row):
        efectividad = row['Efectividad']
        no_contactados = row['No Contactados']

        # Crítico: Efectividad baja (<30%) o muchos sin contactar
        if efectividad < 30 or (no_contactados > row['Total Personas'] * 0.5):
            return '🔴 CRÍTICO'
        # Medio: Efectividad media (30-60%)
        elif efectividad < 60:
            return '🟡 MEDIO'
        # Normal: Efectividad alta (>60%)
        else:
            return '🟢 NORMAL'

    stats_iglesia['Nivel de Atención'] = stats_iglesia.apply(clasificar_nivel, axis=1)

    # Ordenar por nivel de atención (crítico primero)
    orden_nivel = {'🔴 CRÍTICO': 0, '🟡 MEDIO': 1, '🟢 NORMAL': 2}
    stats_iglesia['_orden'] = stats_iglesia['Nivel de Atención'].map(orden_nivel)
    stats_iglesia = stats_iglesia.sort_values('_orden').drop('_orden', axis=1)

    return stats_iglesia


def main():
    # Botón de actualizar datos en la esquina
    col_empty, col_refresh = st.columns([5, 1])
    with col_refresh:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Cargar datos
    df = cargar_datos()

    if df.empty:
        st.warning("No hay datos disponibles. Verifica la configuración del Google Sheet.")
        st.info("Asegúrate de haber configurado el SPREADSHEET_ID en config.py")
        return

    # Filtro por iglesia - MOVER ARRIBA ANTES DE CALCULAR ESTADÍSTICAS
    st.sidebar.header("🔍 Filtros")

    iglesias = ['Todas'] + sorted(df['Iglesia'].unique().tolist())
    iglesia_seleccionada = st.sidebar.selectbox("Seleccionar Iglesia", iglesias)

    # FILTRAR DATAFRAME SEGÚN SELECCIÓN
    if iglesia_seleccionada != 'Todas':
        df_filtrado = df[df['Iglesia'] == iglesia_seleccionada].copy()
    else:
        df_filtrado = df.copy()

    # Obtener estadísticas DEL DATAFRAME FILTRADO
    try:
        manager = get_sheets_manager()
        manager.conectar_sheet()

        # Calcular estadísticas del dataframe filtrado (no del original)
        stats = manager.obtener_estadisticas_de_dataframe(df_filtrado)

        if stats:
            # Mostrar vista general visual CON DATOS FILTRADOS
            mostrar_vista_general_visual(stats, df_filtrado)

            st.markdown("---")

            # Botón para ver datos en Google Sheets
            st.markdown("<br>", unsafe_allow_html=True)
            sheet_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
            titulo_boton = "VER DATOS COMPLETOS EN EXCEL" if iglesia_seleccionada == 'Todas' else f"VER DATOS DE {iglesia_seleccionada} EN EXCEL"
            st.markdown(f"""
            <div style="text-align: center; padding: 30px;">
                <a href="{sheet_url}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border: none;
                        color: white;
                        padding: 20px 50px;
                        text-align: center;
                        display: inline-block;
                        font-size: 1.3em;
                        font-weight: bold;
                        cursor: pointer;
                        border-radius: 50px;
                        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
                        transition: all 0.3s ease;
                    "
                    onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 12px 25px rgba(102, 126, 234, 0.6)';"
                    onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.4)';">
                        📊 {titulo_boton}
                    </div>
                </a>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error al procesar estadísticas: {e}")

if __name__ == "__main__":
    main()
