import paho.mqtt.client as mqttClient
import json
import numpy as np
import cv2
from matplotlib import pyplot as plt
from tensorflow.keras.models import load_model


# OPCIONES
width, height = 48, 48
print_texts = False
print_panel = False

# BROKER MQTT
broker_hostname = "Localhost"
broker_port = 1883

# TOPICS
topic_face = "PJ/Face"
topic_emotion = "PJ/Emotion"

# NOMBRE APP
username = "emotion_detector"

# EMOCIONES
emotions = ["Ira", "Asco", "Miedo", "Alegría", "Tristeza", "Sorpresa", "Neutral"]

# MODELOS
path_hcc_1 = '../haarcascade_frontalface_default.xml'
path_hcc_2 = '../haarcascade_frontalface_alt.xml'
path_hcc_3 = '../haarcascade_frontalface_alt2.xml'
path_cnn = '../my_model_uu_150_60'

classifier_default = cv2.CascadeClassifier()
classifier_alt = cv2.CascadeClassifier()
classifier_alt2 = cv2.CascadeClassifier()
classifiers = [classifier_default, classifier_alt, classifier_alt2]

success = classifier_default.load(path_hcc_1)
if not success:
    print(path_hcc_1, 'no encontrado.')
    exit()

success = classifier_alt.load(path_hcc_2)
if not success:
    print(path_hcc_2, 'no encontrado.')
    exit()

success = classifier_alt2.load(path_hcc_3)
if not success:
    print(path_hcc_3, 'no encontrado.')
    exit()

model_cnn = load_model(path_cnn)
if not model_cnn:
    print(path_cnn, 'no encontrado.')
    exit()
    

def on_connect(client, userdata, rc):
    print('Conectado con código %s' % rc)
    if rc == 0:
        print("Conectado al broker")
    else:
        print("Conexión fallida")
 
def on_message(client, userdata, msg):
    if print_texts:
        print("\n\nNuevo mensaje recibido:")
        print('%s %s' % (msg.topic, msg.payload))
    
    # detectar cara a partir de la imagen recibida
    img_array = np.frombuffer(msg.payload, np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    face = get_face_from_image(image)
    if face is None:
        if print_texts:
            print('Error. Cara no detectada')
        return

    # obtener resultados de la emoción predecida por la CNN
    results = get_predicted_emotion_results(face)
    emotion_position = int(results.argmax())
    confidence_score = int(results[emotion_position]*100)
    if print_texts:
        print("\nResultados:")
        print("  Emoción detectada: ",emotions[emotion_position])
        print("  Confianza: ",confidence_score,"%")

    # crear y publicar mensaje
    msg = json.dumps({"emotion" : emotion_position, "confianza" : confidence_score})
    client.publish(topic_emotion, msg)
    
    if print_panel:
        show_panel(image, face, results)

def on_publish(client, userdata, result):
    print("\nMensaje publicado en el topic ",topic_emotion,"\n")
    #pass


def show_image(image):
    if image is None:
        print('Error. Imagen no detectada')
    else:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.xticks([]), plt.yticks([])
        plt.show()

def show_image_cv2(image):
    cv2.imshow('imagen',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def show_panel(original_image, detected_face, results):
    plt.close()
    plt.ion()
    f = plt.figure(figsize=(8,4))
    # imagen original
    f.add_subplot(2,2, 1)
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.title('Imagen original')
    plt.xticks([]), plt.yticks([])
    # cara detectada
    f.add_subplot(2,2, 3)
    plt.imshow(cv2.cvtColor(detected_face, cv2.COLOR_BGR2RGB))
    plt.title('Cara detectada')
    plt.xticks([]), plt.yticks([])
    # resultados del detector de emociones
    f.add_subplot(1,2, 2)
    y_pos = np.arange(len(emotions))
    plt.bar(y_pos, results, align='center', alpha=0.5)
    plt.xticks(y_pos, emotions, rotation=45)
    plt.ylabel('Porcentaje')
    plt.title('Emoción detectada')
    #f.tight_layout(pad=1.0)
    plt.subplots_adjust(left=0, right=0.9, top=0.9, bottom=0.2, wspace=0.05, hspace=0.3)

    plt.show(block=False)
    plt.pause(0.1)


def get_face_from_image(image):
    final_face = None
    if print_texts:
        print("Detectando cara...")
 
    for c in classifiers:
        detected_faces = c.detectMultiScale(image)
        for face in detected_faces:
            x, y, w, h = [ v for v in face ]
            sub_face = image[y:y+h, x:x+w]
            # nos quedamos con la imagen más grande de las caras que detecte
            if final_face is None:
                final_face = sub_face
            else:
                if (sub_face.shape[0]*sub_face.shape[1]) > (final_face.shape[0]*final_face.shape[1]):
                    final_face = sub_face
    
    #show_image(face_final)
    return final_face


def get_predicted_emotion_results(face):
    if face is None:
        print('Error. Cara no detectada')
    else:
        # reducir tamaño de la imagen y pasar a blanco y negro
        face = cv2.resize(face, (width, height))
        face = face.reshape(1, width, height, 1)/255.0
        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

        # obtener predicción
        result = model_cnn.predict(face)
        return result[0]

def show_emotion_analysis(emotion_values):
    y_pos = np.arange(len(emotions))
    plt.bar(y_pos, emotion_values, align='center', alpha=0.5)
    plt.xticks(y_pos, emotions)
    plt.ylabel('Porcentaje')
    plt.title('Emoción detectada')
    plt.show()


print("\nIniciando cliente ",username)
client = mqttClient.Client(username)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

client.connect(broker_hostname, port=broker_port)
print("Conectado al broker: ",broker_hostname)

client.subscribe(topic_face)
print("Suscrito al topic: ",topic_face)

client.loop_forever()
