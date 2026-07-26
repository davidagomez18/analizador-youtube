import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import re

# ==========================================
# CONFIGURACIÓN Y ESTILOS UI ULTRA-MODERNOS
# ==========================================
st.set_page_config(
    page_title="ViewPulse SaaS | Intelligence & Trends",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado: Dark Glassmorphism, Tarjetas con Miniaturas, Avatares y Grid Responsivo
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #0A0C10;
        color: #F0F3F9;
    }
    
    /* Tarjeta Neomórfica / Glassmorphism */
    .saas-card {
        background: rgba(18, 22, 31, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .saas-card:hover {
        border-color: rgba(255, 0, 0, 0.4);
        transform: translateY(-2px);
    }
    
    /* Tarjeta de Vídeo */
    .video-card {
        background: #12161F;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 15px;
    }
    
    .video-thumb {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Avatar de Canal */
    .channel-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 2px solid #FF0000;
        object-fit: cover;
    }
    
    .channel-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 15px;
    }
    
    /* Badges de Tendencia y Categoría */
    .badge-trend {
        background: linear-gradient(135deg, #FF0000 0%, #B30000 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .badge-metric {
        background: rgba(255, 255, 255, 0.08);
        color: #3B82F6;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Pasos del Tutorial */
    .step-box {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #FF0000;
        padding: 15px 20px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# FUNCIONES DE EXTRACCIÓN Y API DE YOUTUBE
# ==========================================
def parse_iso_duration(duration_str):
    if not duration_str: return 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match: return 0
    return int(match.group(1) or 0)*3600 + int(match.group(2) or 0)*60 + int(match.group(3) or 0)

def format_num(num):
    if num is None or num == 0: return "0"
    if num >= 1_000_000_000: return f"{num/1_000_000_000:.1f}B"
    if num >= 1_000_000: return f"{num/1_000_000:.1f}M"
    if num >= 1_000: return f"{num/1_000:.1f}K"
    return str(num)

def fetch_top_niches_last_month(youtube):
    """Obtiene los temas y vídeos de mayor rendimiento del último mes."""
    niches = [
        {"nombre": "Inteligencia Artificial & Herramientas", "query": "IA herramientas tutorial", "categoria": "Tecnología"},
        {"nombre": "Finanzas & Cripto", "query": "inversiones finanzas crypto", "categoria": "Negocios"},
        {"nombre": "Gaming & Esports", "query": "gaming gameplay español", "categoria": "Entretenimiento"},
        {"nombre": "Productividad & Estilo de Vida", "query": "hábitos rutina productividad", "categoria": "Desarrollo Personal"},
        {"nombre": "Documentales & Storytelling", "query": "documental misterio historia", "categoria": "Cultura"}
    ]
    
    now = datetime.now(timezone.utc)
    one_month_ago = (now - timedelta(days=30)).isoformat()
    
    results = []
    for niche in niches:
        try:
            res = youtube.search().list(
                q=niche["query"],
                type="video",
                order="viewCount",
                publishedAfter=one_month_ago,
                maxResults=3,
                part="snippet"
            ).execute()
            
            videos = []
            for item in res.get("items", []):
                v_id = item["id"]["videoId"]
                # Detalle de estadísticas del vídeo
                v_res = youtube.videos().list(part="statistics,contentDetails,snippet", id=v_id).execute()
                if v_res.get("items"):
                    v_data = v_res["items"][0]
                    videos.append({
                        "titulo": v_data["snippet"]["title"],
                        "canal": v_data["snippet"]["channelTitle"],
                        "channel_id": v_data["snippet"]["channelId"],
                        "vistas": int(v_data["statistics"].get("viewCount", 0)),
                        "likes": int(v_data["statistics"].get("likeCount", 0)),
                        "thumb": v_data["snippet"]["thumbnails"]["medium"]["url"]
                    })
            
            results.append({
                "nicho": niche["nombre"],
                "categoria": niche["categoria"],
                "videos": videos
            })
        except Exception:
            pass
    return results

def get_channel_complete_info(youtube, query):
    """Obtiene datos completos del canal incluyendo logo HD."""
    try:
        if query.startswith("@") or query.startswith("UC"):
            res = youtube.channels().list(
                part="snippet,statistics,contentDetails",
                forHandle=query if query.startswith("@") else None,
                id=query if query.startswith("UC") else None
            ).execute()
        else:
            s_res = youtube.search().list(q=query, type="channel", maxResults=1, part="id").execute()
            if not s_res.get("items"): return None, None
            c_id = s_res["items"][0]["id"]["channelId"]
            res = youtube.channels().list(part="snippet,statistics,contentDetails", id=c_id).execute()
            
        if not res.get("items"): return None, None
        
        ch_item = res["items"][0]
        uploads_id = ch_item["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # Obtener vídeos
        p_res = youtube.playlistItems().list(
            part="snippet,contentDetails", playlistId=uploads_id, maxResults=12
        ).execute()
        
        v_ids = [item["contentDetails"]["videoId"] for item in p_res.get("items", [])]
        v_details = []
        if v_ids:
            vd_res = youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(v_ids)).execute()
            v_details = vd_res.get("items", [])
            
        return ch_item, v_details
    except Exception as e:
        return None, None

# ==========================================
# BARRA LATERAL (CONFIGURACIÓN Y MENU)
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #FF0000; margin:0; font-weight: 800;">⚡ ViewPulse</h2>
        <p style="font-size: 0.8rem; color: #888;">YouTube Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input("🔑 Tu Clave API de YouTube:", type="password", placeholder="AIzaSy...")
    
    st.markdown("---")
    
    menu = st.radio(
        "Navegación:",
        [
            "🔥 Top Nichos del Último Mes",
            "📊 Auditoría Visual de Canal",
            "📘 ¿Cómo sacar tu API Key?"
        ]
    )
    
    st.markdown("---")
    st.caption("🚀 powered by **YouTube Data API v3**")

# ==========================================
# SECCIÓN 1: TUTORIAL DE API KEY (SIEMPRE DISPONIBLE)
# ==========================================
if menu == "📘 ¿Cómo sacar tu API Key?":
    st.title("📘 Cómo obtener tu API Key de YouTube en 3 minutos")
    st.markdown("Sigue estos sencillos pasos para activar tu clave de acceso **100% gratuita** con Google:")
    
    st.markdown("""
    <div class="step-box">
        <h4>Paso 1: Entrar a Google Cloud Console</h4>
        <p>Ve a <a href="https://console.cloud.google.com/" target="_blank" style="color:#3B82F6;">console.cloud.google.com</a> e inicia sesión con cualquier cuenta de Gmail.</p>
    </div>
    
    <div class="step-box">
        <h4>Paso 2: Crear un Proyecto Nuevo</h4>
        <p>En el menú superior azul, haz clic en el desplegable de proyectos y selecciona <strong>"Proyecto Nuevo"</strong>. Ponle de nombre <code>Analizador-YouTube</code> y dale a <strong>Crear</strong>.</p>
    </div>
    
    <div class="step-box">
        <h4>Paso 3: Activar la YouTube Data API v3</h4>
        <p>En el buscador superior de la página, escribe <code>YouTube Data API v3</code>, entra en el resultado y presiona el botón azul grande de <strong>HABILITAR</strong>.</p>
    </div>
    
    <div class="step-box">
        <h4>Paso 4: Generar la Clave</h4>
        <p>En el menú lateral izquierdo, ve a <strong>Credenciales</strong> ➔ haz clic en <strong>"+ Crear credenciales"</strong> (arriba) ➔ elige <strong>"Clave de API"</strong>.</p>
    </div>
    
    <div class="step-box">
        <h4>Paso 5: Copiar y Usar</h4>
        <p>Copia el código largo que empieza por <code>AIzaSy...</code> y pégalo en la casilla de la izquierda en esta app. ¡Listo!</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Si no hay API key ingresada, mostrar advertencia y guía rápida
if not api_key:
    st.warning("👈 Por favor, ingresa tu **API Key de YouTube** en el menú de la izquierda para comenzar.")
    st.info("💡 ¿No tienes una clave aún? Selecciona la opción **'📘 ¿Cómo sacar tu API Key?'** en el menú lateral.")
    st.stop()

# Inicializar cliente de YouTube
try:
    youtube = build("youtube", "v3", developerKey=api_key)
except Exception as e:
    st.error("Error al autenticar la API Key. Verifica que esté correctamente copiada.")
    st.stop()

# ==========================================
# SECCIÓN 2: PANTALLA PRINCIPAL - TOP NICHOS DEL ÚLTIMO MES
# ==========================================
if menu == "🔥 Top Nichos del Último Mes":
    st.title("🔥 Nichos y Tendencias con Mayor Crecimiento (Últimos 30 Días)")
    st.markdown("Análisis automático del mercado en YouTube para identificar temas con alta tracción y vídeos más virales.")
    
    with st.spinner("🔍 Analizando tendencias globales del último mes en YouTube..."):
        top_data = fetch_top_niches_last_month(youtube)
        
    if not top_data:
        st.error("No se pudieron cargar las tendencias. Asegúrate de que tu API Key sea válida.")
    else:
        for item in top_data:
            st.markdown(f"""
            <div class="saas-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h3 style="margin:0; color:#FFF;">📌 {item['nicho']}</h3>
                    <span class="badge-trend">{item['categoria']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Columnas de vídeos del nicho con Miniaturas y Canales
            cols = st.columns(len(item["videos"]))
            for idx, vid in enumerate(item["videos"]):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="video-card">
                        <img src="{vid['thumb']}" class="video-thumb" />
                        <div style="padding: 12px;">
                            <p style="font-weight:700; font-size:0.85rem; margin-bottom:5px; height: 40px; overflow: hidden; color: #FFF;">{vid['titulo']}</p>
                            <p style="font-size:0.75rem; color:#888; margin-bottom:8px;">📺 <strong>{vid['canal']}</strong></p>
                            <div style="display:flex; gap:8px;">
                                <span class="badge-metric">👁️ {format_num(vid['vistas'])}</span>
                                <span class="badge-metric">👍 {format_num(vid['likes'])}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 3: AUDITORÍA VISUAL DE CANAL CON MINIATURAS Y LOGO
# ==========================================
elif menu == "📊 Auditoría Visual de Canal":
    st.title("📊 Auditoría Estratégica de Canal")
    
    channel_query = st.text_input("🔍 Ingresa el Handle o Nombre del Canal a auditar:", "@MrBeast")
    
    if st.button("🚀 Iniciar Análisis Visual"):
        with st.spinner("Cargando perfil, miniaturas y métricas del canal..."):
            ch_data, v_details = get_channel_complete_info(youtube, channel_query)
            
            if not ch_data:
                st.error("No se encontró el canal. Verifica el nombre o handle ingresado.")
            else:
                snippet = ch_data["snippet"]
                stats = ch_data["statistics"]
                
                logo_url = snippet["thumbnails"]["high"]["url"]
                title = snippet["title"]
                desc = snippet.get("description", "Sin descripción disponible.")
                subs = int(stats.get("subscriberCount", 0)) if not stats.get("hiddenSubscriberCount") else None
                views = int(stats.get("viewCount", 0))
                videos_count = int(stats.get("videoCount", 0))
                
                # --- HEADER CON LOGO Y DATOS ---
                st.markdown(f"""
                <div class="saas-card">
                    <div class="channel-header">
                        <img src="{logo_url}" class="channel-avatar" />
                        <div>
                            <h2 style="margin:0; color:#FFF;">{title}</h2>
                            <p style="margin:0; color:#888; font-size:0.85rem;">ID: {ch_data['id']} | País: {snippet.get('country', 'N/A')}</p>
                        </div>
                    </div>
                    <p style="font-size:0.85rem; color:#CCC; line-height:1.4;">{desc[:250]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                # METRICAS CLAVE
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("👥 Suscriptores", format_num(subs) if subs else "Ocultos")
                m2.metric("👁️ Vistas Totales", format_num(views))
                m3.metric("🎬 Total de Vídeos", format_num(videos_count))
                
                avg_views = int(views / max(videos_count, 1))
                m4.metric("📈 Promedio Vistas/Vídeo", format_num(avg_views))
                
                st.markdown("---")
                st.subheader("🖼️ Catálogo Reciente: Miniaturas y Desempeño")
                
                if v_details:
                    # Mostrar vídeos en un Grid Visual de 3 columnas
                    for i in range(0, len(v_details), 3):
                        cols = st.columns(3)
                        for j in range(3):
                            if i + j < len(v_details):
                                v = v_details[i + j]
                                v_snip = v["snippet"]
                                v_stat = v.get("statistics", {})
                                
                                v_thumb = v_snip["thumbnails"]["medium"]["url"]
                                v_title = v_snip["title"]
                                v_views = int(v_stat.get("viewCount", 0))
                                v_likes = int(v_stat.get("likeCount", 0))
                                v_comments = int(v_stat.get("commentCount", 0))
                                
                                with cols[j]:
                                    st.markdown(f"""
                                    <div class="video-card">
                                        <img src="{v_thumb}" class="video-thumb" />
                                        <div style="padding: 12px;">
                                            <p style="font-weight:700; font-size:0.85rem; margin-bottom:8px; height: 40px; overflow: hidden; color: #FFF;">{v_title}</p>
                                            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                                                <span class="badge-metric">👁️ {format_num(v_views)} vistas</span>
                                                <span class="badge-metric">👍 {format_num(v_likes)}</span>
                                            </div>
                                            <p style="font-size:0.75rem; color:#888; margin-top:5px;">💬 {format_num(v_comments)} comentarios</p>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
