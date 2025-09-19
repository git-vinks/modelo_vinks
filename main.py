# Confidencial
# Proyecto VINKS - Startup Chile CORFO
# ESTE CODIGO ES EXPERIMENTAL
# Autor: DRCSR
# Version: 3.0 Multi-Page Dashboard

import streamlit as st
import sys
from pathlib import Path

# Configuración de la página principal
st.set_page_config(
    page_title="VINKS Analytics Suite",
    page_icon="🔬",
    layout="wide"
)

# CSS con color morado vibrante y navegación
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
    
    .nav-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #9810fa;
        margin-bottom: 2rem;
    }
    
    .app-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        cursor: pointer;
    }
    
    .app-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(152, 16, 250, 0.1);
        border-color: #9810fa;
    }
    
    .app-title {
        color: #9810fa;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .app-desc {
        color: #4a5568;
        margin-bottom: 0.5rem;
        line-height: 1.5;
    }
    
    /* Modo oscuro */
    @media (prefers-color-scheme: dark) {
        .nav-container, .app-card {
            background: #2d3748 !important;
            border-color: #9810fa !important;
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
</style>
""", unsafe_allow_html=True)

def get_current_directory():
    return Path(__file__).parent.absolute()

def check_file_exists(app_file):
    return (get_current_directory() / app_file).exists()

# Inicializar estado de sesión para navegación
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

def navigate_to(page):
    """Función para navegar entre páginas"""
    st.session_state.current_page = page
    st.rerun()

def show_home_page():
    """Muestra la página principal del dashboard"""
    # Header principal
    st.markdown("""
    <div class="header-box">
        <h1>🔬 VINKS Analytics Suite</h1>
        <p>Plataforma Integrada de Análisis Empresarial</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navegación
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    st.markdown("### 🚀 Seleccione una aplicación:")
    
    # Aplicaciones en cards clickeables
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Analizador de Publicaciones", key="nav_analizador", use_container_width=True):
            navigate_to('analizador')
        st.markdown("*Análisis de sentimiento en redes sociales*")
        
        if st.button("🏢 Cultura Organizacional", key="nav_cultura", use_container_width=True):
            navigate_to('cultura')
        st.markdown("*Evaluación de clima laboral*")
    
    with col2:
        if st.button("✍️ Recomendador de Contenido", key="nav_recomendador", use_container_width=True):
            navigate_to('recomendador')
        st.markdown("*Sugerencias para contenido digital*")
        
        if st.button("🌐 Análisis de Organigrama", key="nav_tendencia", use_container_width=True):
            navigate_to('tendencia')
        st.markdown("*Visualización de estructura organizacional*")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Información adicional
    st.markdown("---")
    with st.expander("ℹ️ Información y Uso"):
        st.markdown("""
        ### 🚀 Cómo usar:
        1. Haga clic en cualquier botón de aplicación arriba
        2. Cada aplicación mantiene su propia vista y configuración
        3. Use el botón "🏠 Volver al Inicio" en cada aplicación para regresar
        
        ### 📁 Archivos requeridos por aplicación:
        - **📈 Analizador de Publicaciones:** posts.xlsx + comments.xlsx
        - **🏢 Cultura Organizacional:** encuesta_clima.xlsx  
        - **✍️ Recomendador de Contenido:** Solo texto (no requiere archivos)
        - **🌐 Análisis de Organigrama:** estructura_org.xlsx
        """)

def load_app_with_navigation(app_file):
    """Carga una aplicación con botón de navegación"""
    # Botón para volver al inicio
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Volver al Dashboard Principal", key="back_home", use_container_width=True):
            navigate_to('home')
    
    st.markdown("---")
    
    # Cargar el contenido de la aplicación
    try:
        app_path = get_current_directory() / app_file
        if not app_path.exists():
            st.error(f"❌ No se encontró: {app_file}")
            return
        
        # Leer el archivo
        with open(app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Método más simple: reemplazar st.set_page_config por un comentario
        # Esto preserva la indentación original
        lines = code.split('\n')
        filtered_lines = []
        
        for line in lines:
            if 'st.set_page_config(' in line:
                # Comentar la línea en lugar de eliminarla
                filtered_lines.append('# ' + line)
            elif line.strip().startswith('page_title=') or line.strip().startswith('page_icon=') or line.strip().startswith('layout='):
                # Comentar líneas de configuración de página
                filtered_lines.append('# ' + line)
            else:
                filtered_lines.append(line)
        
        filtered_code = '\n'.join(filtered_lines)
        
        # Ejecutar el código filtrado
        exec(filtered_code, globals())
        
    except Exception as e:
        st.error(f"❌ Error al cargar {app_file}:")
        st.exception(e)
        
        # Mostrar información de depuración
        st.markdown("### 🔧 Información de Debug:")
        st.code(f"Error en línea: {e}")
        
        # Opción para mostrar el código filtrado para debugging
        with st.expander("Ver código filtrado (para debugging)"):
            st.code(filtered_code[:1000] + "..." if len(filtered_code) > 1000 else filtered_code)

# Lógica principal de navegación
if st.session_state.current_page == 'home':
    show_home_page()
elif st.session_state.current_page == 'analizador':
    load_app_with_navigation('app_analizador_final.py')
elif st.session_state.current_page == 'cultura':
    load_app_with_navigation('app_cultura_final.py')
elif st.session_state.current_page == 'recomendador':
    load_app_with_navigation('app_recomendador_final.py')
elif st.session_state.current_page == 'tendencia':
    load_app_with_navigation('app_tendencia_final.py')

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1rem; color: #9810fa;'>
    <strong>VINKS Dashboard v3.0</strong> | Sistema Multi-Página
</div>
""", unsafe_allow_html=True)