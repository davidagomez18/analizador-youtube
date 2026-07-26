import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px

# 1. Diseño de la página
st.set_page_config(page_title="Analizador de YouTube", page_icon="📺", layout="wide")
st.title("📺 Analizador de Canales de YouTube")
st.markdown("Busca un tema y descubre qué canales tienen más vistas y suscriptores.")

# 2. Casilla para tu clave secreta (API Key)
st.sidebar.header("⚙️ Configuración")
st.sidebar.markdown("Para que la app funcione, pega tu clave de Google Cloud aquí.")
api_key = st.sidebar.text_input("Tu API Key de YouTube:", type="password")

if not api_key:
    st.warning("👈 Por favor, ingresa tu API Key en el menú de la izquierda para comenzar.")
    st.stop()

# 3. Buscador interactivo
st.subheader("🔍 Buscar canales por temática")
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("¿Qué tema quieres analizar? (Ej: Finanzas, Videojuegos, Recetas)", "Tecnología")
with col2:
    max_results = st.slider("Cantidad de canales", 5, 20, 10)

# 4. Botón de análisis y procesamiento
if st.button("🚀 Analizar Canales"):
    with st.spinner("Buscando datos en YouTube..."):
        try:
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Buscar canales relacionados al tema
            search_response = youtube.search().list(
                q=query, type='channel', order='viewCount', part='id', maxResults=max_results
            ).execute()
            
            channel_ids = [item['id']['channelId'] for item in search_response['items']]
            
            if not channel_ids:
                st.error("No se encontraron canales para ese tema.")
            else:
                # Obtener estadísticas reales de esos canales
                stats_response = youtube.channels().list(
                    part='snippet,statistics', id=','.join(channel_ids)
                ).execute()
                
                canales_data = []
                for item in stats_response['items']:
                    nombre = item['snippet']['title']
                    vistas = int(item['statistics'].get('viewCount', 0))
                    subs = int(item['statistics'].get('subscriberCount', 0))
                    videos = int(item['statistics'].get('videoCount', 0))
                    
                    canales_data.append({
                        "Canal": nombre,
                        "Vistas Totales": vistas,
                        "Suscriptores": subs,
                        "Total de Videos": videos
                    })
                
                # Convertir a tabla y ordenar por más vistos
                df = pd.DataFrame(canales_data)
                df = df.sort_values(by="Vistas Totales", ascending=False)
                
                # Mostrar Tabla
                st.success("¡Datos obtenidos con éxito!")
                st.dataframe(df, use_container_width=True)
                
                # Mostrar Gráficas
                col_graf1, col_graf2 = st.columns(2)
                with col_graf1:
                    st.subheader("📊 Vistas Totales")
                    fig_vistas = px.bar(df, x='Canal', y='Vistas Totales', color='Canal', text_auto='.2s')
                    st.plotly_chart(fig_vistas, use_container_width=True)
                    
                with col_graf2:
                    st.subheader("👥 Suscriptores")
                    fig_subs = px.bar(df, x='Canal', y='Suscriptores', color='Canal', text_auto='.2s')
                    st.plotly_chart(fig_subs, use_container_width=True)
                
        except Exception as e:
            st.error(f"Ocurrió un error. Verifica que tu API Key esté bien copiada y no tenga espacios extra.")
