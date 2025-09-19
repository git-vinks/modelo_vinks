# Confidencial
# Proyecto VINKS - Startup Chile CORFO
# ESTE CODIGO ES EXPERIMENTAL
# Autor: DRCSR
# Version: 2.2 Minimal Dashboard

import streamlit as st
import subprocess
import sys
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="VINKS Analytics Suite",
    page_icon="🔬",
    layout="wide"
)

# CSS simple con color morado vibrante
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #9810fa 0%, #8a0ee6 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 6px 20px rgba(152, 16, 250, 0.3);
    }
    
    .app-box {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    
    .app-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(152, 16, 250, 0.1);
        border-color: #9810fa;
    }
    
    .app-title {
        color: #9810fa;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .app-desc {
        color: #4a5568;
        margin-bottom: 1rem;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    .status-online {
        color: #9810fa;
        font-weight: bold;
    }
    
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
    
    /* Modo oscuro */
    @media (prefers-color-scheme: dark) {
        .app-box {
            background: #2d3748 !important;
            border: 1px solid #4a5568 !important;
            color: #e2e8f0 !important;
        }
        
        .app-title {
            color: #c084fc !important;
        }
        
        .app-desc {
            color: #cbd5e0 !important;
        }
    }
    
    /* Botones con color morado vibrante */
    .stButton > button {
        background: linear-gradient(135deg, #9810fa 0%, #8a0ee6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(152, 16, 250, 0.4);
        background: linear-gradient(135deg, #8a0ee6 0%, #7c0dd1 100%);
    }
    
    .stButton > button:disabled {
        background: #6c757d;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)

def get_current_directory():
    return Path(__file__).parent.absolute()

def check_file_exists(app_file):
    return (get_current_directory() / app_file).exists()

def run_app(app_file):
    try:
        app_path = get_current_directory() / app_file
        if not app_path.exists():
            st.error(f"No se encontró: {app_file}")
            return
        
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
        subprocess.Popen(cmd, cwd=str(get_current_directory()))
        st.success(f"✅ {app_file} iniciado correctamente")
        st.info("La aplicación se abrirá en una nueva pestaña")
        
    except Exception as e:
        st.error(f"Error: {e}")

# Aplicaciones disponibles
apps = {
    "app_analizador_final.py": {
        "name": "📈 Analizador de Publicaciones",
        "desc": "Análisis de sentimiento en redes sociales"
    },
    "app_cultura_final.py": {
        "name": "🏢 Análisis de Cultura Organizacional", 
        "desc": "Evaluación de clima laboral"
    },
    "app_recomendador_final.py": {
        "name": "✍️ Recomendador de Contenido",
        "desc": "Sugerencias para contenido digital"
    },
    "app_tendencia_final.py": {
        "name": "🌐 Análisis de Organigrama",
        "desc": "Visualización de estructura organizacional"
    }
}

# Header principal
st.markdown("""
<div class="header-box">
    <h1>🔬 VINKS Analytics Suite</h1>
    <p>Seleccione la aplicación que desea ejecutar</p>
</div>
""", unsafe_allow_html=True)

# Lista de aplicaciones
st.header("🚀 Aplicaciones")

for app_file, info in apps.items():
    file_exists = check_file_exists(app_file)
    status = "✅ Disponible" if file_exists else "❌ No encontrado"
    status_class = "status-online" if file_exists else "status-offline"
    
    st.markdown(f"""
    <div class="app-box">
        <div class="app-title">{info['name']}</div>
        <div class="app-desc">{info['desc']}</div>
        <p class="{status_class}">Estado: {status}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón integrado en la card
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if file_exists:
            if st.button(f"▶️ Ejecutar", key=app_file, use_container_width=True):
                run_app(app_file)
        else:
            st.button("❌ No disponible", disabled=True, key=f"disabled_{app_file}", use_container_width=True)
    
    if app_file != list(apps.keys())[-1]:
        st.markdown("---")

# Información adicional
st.markdown("---")
with st.expander("ℹ️ Información y Uso"):
    st.markdown("""
    ### 🚀 Cómo usar:
    1. Haga clic en "▶️ Ejecutar" dentro de cada aplicación
    2. La aplicación se abrirá en una nueva pestaña del navegador
    3. Puede ejecutar múltiples aplicaciones al mismo tiempo
    
    ### 📁 Archivos requeridos por aplicación:
    - **📈 Analizador de Publicaciones:** posts.xlsx + comments.xlsx
    - **🏢 Cultura Organizacional:** encuesta_clima.xlsx  
    - **✍️ Recomendador de Contenido:** Solo texto (no requiere archivos)
    - **🌐 Análisis de Organigrama:** estructura_org.xlsx
    """)

# Footer minimalista
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1rem; color: #9810fa;'>
    <strong>VINKS Dashboard</strong> 
</div>
""", unsafe_allow_html=True)