# Confidencial
# Proyecto VINKS - Startup Chile CORFO
# ESTE CODIGO ES EXPERIMENTAL
# Autor: DRCSR
# Version: 1.0 operacional

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from statistics import mode, StatisticsError
import re
from transformers import pipeline
from collections import Counter

STOPWORDS_ES = set([
    "y","en","de","la","el","los","las","un","una","unos","unas",
    "que","por","para","con","sin","es","son","al","como","pero",
    "muy","más","menos","su","sus","le","lo","se","del","mi","tu",
    "ya","sí","no","me","te","a","o","u","ha","han","ser","fue",
    "soy","era","está","están","estaba","estuve","etcétera","siendo","cada",
    "cuando","donde","nuestro","nuestra","también","porque","entre"
])

def calcular_moda_serie(serie):
    valores = [x for x in serie.dropna()]
    if len(valores) == 0:
        return None
    try:
        return mode(valores)
    except StatisticsError:
        return Counter(valores).most_common(1)[0][0]

def limpiar_arquetipo(texto):
    if pd.isna(texto):
        return None
    limpio = re.sub(r"[^\w\s-]", "", str(texto)).strip()
    if "–" in limpio:
        limpio = limpio.split("–")[0].strip()
    elif "-" in limpio:
        limpio = limpio.split("-")[0].strip()
    return limpio

def nube_palabras(textos):
    texto = " ".join([str(t) for t in textos if pd.notna(t)])
    if not texto.strip():
        return None
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        stopwords=STOPWORDS_ES,
        collocations=False
    ).generate(texto)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    return fig

def grafico_categorico(column):
    conteo = column.astype(str).str.split("|").explode().str.strip().value_counts()
    if conteo.empty:
        return None
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=conteo.values, y=conteo.index, ax=ax, palette="viridis")
    ax.set_xlabel("frecuencia")
    ax.set_ylabel("categoría")
    st.pyplot(fig)

def agrupar_edad(df):
    if "edad" not in df.columns:
        return df
    bins = [0, 20, 30, 40, 50, 200]
    labels = ["0-20", "21-30", "31-40", "41-50", "50+"]
    df["grupo_etario"] = pd.cut(df["edad"], bins=bins, labels=labels, right=True)
    return df

def analizar_sentimiento_texto(textos, nlp_model):
    resultados = []
    for t in textos:
        if pd.isna(t) or not str(t).strip():
            resultados.append("neutro")
        else:
            res = nlp_model(str(t)[:512])
            label = res[0]["label"]
            if label == "POS":
                resultados.append("positivo")
            elif label == "NEG":
                resultados.append("negativo")
            else:
                resultados.append("neutro")
    return resultados

def categorias_negativas(textos):
    todo = " ".join([str(t) for t in textos if pd.notna(t)])
    palabras = [w.lower() for w in re.findall(r"\b\w+\b", todo) if w.lower() not in STOPWORDS_ES and len(w) > 2]
    return Counter(palabras).most_common(10)

def generar_recomendaciones_desde_feedback(temas_negativos, demografia_afectada):
    recommendations = {}
    
    tasks_temas = []
    palabras_clave = [tema[0] for tema in temas_negativos]

    mapa_temas = {
        ("comunicacion", "informacion", "transparencia"): {
            "problema": "la comunicación interna parece ser un punto de dolor.",
            "accion": "implementar reuniones generales quincenales y crear un boletín semanal con actualizaciones clave."
        },
        ("salario", "sueldo", "compensacion", "paga"): {
            "problema": "existe insatisfacción con la compensación.",
            "accion": "realizar un estudio de mercado de salarios para asegurar la competitividad y comunicar claramente la política de compensación."
        },
        ("lider", "jefe", "gerente", "liderazgo"): {
            "problema": "el estilo de liderazgo o la gestión directa está generando fricción.",
            "accion": "lanzar un programa de capacitación para gerentes enfocado en retroalimentación constructiva y comunicación efectiva."
        },
        ("carga", "trabajo", "estres", "horario", "horas"): {
            "problema": "hay una percepción de sobrecarga de trabajo y posible agotamiento.",
            "accion": "revisar la distribución de tareas en los equipos más afectados y promover activamente políticas de desconexión digital."
        },
        ("crecimiento", "carrera", "oportunidades", "desarrollo"): {
            "problema": "los empleados no perciben un camino claro de desarrollo profesional.",
            "accion": "definir y comunicar planes de carrera claros para cada rol y asignar presupuestos para formación y certificaciones."
        },
        ("reconocimiento", "valorado", "gracias"): {
            "problema": "existe una falta de reconocimiento por el trabajo bien realizado.",
            "accion": "crear un programa de reconocimiento entre pares y capacitar a los líderes para entregar retroalimentación positiva de forma regular."
        }
    }

    for keywords, details in mapa_temas.items():
        if any(palabra in palabras_clave for palabra in keywords):
            tasks_temas.append(f"**problema:** {details['problema']} **acción sugerida:** {details['accion']}")
    
    if tasks_temas:
        recommendations['temas críticos'] = tasks_temas

    tasks_demografia = []
    if 'rol' in demografia_afectada:
        rol = demografia_afectada['rol']
        tasks_demografia.append(f"el rol de **{rol}** concentra la mayor cantidad de retroalimentación negativa. **acción sugerida:** organice una sesión de grupo focal con este colectivo para profundizar en sus preocupaciones específicas.")

    if 'edad' in demografia_afectada:
        edad = demografia_afectada['edad']
        tasks_demografia.append(f"el grupo etario de **{edad} años** muestra una mayor insatisfacción. **acción sugerida:** analice si las políticas de beneficios y desarrollo profesional están alineadas con las expectativas de esta generación.")
    
    if 'genero' in demografia_afectada:
        genero = demografia_afectada['genero']
        tasks_demografia.append(f"se ha detectado una mayor prevalencia de comentarios negativos en el género **{genero}**. **acción sugerida:** revise las políticas de equidad, inclusión y oportunidades de crecimiento para asegurar que no existan sesgos inconscientes.")

    if tasks_demografia:
        recommendations['grupos de enfoque'] = tasks_demografia
        
    return recommendations

st.set_page_config(page_title="análisis organizacional", layout="wide")
st.title("panel de inteligencia organizacional")

uploaded_file = st.file_uploader("cargue un archivo excel con los datos de la encuesta", type=["xlsx", "xls"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("archivo cargado con éxito.")

    for col in ["arquetipo_asociado", "arquetipo_asociado_usuario"]:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(limpiar_arquetipo)

    df = agrupar_edad(df)

    st.sidebar.header("filtros")
    if "rol" in df.columns:
        roles = ["todos"] + sorted(df["rol"].dropna().unique().tolist())
        selected_rol = st.sidebar.selectbox("seleccione un grupo de interés (rol)", roles)
        if selected_rol != "todos":
            df_filtrado = df[df["rol"] == selected_rol].copy()
            st.info(f"filtrando resultados para el rol: **{selected_rol}**")
        else:
            df_filtrado = df.copy()
            st.info("mostrando resultados para todos los grupos de interés")
    else:
        df_filtrado = df.copy()

    @st.cache_resource
    def load_model():
        return pipeline("sentiment-analysis", model="finiteautomata/beto-sentiment-analysis")
    nlp_model = load_model()

    tabs = st.tabs([
        "visión general",
        "segmentación por género",
        "segmentación por edad",
        "análisis de texto",
        "enfoque en respuestas negativas",
        "resumen y recomendaciones"
    ])

    with tabs[0]:
        st.header("resultados generales")
        st.subheader("indicadores de escala (Likert)")
        likert_cols = ["integridad", "coherencia_valores", "comunicacion", "escucha", "satisfaccion", "confianza_marca"]
        for col in likert_cols:
            if col in df_filtrado.columns:
                st.write(f"**{col.replace('_', ' ')}** → promedio: {df_filtrado[col].mean():.2f}, moda: {calcular_moda_serie(df_filtrado[col])}")
        
        st.subheader("temas en respuestas abiertas ('resumen_historia')")
        if "resumen_historia" in df_filtrado.columns:
            fig_wc = nube_palabras(df_filtrado["resumen_historia"])
            if fig_wc:
                st.pyplot(fig_wc)
        
        st.subheader("análisis de categorías")
        for col in ["emociones", "arquetipo_asociado"]:
            if col in df_filtrado.columns:
                st.write(f"**distribución de '{col.replace('_', ' ')}'**")
                grafico_categorico(df_filtrado[col].dropna())

    with tabs[1]:
        st.header("segmentación por género")
        if "genero" in df_filtrado.columns:
            for genero in df_filtrado["genero"].dropna().unique():
                sub = df_filtrado[df_filtrado["genero"] == genero]
                st.subheader(f"resultados para el género: {genero} (n={len(sub)})")
                for col in ["integridad", "satisfaccion", "confianza_marca"]:
                    if col in sub.columns:
                        st.write(f"**{col.replace('_', ' ')}** → promedio: {sub[col].mean():.2f}, moda: {calcular_moda_serie(sub[col])}")

    with tabs[2]:
        st.header("segmentación por grupo etario")
        if "grupo_etario" in df_filtrado.columns:
            for grupo in sorted(df_filtrado["grupo_etario"].dropna().unique().tolist()):
                sub = df_filtrado[df_filtrado["grupo_etario"] == grupo]
                st.subheader(f"resultados para el grupo etario: {grupo} (n={len(sub)})")
                for col in ["integridad", "satisfaccion", "confianza_marca"]:
                    if col in sub.columns:
                        st.write(f"**{col.replace('_', ' ')}** → promedio: {sub[col].mean():.2f}, moda: {calcular_moda_serie(sub[col])}")

    with tabs[3]:
        st.header("análisis de sentimiento") #USANDO BERT O BETO EN ESPAÑOL OJO AQUI CON LA LIBRERÍA
        text_cols = ["resumen_historia", "rituales", "motivacion_texto", "conoce_proposito"]
        for col in text_cols:
            if col in df_filtrado.columns:
                st.subheader(f"sentimiento en '{col.replace('_', ' ')}'")
                if f"sent_{col}" not in df_filtrado.columns:
                    df_filtrado[f"sent_{col}"] = analizar_sentimiento_texto(df_filtrado[col], nlp_model)
                st.bar_chart(df_filtrado[f"sent_{col}"].value_counts())

    with tabs[4]:
        st.header("detalle de respuestas con sentimiento negativo")
        text_cols_for_sentiment = ["resumen_historia", "rituales", "motivacion_texto", "conoce_proposito"]
        for col in text_cols_for_sentiment:
            if col in df_filtrado.columns and f"sent_{col}" not in df_filtrado.columns:
                df_filtrado[f"sent_{col}"] = analizar_sentimiento_texto(df_filtrado[col], nlp_model)

        negativos = pd.DataFrame()
        for sent, orig in [("sent_resumen_historia", "resumen_historia"),
                           ("sent_rituales", "rituales"),
                           ("sent_motivacion_texto", "motivacion_texto"),
                           ("sent_conoce_proposito", "conoce_proposito")]:
            if sent in df_filtrado.columns:
                sub = df_filtrado[df_filtrado[sent] == "negativo"].copy()
                if not sub.empty:
                    display_cols = [col for col in ["rol", "genero", "grupo_etario", orig] if col in sub.columns]
                    sub_display = sub[display_cols]
                    sub_display = sub_display.rename(columns={orig: "respuesta_negativa"})
                    sub_display["columna_origen"] = orig
                    negativos = pd.concat([negativos, sub_display])

        if not negativos.empty:
            st.write(f"se encontraron **{len(negativos)}** respuestas clasificadas como negativas.")
            st.dataframe(negativos)
        else:
            st.success("no se encontraron respuestas con sentimiento negativo en los datos filtrados.")

    with tabs[5]:
        st.header("resumen de puntos críticos y recomendaciones")
        
        if 'negativos' in locals() and not negativos.empty:
            st.write(f"análisis sobre las **{len(negativos)}** respuestas negativas identificadas:")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("temas principales")
                todas_resp_neg = negativos["respuesta_negativa"].dropna().tolist()
                frecuentes = categorias_negativas(todas_resp_neg)
                if frecuentes:
                    df_frecuentes = pd.DataFrame(frecuentes, columns=["palabra", "frecuencia"])
                    st.table(df_frecuentes)
            
            with col2:
                st.subheader("grupos más afectados")
                demografia_afectada = {}
                if "grupo_etario" in negativos.columns:
                    comunes_edad = negativos["grupo_etario"].value_counts().idxmax()
                    st.write(f"grupo etario: **{comunes_edad}**")
                    demografia_afectada['edad'] = comunes_edad
                if "genero" in negativos.columns:
                    comunes_gen = negativos["genero"].value_counts().idxmax()
                    st.write(f"género: **{comunes_gen}**")
                    demografia_afectada['genero'] = comunes_gen
                if "rol" in negativos.columns and selected_rol == "todos":
                    rol_max = negativos["rol"].value_counts().idxmax()
                    st.write(f"rol (grupo de interés): **{rol_max}**")
                    demografia_afectada['rol'] = rol_max
            
            st.markdown("---")
            
            st.header("recomendaciones para la acción")
            st.info("basado en el diagnóstico de la retroalimentación, a continuación se presenta una lista de acciones sugeridas para abordar los puntos críticos identificados.")
            
            recommendations = generar_recomendaciones_desde_feedback(frecuentes, demografia_afectada)
            
            if not recommendations:
                st.success("no se activaron alertas automáticas significativas basadas en la retroalimentación negativa.")
            else:
                for category, tasks in recommendations.items():
                    with st.expander(f"{category} ({len(tasks)} sugerencias)", expanded=True):
                        for task in tasks:
                            st.markdown(f"- {task}")

        else:
            st.info("no hay datos negativos disponibles para generar este resumen.")