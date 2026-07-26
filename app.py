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
    page_title="ViewPulse | Los 10 Nichos Potentes de YouTube",
    page_icon="🚀",
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
    
    /* Badges */
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
# LOS 10 NICHOS Y MICRONICHOS POTENTES
# ==========================================
DICCIONARIO_10_NICHOS = {
    "⚽ Fútbol + Polémica": [
        "Fiascos y Arbitrajes Polémicos",
        "Transferencias Millonarias y Estafas",
        "Peleas y Conflictos de Futbolistas",
        "Decisiones Polémicas del VAR"
    ],
    "❓ ¿Qué pasaría si...?": [
        "Escenarios Hipotéticos de la Humanidad",
        "Ciencia y Eventos Apocalípticos",
        "Experimentos Mentales y Futuro",
        "Teorías de Historia Alternativa"
    ],
    "✝️ Religión y Profecías": [
        "Misterios y Profecías Bíblicas",
        "Milagros Modernos y Apariciones",
        "El Apocalipsis y Fin de los Tiempos",
        "Secretos de la Arqueología Sagrada"
    ],
    "🕵️‍♂️ Casos Criminales (True Crime)": [
        "Interrogatorios y Grabaciones Reales",
        "Desapariciones Misteriosas Sin Resolver",
        "Perfiles de Asesinos y Criminales",
        "Archivos Extraños y Casos Perturbadores"
    ],
    "🌐 Geopolítico + Morbo": [
        "Guerras Secretas y Espionaje",
        "Conflictos Internacionales y Tensiones",
        "Secretos Gubernamentales y Poder",
        "Análisis de Geopolítica Global"
    ],
    "🛸 Misterios y Conspiraciones": [
        "Área 51 y Fenómenos Extraterrestres",
        "Civilizaciones Perdidas y Enigmas",
        "Experimentos Secretos e Historia Oculta",
        "Teorías de Conspiración Populares"
    ],
    "🎵 Canciones con IA en Loop": [
        "Loops Virales de Música 10 Horas",
        "Covers Virales de Canciones con IA",
        "Musica Relax y Beats para Estudiar",
        "Parodias Musicales y Personajes"
    ],
    "💎 Lujos y Millonarios": [
        "Vida Oculta de los Multimillonarios",
        "Supercoches y Mansiones Incredibles",
        "Fortunas y Estilos de Vida Extremos",
        "Negocios Gigantes y Cómo Hicieron Dinero"
    ],
    "👽 Historias Oscuras de Reddit": [
        "Confesiones Anónimas Aterradoras",
        "Historias Perturbadoras de Reddit",
        "Misterios Reales Confesados en Internet",
        "Relatos de Terror y Anécdotas Extrañas"
    ],
    "🎬 Cine y Famosos": [
        "Escándalos y Vida Oculta de Famosos",
        "Secretos Oscuros de Hollywood",
        "Caídas y Cancelaciones de Celebridades",
        "Errores e Historias Inéditas de Películas"
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
# FUNCIONES AUXILIARES DE YOUTUBE DATA API
# ==========================================
def format_num(num):
    if num is None or num == 0: return "0"
    if num >= 1_000_000_000: return f"{num/1_000_000_000:.1f}B"
    if num >= 1_000_000: return f"{num/1_000_000:.1f}M"
    if num >= 1_000: return f"{num/1_000:.1f}K"
    return str(num)

def fetch_top_10_niches_trending(youtube):
    """Busca vídeos virales recientes de los 10 nichos potentes."""
    niches_list = [
        {"nombre": "Fútbol + Polémica", "query": "futbol polemica arbitraje fiascos", "categoria": "Deportes"},
        {"nombre": "¿Qué pasaría si...?", "query": "que pasaria si ciencia humanidad", "categoria": "Curiosidades"},
        {"nombre": "Casos Criminales (True Crime)", "query": "casos criminales true crime misterio", "categoria": "True Crime"},
        {"nombre": "Historias Oscuras de Reddit", "query": "historias reddit terror confesiones", "categoria": "Relatos"},
        {"nombre": "Lujos y Millonarios", "query": "lujos millonarios fortuna mansiones", "categoria": "Estilo de Vida"}
    ]
    
    now = datetime.now(timezone.utc)
    one_month_ago = (now - timedelta(days=30)).isoformat()
    
    results = []
    for niche in niches_list:
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

def search_channels_global(youtube, query_keyword, lang_code="", max_results=12):
    """Busca los mejores canales en YouTube de forma abierta y directa."""
    try:
        search_kwargs = {
            "q": query_keyword,
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
        st.error(f"Error en la búsqueda de canales: {e}")
        return []

# ==========================================
# BARRA LATERAL (CONFIGURACIÓN Y MENÚ)
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #FF0000; margin:0; font-weight: 800;">🚀 ViewPulse</h2>
        <p style="font-size: 0.8rem; color: #888;">Los 10 Nichos Potentes de YouTube</p>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input("🔑 Tu Clave API de YouTube:", type="password", placeholder="AIzaSy...")
    
    st.markdown("---")
    
    menu = st.radio(
        "Navegación:",
        [
            "🔥 Tendencias en los 10 Nichos",
            "🔗 Canales Relacionados por Nicho",
            "🔍 Explorador por Nicho & Micronicho",
            "📊 Auditoría Visual de Canal",
            "📘 ¿Cómo sacar tu API Key?"
        ]
    )
    
    st.markdown("---")
    st.caption("🚀 powered by **YouTube Data API v3**")

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
        <p>En la barra superior, haz clic en el selector de proyectos y crea uno llamado <code>Analizador-YouTube</code>.</p>
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
# SECCIÓN 1: TENDENCIAS EN LOS 10 NICHOS
# ==========================================
if menu == "🔥 Tendencias en los 10 Nichos":
    st.title("🔥 Vídeos Virales Recientes en los Nichos Más Potentes")
    st.markdown("Análisis automático del mercado de YouTube en los formatos de mayor crecimiento e impacto del último mes.")
    
    with st.spinner("🔍 Cargando vídeos más vistos del mercado..."):
        top_data = fetch_top_10_niches_trending(youtube)
        
    for item in top_data:
        st.markdown(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin:0; color:#FFF;">📌 {item['nicho']}</h3>
                <span class="badge-trend">{item['categoria']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if item["videos"]:
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
        else:
            st.info("No se encontraron vídeos en las últimas semanas para esta categoría.")
            
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SECCIÓN 2: CANALES RELACIONADOS POR NICHO
# ==========================================
elif menu == "🔗 Canales Relacionados por Nicho":
    st.title("🔗 Buscador de Canales Competidores por Nicho")
    st.markdown("Ingresa un canal de referencia y descubre los **mejores canales competidores** de su misma categoría.")
    
    col_input, col_lang = st.columns([3, 1])
    with col_input:
        target_channel = st.text_input("🎯 Canal de Referencia (Handle o Nombre):", "@MrBeast")
    with col_lang:
        selected_lang_label = st.selectbox("🌐 Filtrar Idioma:", list(DICCIONARIO_IDIOMAS.keys()))
        selected_lang_code = DICCIONARIO_IDIOMAS[selected_lang_label]
        
    if st.button("🚀 Buscar Canales Competidores"):
        with st.spinner(f"Analizando competidores para {target_channel}..."):
            ch_item, _ = get_channel_complete_info(youtube, target_channel)
            if not ch_item:
                st.error("No se pudo encontrar el canal de referencia.")
            else:
                base_title = ch_item["snippet"]["title"]
                base_desc = ch_item["snippet"].get("description", "")
                
                search_query = f"{base_title} {base_desc[:80]}"
                related_channels = search_channels_global(youtube, search_query, lang_code=selected_lang_code, max_results=12)
                
                related_channels = [c for c in related_channels if c["id"] != ch_item["id"]]
                
                st.markdown(f"### 🎯 Mejores Canales Competidores de **{base_title}**")
                
                if not related_channels:
                    st.warning("No se encontraron canales relacionados con esos filtros.")
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
# SECCIÓN 3: EXPLORADOR DE NICHOS Y MICRONICHOS
# ==========================================
elif menu == "🔍 Explorador por Nicho & Micronicho":
    st.title("🔍 Explorador por Nicho & Micronicho Potente")
    st.markdown("Selecciona una de las 10 categorías principales de la lista, ajusta el micronicho e idioma para descubrir los canales líderes.")
    
    col_n, col_mn, col_l = st.columns([2, 2, 1])
    
    with col_n:
        sel_nicho = st.selectbox("📌 Selecciona el Nicho Potente:", list(DICCIONARIO_10_NICHOS.keys()))
    with col_mn:
        sel_micronicho = st.selectbox("🎯 Selecciona el Micronicho:", DICCIONARIO_10_NICHOS[sel_nicho])
    with col_l:
        sel_lang_lbl = st.selectbox("🌐 Idioma:", list(DICCIONARIO_IDIOMAS.keys()))
        sel_lang_code = DICCIONARIO_IDIOMAS[sel_lang_lbl]
        
    if st.button("🔎 Explorar Canales Líderes"):
        with st.spinner(f"Buscando canales con más vistas en '{sel_micronicho}'..."):
            channels = search_channels_global(youtube, sel_micronicho, lang_code=sel_lang_code, max_results=12)
            
            if not channels:
                st.warning("No se encontraron canales para esta combinación de filtros.")
            else:
                st.markdown(f"### 🏆 Top Canales Líderes en **{sel_micronicho}**")
                
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
# SECCIÓN 4: AUDITORÍA VISUAL DE CANAL
# ==========================================
elif menu == "📊 Auditoría Visual de Canal":
    st.title("📊 Auditoría Visual de Canal")
    
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
                
                st.markdown(f"""
                <div class="saas-card">
                    <div class="channel-header">
                        <img src="{logo_url}" class="channel-avatar-sm" />
                        <div>
                            <h2 style="margin:0; color:#FFF;">{title}</h2>
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
