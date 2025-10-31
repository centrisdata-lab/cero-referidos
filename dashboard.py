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

            # Asegurar que las columnas de contacto sean texto limpio
            if 'Contactado' in df.columns:
                df['Contactado'] = df['Contactado'].astype(str).str.strip().str.upper()
            if 'Contestaron' in df.columns:
                df['Contestaron'] = df['Contestaron'].astype(str).str.strip().str.upper()

        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

def crear_barra_progreso(valor, total, label, color="#1E88E5", mostrar_porcentaje_abajo=True):
    """Crea una barra de progreso horizontal con porcentaje"""
    porcentaje = (valor / total * 100) if total > 0 else 0

    porcentaje_html = ""
    if mostrar_porcentaje_abajo:
        porcentaje_html = f'<span style="position: absolute; width: 100%; text-align: center; line-height: 30px; font-weight: bold; color: {"white" if porcentaje > 50 else "#333"}; font-size: 1.1em;">{porcentaje:.1f}%</span>'

    html = f"""<div style="margin: 20px 0;"><div style="display: flex; justify-content: space-between; margin-bottom: 5px;"><span style="font-weight: bold; font-size: 1.1em;">{label}</span><span style="font-weight: bold; font-size: 1.1em; color: {color};">{valor} / {total} ({porcentaje:.1f}%)</span></div><div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 30px; position: relative;"><div style="width: {porcentaje}%; background-color: {color}; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>{porcentaje_html}</div></div>"""
    return html

def mostrar_vista_general_visual(df, promedio_lideres):
    """Muestra la vista general con flujo visual del proceso"""

    # Título principal con estilo
    st.markdown("""
        <h1 style='text-align: center; color: #1E88E5; font-size: 2.2em; margin-bottom: 15px; margin-top: -10px;'>
            📊 Dashboard Cero Referidos
        </h1>
    """, unsafe_allow_html=True)

    # CÁLCULOS GENERALES
    total_lideres = len(df)
    lideres_cero_referidos = len(df[df['Referidos Activos'] == 0])

    # Contactabilidad - usar la columna "Contestaron" si existe, sino usar "Contactado"
    columna_contacto = 'Contestaron' if 'Contestaron' in df.columns else 'Contactado'
    contactados = len(df[df[columna_contacto] == 'SI'])
    no_contactados = len(df[df[columna_contacto] != 'SI'])

    # ============================================================
    # SECCIÓN 1: LÍDERES CON CERO REFERIDOS (SIN PORCENTAJE ABAJO)
    # ============================================================
    st.markdown(crear_barra_progreso(
        lideres_cero_referidos,
        promedio_lideres,
        "Líderes con Cero Referidos",
        "#E53935",
        mostrar_porcentaje_abajo=False
    ), unsafe_allow_html=True)

    # ============================================================
    # SECCIÓN 2: CONTACTABILIDAD (SIN PORCENTAJE ABAJO)
    # ============================================================
    st.markdown("""
        <h2 style='color: #424242; font-size: 1.6em; margin-top: 15px; margin-bottom: 10px;'>
            📞 Contactabilidad
        </h2>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(crear_barra_progreso(
            contactados,
            total_lideres,
            "Contestaron",
            "#43A047",
            mostrar_porcentaje_abajo=False
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(crear_barra_progreso(
            no_contactados,
            total_lideres,
            "No Contestaron",
            "#FB8C00",
            mostrar_porcentaje_abajo=False
        ), unsafe_allow_html=True)

    # ============================================================
    # SECCIÓN 3: ACTIVACIÓN DE REFERIDOS (DEBAJO DE CONTACTABILIDAD)
    # ============================================================

    # Calcular métricas para CONTESTARON
    df_contestaron = df[df[columna_contacto] == 'SI'].copy()
    contestaron_activaron = len(df_contestaron[df_contestaron['Referidos Activos'] > 0])
    contestaron_sin_activar = len(df_contestaron[df_contestaron['Referidos Activos'] == 0])
    contestaron_total_refs_activos = int(df_contestaron['Referidos Activos'].sum())
    contestaron_total_refs_inactivos = int(df_contestaron['Referidos Inactivos'].sum())
    contestaron_pct_activaron = (contestaron_activaron / len(df_contestaron) * 100) if len(df_contestaron) > 0 else 0

    # Calcular métricas para NO CONTESTARON
    df_no_contestaron = df[df[columna_contacto] != 'SI'].copy()
    no_contestaron_activaron = len(df_no_contestaron[df_no_contestaron['Referidos Activos'] > 0])
    no_contestaron_sin_activar = len(df_no_contestaron[df_no_contestaron['Referidos Activos'] == 0])
    no_contestaron_total_refs_activos = int(df_no_contestaron['Referidos Activos'].sum())
    no_contestaron_total_refs_inactivos = int(df_no_contestaron['Referidos Inactivos'].sum())
    no_contestaron_pct_activaron = (no_contestaron_activaron / len(df_no_contestaron) * 100) if len(df_no_contestaron) > 0 else 0

    col_contest, col_no_contest = st.columns(2)

    # COLUMNA CONTESTARON
    with col_contest:
        st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 12px; border-radius: 8px; margin-bottom: 8px;'>
                <h4 style='color: #424242; margin-top: 0; margin-bottom: 8px; font-size: 1.1em;'>👥 Activación de Referidos</h4>
                <p style='font-size: 1.1em; margin: 5px 0;'>
                    <strong style='color: #43A047;'>{contestaron_activaron}</strong> activaron referidos
                    <span style='color: #666;'>({contestaron_pct_activaron:.1f}%)</span>
                </p>
                <p style='font-size: 1.1em; margin: 5px 0;'>
                    <strong style='color: #E53935;'>{contestaron_sin_activar}</strong> sin activar
                    <span style='color: #666;'>({100-contestaron_pct_activaron:.1f}%)</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 12px; border-radius: 8px;'>
                <h4 style='color: #424242; margin-top: 0; margin-bottom: 8px; font-size: 1.1em;'>📈 Referidos</h4>
                <p style='font-size: 1.2em; margin: 5px 0;'>
                    <strong style='color: #1E88E5;'>{contestaron_total_refs_activos}</strong> referidos activos
                </p>
                <p style='font-size: 1em; margin: 5px 0; color: #666;'>
                    {contestaron_total_refs_inactivos} referidos inactivos
                </p>
            </div>
        """, unsafe_allow_html=True)

    # COLUMNA NO CONTESTARON
    with col_no_contest:
        st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 12px; border-radius: 8px; margin-bottom: 8px;'>
                <h4 style='color: #424242; margin-top: 0; margin-bottom: 8px; font-size: 1.1em;'>👥 Activación de Referidos</h4>
                <p style='font-size: 1.1em; margin: 5px 0;'>
                    <strong style='color: #43A047;'>{no_contestaron_activaron}</strong> activaron referidos
                    <span style='color: #666;'>({no_contestaron_pct_activaron:.1f}%)</span>
                </p>
                <p style='font-size: 1.1em; margin: 5px 0;'>
                    <strong style='color: #E53935;'>{no_contestaron_sin_activar}</strong> sin activar
                    <span style='color: #666;'>({100-no_contestaron_pct_activaron:.1f}%)</span>
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='background-color: #f5f5f5; padding: 12px; border-radius: 8px;'>
                <h4 style='color: #424242; margin-top: 0; margin-bottom: 8px; font-size: 1.1em;'>📈 Referidos</h4>
                <p style='font-size: 1.2em; margin: 5px 0;'>
                    <strong style='color: #1E88E5;'>{no_contestaron_total_refs_activos}</strong> referidos activos
                </p>
                <p style='font-size: 1em; margin: 5px 0; color: #666;'>
                    {no_contestaron_total_refs_inactivos} referidos inactivos
                </p>
            </div>
        """, unsafe_allow_html=True)

    # ============================================================
    # SECCIÓN 3: DISTRIBUCIÓN DE RESPUESTAS (Solo contestaron)
    # ============================================================
    st.markdown("""
        <h2 style='color: #424242; font-size: 1.6em; margin-top: 15px; margin-bottom: 10px;'>
            💬 Distribución de Respuestas (Solo Contestaron)
        </h2>
    """, unsafe_allow_html=True)

    df_contactados_full = df[df[columna_contacto] == 'SI'].copy()

    if len(df_contactados_full) > 0:
        # Contar respuestas
        respuestas_count = df_contactados_full['Respuesta'].value_counts().reset_index()
        respuestas_count.columns = ['Respuesta', 'Cantidad']

        # Crear gráfica de barras horizontal
        fig_respuestas = go.Figure()

        colores = ['#1E88E5', '#43A047', '#FB8C00', '#E53935', '#8E24AA', '#00ACC1']

        for idx, row in respuestas_count.iterrows():
            porcentaje = (row['Cantidad'] / contactados * 100)
            fig_respuestas.add_trace(go.Bar(
                y=[row['Respuesta']],
                x=[row['Cantidad']],
                orientation='h',
                text=f"{row['Cantidad']} ({porcentaje:.1f}%)",
                textposition='auto',
                marker_color=colores[idx % len(colores)],
                name=row['Respuesta']
            ))

        fig_respuestas.update_layout(
            showlegend=False,
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Cantidad de Líderes",
            yaxis_title="",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=11)
        )

        st.plotly_chart(fig_respuestas, use_container_width=True)
    else:
        st.info("No hay líderes contactados aún")


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

    # Filtro por iglesia en el sidebar
    st.sidebar.header("🔍 Filtros")

    iglesias = ['Todas'] + sorted(df['Iglesia'].unique().tolist())

    # Definir valor por defecto: SAN DIEGO si existe, sino el primero disponible
    default_iglesia = "SAN DIEGO" if "SAN DIEGO" in iglesias else iglesias[0]
    default_index = iglesias.index(default_iglesia)

    iglesia_seleccionada = st.sidebar.selectbox("Seleccionar Iglesia", iglesias, index=default_index)

    # Calcular el promedio de la columna "Cantidad de lideres" si existe en el Excel
    if 'Cantidad de lideres' in df.columns:
        # Convertir a numérico y calcular el promedio
        promedio_lideres_cero = int(pd.to_numeric(df['Cantidad de lideres'], errors='coerce').mean())
    else:
        # Si no existe la columna, calcular el promedio contando líderes con cero referidos por iglesia
        lideres_cero_por_iglesia = df[df['Referidos Activos'] == 0].groupby('Iglesia').size()
        promedio_lideres_cero = int(lideres_cero_por_iglesia.mean())

    # Filtrar dataframe según selección
    if iglesia_seleccionada != 'Todas':
        df_filtrado = df[df['Iglesia'] == iglesia_seleccionada].copy()
    else:
        df_filtrado = df.copy()

    # Mostrar el dashboard con los datos filtrados
    mostrar_vista_general_visual(df_filtrado, promedio_lideres_cero)

    # Separador
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

if __name__ == "__main__":
    main()
