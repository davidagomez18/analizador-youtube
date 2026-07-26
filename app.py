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
    page_title="ViewPulse SaaS | Intelligence & Discovery",
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
# DICCIONARIO DE NICHOS Y MICRONICHOS
# ==========================================
DICCIONARIO_NICHOS = {
    "Tecnología e Inteligencia Artificial": [
        "Inteligencia Artificial y Tools",
        "Ciberseguridad y Hacking Ético",
        "Smartphones y Reviews de Gadgets",
        "Programación y Desarrollo Software",
        "Tecnología Futurista y Ciencia"
    ],
    "Finanzas, Negocios y Cripto": [
        "Inversiones y Bolsa de Valores",
        "Criptomonedas y Web3",
        "Emprendimiento y E-commerce",
        "Finanzas Personales y Ahorro",
        "Bienes Raíces / Real Estate"
    ],
    "Gaming y Esports": [
        "Minecraft y Sandbox",
        "Shooters (Valorant, CoD, Fortnite)",
        "Guias y Lore de RPGs",
        "Noticias de Gaming y Consolas",
        "Esports y Competición"
    ],
    "Desarrollo Personal y Estilo de Vida": [
        "Productividad y Hábitos",
        "Fitness, Calistenia y Nutrición",
        "Viajes y Vlogs de Estilo de Vida",
        "Minimalismo y Organización",
        "Biohacking y Salud Mental"
    ],
    "Entretenimiento y Cultura Pop": [
        "Cine, Series y Análisis de Guion",
        "Documentales y Casos Misteriosos",
        "Curiosidades y Datos Fascinantes",
        "Humor y Comedia",
        "Música, Beats y Producción"
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

def fetch_top_niches_last_month(youtube):
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

def search_channels_by_keyword(youtube, query_keyword, lang_code="", max_results=12):
    """Busca y extrae los mejores canales basados en una palabra clave e idioma."""
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

        # Obtener estadísticas detalladas
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
            
        # Ordenar por vistas totales
        channels_data.sort(key=lambda x: x["vistas"], reverse=True)
        return channels_data
    except Exception as e:
        st.error(f"Error al buscar canales: {e}")
        return []

# ==========================================
# BARRA LATERAL (CONFIGURACIÓN Y MENÚ)
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
            "🔗 Canales Relacionados por Nicho",
            "🔍 Explorador de Nichos y Micronichos",
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
# SECCIÓN 1: TOP NICHOS DEL ÚLTIMO MES
# ==========================================
if menu == "🔥 Top Nichos del Último Mes":
    st.title("🔥 Nichos y Tendencias con Mayor Crecimiento (Últimos 30 Días)")
    st.markdown("Análisis del mercado en YouTube para identificar temas de alta tracción y contenidos virales recientes.")
    
    with st.spinner("🔍 Cargando tendencias globales del último mes..."):
        top_data = fetch_top_niches_last_month(youtube)
        
    for item in top_data:
        st.markdown(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="margin:0; color:#FFF;">📌 {item['nicho']}</h3>
                <span class="badge-trend">{item['categoria']}</span>
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
# SECCIÓN 2: CANALES RELACIONADOS POR NICHO (NUEVO)
# ==========================================
elif menu == "🔗 Canales Relacionados por Nicho":
    st.title("🔗 Buscador de Canales Relacionados por Nicho")
    st.markdown("Ingresa un canal de referencia y descubre los **mejores canales competidores y afines** de su mismo ecosistema.")
    
    col_input, col_lang = st.columns([3, 1])
    with col_input:
        target_channel = st.text_input("🎯 Canal de Referencia (Handle o Nombre):", "@MrBeast")
    with col_lang:
        selected_lang_label = st.selectbox("🌐 Filtrar Idioma:", list(DICCIONARIO_IDIOMAS.keys()))
        selected_lang_code = DICCIONARIO_IDIOMAS[selected_lang_label]
        
    if st.button("🚀 Buscar Canales Relacionados"):
        with st.spinner(f"Analizando el nicho de {target_channel}..."):
            # 1. Obtener información del canal base
            ch_item, _ = get_channel_complete_info(youtube, target_channel)
            if not ch_item:
                st.error("No se pudo encontrar el canal de referencia.")
            else:
                base_title = ch_item["snippet"]["title"]
                base_desc = ch_item["snippet"].get("description", "")
                
                # Extraer palabras clave del nombre/descripción para buscar el nicho
                search_query = f"{base_title} {base_desc[:100]}"
                related_channels = search_channels_by_keyword(youtube, search_query, lang_code=selected_lang_code, max_results=12)
                
                # Filtrar el propio canal de referencia de los resultados
                related_channels = [c for c in related_channels if c["id"] != ch_item["id"]]
                
                st.markdown(f"### 🎯 Mejores Canales Relacionados con **{base_title}**")
                
                if not related_channels:
                    st.warning("No se encontraron canales relacionados con los filtros seleccionados.")
                else:
                    # Renderizar en Grid de 3 columnas
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
# SECCIÓN 3: EXPLORADOR DE NICHOS Y MICRONICHOS (NUEVO)
# ==========================================
elif menu == "🔍 Explorador de Nichos y Micronichos":
    st.title("🔍 Explorador Inteligente de Canales por Nicho & Micronicho")
    st.markdown("Selecciona una categoría, ajusta el micronicho e idioma para descubrir los **canales con mayor impacto**.")
    
    col_n, col_mn, col_l = st.columns([2, 2, 1])
    
    with col_n:
        sel_nicho = st.selectbox("📌 Selecciona el Nicho:", list(DICCIONARIO_NICHOS.keys()))
    with col_mn:
        sel_micronicho = st.selectbox("🎯 Selecciona el Micronicho:", DICCIONARIO_NICHOS[sel_nicho])
    with col_l:
        sel_lang_lbl = st.selectbox("🌐 Idioma:", list(DICCIONARIO_IDIOMAS.keys()))
        sel_lang_code = DICCIONARIO_IDIOMAS[sel_lang_lbl]
        
    if st.button("🔎 Explorar Mejores Canales"):
        with st.spinner(f"Buscando los líderes de '{sel_micronicho}'..."):
            channels = search_channels_by_keyword(youtube, sel_micronicho, lang_code=sel_lang_code, max_results=12)
            
            if not channels:
                st.warning("No se encontraron canales para esta combinación de filtros.")
            else:
                st.markdown(f"### 🏆 Top Canales Líderes en **{sel_micronicho}**")
                
                # Renderizar en Grid de 3 columnas
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
                st.subheader("🖼️ Catálogo Reciente: Miniaturas y Desempeño")
                
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
