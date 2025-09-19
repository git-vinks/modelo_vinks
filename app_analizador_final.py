# Confidencial
# Proyecto VINKS - Startup Chile CORFO
# ESTE CODIGO ES EXPERIMENTAL
# Autor: DRCSR
# Version: 1.1 Alpha

import streamlit as st
import pandas as pd
from transformers import pipeline
import plotly.express as px

st.set_page_config(layout="wide", page_title="análisis de publicaciones y comunidad")

@st.cache_resource
def cargar_modelo_sentimiento():
    return pipeline(
        "sentiment-analysis",
        model="pysentimiento/robertuito-sentiment-analysis", #Se puede usar otro BERT pero no lo recomiendo
        truncation=True
    )

@st.cache_resource
def cargar_modelo_clasificacion():
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

@st.cache_data
def procesar_archivos(posts_file, comments_file):
    df_posts = pd.read_excel(posts_file)
    df_comments = pd.read_excel(comments_file)

    required_post_cols = ['post_id', 'created_time', 'message', 'permalink_url', 'total_reactions', 'comments_count', 'shares']
    for col in required_post_cols:
        if col not in df_posts.columns:
            raise KeyError(f"la columna requerida '{col}' no se encontró en el archivo de publicaciones.")

    df_posts.rename(columns={'created_time': 'fecha', 'message': 'texto_post'}, inplace=True)
    df_posts['fecha'] = pd.to_datetime(df_posts['fecha'])
    df_posts['texto_post'] = df_posts['texto_post'].fillna('')
    df_posts = df_posts.sort_values(by='fecha', ascending=True).reset_index(drop=True)

    sentiment_analyzer = cargar_modelo_sentimiento()
    textos_validos = df_posts[df_posts['texto_post'].str.strip().str.len() > 0]['texto_post'].tolist()
    if textos_validos:
        resultados_sentimiento = sentiment_analyzer(textos_validos)
        sentimientos_df = pd.DataFrame(resultados_sentimiento)
        sentimientos_df.index = df_posts[df_posts['texto_post'].str.strip().str.len() > 0].index
        df_posts['sentiment_label'] = sentimientos_df['label']
        df_posts['sentiment_score'] = sentimientos_df['score']
    
    df_comments.rename(columns={'id_post': 'post_id', 'message': 'texto_comentario'}, inplace=True)
    df_comments['texto_comentario'] = df_comments['texto_comentario'].fillna('')
    
    return df_posts, df_comments

@st.cache_data
def analizar_comentarios(post_id, _df_comments, _sentiment_analyzer):
    comentarios_post = _df_comments[_df_comments['post_id'] == post_id]['texto_comentario'].dropna().tolist()
    comentarios_validos = [c for c in comentarios_post if str(c).strip()]
    if not comentarios_validos:
        return pd.DataFrame(), {}

    resultados = _sentiment_analyzer(comentarios_validos)
    df_sentimientos = pd.DataFrame(resultados)
    df_sentimientos['texto_comentario'] = comentarios_validos
    
    conteo_sentimientos = df_sentimientos['label'].value_counts().to_dict()
    return df_sentimientos, conteo_sentimientos

@st.cache_data
def extraer_temas_negativos(comentarios_negativos, _classifier):
    if not comentarios_negativos:
        return {}
    
    texto_completo = ". ".join(comentarios_negativos)
    temas_candidatos = [
        "calidad del producto", "servicio al cliente", "problemas de envío", 
        "precio o costo", "información engañosa", "mala experiencia", "opinión política"
    ]
    resultado = _classifier(texto_completo, candidate_labels=temas_candidatos, multi_label=True)
    
    temas_relevantes = {label: score for label, score in zip(resultado['labels'], resultado['scores']) if score > 0.6}
    return dict(sorted(temas_relevantes.items(), key=lambda item: item[1], reverse=True)[:3])

def generar_recomendaciones(conteo_sentimientos, temas_negativos):
    recomendaciones = []
    total_comentarios = sum(conteo_sentimientos.values())
    if total_comentarios == 0:
        return ["no existen comentarios suficientes para generar una recomendación."]

    neg_count = conteo_sentimientos.get('NEG', 0)
    pos_count = conteo_sentimientos.get('POS', 0)
    neg_percentage = (neg_count / total_comentarios) * 100
    pos_percentage = (pos_count / total_comentarios) * 100

    if neg_percentage > 20:
        recomendaciones.append(
            f"**Atención:** más del {neg_percentage:.0f}% de los comentarios son negativos. se requiere atención inmediata."
        )
        if temas_negativos:
            primer_tema = list(temas_negativos.keys())[0]
            recomendaciones.append(
                f"**causa principal:** el tema recurrente es '{primer_tema}'. **acción sugerida:** se recomienda derivar esta publicación y sus comentarios al equipo de {primer_tema.split(' ')[0]} para coordinar una respuesta. prepare una declaración pública si fuese necesario."
            )
        else:
            recomendaciones.append(
                "**acción sugerida:** realice un análisis manual de los comentarios negativos para identificar el problema central y responda a los usuarios más críticos de manera proactiva."
            )
    elif pos_percentage > 60:
        recomendaciones.append(
            f"**contenido exitoso:** esta publicación ha generado una reacción muy positiva ({pos_percentage:.0f}% de comentarios positivos). excelente gestión."
        )
        recomendaciones.append(
            "**acción sugerida:** considere promocionar esta publicación para ampliar su alcance. analice su formato y mensaje para replicar el éxito en comunicaciones futuras."
        )
    else:
        recomendaciones.append(
            "**recepción mixta:** la reacción de la comunidad es variada. no se detectan alertas críticas, pero se recomienda supervisar la conversación."
        )
        recomendaciones.append(
            "**acción sugerida:** identifique y responda las preguntas o dudas legítimas en los comentarios para mejorar la percepción y demostrar una escucha activa."
        )
        
    return recomendaciones

st.title("Panel de análisis de reputación en publicaciones")
st.markdown("Cargue sus archivos para visualizar la línea de tiempo, analizar la reacción de la comunidad y obtener recomendaciones estratégicas.")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

with st.sidebar:
    st.header("Carga de datos")
    uploaded_posts_file = st.file_uploader("1. Cargue el archivo de publicaciones", type=["xlsx"])
    uploaded_comments_file = st.file_uploader("2. Cargue el archivo de comentarios", type=["xlsx"])

    if uploaded_posts_file and uploaded_comments_file:
        if st.button("Procesar y analizar todo"):
            with st.spinner("Procesando archivos y analizando publicaciones..."):
                try:
                    df_posts, df_comments = procesar_archivos(uploaded_posts_file, uploaded_comments_file)
                    st.session_state.df_posts = df_posts
                    st.session_state.df_comments = df_comments
                    st.session_state.data_loaded = True
                    st.success("Los datos se han cargado y procesado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"se ha producido un error durante el procesamiento: {e}")
                    st.session_state.data_loaded = False

if st.session_state.data_loaded:
    df_posts = st.session_state.df_posts
    df_comments = st.session_state.df_comments
    sentiment_analyzer = cargar_modelo_sentimiento()
    classifier = cargar_modelo_clasificacion()

    st.header("línea de tiempo analítica (desde la más antigua a la más reciente)")
    for index, post in df_posts.iterrows():
        with st.spinner(f"analizando los comentarios de la publicación del {post['fecha'].strftime('%d-%b-%Y')}..."): #No pude poner el mes en español, posiblemente sea la libreria. Revisar antes de montar en lambda.
            df_sentimientos_com, conteo_sentimientos = analizar_comentarios(post['post_id'], df_comments, sentiment_analyzer)
        
        fecha_str = post['fecha'].strftime('%d de %B de %Y')
        expander_title = f"publicación del {fecha_str} | {post['comments_count']} comentarios"
        with st.expander(expander_title):
            col_post, col_reaccion, col_recomendacion = st.columns([1.5, 1, 1.5])
            
            with col_post:
                st.subheader("contenido y métricas de la publicación")
                st.markdown(post['texto_post'] if post['texto_post'] else "_esta publicación no contiene texto._")
                if 'sentiment_label' in post and pd.notna(post['sentiment_label']):
                    sentimiento_post = {'POS': 'positivo', 'NEU': 'neutral', 'NEG': 'negativo'}.get(post['sentiment_label'])
                    st.markdown(f"**sentimiento de la publicación:** {sentimiento_post}")
                st.markdown(f"**reacciones:** {post.get('total_reactions', 0):,} | **veces compartido:** {post.get('shares', 0):,}")
                st.markdown(f"[ver publicación original]({post['permalink_url']})", unsafe_allow_html=True)

            with col_reaccion:
                st.subheader("reacción de la comunidad")
                if not conteo_sentimientos:
                    st.info("no existen comentarios para analizar.")
                else:
                    df_pie = pd.DataFrame(conteo_sentimientos.items(), columns=['sentimiento', 'cantidad'])
                    color_map = {'POS': 'green', 'NEU': 'grey', 'NEG': 'red'}
                    fig = px.pie(df_pie, values='cantidad', names='sentimiento', 
                                 title='sentimiento de los comentarios', color='sentimiento',
                                 color_discrete_map=color_map)
                    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=40, b=0))
                    
                    st.plotly_chart(fig, use_container_width=True, key=f"pie_chart_{index}")

            with col_recomendacion:
                st.subheader("diagnóstico y acciones")
                
                comentarios_negativos = [] 
                if not df_sentimientos_com.empty:
                    comentarios_negativos = df_sentimientos_com[df_sentimientos_com['label'] == 'NEG']['texto_comentario'].tolist()

                temas_negativos = extraer_temas_negativos(comentarios_negativos, classifier)
                
                if temas_negativos:
                    st.warning("temas principales en comentarios negativos:")
                    for tema, score in temas_negativos.items():
                        st.markdown(f"- **{tema}** (confianza: {score:.0%})")

                recomendaciones = generar_recomendaciones(conteo_sentimientos, temas_negativos)
                st.info("recomendaciones estratégicas:")
                for rec in recomendaciones:
                    st.markdown(f"- {rec}")
else:
    st.info("Por favor, cargue ambos archivos de Excel y presione 'procesar y analizar' en la barra lateral para comenzar.")