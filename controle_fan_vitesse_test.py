import time
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

# Configuration des pins GPIO
ventilateur_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(ventilateur_pin, GPIO.OUT)

# Création d'un objet "sensor" pour lire la température
sensor = W1ThermSensor()

try:
    while True:
        # Lecture de la température
        temperature = sensor.get_temperature()
        print("Température: {:.2f}°C".format(temperature))

        # Contrôle de la vitesse du ventilateur en fonction de la température
        if temperature > 30:
            # Température élevée, on met le ventilateur à fond
            GPIO.output(ventilateur_pin, GPIO.HIGH)
        elif temperature > 25:
            # Température moyenne, on met le ventilateur à mi-puissance
            pwm.ChangeDutyCycle(50)
        else:
            # Température basse, on éteint le ventilateur
            GPIO.output(ventilateur_pin, GPIO.LOW)

        # Attente avant la prochaine mesure
        time.sleep(10)

except KeyboardInterrupt:
    # Nettoyage des ressources avant de quitter
    pwm.stop()
    GPIO.cleanup()
