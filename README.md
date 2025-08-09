# Reconocimiento de emociones en avatares para simulador de vehículos aéreos no tripulados en robótica asistencial

Trabajo de Fin de Máster del curso MUII 2024/2025 (Máster Universitario en Ingeniería Informática de la UCLM).

**Autor**: Anselmo Martínez Martínez

---

## Resumen

Para este trabajo de Fin de Máster se ha desarrollado un sistema de reconocimiento de emociones para detectar la expresión de un avatar en una aplicación implementada en Unity para la simulación del vuelo de un vehículo aéreo no tripulado con fines asistenciales. Dentro de este entorno virtual se van tomando periódicamente imágenes desde la cámara embarcada del vehículo aéreo para la monitorización del avatar. Estas imágenes se envían mediante el protocolo de mensajes MQTT al sistema externo implementado para el análisis de emociones. Gracias al uso de algoritmos de visión artificial, este sistema programado en lenguaje Python es capaz de detectar la cara en la imagen recibida y clasificar la emoción del avatar en una de siete posibles (ira, asco, miedo, felicidad, tristeza, sorpresa o neutral) con un porcentaje de certeza. Finalmente, la información de la emoción detectada se envía de vuelta a Unity, de nuevo mediante MQTT, para mostrarla en la interfaz de usuario de la aplicación principal.

---

## Desarrollo

Se ha programado una aplicación en Python en la que inicialmente se realiza el proceso de detección de una cara en la imagen y posteriormente se clasifica su emoción en una de siete posibles gracias al uso de una red neuronal convolucional creada especialmente para esta tarea.

### 1. Detección de la cara

Para el reconocimiento de la cara de la persona a partir de una fotografía se usa un clasificador en cascada basado en filtros Haar. OpenCV proporciona varios modelos ya entrenados de estos clasificadores y que pueden ser cargados mediante la propia librería. Se va a usar tres modelos diferentes debido a que es posible que uno solo no consiga detectar la cara. Al usar tres, la probabilidad de encontrarla está casi garantizada, aunque siempre puede surgir algún error puntual debido a sombras, desenfoques o giros. De esta forma, se busca si existe una cara en la imagen usando los tres modelos y se guarda si se encuentra. Finalmente, la foto del rostro se recorta para quedarnos solamente con la parte que nos interesa y quitarle todo lo demás. Las imágenes resultantes pasan entonces a introducirse en la red neuronal convolucional para su clasificación en una de las posibles emociones.

Se utilizan los modelos "haarcascade_frontalface_default", "haarcascade_frontalface_alt" y "haarcascade_frontalface_alt2".


### 2. Red neuronal convolucional (CNN)

Esta red ha sido creada mediante el uso de la API de Keras. El modelo se inicia desde cero y se le debe añadir una a una las capas que formarán su estructura. Entre las capas que podemos incluir se encuentran: 
   * Las capas convolucionales: Se encargan de obtener características a partir de las dependencias espaciales entre los píxeles de la imagen, generando múltiples filtros que producen un mapa de características. Se suele incluir varias de estas capas (a veces seguidas una de otra) para capturar la mayor información posible. Las primeras capas detectan formas sencillas como líneas y curvas mientras que las últimas están más especializadas y pueden reconocer formas complejas. Sin embargo, no conviene añadir demasiadas porque llega un momento en el que no suponen una mejora significativa para el modelo y solo se aumenta su complejidad y tiempo de cómputo.
   * Las capas de subsampling (como la MaxPooling o la AveragePooling): Se incluyen tras las convolucionales para disminuir el número de parámetros que se generan y reducir posteriormente el sobreajuste del modelo.
   * La capa Flatten: Se coloca justo antes de la capa de entrada de la red neuronal final para convertir la salida de las convoluciones en un vector y poder introducir los valores en la red.
   * Las capas de la red neuronal totalmente conectada: Tiene una capa de entrada, una o varias ocultas y una de salida.
   * Las capas Dropout: Se ponen entre las capas de la red neuronal para quitar un porcentaje de sus neuronas y reducir el sobreajuste.


Se ha decidido añadir tres conjuntos de capas convolucionales (el primero con solo una capa y los demás con dos) para que el modelo sea capaz de detectar una gran cantidad de información de las imágenes. Después de cada conjunto se adjunta una capa de subsampling para ir reduciendo el tamaño de sus parámetros antes de que se introduzcan en la red neuronal final. Estas capas son las siguientes:
   * Conv (1): La primera capa convolucional tiene 64 kernels de 5x5 y usa ReLU como función de activación. El tamaño de su entrada es de 48x48x1 ya que las imágenes que se introducen son de 48 píxeles de ancho por 48 de alto con un solo canal de color (en blanco y negro).
   * MaxP: Una capa MaxPooling de 5x5 con 2 unidades de desplazamiento.
   * Conv (2): Una segunda capa convolucional con 64 kernels de 3x3 y ReLU como función de activación.
   * Conv (3): Una tercera capa convolucional igual que la anterior.
   * AvgP (1): Una primera capa AveragePooling de 3x3 con 2 unidades de desplazamiento.
   * Conv (4): Una cuarta capa convolucional con 128 kernels de 3x3 y ReLU como función de activación.
   * Conv (5): Una quinta capa convolucional igual que la anterior.
   * AvgP (2): Una segunda capa AveragePooling de 3x3 con 2 unidades de desplazamiento.
   * Flatten: Una capa Flatten entre las capas en las que se realiza la convolución y la siguiente red neuronal totalmente conectada.% para convertir la salida a un vector y poder introducir los valores en la red.
   * Capa de entrada de la red neuronal'': Una capa de entrada con 1\,024 neuronas.
   * Drop (1): Una primera capa de Dropout con el objetivo de deshacerse del 20\% de las neuronas y reducir el sobreajuste.
   * Capa oculta de la red neuronal: Una capa oculta con el mismo número de neuronas que la entrada.
   * Drop (2): Una segunda capa de Dropout igual que la anterior.
   * Capa de salida de la red neuronal: La capa de salida en la que se ejecuta una función Softmax para convertir la salida en una distribución de probabilidad de tamaño 7 (igual al número de clases a clasificar, es decir, las seis emociones básicas más la neutral).


<img width="964" height="698" alt="tfm_cnn" src="https://github.com/user-attachments/assets/5b2b67f5-ce20-4e0f-b48a-82a6c388ecaa" />

---

## Cómo iniciar la aplicación en tu propia máquina

Iniciar el archivo principal de la aplicación:

   ```
   $ python -m emotion_detector.py
   ```

---

## Imagen de la aplicación

<img width="904" height="494" alt="tfm_app" src="https://github.com/user-attachments/assets/ef8c8f48-0578-4f6b-a29c-dc1e5a8be7ca" />
