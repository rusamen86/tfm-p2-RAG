# Asistente de Talleres Meseta: chat para preguntar al RAG del proyecto.
#
# Para ejecutarlo (desde la carpeta del proyecto, con el entorno activado):
#     streamlit run app.py
#
# Usa la misma búsqueda con re-ranking, el mismo prompt y los mismos modelos
# que el cuaderno 05. Necesita la base chroma_db que crea el cuaderno 02 y la
# clave GROQ_API_KEY (en local, en el archivo .env; nunca escrita en el código).
#
# Cómo funciona Streamlit: cada vez que el usuario toca algo en la página,
# Streamlit vuelve a ejecutar este archivo entero, de arriba abajo. Por eso:
#   - Los modelos se cargan dentro de una función con st.cache_resource,
#     que los guarda en memoria para no volver a cargarlos en cada ejecución.
#   - La conversación se guarda en st.session_state, que es la "memoria"
#     de la página entre una ejecución y la siguiente.

import os
import time
from dotenv import load_dotenv
import chromadb
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer, CrossEncoder
from groq import Groq


# ---------- Configuración ----------

st.set_page_config(page_title='Asistente de Talleres Meseta', page_icon='🔧', layout='centered')

carpeta = os.path.dirname(os.path.abspath(__file__))
ruta_chroma = os.path.join(carpeta, 'chroma_db')

# Nombre que se ve en la página -> nombre del modelo en Groq
modelos = {'gpt-oss-120b': 'openai/gpt-oss-120b',
           'qwen3.8-27b': 'qwen/qwen3.8-27b'}

opcion_comparar = 'Comparar los dos'

ejemplos = ['¿Cuánto dura la garantía de una reparación?',
            '¿Qué estaciones ITV hay en la provincia de Valladolid?',
            '¿Cómo sé si mi coche tiene una llamada a revisión?']

prompt_sistema = '''Eres el asistente de un taller de vehículos en España.
Responde en español, de forma breve y clara, usando SOLO la información del contexto.
Indica al final la fuente o fuentes que has usado (el nombre del archivo).
Si el contexto no contiene la respuesta, di exactamente: No lo sé con la información disponible.'''


# ---------- Clave de Groq ----------

# En local la clave está en .env. En un servicio en la nube se guarda en sus
# "secrets", que llegan al programa igual, como variable de entorno.
load_dotenv(os.path.join(carpeta, '.env'))

if os.getenv('GROQ_API_KEY') is None:
    st.error('Falta la clave GROQ_API_KEY. En local va en el archivo .env; en la nube, en los secrets del servicio.')
    st.stop()

if not os.path.isdir(ruta_chroma):
    st.error('No encuentro la base vectorial chroma_db. Ejecuta antes los cuadernos 01 y 02.')
    st.stop()


# ---------- Carga de Chroma y de los modelos (una sola vez) ----------

@st.cache_resource(show_spinner='Cargando los documentos y los modelos de búsqueda...')
def cargar_recursos():
    client = chromadb.PersistentClient(path=ruta_chroma)
    collection = client.get_collection('taller')
    model = SentenceTransformer('intfloat/multilingual-e5-small')
    reranker = CrossEncoder('cross-encoder/mmarco-mMiniLMv2-L12-H384-v1')
    cliente = Groq(api_key=os.getenv('GROQ_API_KEY'), timeout=30, max_retries=1)
    return collection, model, reranker, cliente


collection, model, reranker, cliente = cargar_recursos()


# ---------- Funciones del RAG (las mismas del cuaderno 05) ----------

def buscar_basico(pregunta, k=4):
    vector = model.encode('query: ' + pregunta, normalize_embeddings=True).tolist()
    resultados = collection.query(query_embeddings=[vector], n_results=k)
    trozos = resultados['documents'][0]
    fuentes = []
    for metadato in resultados['metadatas'][0]:
        fuentes.append(metadato['fuente'])
    return trozos, fuentes


def buscar_reranking(pregunta, candidatos=20, k=4):
    trozos, fuentes = buscar_basico(pregunta, k=candidatos)
    parejas = []
    for trozo in trozos:
        parejas.append([pregunta, trozo])
    puntuaciones = reranker.predict(parejas, show_progress_bar=False)
    orden = np.argsort(puntuaciones)[::-1]
    mejores_trozos = []
    mejores_fuentes = []
    for i in orden[:k]:
        mejores_trozos.append(trozos[i])
        mejores_fuentes.append(fuentes[i])
    return mejores_trozos, mejores_fuentes


def construir_prompt(pregunta, trozos, fuentes):
    contexto = ''
    for i in range(len(trozos)):
        contexto = contexto + '[' + str(i + 1) + '] Fuente: ' + fuentes[i] + '\n' + trozos[i] + '\n\n'
    prompt = 'Contexto:\n' + contexto + 'Pregunta: ' + pregunta
    return prompt


def generar(modelo, pregunta, trozos, fuentes):
    # Igual que en el cuaderno 05, pero sin la pausa de 15 segundos: en un chat
    # no se puede hacer esperar al usuario. Si Groq corta por el límite gratuito
    # (8.000 tokens por minuto y modelo), se avisa en vez de dar un error.
    prompt = construir_prompt(pregunta, trozos, fuentes)
    inicio = time.time()
    try:
        respuesta = cliente.chat.completions.create(
            model=modelo,
            temperature=0.1,
            messages=[{'role': 'system', 'content': prompt_sistema},
                      {'role': 'user', 'content': prompt}])
        texto = respuesta.choices[0].message.content
    except Exception as error:
        texto = ('No he podido responder ahora (' + type(error).__name__ + '). '
                 'El plan gratuito de Groq admite pocas preguntas por minuto: espera un minuto y vuelve a intentarlo.')
    segundos = time.time() - inicio
    return texto, segundos


# ---------- Cómo se pinta un mensaje del chat ----------

def mostrar_mensaje(mensaje):
    with st.chat_message(mensaje['rol']):
        if mensaje['rol'] == 'user':
            st.markdown(mensaje['texto'])
        else:
            # Una columna por respuesta: una sola, o dos si se comparan los modelos.
            # En una pantalla estrecha (móvil) Streamlit pone las columnas una debajo de otra.
            columnas = st.columns(len(mensaje['respuestas']))
            for i in range(len(mensaje['respuestas'])):
                respuesta = mensaje['respuestas'][i]
                with columnas[i]:
                    st.caption(respuesta['modelo'] + ' · ' + str(round(respuesta['segundos'], 1)) + ' s')
                    st.markdown(respuesta['texto'])
            with st.expander('Fuentes y fragmentos usados (' + str(len(mensaje['trozos'])) + ')'):
                for i in range(len(mensaje['trozos'])):
                    st.markdown('**[' + str(i + 1) + '] ' + mensaje['fuentes'][i] + '**')
                    st.code(mensaje['trozos'][i], language=None, wrap_lines=True)


# ---------- Página ----------

# El diseño está inspirado en la web de la DGT (colores, tipografía y formas), con nombre
# y cabecera propios. Los colores generales están en .streamlit/config.toml y el resto en
# estilo.css, que se carga aquí. st.html sirve para escribir un trozo de HTML en la página;
# las clases "tm-..." son las que define estilo.css.
with open(os.path.join(carpeta, 'estilo.css'), encoding='utf-8') as archivo:
    st.html('<style>' + archivo.read() + '</style>')

st.html('''
<div class="tm-cabecera">
    <span class="tm-marca">Talleres Meseta</span>
    <span class="tm-lema">Asistente de documentación</span>
</div>
<h1 class="tm-titulo">Pregunta a la documentación del taller</h1>
<p class="tm-subtitulo">Respuestas basadas en la normativa oficial y en las preguntas frecuentes del taller, siempre con su fuente.</p>
<p class="tm-meta">Documentos: BOE, DGT, Ministerio de Industria y FAQ del taller · Cada pregunta se responde por separado</p>
''')

st.html('''
<div class="tm-aviso">
    <span class="tm-aviso-icono">i</span>
    <span>Talleres Meseta es un taller ficticio creado para un Trabajo Fin de Máster. Esta página no es un servicio oficial.</span>
</div>
''')

# La conversación se guarda en session_state para que no se pierda en cada ejecución.
if 'mensajes' not in st.session_state:
    st.session_state.mensajes = []

# Orden en la página: primero la conversación y debajo los controles, pegados a la caja
# de escribir, para que en el móvil no haya que subir hasta arriba para cambiar de modelo.
# st.container reserva ya el hueco de la conversación; se rellena más abajo, con "with zona_chat".
zona_chat = st.container()

st.html('<p class="tm-apartado">Modelo</p>')
modo = st.radio('Modelo', list(modelos.keys()) + [opcion_comparar], horizontal=True, label_visibility='collapsed')
pregunta = st.chat_input('Escribe tu pregunta')

with zona_chat:
    for mensaje in st.session_state.mensajes:
        mostrar_mensaje(mensaje)

    # Con el chat vacío se ofrecen unas preguntas de ejemplo. Van dentro de otro hueco
    # (st.empty) para poder quitarlas de la página en cuanto se hace la primera pregunta.
    zona_ejemplos = st.empty()
    if len(st.session_state.mensajes) == 0:
        with zona_ejemplos.container():
            st.html('<p class="tm-apartado">Preguntas de ejemplo</p>')
            for ejemplo in ejemplos:
                if st.button(ejemplo):
                    pregunta = ejemplo

    if pregunta:
        zona_ejemplos.empty()
        mensaje_usuario = {'rol': 'user', 'texto': pregunta}
        st.session_state.mensajes.append(mensaje_usuario)
        mostrar_mensaje(mensaje_usuario)

        # La búsqueda se hace una sola vez: si se comparan los dos modelos, reciben los mismos trozos.
        with st.spinner('Buscando en los documentos...'):
            trozos, fuentes = buscar_reranking(pregunta)

        if modo == opcion_comparar:
            nombres = list(modelos.keys())
        else:
            nombres = [modo]

        respuestas = []
        for nombre in nombres:
            with st.spinner('Respondiendo con ' + nombre + '...'):
                texto, segundos = generar(modelos[nombre], pregunta, trozos, fuentes)
            respuestas.append({'modelo': nombre, 'texto': texto, 'segundos': segundos})

        mensaje_asistente = {'rol': 'assistant', 'respuestas': respuestas, 'trozos': trozos, 'fuentes': fuentes}
        st.session_state.mensajes.append(mensaje_asistente)
        mostrar_mensaje(mensaje_asistente)

# El botón de borrar se dibuja al final, debajo del selector de modelo.
if len(st.session_state.mensajes) > 0:
    if st.button('Borrar conversación'):
        st.session_state.mensajes = []
        st.rerun()

# Pie de página.
st.html('''
<div class="tm-pie">
    <p class="tm-pie-titulo">Sobre este asistente</p>
    <p>Proyecto de fin de máster. El diseño está inspirado en la web de la DGT, pero esta página no pertenece a la DGT ni es un servicio oficial.</p>
</div>
''')
