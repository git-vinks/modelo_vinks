# Confidencial
# Proyecto VINKS - Startup Chile CORFO
# ESTE CODIGO ES EXPERIMENTAL
# Autor: DRCSR
# Version: 1.7 Alpha

import streamlit as st
from transformers import pipeline

st.set_page_config(layout="wide", page_title="asistente y analizador de contenido")

categorias = {
    "personas": {
        "empleo": ["LinkedIn"], "inclusión": ["LinkedIn", "Instagram"], "diversidad": ["LinkedIn", "Instagram"],
        "bienestar": ["Facebook", "Instagram"], "seguridad": ["LinkedIn"], "salud laboral": ["LinkedIn"],
        "capacitación": ["LinkedIn"], "desarrollo profesional": ["LinkedIn"], "retención de talento": ["LinkedIn"],
        "clima laboral": ["LinkedIn", "Facebook"], "cultura organizacional": ["LinkedIn"], "liderazgo": ["LinkedIn"],
        "equidad": ["LinkedIn", "Instagram"], "remuneración": ["LinkedIn"], "beneficios": ["Facebook", "LinkedIn"],
        "reconocimiento": ["LinkedIn", "Facebook"], "conciliación vida-trabajo": ["LinkedIn"],
        "salud mental": ["Instagram", "Facebook"], "derechos humanos": ["Twitter", "LinkedIn"],
        "derechos laborales": ["Twitter", "LinkedIn"], "plan de carrera": ["LinkedIn"],
        "igualdad de oportunidades": ["LinkedIn", "Instagram"], "ética laboral": ["LinkedIn"],
        "prevención de riesgos": ["LinkedIn"], "comunicación interna": ["LinkedIn"], "relaciones laborales": ["LinkedIn", "Facebook"]
    },
    "nuestra operación": {
        "alto estándar": ["LinkedIn"], "innovación": ["LinkedIn", "Twitter"], "tecnología": ["LinkedIn", "Twitter"],
        "operación limpia": ["LinkedIn", "Instagram"], "trabajo": ["LinkedIn"], "sueldo": ["Facebook"],
        "Antioquia": ["Facebook"], "minería": ["LinkedIn", "Twitter"], "eficiencia operativa": ["LinkedIn"],
        "productividad": ["LinkedIn"], "optimización de procesos": ["LinkedIn"], "mejora continua": ["LinkedIn"],
        "excelencia operacional": ["LinkedIn"], "gestión de riesgos": ["LinkedIn", "Twitter"],
        "seguridad industrial": ["LinkedIn"], "cumplimiento normativo": ["LinkedIn"], "certificaciones": ["LinkedIn"],
        "protocolos de seguridad": ["LinkedIn"], "cadena de suministro": ["LinkedIn"], "logística": ["LinkedIn"],
        "infraestructura": ["LinkedIn", "Facebook"], "mantenimiento": ["LinkedIn"], "automatización": ["LinkedIn", "Twitter"],
        "digitalización": ["LinkedIn", "Twitter"], "producción responsable": ["LinkedIn", "Instagram"],
        "exploración": ["Twitter", "LinkedIn"], "inversión": ["LinkedIn"], "calidad": ["LinkedIn"]
    },
    "medioambiente": {
        "biodiversidad": ["Instagram", "Facebook"], "gestión del agua": ["Instagram", "LinkedIn"],
        "economía circular": ["LinkedIn", "Twitter"], "huella de carbono": ["LinkedIn", "Twitter"],
        "cambio climático": ["Twitter", "LinkedIn"], "eficiencia energética": ["LinkedIn", "Twitter"],
        "energías renovables": ["LinkedIn", "Instagram"], "gestión de residuos": ["Instagram", "Facebook"],
        "calidad del aire": ["Twitter", "Facebook"], "reforestación": ["Instagram", "Facebook"],
        "conservación": ["Instagram", "Facebook"], "cierre de minas": ["Twitter", "LinkedIn"],
        "remediación ambiental": ["Instagram", "LinkedIn"], "gestión de relaves": ["Twitter", "LinkedIn"],
        "monitoreo ambiental": ["LinkedIn", "Twitter"], "uso de suelo": ["Twitter", "LinkedIn"],
        "protección de ecosistemas": ["Instagram", "Twitter"], "pasivos ambientales": ["Twitter", "LinkedIn"],
        "emisiones": ["Twitter", "LinkedIn"], "calidad del suelo": ["Twitter", "LinkedIn"],
        "plan de manejo ambiental": ["LinkedIn"], "sostenibilidad": ["Instagram", "LinkedIn"]
    },
    "territorio": {
        "desarrollo": ["Facebook", "LinkedIn"], "desarrollo social": ["Facebook"], "desarrollo económico": ["LinkedIn"],
        "formalización minera": ["LinkedIn"], "fortalecimiento": ["Facebook", "LinkedIn"], "comunidad": ["Facebook"],
        "desarrollo local": ["Facebook"], "inversión social": ["Facebook"], "infraestructura comunitaria": ["Facebook"],
        "educación local": ["Facebook", "Instagram"], "salud comunitaria": ["Facebook", "Instagram"],
        "proyectos productivos": ["Facebook", "LinkedIn"], "desarrollo de proveedores": ["LinkedIn"],
        "emprendimiento": ["Instagram", "LinkedIn"], "fortalecimiento institucional": ["LinkedIn"],
        "gobernanza": ["LinkedIn"], "diálogo social": ["Facebook", "Twitter"], "relacionamiento comunitario": ["Facebook"],
        "consulta previa": ["Twitter", "LinkedIn"], "patrimonio cultural": ["Instagram", "Facebook"],
        "alianzas público-privadas": ["LinkedIn"], "compras locales": ["Facebook"], "calidad de vida comunitaria": ["Facebook"],
        "impacto social": ["Instagram", "Facebook"], "ordenamiento territorial": ["Facebook", "LinkedIn"]
    },
    "participación y comunicación": {
        "atención": ["Facebook"], "comunidad": ["Facebook"], "reunión comunitaria": ["Facebook"],
        "rendición de cuentas": ["Twitter", "Facebook"], "medios de comunicación": ["Twitter"],
        "línea de atención": ["Facebook"], "diálogo con grupos de interés": ["LinkedIn", "Twitter"],
        "transparencia": ["Twitter", "LinkedIn"], "comunicación de crisis": ["Twitter"], "redes sociales": ["Twitter", "Instagram"],
        "comunicados de prensa": ["Twitter", "LinkedIn"], "informe de sostenibilidad": ["LinkedIn"],
        "mesas de diálogo": ["Facebook"], "mecanismos de queja": ["Facebook"], "escucha activa": ["Facebook"],
        "retroalimentación": ["Facebook"], "relaciones públicas": ["LinkedIn"], "mapeo de actores": ["Twitter"],
        "canales de comunicación": ["Twitter"], "audiencias públicas": ["Facebook"], "consulta ciudadana": ["Facebook"],
        "comunicación externa": ["Twitter", "LinkedIn"], "percepción pública": ["Twitter"], "reputación": ["Twitter", "LinkedIn"],
        "acceso a la información": ["Twitter", "LinkedIn"]
    }
}

@st.cache_resource
def cargar_clasificador():
    return pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")

@st.cache_resource
def cargar_sentimiento():
    return pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

classifier = cargar_clasificador()
sentiment_pipeline = cargar_sentimiento()

def clasificar_categoria_principal(texto):
    labels = list(categorias.keys())
    resultado = classifier(str(texto), candidate_labels=labels, hypothesis_template="la temática del texto es {}.")
    return resultado['labels'][0], resultado['scores'][0]

def clasificar_subcategoria(texto, categoria):
    if categoria not in categorias:
        return "no aplica", 0.0
    subtemas = list(categorias[categoria].keys())
    resultado = classifier(str(texto), candidate_labels=subtemas, hypothesis_template="la subtemática del texto es {}.")
    return resultado['labels'][0], resultado['scores'][0]

def analizar_sentimiento(texto):
    resultado = sentiment_pipeline(str(texto))[0]
    label = resultado['label']
    if label in ['4 stars', '5 stars']:
        return "positivo"
    elif label in ['1 star', '2 stars']:
        return "negativo"
    else:
        return "neutro"

def recomendar_red(categoria, subcategoria):
    try:
        return categorias[categoria][subcategoria]
    except KeyError:
        return ["LinkedIn"]

def generar_sugerencias_estrategicas(subcategoria, sentimiento, redes_recomendadas):
    sugerencias = {
        "criticas": [],
        "generales": []
    }

    if sentimiento == "negativo":
        sugerencias["criticas"].append(
            "**alerta de tono negativo:** el texto posee un sentimiento negativo. su publicación podría afectar la reputación de la marca. **acción:** reformule el mensaje para centrarse en soluciones, aprendizajes o un plan de acción positivo. evite un lenguaje que pueda ser percibido como defensivo o evasivo."
        )
    elif sentimiento == "neutro":
        sugerencias["generales"].append(
            "**oportunidad de tono:** el sentimiento es neutro. para aumentar la interacción, considere añadir un lenguaje más entusiasta, una pregunta directa a la audiencia o un llamado a la acción claro."
        )
    elif sentimiento == "positivo":
        sugerencias["generales"].append(
            "**tono positivo:** excelente. el tono es ideal para conectar con la audiencia. asegúrese de que el mensaje principal y el llamado a la acción sean claros para capitalizar este sentimiento."
        )

    for red in redes_recomendadas:
        if red == "LinkedIn":
            sugerencias["generales"].append(
                "**para LinkedIn:** mantenga un tono profesional y basado en datos. etiquete a empresas o líderes relevantes. utilice etiquetas como #industria #liderazgo #innovación."
            )
        elif red == "Instagram":
            sugerencias["generales"].append(
                "**para Instagram:** el impacto visual es fundamental. acompañe el texto con una fotografía o video de alta calidad. utilice el texto para narrar una historia y finalice con una pregunta para fomentar comentarios."
            )
        elif red == "Facebook":
            sugerencias["generales"].append(
                "**para Facebook:** fomente la conversación comunitaria. utilice un lenguaje cercano y directo. considere crear una encuesta o formular una pregunta abierta para que las personas compartan sus opiniones."
            )
        elif red == "Twitter":
            sugerencias["generales"].append(
                "**para Twitter:** sea conciso y directo. la primera línea es crucial para captar la atención. utilice una o dos etiquetas relevantes para unirse a conversaciones existentes."
            )
    
    if subcategoria in ["capacitación", "desarrollo profesional"]:
        sugerencias["generales"].append(
            "**enriquezca el contenido:** para temas de desarrollo, considere incluir un testimonio breve de un participante o un dato de impacto (ejemplo: 'el 95% de los participantes mejoró sus habilidades')."
        )
    elif subcategoria in ["innovación", "tecnología"]:
        sugerencias["generales"].append(
            "**enriquezca el contenido:** al hablar de tecnología, explique claramente el beneficio para las personas o el medioambiente, no solo la característica técnica. esto lo hace más comprensible."
        )
    elif subcategoria in ["biodiversidad", "reforestación"]:
        sugerencias["generales"].append(
            "**enriquezca el contenido:** en temas ambientales, los datos visuales son poderosos. mencione el número de árboles plantados, hectáreas protegidas o especies beneficiadas."
        )

    return sugerencias

st.title("asistente estratégico de contenido")
st.markdown("esta herramienta utiliza inteligencia artificial para clasificar un texto, analizar su sentimiento y generar recomendaciones con el fin de optimizar su impacto en redes sociales.")

texto_usuario = st.text_area("escriba o pegue el texto de la publicación aquí:", height=150, placeholder="ejemplo: '¿Sabes lo que significa la minería?: En este post te lo mostraremos!'")

if st.button("analizar y recomendar", type="primary"):
    if not texto_usuario.strip():
        st.warning("por favor, ingrese un texto válido para el análisis.")
    else:
        with st.spinner('realizando el análisis completo...'):
            categoria, cat_score = clasificar_categoria_principal(texto_usuario)
            subcategoria, sub_score = clasificar_subcategoria(texto_usuario, categoria)
            sentimiento = analizar_sentimiento(texto_usuario)
            redes_recomendadas = recomendar_red(categoria, subcategoria)
            sugerencias = generar_sugerencias_estrategicas(subcategoria, sentimiento, redes_recomendadas)
        
        st.success("análisis completado con éxito.")
        
        st.subheader("resultados del análisis:")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="categoría principal", 
                value=categoria, 
                help=f"confianza del modelo: {cat_score*100:.1f}%"
            )

        with col2:
            st.metric(
                label="subcategoría", 
                value=subcategoria, 
                help=f"confianza del modelo: {sub_score*100:.1f}%"
            )
        
        with col3:
            st.metric(label="sentimiento general", value=sentimiento)

        with col4:
            st.metric(label="redes recomendadas", value=", ".join(redes_recomendadas))

        st.markdown("---")

        st.subheader("estrategias para mejorar su publicación")

        if sugerencias["criticas"]:
            for critica in sugerencias["criticas"]:
                st.warning(critica)
        
        if sugerencias["generales"]:
            with st.expander("ver sugerencias de optimización", expanded=True):
                for sugerencia in sugerencias["generales"]:
                    st.markdown(f"- {sugerencia}")
        
        if not sugerencias["criticas"] and not sugerencias["generales"]:
            st.info("no se generaron sugerencias automáticas para este texto.")