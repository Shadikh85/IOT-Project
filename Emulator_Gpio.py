'''

Projet realisé par ...
'''

from enum import Enum
from RPiSim import GPIO
from threading import Thread
import paho.mqtt.client as mqtt
import sys
import signal
import time

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
    #status_client.username_pw_set(USER_NAME, PASSWORD)
    status_client.connect(HOST, PORT)
    return status_client

PORTE_PIN = 15
SIRENE_PIN = 14
VENTILATEUR = 18
DEL_PIN = 17
LUMIERE_CUISINE = 11
LUMIERE_SALON = 12
   
class Etat(Enum):
    OFF = 1
    DELAI_E = 2
    ARME = 3
    DELAI_S = 4
    SIRENE = 5

etat = Etat.OFF

class Event(Enum):
    porte = 1
    btnArm = 2
    code = 3
    boutonInterface = 4
    finDelais = 5

###############################################
""" Les fonctions """
###############################################
    
def terminer(signum, frame):
    print("Terminer")
    GPIO.output(SIRENE_PIN, GPIO.LOW)
    GPIO.cleanup()
    sys.exit(0)

def event_btnArm(channel):
    print("event bouton arm")
    setEtat(Event.btnArm)




""" Configuration des GPIOs """
signal.signal(signal.SIGINT, terminer)
try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    """ Porte : Changé en OUT pour afficher s'elle est ouverte ou pas """
    GPIO.setup(PORTE_PIN,GPIO.MODE_OUT, initial=GPIO.LOW)



    """ DEL """
    GPIO.setup(DEL_PIN,GPIO.MODE_OUT, initial=GPIO.LOW)

    """ Lumiere Entree """
    GPIO.setup(LUMIERE_CUISINE, GPIO.MODE_OUT, initial=GPIO.LOW)

    """ Lumiere Salon """
    GPIO.setup(LUMIERE_SALON, GPIO.MODE_OUT, initial=GPIO.LOW)
    
    """ Ventilateur """
    GPIO.setup(VENTILATEUR, GPIO.MODE_OUT, initial=GPIO.LOW)
except Exception:
    print("Problème avec les GPIO")


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

def on_message_ventilateur(client, userdata, message):
    print("Received message pour Ventilateur ..")
    if message.payload.decode("utf-8") == "ON":
        GPIO.output(VENTILATEUR, GPIO.HIGH)
        status_client = get_status_client()
        status_client.publish("Status/Ventilateur", "ON")
        status_client.disconnect()
    else:
        GPIO.output(VENTILATEUR, GPIO.LOW)
        status_client = get_status_client()
        status_client.publish("Status/Ventilateur", "OFF")
        status_client.disconnect()



commande_client.message_callback_add("Commande/LumiereCuisine", on_message_lumiere_cuisine)
commande_client.message_callback_add("Commande/LumiereSalon", on_message_lumiere_salon)
commande_client.message_callback_add("Commande/Ventilateur", on_message_ventilateur)

#commande_client.username_pw_set(USER_NAME, PASSWORD)
commande_client.connect(HOST, PORT)
commande_client.subscribe("Commande/#")
commande_client.loop_forever()
