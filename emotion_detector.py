#!/usr/bin/env python3
import paho.mqtt.client as mqttClient
import json
import numpy as np
import cv2
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from tensorflow.keras.models import load_model


brokerHostname = "Localhost"
username = "emotion_detector"
topic = "PJ/Face"

topic_ = "PJ/Emotion"

width, height = 48, 48
emotions = ["Ira", "Asco", "Miedo", "Alegría", "Tristeza", "Sorpresa", "Neutral"]

path_haarcascade1 = '../haarcascade_frontalface_default.xml'
path_haarcascade2 = '../haarcascade_frontalface_alt.xml'
path_haarcascade3 = '../haarcascade_frontalface_alt2.xml'

path_model = '../my_model_u_100'

def hcc_cargado(h, cargando):
    if cargando:
        print(h, "cargado.")
    else:
        print(h, "no encontrado.")
        exit()


classifier_default = cv2.CascadeClassifier()
cargando = classifier_default.load(path_haarcascade1)
hcc_cargado(path_haarcascade1, cargando)

classifier_alt = cv2.CascadeClassifier()
cargando = classifier_alt.load(path_haarcascade2)
hcc_cargado(path_haarcascade2, cargando)

classifier_alt2 = cv2.CascadeClassifier()
cargando = classifier_alt2.load(path_haarcascade3)
hcc_cargado(path_haarcascade3, cargando)

classifiers = [classifier_default, classifier_alt, classifier_alt2]

model = load_model(path_model)
if model is not None:
    print('Modelo cargado: ',path_model)
else:
    print(path_model, "no encontrado.")
    exit()
    

def on_connect(client, userdata, rc):
    print('Connected with result code %s' % rc)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed. There are other methods to achieve this.
    if rc == 0:
        print("Connected to broker")
    else:
        print("Connection failed")
 

def on_message(client, userdata, msg):
    print("\n\nNuevo mensaje recibido")
    #print('%s %s' % (msg.topic, msg.payload))
    img_array = np.frombuffer(msg.payload, np.uint8)
    #print(img_array)
    #print(len(img_array))
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    cara = detectar_cara(image)
    if cara is None:
        print('Error. Cara no detectada')
        return
    resultados = predecir_emocion(cara)

    e = int(resultados.argmax())
    c = int(resultados[e]*100)
    print("Emoción detectada: ",emotions[e])
    print("Confianza: ",c,"%")

    msg = json.dumps({"emotion" : e, "confianza" : c})
    #print(msg)
    client.publish(topic_, msg)
    
    imprimir_panel(image, cara, resultados)
    #mostrar_imagen(image)

def on_publish(client,userdata,result):
    print("\nMensaje publicado en el topic ",topic_,"\n")
    #pass
    
def mostrar_imagen(image):
    if image is None:
        print('Error. Imagen no detectada')
    else:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.xticks([]), plt.yticks([])
        plt.show()

def mostrar_imagen_cv2(image):
    cv2.imshow('imagen',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def imprimir_panel(original, cara, resultados):
    plt.close()
    plt.ion()
    f = plt.figure(figsize=(8,4))
    #imagen original
    f.add_subplot(2,2, 1)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title('Imagen original')
    plt.xticks([]), plt.yticks([])
    #cara detectada
    f.add_subplot(2,2, 3)
    plt.imshow(cv2.cvtColor(cara, cv2.COLOR_BGR2RGB))
    plt.title('Cara detectada')
    plt.xticks([]), plt.yticks([])
    #resultados del detector de emociones
    f.add_subplot(1,2, 2)
    y_pos = np.arange(len(emotions))
    plt.bar(y_pos, resultados, align='center', alpha=0.5)
    plt.xticks(y_pos, emotions, rotation=45)
    plt.ylabel('Porcentaje')
    plt.title('Emoción detectada')
    #f.tight_layout(pad=1.0)
    plt.subplots_adjust(left=0, right=0.9, top=0.9, bottom=0.2, wspace=0.05, hspace=0.3)

    plt.show(block=False)
    plt.pause(0.1)



def detectar_cara(image):
    face_final=None
    print("Detectando cara...")
 
    for c in classifiers:
        faces = c.detectMultiScale(image)
        for f in faces:
            x, y, w, h = [ v for v in f ]
            sub_face = image[y:y+h, x:x+w]
            # nos quedamos con la imagen más grande de las caras que detecte
            if face_final is None:
                face_final=sub_face
            else:
                if (sub_face.shape[0]*sub_face.shape[1])>(face_final.shape[0]*face_final.shape[1]):
                    face_final=sub_face
    
    #mostrar_imagen(face_final)
    return face_final


def predecir_emocion(cara):
    if cara is None:
        print('Error. Cara no detectada')
    else:
        cara = cv2.cvtColor(cara, cv2.COLOR_BGR2GRAY)
        cara = cv2.resize(cara, (width, height))
        cara = cara.reshape(1, width, height, 1)/255.0
        
        result = model.predict(cara)
        return result[0]

def emotion_analysis(emotion_values):
    y_pos = np.arange(len(emotions))

    plt.bar(y_pos, emotion_values, align='center', alpha=0.5)
    plt.xticks(y_pos, emotions)
    plt.ylabel('Porcentaje')
    plt.title('Emoción detectada')

    plt.show()

print("\nIniciando...")

client = mqttClient.Client(username)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

client.connect(brokerHostname, port=1883)
print("Conectado al broker: ",brokerHostname)

client.subscribe(topic)
print("Suscrito al topic: ",topic)

client.loop_forever()
