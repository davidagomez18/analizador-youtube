import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import re

# ==========================================
# CONFIGURACIÓN Y ESTILOS UI ULTRA-MODERNOS (AI FOCUS)
# ==========================================
st.set_page_config(
    page_title="ViewPulse AI | YouTube AI Channel Intelligence",
    page_icon="🤖",
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
    
    /* Tarjeta de Canal */
    .channel-card {
        background: #12161F;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        transition: border-color 0.2s;
    }
    
    .channel-card:hover {
        border-color: #FF0000;
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
        width: 70px;
        height: 70px;
        border-radius: 50%;
        border: 2px solid #FF0000;
        object-fit: cover;
        margin-bottom: 10px;
    }
    
    .channel-avatar-sm {
        width: 50px;
        height: 50px;
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
    
    .badge-ai {
        background: rgba(22, 199, 132, 0.15);
        color: #16C784;
        border: 1px solid #16C784;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
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
# DICCIONARIO ESPECÍFICO DE NICHOS IA
# ==========================================
DICCIONARIO_NICHOS_IA = {
    "🎬 Canales Faceless & Historias IA": [
        "Historias de Terror y Misterio IA",
        "Documentales e Historia Antigua IA",
        "Filosofía, Estoicismo y Motivación IA",
        "Cuentos y Leyendas Animadas IA",
        "Casos Criminales y True Crime IA"
    ],
    "🤖 Avatares & Presentadores Sintéticos": [
        "Noticias y Actualidad con Avatares IA",
        "Explicaciones Científicas y Espacio IA",
        "Finanzas y Cripto con Presentador IA",
        "Salud, Curiosidades y Biología IA",
        "Resúmenes de Libros y Desarrollo IA"
    ],
    "⚡ Shorts Virales & Contenido Rápido IA": [
        "Curiosidades y Datos 'Sabías Que' IA",
        "Quiz, Acertijos y Preguntas IA",
        "Comparativas y Escalas Visuales IA",
        "Historias Bíblicas o Mitología IA",
        "Lifehacks y Experimentos IA"
    ],
    "🎵 Música, Relax y Contenido Sensorial IA": [
        "Música Lo-Fi y Beats Creados con IA",
        "Frecuencias de Meditación y Relax IA",
        "ASMR Visual y Animaciones IA",
        "Canciones y Parodias Generadas con IA",
        "Fondos de Pantalla Animados IA"
    ],
    "🚀 Automatización & Herramientas de IA": [
        "Canales de Automatización de YouTube",
        "Tutoriales de HeyGen / Midjourney / ElevenLabs",
        "Creación de Vídeos Automatizados",
        "Monetización de Canales Faceless IA",
        "Agentes y Herramientas IA para Creadores"
    ]
}

DICCIONARIO_IDIOMAS = {
    "Todos los idiomas": "",
    "Español 🇪🇸": "es",
    "Inglés 🇺🇸": "en",
    "Portugués 🇧🇷": "pt",
    "Francés 🇫🇷": "fr"
}

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def format_num(num):
    if num is None or num == 0: return "0"
    if num >= 1_000_000_000: return f"{num/1_000_000_000:.1f}B"
    if num >= 1_000_000: return f"{num/1_000_000:.1f}M"
    if num >= 1_000: return f"{num/1_000:.1f}K"
    return str(num)

def fetch_top_ai_niches_last_month(youtube):
    """Busca los vídeos y canales basados en IA con más vistas en los últimos 30 días."""
    niches_ia = [
        {"nombre": "Historias & Documentales IA", "query": "historia IA generado faceless", "categoria": "Faceless IA"},
        {"nombre": "Shorts Virales & Curiosidades IA", "query": "datos curiosos IA shorts faceless", "categoria": "Shorts IA"},
        {"nombre": "Avatares & Noticias IA", "query": "avatar IA noticias explicacion", "categoria": "Sintéticos"},
        {"nombre": "Música & Lo-Fi Generado con IA", "query": "lofi AI generated music relax", "categoria": "Audio IA"},
        {"nombre": "Automatización de Canales IA", "query": "crear canal con inteligencia artificial faceless", "categoria": "Growth IA"}
    ]
    
    now = datetime.now(timezone.utc)
    one_month_ago = (now - timedelta(days=30)).isoformat()
    
    results = []
    for niche in niches_ia:
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
                v_res = youtube.videos().list(part="statistics,snippet", id=v_id).execute()
                if v_res.get("items"):
                    v_data = v_res["items"][0]
                    videos.append({
                        "titulo": v_data["snippet"]["title"],
                        "canal": v_data["snippet"]["channelTitle"],
                        "vistas": int(v_data["statistics"].get("viewCount", 0)),
                        "likes": int(v_data["statistics"].get("likeCount", 0)),
                        "thumb": v_data["snippet"]["thumbnails"]["medium"]["url"]
                    })
            results.append({"nicho": niche["nombre"], "categoria": niche["categoria"], "videos": videos})
        except Exception:
            pass
    return results

def get_channel_complete_info(youtube, query):
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
        
        p_res = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=uploads_id, maxResults=12).execute()
        v_ids = [item["contentDetails"]["videoId"] for item in p_res.get("items", [])]
        v_details = []
        if v_ids:
            vd_res = youtube.videos().list(part="snippet,statistics,contentDetails", id=",".join(v_ids)).execute()
            v_details = vd_res.get("items", [])
            
        return ch_item, v_details
    except Exception:
        return None, None

def search_ai_channels_by_keyword(youtube, query_keyword, lang_code="", max_results=12):
    """Filtra y busca específicamente canales enfocados en IA/Faceless."""
    try:
        # Añadir contexto de IA a la búsqueda si no lo tiene implícito
        full_query = f"{query_keyword} IA AI faceless"
        
        search_kwargs = {
            "q": full_query,
            "type": "channel",
            "order": "viewCount",
            "maxResults": max_results,
            "part": "snippet"
        }
        if lang_code:
            search_kwargs["relevanceLanguage"] = lang_code

        s_res = youtube.search().list(**search_kwargs).execute()
        channel_ids = [item["snippet"]["channelId"] for item in s_res.get("items", [])]
        
        if not channel_ids:
            return []

        c_res = youtube.channels().list(
            part="snippet,statistics",
            id=",".join(channel_ids)
        ).execute()

        channels_data = []
        for item in c_res.get("items", []):
            snip = item["snippet"]
            stat = item["statistics"]
            channels_data.append({
                "id": item["id"],
                "titulo": snip["title"],
                "desc": snip.get("description", ""),
                "logo": snip["thumbnails"]["high"]["url"],
                "subs": int(stat.get("subscriberCount", 0)) if not stat.get("hiddenSubscriberCount") else 0,
                "vistas": int(stat.get("viewCount", 0)),
                "videos": int(stat.get("videoCount", 0)),
                "custom_url": snip.get("customUrl", "")
            })
            
        channels_data.sort(key=lambda x: x["vistas"], reverse=True)
        return channels_data
    except Exception as e:
        st.error(f"Error al buscar canales de IA: {e}")
        return []

# ==========================================
# BARRA LATERAL (CONFIGURACIÓN Y MENÚ)
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #FF0000; margin:0; font-weight: 800;">🤖 ViewPulse AI</h2>
        <p style="font-size: 0.8rem; color: #16C784; font-weight: 600;">Plataforma para Canales de IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input("🔑 Tu Clave API de YouTube:", type="password", placeholder="AIzaSy...")
    
    st.markdown("---")
    
    menu = st.radio(
        "Navegación:",
        [
            "🔥 Top Nichos de IA del Último Mes",
            "🔗 Canales de IA Relacionados",
            "🔍 Explorador por Nicho & Micronicho IA",
            "📊 Auditoría Visual de Canal IA",
            "📘 ¿Cómo sacar tu API Key?"
        ]
    )
    
    st.markdown("---")
    st.caption("🤖 Enfocado 100% en **Canales Creados con IA**")

# ==========================================
# SECCIÓN: TUTORIAL API KEY
# ==========================================
if menu == "📘 ¿Cómo sacar tu API Key?":
    st.title("📘 Cómo obtener tu API Key de YouTube en 3 minutos")
    st.markdown("""
    <div class="step-box">
        <h4>Paso 1: Entrar a Google Cloud Console</h4>
        <p>Ve a <a href="https://console.cloud.google.com/" target="_blank" style="color:#3B82F6;">console.cloud.google.com</a> e inicia sesión con tu correo.</p>
    </div>
    <div class="step-box">
        <h4>Paso 2: Crear un Proyecto Nuevo</h4>
        <p>En la barra superior, haz clic en el selector de proyectos y crea uno llamado <code>Analizador-YouTube-IA</code>.</p>
    </div>
    <div class="step-box">
        <h4>Paso 3: Activar la YouTube Data API v3</h4>
        <p>Busca <code>YouTube Data API v3</code> en el buscador superior y presiona el botón azul <strong>HABILITAR</strong>.</p>
    </div>
    <div class="step-box">
        <h4>Paso 4: Generar la Clave</h4>
        <p>Ve a <strong>Credenciales</strong> ➔ <strong>"+ Crear credenciales"</strong> ➔ <strong>"Clave de API"</strong>.</p>
    </div>
    <div class="step-box">
        <h4>Paso 5: Copiar y Usar</h4>
        <p>Copia la clave generada y pégala en la barra lateral de esta aplicación.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Verificación de API Key
if not api_key:
    st.warning("👈 Por favor, ingresa tu **API Key de YouTube** en el menú de la izquierda para comenzar.")
    st.info("💡 ¿No tienes una clave aún? Haz clic en la opción **'📘 ¿Cómo sacar tu API Key?'** en el menú lateral.")
    st.stop()

try:
    youtube = build("youtube", "v3", developerKey=api_key)
except Exception:
    st.error("Error al autenticar la API Key. Verifica que esté correctamente copiada.")
    st.stop()

# ==========================================
# SECCIÓN 1: TOP NICHOS DE IA
# ==========================================
if menu == "🔥 Top Nichos de IA del Último Mes":
    st.title("🔥 Top Nichos y Contenidos de IA con Mayor Crecimiento (30 Días)")
    st.markdown("Análisis automático enfocado en la galaxia de **canales creados con Inteligencia Artificial** (*Faceless*, Avatares, Historias, Lo-Fi, etc.).")
    
    with st.spinner("🔍 Cargando tendencias de contenido generado por IA..."):
        top_data = fetch_top_ai_niches_last_month(youtube)
        
    for item in top_data:
        st.markdown(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin:0; color:#FFF;">📌 {item['nicho']}</h3>
                <span class="badge-ai">{item['categoria']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(item["videos"]))
        for idx, vid in enumerate(item["videos"]):
            with cols[idx]:
                st.markdown(f"""
                <div class="video-card">
                    <img src="{vid['thumb']}" class="video-thumb" />
                    <div style="padding: 12px;">
                        <p style="font-weight:700; font-size:0.85rem; margin-bottom:5px; height: 40px; overflow: hidden; color: #FFF;">{vid['titulo']}</p>
                        <p style="font-size:0.75rem; color:#888; margin-bottom:8px;">🤖 <strong>{vid['canal']}</strong></p>
                        <div style="display:flex; gap:8px;">
                            <span class="badge-metric">👁️ {format_num(vid['vistas'])}</span>
                            <span class="badge-metric">👍 {format_num(vid['likes'])}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 2: CANALES DE IA RELACIONADOS
# ==========================================
elif menu == "🔗 Canales de IA Relacionados":
    st.title("🔗 Buscador de Canales Competidores en el Nicho de IA")
    st.markdown("Ingresa un canal de referencia y descubre los **mejores canales creados con IA** dentro de su misma temática.")
    
    col_input, col_lang = st.columns([3, 1])
    with col_input:
        target_channel = st.text_input("🎯 Canal de Referencia IA (Handle o Nombre):", "@CreacionesIA")
    with col_lang:
        selected_lang_label = st.selectbox("🌐 Filtrar Idioma:", list(DICCIONARIO_IDIOMAS.keys()))
        selected_lang_code = DICCIONARIO_IDIOMAS[selected_lang_label]
        
    if st.button("🚀 Buscar Canales de IA Competidores"):
        with st.spinner(f"Analizando competidores de IA para {target_channel}..."):
            ch_item, _ = get_channel_complete_info(youtube, target_channel)
            if not ch_item:
                st.error("No se pudo encontrar el canal de referencia.")
            else:
                base_title = ch_item["snippet"]["title"]
                base_desc = ch_item["snippet"].get("description", "")
                
                search_query = f"{base_title} {base_desc[:80]}"
                related_channels = search_ai_channels_by_keyword(youtube, search_query, lang_code=selected_lang_code, max_results=12)
                
                related_channels = [c for c in related_channels if c["id"] != ch_item["id"]]
                
                st.markdown(f"### 🎯 Mejores Canales de IA Competidores de **{base_title}**")
                
                if not related_channels:
                    st.warning("No se encontraron canales de IA relacionados con esos filtros.")
                else:
                    for i in range(0, len(related_channels), 3):
                        cols = st.columns(3)
                        for j in range(3):
                            if i + j < len(related_channels):
                                c = related_channels[i + j]
                                with cols[j]:
                                    handle_str = f"@{c['custom_url']}" if c['custom_url'] else ""
                                    st.markdown(f"""
                                    <div class="channel-card">
                                        <img src="{c['logo']}" class="channel-avatar" />
                                        <h4 style="margin:0 0 5px 0; color:#FFF; font-size:1rem;">{c['titulo']}</h4>
                                        <p style="color:#888; font-size:0.75rem; margin-bottom:10px;">{handle_str}</p>
                                        <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:center; margin-bottom:12px;">
                                            <span class="badge-metric">👥 {format_num(c['subs'])} subs</span>
                                            <span class="badge-metric">👁️ {format_num(c['vistas'])} vistas</span>
                                        </div>
                                        <p style="font-size:0.75rem; color:#AAA; height:45px; overflow:hidden; margin-bottom:10px;">{c['desc'][:90]}...</p>
                                        <a href="https://youtube.com/channel/{c['id']}" target="_blank" style="color:#FF0000; text-decoration:none; font-weight:700; font-size:0.8rem;">Ver Canal en YouTube ↗</a>
                                    </div>
                                    """, unsafe_allow_html=True)

# ==========================================
# SECCIÓN 3: EXPLORADOR DE NICHOS Y MICRONICHOS IA
# ==========================================
elif menu == "🔍 Explorador por Nicho & Micronicho IA":
    st.title("🔍 Explorador de Canales por Nicho & Micronicho de IA")
    st.markdown("Selecciona una categoría de creación con Inteligencia Artificial, ajusta el micronicho e idioma para descubrir los canales más exitosos.")
    
    col_n, col_mn, col_l = st.columns([2, 2, 1])
    
    with col_n:
        sel_nicho = st.selectbox("📌 Categoría de IA:", list(DICCIONARIO_NICHOS_IA.keys()))
    with col_mn:
        sel_micronicho = st.selectbox("🎯 Micronicho de IA:", DICCIONARIO_NICHOS_IA[sel_nicho])
    with col_l:
        sel_lang_lbl = st.selectbox("🌐 Idioma:", list(DICCIONARIO_IDIOMAS.keys()))
        sel_lang_code = DICCIONARIO_IDIOMAS[sel_lang_lbl]
        
    if st.button("🔎 Explorar Canales de IA"):
        with st.spinner(f"Buscando los canales más vistos en '{sel_micronicho}'..."):
            channels = search_ai_channels_by_keyword(youtube, sel_micronicho, lang_code=sel_lang_code, max_results=12)
            
            if not channels:
                st.warning("No se encontraron canales de IA para esta combinación de filtros.")
            else:
                st.markdown(f"### 🤖 Top Canales de IA en **{sel_micronicho}**")
                
                for i in range(0, len(channels), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i + j < len(channels):
                            c = channels[i + j]
                            with cols[j]:
                                handle_str = f"@{c['custom_url']}" if c['custom_url'] else ""
                                st.markdown(f"""
                                <div class="channel-card">
                                    <img src="{c['logo']}" class="channel-avatar" />
                                    <h4 style="margin:0 0 5px 0; color:#FFF; font-size:1rem;">{c['titulo']}</h4>
                                    <p style="color:#888; font-size:0.75rem; margin-bottom:10px;">{handle_str}</p>
                                    <div style="display:flex; gap:6px; flex-wrap:wrap; justify-content:center; margin-bottom:12px;">
                                        <span class="badge-metric">👥 {format_num(c['subs'])} subs</span>
                                        <span class="badge-metric">👁️ {format_num(c['vistas'])} vistas</span>
                                    </div>
                                    <p style="font-size:0.75rem; color:#AAA; height:45px; overflow:hidden; margin-bottom:10px;">{c['desc'][:90]}...</p>
                                    <a href="https://youtube.com/channel/{c['id']}" target="_blank" style="color:#FF0000; text-decoration:none; font-weight:700; font-size:0.8rem;">Ver Canal en YouTube ↗</a>
                                </div>
                                """, unsafe_allow_html=True)

# ==========================================
# SECCIÓN 4: AUDITORÍA VISUAL DE CANAL IA
# ==========================================
elif menu == "📊 Auditoría Visual de Canal IA":
    st.title("📊 Auditoría Visual de Canal Creado con IA")
    
    channel_query = st.text_input("🔍 Ingresa el Handle o Nombre del Canal IA a auditar:", "@AIHistorias")
    
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
                
                st.markdown(f"""
                <div class="saas-card">
                    <div class="channel-header">
                        <img src="{logo_url}" class="channel-avatar-sm" />
                        <div>
                            <h2 style="margin:0; color:#FFF;">{title} <span class="badge-ai">IA Channel</span></h2>
                            <p style="margin:0; color:#888; font-size:0.85rem;">ID: {ch_data['id']} | País: {snippet.get('country', 'N/A')}</p>
                        </div>
                    </div>
                    <p style="font-size:0.85rem; color:#CCC; line-height:1.4;">{desc[:250]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("👥 Suscriptores", format_num(subs) if subs else "Ocultos")
                m2.metric("👁️ Vistas Totales", format_num(views))
                m3.metric("🎬 Total de Vídeos", format_num(videos_count))
                m4.metric("📈 Promedio Vistas/Vídeo", format_num(int(views / max(videos_count, 1))))
                
                st.markdown("---")
                st.subheader("🖼️ Catálogo Reciente: Miniaturas y Rendimiento")
                
                if v_details:
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
