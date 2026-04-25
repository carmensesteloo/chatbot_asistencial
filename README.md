# Asistente Conversacional Interactivo

Este proyecto es un asistente de voz desarrollado en Python con una interfaz gráfica en **Streamlit**. Permite a los usuarios interactuar mediante voz para realizar diferentes acciones, enfocado en la accesibilidad y el entretenimiento.

## Funcionalidades Principales

1. Contar Chistes: El usuario puede pedir chistes por categorías (Jaimito, Lepe, cortos, etc.) o al azar.
2. Búsqueda en YouTube: El asistente escucha de qué quieres ver un vídeo, lo busca en YouTube y te muestra las 3 mejores opciones en pantalla.
3. Terapia de Reminiscencia: Un modo de charla empática (disponible en castellano y gallego normativo) diseñado para hacer compañía a personas mayores y animarles a hablar de su pasado.

## Tecnologías y Librerías Utilizadas

* **Streamlit:** Para la interfaz gráfica web.
* **SpeechRecognition:** Para capturar y transcribir la voz del usuario.
* **Edge-tts y Pygame:** Para generar y reproducir la voz del asistente.
* **Ollama (Llama 3):** Para el motor de inteligencia artificial local (procesamiento de lenguaje natural).
* **Urllib / Regex:** Para la búsqueda y extracción de enlaces de YouTube.

## Cómo ejecutar el proyecto

### 1. Requisitos previos
* Tener instalado [Ollama](https://ollama.com/) en tu ordenador.
* Descargar el modelo Llama 3 abriendo una terminal y ejecutando: `ollama pull llama3`
* Tener un archivo `chistes.json` en la carpeta raíz del proyecto.

### 2. Instalar dependencias
Abre la terminal en la carpeta del proyecto y ejecuta:
```bash
pip install streamlit SpeechRecognition pyaudio pygame edge-tts ollama
