'''
Projet réalisé par Shadi Khalil, Maher Khaznaji, et Nadir Marjane dans le cadre
du cours de Projet Intégrateur enseigné par le Professeur Moevus.

dernière version: 18 Janvier 2023
Ce programme décrit la partie hardware du projet.
'''

import RPi.GPIO as GPIO
from threading import Thread
import paho.mqtt.client as mqtt
import sys
import signal
import time

# Connection au serveur MQTT
HOST                = "localhost"
PORT                = 1883
CLEAN_SESSION       = True
COMMANDE_CLIENT_ID  = "Commande"
STATUS_CLIENT_ID    = "Status"
USER_NAME           = "Maherkhaznaji"
PASSWORD            = "maher123"


commande_client = mqtt.Client(clean_session=CLEAN_SESSION)

def get_status_client():
    status_client = mqtt.Client(clean_session=CLEAN_SESSION)
    status_client.connect(HOST, PORT)
    return status_client

# Numéros des pins
VENTILATEUR = 18
LUMIERE_CUISINE = 11
LUMIERE_SALON = 40

    
def terminer(signum, frame):
    print("Terminer")
    GPIO.cleanup()
    sys.exit(0)


""" Configuration des GPIOs """
signal.signal(signal.SIGINT, terminer)
try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    """ Lumiere Cuisine """
    GPIO.setup(LUMIERE_CUISINE, GPIO.OUT)

    """ Lumiere Salon """
    GPIO.setup(LUMIERE_SALON, GPIO.OUT)
    
    """ Ventilateur """
    GPIO.setup(VENTILATEUR, GPIO.OUT)
except Exception:
    print("Problème avec les GPIO")

ventilateur_status = False
on =0
off =0
# La temperature courante du CPU du Rasberry Pi est contenue dans le fichier '
#/sys/class/thermal/thermal_zone0/temp'. Pour obtenir les valeurs en celcius
#il faut diviser les valeurs du fichier par 1000.
def ventilateur_control():
    global on
    global off
    while(True):
        # Tant que la variable ventilateur_statut est True, le ventilateur sera controle
        # automatiquement par la temperature du CPU
        if ventilateur_status:
            with open(r"/sys/class/thermal/thermal_zone0/temp") as file:
                temperature = file.read()
                print(float(temperature)/1000)
            if float(temperature)/1000 < 50:
                if off ==0:
                # Si temperature est inferieure a 50°, fermer le ventilateur
                    GPIO.output(VENTILATEUR, GPIO.LOW)
                    status_client = get_status_client()
                    status_client.publish("Status/Ventilateur", "OFF")
                    status_client.disconnect()
                    off=off+1
                    on=0
            else:
                if on==0:
                
                    GPIO.output(VENTILATEUR, GPIO.HIGH)
                    status_client = get_status_client()
                    status_client.publish("Status/Ventilateur", "ON")
                    status_client.disconnect()
                    on =on+1
                    off=0
        time.sleep(2)

ventilateur_thread = Thread(target=ventilateur_control, args=())
ventilateur_thread.start()

# Changement du statut de la lumiere cuisine et son publication via MQTT
def on_message_lumiere_cuisine(client, userdata, message):
    print("Received message pour Lumiere Cuisine ..")
    if message.payload.decode("utf-8") == "ON":
        GPIO.output(LUMIERE_CUISINE, GPIO.HIGH)
        status_client = get_status_client()
        status_client.publish("Status/LumiereCuisine", "ON")
        status_client.disconnect()
    else:
        GPIO.output(LUMIERE_CUISINE, GPIO.LOW)
        status_client = get_status_client()
        status_client.publish("Status/LumiereCuisine", "OFF")
        status_client.disconnect()

# Changement du statut de la lumiere salon et son publication via MQTT
def on_message_lumiere_salon(client, userdata, message):
    print("Received message pour Lumiere Salon ..")
    if message.payload.decode("utf-8") == "ON":
        GPIO.output(LUMIERE_SALON, GPIO.HIGH)
        status_client = get_status_client()
        status_client.publish("Status/LumiereSalon", "ON")
        status_client.disconnect()
    else:
        GPIO.output(LUMIERE_SALON, GPIO.LOW)
        status_client = get_status_client()
        status_client.publish("Status/LumiereSalon", "OFF")
        status_client.disconnect()

# Changement du statut du ventilateur et son publication via MQTT
def on_message_ventilateur(client, userdata, message):
    global ventilateur_status
    global on
    global off
    print("Received message pour Ventilateur ..")
    if message.payload.decode("utf-8") == "ON":
        GPIO.output(VENTILATEUR, GPIO.HIGH)
        status_client = get_status_client()
        status_client.publish("Status/Ventilateur", "ON")
        status_client.disconnect()
    elif message.payload.decode("utf-8") == "OFF":
        GPIO.output(VENTILATEUR, GPIO.LOW)
        status_client = get_status_client()
        status_client.publish("Status/Ventilateur", "OFF")
        status_client.disconnect()
    elif message.payload.decode("utf-8") == "automatic":
        ventilateur_status = True
        on =0
        off=0
    elif message.payload.decode("utf-8") == "manual":
        ventilateur_status = False


# Etablissement des fonctions callback en réponse aux messages reçus via MQTT
commande_client.message_callback_add("Commande/LumiereCuisine", on_message_lumiere_cuisine)
commande_client.message_callback_add("Commande/LumiereSalon", on_message_lumiere_salon)
commande_client.message_callback_add("Commande/Ventilateur", on_message_ventilateur)

# Souscription MQTT aux commandes émises par l'interface utilisateur
commande_client.connect(HOST, PORT)
commande_client.subscribe("Commande/#")
commande_client.loop_forever()
