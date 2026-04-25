import streamlit as st
from voice_final import main as run_agent

st.set_page_config(
    page_title="Asistente Fácil", 
    layout="centered" 
)

st.markdown("""
<style>

/* escogemos fuente */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

html, body, [class*="st-"] {
    font-family: 'Montserrat', sans-serif !important;
}

/* ponemos fondo */
.stApp {
    background: radial-gradient(circle at 20% 20%, #1f3d39, #0c1a1a 60%);
    min-height: 100vh;
}

/* ponemos las formas verdes */
.stApp::before{
    content:"";
    position:fixed;
    width:600px;
    height:600px;
    background:#2ecc71;
    border-radius:50%;
    top:-200px;
    right:-200px;
    filter: blur(40px);
    opacity:0.35;
}

.stApp::after{
    content:"";
    position:fixed;
    width:500px;
    height:500px;
    background:#27ae60;
    border-radius:50%;
    bottom:-200px;
    left:-200px;
    filter: blur(40px);
    opacity:0.35;
}

/* ocultamos el menu de streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* textos */
.titulo-app {
    text-align: center;
    font-weight: 900;
    font-size: 4rem;
    color: white;
    margin-bottom: 0px;
}

.subtitulo-app {
    text-align: center;
    font-size: 1.5rem;
    color: #cfd8dc;
    margin-bottom: 40px;
}

/* forzamos el color blanco en textos normales de Streamlit */
p, div {
    color: #ffffff !important;
}

/* poenmos el boton en negrita */
.stButton > button {
    height: 100px;
    font-size: 24px !important;
    font-weight: 900 !important; /* Negrita al máximo (Black) */
    background: linear-gradient(90deg, #27ae60, #2ecc71) !important;
    color: white !important;
    border-radius: 50px !important; /* Forma de cápsula */
    border: none !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4) !important;
    transition: 0.3s;
}

/* forzamos negrita incluso si Streamlit lo envuelve en un parrafo */
.stButton > button p {
    font-weight: 900 !important;
    font-size: 24px !important;
}

.stButton > button:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.5) !important;
}

/* ponemos una liena separadora */
hr {
    border: 0;
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: 30px 0;
}

</style>
""", unsafe_allow_html=True)

#contenido de la pagina

st.markdown("<h1 class='titulo-app'>Tu Asistente</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitulo-app'>Toca el botón verde y pídeme un chiste, un vídeo, o dime que quieres hablar</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    #ponemos el texto en el boton
    boton_hablar = st.button("PULSAR PARA HABLAR", use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

pantalla_dinamica = st.empty()

if boton_hablar:
    run_agent(ui_placeholder=pantalla_dinamica)
