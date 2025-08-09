# Reconocimiento de emociones en avatares para simulador de vehículos aéreos no tripulados en robótica asistencial

Trabajo de Fin de Máster del curso MUII 2024/2025 (Máster Universitario en Ingeniería Informática de la UCLM).

**Autor**: Anselmo Martínez Martínez

---

## Resumen

Para este trabajo de Fin de Máster se ha desarrollado un sistema de reconocimiento de emociones para detectar la expresión de un avatar en una aplicación implementada en Unity para la simulación del vuelo de un vehículo aéreo no tripulado con fines asistenciales. Dentro de este entorno virtual se van tomando periódicamente imágenes desde la cámara embarcada del vehículo aéreo para la monitorización del avatar. Estas imágenes se envían mediante el protocolo de mensajes MQTT al sistema externo implementado para el análisis de emociones. Gracias al uso de algoritmos de visión artificial, este sistema programado en lenguaje Python es capaz de detectar la cara en la imagen recibida y clasicar la emoción del avatar en una de siete posibles (ira, asco, miedo, felicidad, tristeza, sorpresa o neutral) con un porcentaje de certeza. Finalmente, la información de la emoción detectada se envía de vuelta a Unity, de nuevo mediante MQTT, para mostrarla en la interfaz de usuario de la aplicación principal.

---

## Cómo iniciar la aplicación en tu propia máquina

Iniciar el archivo principal de la aplicación:

   ```
   $ python -m emotion_detector.py
   ```

---

## Imagen de la aplicación

<img width="904" height="494" alt="tfm_app" src="https://github.com/user-attachments/assets/ef8c8f48-0578-4f6b-a29c-dc1e5a8be7ca" />
