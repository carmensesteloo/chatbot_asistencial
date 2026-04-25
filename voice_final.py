import streamlit as st
import speech_recognition as sr
import threading
import random
import time
import json
import pygame
import os
import edge_tts
import asyncio
import urllib.request
import urllib.parse
import re
import ollama 

'''
PRIMER SERVICIO QUE PROPONEMOS! CONTAR CHISTES
'''
def cargar_json():
    nombre_archivo = "chistes.json"
    if not os.path.exists(nombre_archivo):
        return None
    
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return datos

'''
Función con la que seleccionamos la categoria del chiste en función de lo que se diga por voz
'''
def seleccionar_chiste(comando, datos_chistes):
    palabras_clave = {
        "jaimito": "jaimito", "de jaimito": "jaimito",
        "lepe": "lepe", "de lepe": "lepe",
        "corto": "cortos", "cortos": "cortos",
        "juego de palabras": "juego de palabras", "juegos de palabras": "juego de palabras"
    }
    
    categoria_elegida = None
    #si existe la palabra entonces buscamos un chiste en el json
    for palabra, clave_json in palabras_clave.items():
        if palabra in comando:
            categoria_elegida = clave_json
            break
    
    #sino, lanzamos uno al azar
    if categoria_elegida is None or "azar" in comando:
        lista_categorias = list(datos_chistes.keys())
        categoria_elegida = random.choice(lista_categorias)

    lista_de_esa_categoria = datos_chistes.get(categoria_elegida, [])
        
    return random.choice(lista_de_esa_categoria)

'''
Función para escuchar por voz
'''
def get_voice_command(mensaje_consola="Habla ahora...", tiempo_silencio=1.5, lang='es-ES'):
    r = sr.Recognizer()
    r.dynamic_energy_threshold = False
    r.energy_threshold = 600 # filtro del sonido
    r.pause_threshold = tiempo_silencio  # dejamos 1.5 segundos desde que el chatbot habla paqra que la persona piense
    
    with sr.Microphone() as source:
        print(mensaje_consola)

        #escuchamos lo que dice,lo printeamos y lo guardamos
        try:
            audio = r.listen(source, timeout=10)
            text = r.recognize_google(audio, language=lang)
            print("Dijiste:", text)
            return text.lower()
        
        #excepciones    
        except sr.WaitTimeoutError:
            print("Silencio detectado")
            return "silencio"
        except sr.UnknownValueError:
            return "no entendí"
        except Exception as e:
            print(f"Error: {e}")
            return "error"

'''
Función que genera el mp3 dondeguardamos temporalmente la voz del chatbot
'''    
def hablar_hilo(text, voz):
    texto_limpio = text.replace("|", "... ")
    archivo_audio = "chiste_temp.mp3"
    
    async def generar_audio():
        comunicador = edge_tts.Communicate(texto_limpio, voz, rate="-5%")
        await comunicador.save(archivo_audio)
        
    asyncio.run(generar_audio())
    
    pygame.mixer.init()
    pygame.mixer.music.load(archivo_audio)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
        
    pygame.mixer.quit()
    try:
        os.remove(archivo_audio)
    except OSError:
        pass

'''
Lanzamos la voz en esañol,elegimos la de Elvira
'''
def speak_text(text, voz="es-ES-ElviraNeural"):
    hilo = threading.Thread(target=hablar_hilo, args=(text, voz))
    hilo.start()
    hilo.join()

'''
SEGUNDO SERVICIO QUE PROPONEMOS! BUSCAR VIDEOS EN YOUTUBE
'''
def buscar_video_youtube(busqueda, cantidad=3):
    try:
        #pasamos del comando de voz 'busqueda' a decodificarlo para buscarlo como video de youtube
        query_encoded = urllib.parse.quote(busqueda)
        url = f"https://www.youtube.com/results?search_query={query_encoded}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        video_ids = re.findall(r'"videoRenderer":\{"videoId":"(.*?)"', html)
        
        #para evitar  que salgan videos repetidos, simplemente comprobamos que no tengan el mismo id
        ids_unicos = []
        for vid in video_ids:
            if vid not in ids_unicos and len(vid) == 11: #con len(vid)==11 comprobamos que es un video valido
                ids_unicos.append(vid)
                
        enlaces = []
        if ids_unicos:
            for vid in ids_unicos[:cantidad]:
                enlaces.append(f"https://www.youtube.com/watch?v={vid}")
            return enlaces
        
    except Exception as e:
        print(f"error al buscar en YouTube: {e}")
    return []

'''
TERCER SERVICIO QUE PROPONEMOS! REMINISCENCIA
'''

'''
Con estas dos funciones guardamos en un txt la conversación completa
'''
def guardar_log_charla(rol, mensaje):
    with open("historial_reminiscencia.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{rol}: {mensaje}\n")

def conversacion_reminiscencia(ui_placeholder, idioma="es"):
    with open("historial_reminiscencia.txt", "a", encoding="utf-8") as archivo:
        archivo.write("\n" + "="*50 + "\n")
        archivo.write(f"NUEVA SESIÓN DE REMINISCENCIA ({idioma.upper()}) - {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
        archivo.write("="*50 + "\n")

    # CONFIGURAMOS SEGÚN EL IDIOMA
    if idioma == "gl":
        stt_lang = "gl-ES"
        tts_voice = "gl-ES-SabelaNeural" #la voz gallega
        
        #PROMPT PARA QUE LA IA ENTIENDA QUE QUEREMOS QUE SE ESPECIALICE EN REMINISCENCIA    
        system_prompt = (
            "Eres un asistente cálido y empático especializado en terapia de reminiscencia para personas mayores. "
            "REGLA ABSOLUTA Y ESTRICTA: Debes escribir ÚNICA y EXCLUSIVAMENTE en Gallego Normativo (ILG-RAG). "
            "ESTÁ PROHIBIDO usar vocabulario portugués o brasileño. "
            "Ejemplos de lo que NO debes hacer y su corrección: "
            "No digas 'muito', di 'moito'. No digas 'ficar', di 'quedar'. No digas 'obrigado', di 'grazas'. "
            "No digas 'você', di 'ti' o 'vostede'. No digas 'bom/boa', di 'bo/boa'. "
            "Haz preguntas muy breves, sencillas y abiertas. Nunca des respuestas largas."
        )
        
        #mensajes predefinidos para el gallego
        saludo_inicial = "Que boa idea! Encantaríame escoitarte. De que época ou recordo che gustaría que falásemos hoxe?"
        msg_escuchando = "Escoitando os teus recordos... (Di 'rematar' ou 'adeus' para saír)"
        msg_pensando = "Pensando..."
        despedida = "Foi xenial falar contigo e coñecer máis da túa vida. Avísame cando queiras volver charlar. Unha aperta!"
        error_msg = "Perdoa, despisteime un momento. Podes repetilo?"
        palabras_salida = ["terminar", "adiós", "adios", "salir", "rematar", "adeus", "saír"]
    else:
        #mensajes predefinidos para el español
        stt_lang = "es-ES"
        tts_voice = "es-ES-ElviraNeural"
        system_prompt = "Eres un asistente amable, cálido, empático y paciente especializado en terapia de reminiscencia para personas mayores. Tu objetivo es hacerles compañía y animarles a hablar de su pasado. Haz preguntas breves, sencillas y abiertas. Nunca des respuestas muy largas. Sé muy amable y usa un tono conversacional natural de España."
        saludo_inicial = "¡Qué buena idea! Me encantaría escucharte. ¿De qué época o recuerdo te gustaría que habláramos hoy?"
        msg_escuchando = "Escuchando tus recuerdos... (Di 'terminar' o 'adiós' para salir)"
        msg_pensando = "Pensando..."
        despedida = "Ha sido genial hablar contigo y conocer más de tu vida. Avísame cuando quieras volver a charlar. ¡Un abrazo!"
        error_msg = "Perdona, me he despistado un momento. ¿Puedes repetirlo?"
        palabras_salida = ["terminar", "adiós", "adios", "salir"]

    mensajes = [{"role": "system", "content": system_prompt}]
    
    if ui_placeholder: 
        ui_placeholder.empty()
        ui_placeholder.info(saludo_inicial)
    
    speak_text(saludo_inicial, voz=tts_voice)
    guardar_log_charla("Asistente", saludo_inicial)
    mensajes.append({"role": "assistant", "content": saludo_inicial})
    
    while True:
        #informamos al usuario de que estamos escuchando
        if ui_placeholder: ui_placeholder.warning(msg_escuchando)
        
        #convertimso voz en texto
        usuario_dice = get_voice_command("Escuchando...", tiempo_silencio=4.5, lang=stt_lang)
        
        #si no dice nada claro entonces saltamos el resto del codigo para volver a empezar
        if usuario_dice in ["silencio", "no entendí", "error"]:
            continue
        
        #llamamos a la funcion para guardar el log de la conversacion
        guardar_log_charla("Usuario", usuario_dice.capitalize())
        
        #condicion de salida
        if any(palabra in usuario_dice for palabra in palabras_salida):
            if ui_placeholder: 
                ui_placeholder.empty()
                ui_placeholder.success(despedida)
            
            guardar_log_charla("Asistente", despedida)
            speak_text(despedida, voz=tts_voice)
            break

        # guardamos lo que decimos   
        if ui_placeholder: 
            ui_placeholder.empty()
            ui_placeholder.write(f" **Tú:** {usuario_dice.capitalize()}")
            
        mensajes.append({"role": "user", "content": usuario_dice})
        
        #fase donde llamamos a la IA para que procese
        if ui_placeholder: ui_placeholder.info(msg_pensando)
        try:
            respuesta_ia = ollama.chat(model='llama3', messages=mensajes)
            texto_respuesta = respuesta_ia['message']['content']
            
            if ui_placeholder: 
                ui_placeholder.empty()
                ui_placeholder.success(f" **Asistente:** {texto_respuesta}")
            
            guardar_log_charla("Asistente", texto_respuesta)
            speak_text(texto_respuesta, voz=tts_voice)
            mensajes.append({"role": "assistant", "content": texto_respuesta})
        
        #trata de excepciones
        except Exception as e:
            print(f"Error con llama: {e}")
            if ui_placeholder: ui_placeholder.error(error_msg)
            guardar_log_charla("error", error_msg)
            speak_text(error_msg, voz=tts_voice)

def main(ui_placeholder=None):
    datos_chistes = cargar_json()
    
    if datos_chistes is None:
        mensaje_error = "Error. No he encontrado el archivo de chistes."
        if ui_placeholder: ui_placeholder.error(mensaje_error)
        speak_text(mensaje_error)
        return

    if ui_placeholder:
        ui_placeholder.info("Esperando... Di: **'Cuéntame un chiste'**, **'Pon un vídeo de...'**, **'Quiero hablar'** o **'Quero falar'**")

    comando_inicial = get_voice_command("Esperando orden...", tiempo_silencio=1.5)

    if "vídeo" in comando_inicial or "video" in comando_inicial:
        palabras_sobrantes = ["pon", "ponme", "un", "una", "unos", "unas", "el", "la", "los", "las", "vídeo", "video", "de", "me", "quiero", "busca", "por", "favor", "del", "de la", "de los", "de las"]
        palabras = comando_inicial.split()
        palabras_limpias = [p for p in palabras if p not in palabras_sobrantes]
        busqueda = " ".join(palabras_limpias)
        
        if not busqueda:
            speak_text("¿De qué quieres que busque el vídeo?")
            busqueda = get_voice_command("Escuchando búsqueda...")
            
        if busqueda not in ["silencio", "no entendí", "error"]:
            msg = f"Buscando un vídeo sobre {busqueda}..."
            if ui_placeholder: ui_placeholder.warning(f"{msg}")
            speak_text(msg)
            
            urls_videos = buscar_video_youtube(busqueda, cantidad=3)
            if urls_videos:
                speak_text("Aquí tienes algunas opciones. Haz clic en la que prefieras.")
                if ui_placeholder:
                    ui_placeholder.empty()
                    with ui_placeholder.container():
                        st.markdown(f"### Resultados para: {busqueda.capitalize()}")
                        columnas = st.columns(len(urls_videos))
                        for i, url in enumerate(urls_videos):
                            with columnas[i]:
                                st.video(url)
            else:
                speak_text("Lo siento, hubo un problema y no he podido encontrar vídeos.")
                
    elif "chiste" in comando_inicial:
        tiene_categoria = False
        palabras_comprobar = ["jaimito", "lepe", "corto", "cortos", "juego", "juegos", "azar"]
        for palabra in palabras_comprobar:
            if palabra in comando_inicial:
                tiene_categoria = True
                break
                
        if tiene_categoria:
            respuesta_usuario = comando_inicial
        else:
            categorias_disponibles = list(datos_chistes.keys())
            texto_categorias = ", ".join(categorias_disponibles)
            pregunta = f"¿De qué tipo quieres el chiste? Tengo de {texto_categorias}. También puedes decirme, al azar."
            if ui_placeholder: ui_placeholder.warning(f"{pregunta}")
            speak_text(pregunta)
            respuesta_usuario = get_voice_command("Escuchando la categoría...")
            if respuesta_usuario in ["silencio", "no entendí", "error"]:
                aviso = "Como no te he entendido bien, te voy a contar uno al azar."
                if ui_placeholder: ui_placeholder.warning(aviso)
                speak_text(aviso)
                respuesta_usuario = "azar"
            
        chiste_final = seleccionar_chiste(respuesta_usuario, datos_chistes)
        if ui_placeholder:
            ui_placeholder.empty()
            chiste_pantalla = chiste_final.replace('|', '\n\n')
            ui_placeholder.markdown(f"<h2 style='text-align: center; color: #2E86C1;'>{chiste_pantalla}</h2>", unsafe_allow_html=True)
        speak_text(chiste_final)

    elif any(palabra in comando_inicial for palabra in ["hablar", "recuerdo", "charla", "pasado", "falar", "galego", "gallego"]):
        if "galego" in comando_inicial or "gallego" in comando_inicial or "falar" in comando_inicial:
            conversacion_reminiscencia(ui_placeholder, idioma="gl")
        else:
            conversacion_reminiscencia(ui_placeholder, idioma="es")
            
    elif comando_inicial == "error":
        msg = "Hubo un problema con el micrófono."
        if ui_placeholder: ui_placeholder.error(msg)
        speak_text(msg)
    elif comando_inicial not in ["silencio", "no entendí"]:
        msg = "Por favor, pídeme un chiste, que ponga un vídeo, o dime que quieres hablar."
        if ui_placeholder: ui_placeholder.warning(msg)
        speak_text(msg)

if __name__ == "__main__":
    main()