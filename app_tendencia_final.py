# Confidencial
# Proyecto VINKS - Startup Chile CORFO
# ESTE CODIGO ES EXPERIMENTAL
# Autor: DRCSR
# Version: 1.0 

import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx
import numpy as np

def clean_salary(salary_str):
    """convierte una cadena de texto de sueldo (ej: '$ 5.000.000') a un número entero."""
    try:
        if not isinstance(salary_str, str):
            return 0
        cleaned_str = salary_str.strip()
        cleaned_str = cleaned_str.replace('$', '')
        cleaned_str = cleaned_str.replace('.', '')
        cleaned_str = cleaned_str.replace(' ', '')
        return int(cleaned_str)
    except (ValueError, AttributeError):
        return 0

def build_org_chart(df):
    nodes, edges = [], []
    rol_to_id_map = df.set_index('rol')['id'].to_dict()
    for _, row in df.iterrows():
        nodes.append(Node(id=str(row['id']), label=str(row['rol']), title=f"{row['nombre']} {row['apellido_1']} ({row['rol']})", shape="box", font={'size': 18}))
        jefatura_rol = row['jefatura']
        if jefatura_rol != '-' and jefatura_rol in rol_to_id_map:
            edges.append(Edge(source=str(rol_to_id_map[jefatura_rol]), target=str(row['id'])))
    return nodes, edges

def build_location_graph(df):
    nodes, edges = [], []
    rol_to_id_map = df.set_index('rol')['id'].to_dict()
    ubicaciones = df['ubicación'].unique()
    for ubicacion in ubicaciones:
        nodes.append(Node(id=ubicacion, label=ubicacion, size=40, shape="dot", color="#FFC107"))
    for _, row in df.iterrows():
        nodes.append(Node(id=str(row['id']), label=str(row['rol']), title=f"{row['nombre']} {row['apellido_1']} ({row['rol']})", shape="box", color="#42A5F5"))
        edges.append(Edge(source=row['ubicación'], target=str(row['id']), dashes=True))
        jefatura_rol = row['jefatura']
        if jefatura_rol != '-' and jefatura_rol in rol_to_id_map:
            edges.append(Edge(source=str(rol_to_id_map[jefatura_rol]), target=str(row['id']), color="#616161"))
    return nodes, edges

def analyze_social_network(df):
    G = nx.DiGraph()
    rol_to_id_map = df.set_index('rol')['id'].to_dict()
    for _, row in df.iterrows():
        G.add_node(row['id'], label=row['rol'], name=f"{row['nombre']} {row['apellido_1']}")
    for _, row in df.iterrows():
        if row['jefatura'] != '-' and row['jefatura'] in rol_to_id_map:
            G.add_edge(rol_to_id_map[row['jefatura']], row['id'])
    
    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    
    results = [{"id": nid, "nombre": G.nodes[nid]['name'], "rol": G.nodes[nid]['label'], "grado_centralidad": degree.get(nid, 0), "intermediacion_centralidad": betweenness.get(nid, 0), "cercania_centralidad": closeness.get(nid, 0)} for nid in G.nodes]
    results_df = pd.DataFrame(results)
    
    max_intermediacion = results_df['intermediacion_centralidad'].max()
    results_df['intermediacion_normalizada'] = results_df['intermediacion_centralidad'] / max_intermediacion if max_intermediacion > 0 else 0
    return G, results_df

def perform_diagnostic_analysis(df, G):
    diagnostics = {}
    managers = set(df['jefatura']) - {'-'}
    span_of_control = df['jefatura'].value_counts().drop('-', errors='ignore')
    diagnostics['span_of_control'] = span_of_control
    _, results_df = analyze_social_network(df)
    diagnostics['key_person_risk'] = results_df.sort_values('intermediacion_centralidad', ascending=False).head(5)
    try:
        diagnostics['hierarchy_depth'] = nx.dag_longest_path_length(G)
    except nx.NetworkXError:
        diagnostics['hierarchy_depth'] = "no aplicable"
    num_managers = len(managers)
    num_ics = len(df) - num_managers
    diagnostics['manager_ratio'] = {'managers': num_managers, 'ics': num_ics, 'ratio': num_ics / num_managers if num_managers > 0 else 0}
    manager_df = df[df['rol'].isin(managers)]
    manager_dist = manager_df['ubicación'].value_counts(normalize=True) * 100
    staff_dist = df['ubicación'].value_counts(normalize=True) * 100
    diagnostics['geo_centralization'] = pd.DataFrame({'porcentaje del personal': staff_dist, 'porcentaje del liderazgo': manager_dist}).fillna(0)
    diagnostics['team_costs'] = df.groupby('jefatura').agg(costo_total_equipo=('sueldo_numerico', 'sum'), sueldo_promedio=('sueldo_numerico', 'mean'), numero_miembros=('id', 'count')).drop('-', errors='ignore').sort_values('costo_total_equipo', ascending=False)
    return diagnostics

def generate_recommendations(diagnostics):
    recommendations = {}
    key_people = diagnostics['key_person_risk']
    if not key_people.empty:
        tasks = []
        for _, person in key_people.iterrows():
            if person['intermediacion_centralidad'] > 0.1:
                tasks.append(f"**{person['nombre']} ({person['rol']})** es un puente de comunicación crítico. **acción:** se sugiere crear un plan de sucesión y documentar sus procesos clave para mitigar riesgos.")
        if tasks:
            recommendations['riesgo de persona clave'] = tasks
    tasks = []
    overloaded_managers = diagnostics['span_of_control'][diagnostics['span_of_control'] > 7]
    for manager, count in overloaded_managers.items():
        tasks.append(f"el rol de **{manager}** supervisa a {count} personas, lo que puede indicar una sobrecarga. **acción:** se sugiere evaluar la división de su equipo o la creación de un rol de líder de equipo intermedio.")
    micromanagers = diagnostics['span_of_control'][diagnostics['span_of_control'] < 3]
    for manager, count in micromanagers.items():
        tasks.append(f"el rol de **{manager}** supervisa solo a {count} persona(s), lo que podría constituir una capa jerárquica ineficiente. **acción:** se sugiere considerar la simplificación de la estructura mediante la fusión de su equipo con otro.")
    depth = diagnostics['hierarchy_depth']
    if isinstance(depth, int) and depth > 6:
        tasks.append(f"la jerarquía tiene **{depth} niveles**, lo que puede ralentizar la toma de decisiones. **acción:** se sugiere fomentar la comunicación directa entre distintos niveles jerárquicos y empoderar la toma de decisiones en los niveles inferiores.")
    if tasks:
        recommendations['estructura y eficiencia'] = tasks
    geo_df = diagnostics['geo_centralization']
    imbalances = geo_df[abs(geo_df['porcentaje del personal'] - geo_df['porcentaje del liderazgo']) > 20]
    if not imbalances.empty:
        tasks = []
        for location, row in imbalances.iterrows():
            if row['porcentaje del liderazgo'] > row['porcentaje del personal']:
                tasks.append(f"la ubicación **{location}** concentra un {row['porcentaje del liderazgo']:.0f}% del liderazgo, pero solo un {row['porcentaje del personal']:.0f}% del personal. **acción:** se sugiere fomentar el desarrollo de líderes en otras ubicaciones para evitar una cultura de 'oficina central'.")
        if tasks:
            recommendations['geografía y cultura'] = tasks
    return recommendations

st.set_page_config(layout="wide")
st.title("visor de organigrama interactivo y análisis de red")
uploaded_file = st.file_uploader("seleccione un archivo xlsx", type="xlsx")

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        df['rol'] = df['rol'].str.strip()
        df['jefatura'] = df['jefatura'].str.strip()
        df['ubicación'] = df['ubicación'].str.strip()
        df['sueldo_numerico'] = df['rango_sueldo'].apply(clean_salary)

        tabs = st.tabs(["organigrama", "grafo por ubicación", "análisis de red social", "diagnóstico", "tareas recomendadas", "datos"])

        with tabs[0]:
            st.subheader("organigrama de la empresa (vista jerárquica)")
            nodes, edges = build_org_chart(df)
            config = Config(width=1200, height=800, directed=True, physics=False, hierarchical={"enabled": True, "sortMethod": "directed"}, node={'size': 25})
            agraph(nodes=nodes, edges=edges, config=config)

        with tabs[1]:
            st.subheader("interacción de grupos por ubicación")
            loc_nodes, loc_edges = build_location_graph(df)
            loc_config = Config(width=1200, height=800, directed=True, physics=True, node={'size': 20, 'font': {'size': 16}})
            agraph(nodes=loc_nodes, edges=loc_edges, config=loc_config)

        with tabs[2]:
            st.subheader("análisis de la red organizacional")
            G, results_df = analyze_social_network(df)
            st.write("este análisis revela los roles clave dentro de la estructura formal de la empresa.")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### personas con mayor conexión (grado)")
                st.dataframe(results_df.sort_values("grado_centralidad", ascending=False).head(5)[['nombre', 'rol', 'grado_centralidad']], hide_index=True)
            with col2:
                st.markdown("#### puentes y cuellos de botella (intermediación)")
                st.dataframe(results_df.sort_values("intermediacion_centralidad", ascending=False).head(5)[['nombre', 'rol', 'intermediacion_centralidad']], hide_index=True)
            st.markdown("---")
            st.subheader("visualización del grafo de influencia y ubicación")
            st.markdown("""<div style="background-color: #D6EAF8; padding: 10px; border-radius: 5px; border: 1px solid #AED6F1;">este grafo representa visualmente la red organizacional. el tamaño de cada nodo indica su nivel de intermediación (cuellos de botella), mientras que el color representa su ubicación geográfica.</div>""", unsafe_allow_html=True)
            location_color_map = {"Las Condes": "#E74C3C", "Quilicura": "#3498DB", "Maipú": "#F1C40F"}
            default_color = "#95A5A6"
            MIN_NODE_SIZE, MAX_NODE_SIZE = 15, 75
            df_con_analisis = df.merge(results_df, left_on='id', right_on='id')
            viz_nodes = []
            for _, row in df_con_analisis.iterrows():
                node_size = MIN_NODE_SIZE + row['intermediacion_normalizada'] * (MAX_NODE_SIZE - MIN_NODE_SIZE)
                node_color = location_color_map.get(row['ubicación'], default_color)
                viz_nodes.append(Node(id=str(row['id']), label=row['rol_x'], title=f"{row['nombre_x']} ({row['ubicación']})", size=node_size, color=node_color))
            viz_edges = [Edge(source=str(u), target=str(v)) for u, v in G.edges()]
            viz_config = Config(width=1200, height=800, directed=True, physics=True)
            agraph(nodes=viz_nodes, edges=viz_edges, config=viz_config)

        with tabs[3]:
            st.subheader("diagnóstico organizacional automatizado")
            st.info("esta sección utiliza métricas para identificar posibles áreas de mejora en la estructura, los costos y la comunicación de la empresa.")
            G, _ = analyze_social_network(df)
            diagnostics = perform_diagnostic_analysis(df, G)
            st.markdown("### 1. amplitud de control")
            avg_span = diagnostics['span_of_control'].mean()
            st.metric(label="amplitud de control promedio", value=f"{avg_span:.1f} personas")
            col1, col2 = st.columns(2)
            with col1:
                st.warning("posibles gerentes con sobrecarga (amplitud > 7)")
                st.dataframe(diagnostics['span_of_control'][diagnostics['span_of_control'] > 7], use_container_width=True)
            with col2:
                st.info("posible microgestión (amplitud < 3)")
                st.dataframe(diagnostics['span_of_control'][diagnostics['span_of_control'] < 3], use_container_width=True)
            st.markdown("### 2. riesgo de persona clave")
            st.warning("las cinco personas más críticas (mayor intermediación)")
            st.dataframe(diagnostics['key_person_risk'][['nombre', 'rol', 'intermediacion_centralidad']], hide_index=True, use_container_width=True)
            st.markdown("### 3. profundidad jerárquica")
            depth = diagnostics['hierarchy_depth']
            st.metric(label="máximo de niveles jerárquicos", value=f"{depth} niveles")
            st.markdown("### 4. proporción entre gerentes y contribuyentes individuales")
            ratio_data = diagnostics['manager_ratio']
            col1, col2, col3 = st.columns(3)
            col1.metric("número de gerentes", ratio_data['managers'])
            col2.metric("número de contribuyentes", ratio_data['ics'])
            col3.metric("contribuyentes por gerente", f"{ratio_data['ratio']:.1f}")
            st.markdown("### 5. centralización geográfica del liderazgo")
            st.bar_chart(diagnostics['geo_centralization'])
            st.markdown("### 6. análisis de costos por equipo")
            st.dataframe(diagnostics['team_costs'], column_config={"costo_total_equipo": st.column_config.NumberColumn(format="$ %d"),"sueldo_promedio": st.column_config.NumberColumn(format="$ %d")}, use_container_width=True)
            st.markdown("### 7. análisis de silos organizacionales")
            all_roles = sorted(df['rol'].unique().tolist())
            if len(all_roles) >= 2:
                col1, col2 = st.columns(2)
                team1_rol = col1.selectbox("seleccione el primer rol o cargo:", all_roles, index=0)
                team2_rol = col2.selectbox("seleccione el segundo rol o cargo:", all_roles, index=1)
                if team1_rol != team2_rol:
                    rol_to_id, id_to_rol = df.set_index('rol')['id'].to_dict(), df.set_index('id')['rol'].to_dict()
                    root_nodes = [n for n, d in G.in_degree() if d == 0]
                    if root_nodes:
                        root_node = root_nodes[0]
                        node1, node2 = rol_to_id.get(team1_rol), rol_to_id.get(team2_rol)
                        if node1 and node2:
                            lca_id = nx.lowest_common_ancestor(G, node1, node2)
                            lca_rol = id_to_rol.get(lca_id)
                            depth = nx.shortest_path_length(G, source=root_node, target=lca_id)
                            st.metric(label=f"ancestro común entre '{team1_rol}' y '{team2_rol}'", value=lca_rol if lca_rol else "no aplicable")
                            st.info(f"la comunicación entre estos dos cargos debe escalar {depth} nivel(es) hasta '{lca_rol}' para ser coordinada formalmente.")

        with tabs[4]:
            st.subheader("tareas recomendadas para la mejora organizacional")
            st.info("basado en el diagnóstico, a continuación se presenta una lista de acciones sugeridas para fortalecer la red de comunicación, mitigar riesgos y mejorar la eficiencia.")
            G, _ = analyze_social_network(df)
            diagnostics = perform_diagnostic_analysis(df, G)
            recommendations = generate_recommendations(diagnostics)
            if not recommendations:
                st.success("felicitaciones. según las métricas analizadas, la organización parece encontrarse en un estado saludable y no se detectaron alertas significativas.")
            else:
                for category, tasks in recommendations.items():
                    with st.expander(f"{category} ({len(tasks)} sugerencias)", expanded=True):
                        for task in tasks:
                            st.markdown(f"- {task}")
        
        with tabs[5]:
            st.subheader("datos del archivo cargado")
            st.dataframe(df)

    except Exception as e:
        st.error(f"se ha producido un error al procesar el archivo: {e}")
        st.exception(e)