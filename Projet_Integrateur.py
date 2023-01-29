'''
Projet réalisé par Shadi Khalil, Maher Khaznaji, et Nadir Marjane dans le cadre
du cours de Projet Intégrateur enseigné par le Professeur Moevus.

dernière version: 18 Janvier 2023
'''

'Les librairies utilisées'
from multiprocessing.sharedctypes import Value
import multiprocessing
from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
import customtkinter
from datetime import datetime
from threading import Thread
import paho.mqtt.client as mqtt
import pymongo
import time
import os
import cv2
import PyPDF2 
from fuzzywuzzy import fuzz, process
#from fuzzywuzzy import process
import speech_recognition as sr
from gtts import gTTS
import pyttsx3
import pyowm
import pywhatkit
import pyautogui
from pynput.keyboard import Key, Controller
import wikipedia
import pyjokes
import googletrans 
import random
from playsound import playsound
import webbrowser as web
from PyDictionary import PyDictionary
from pydub import AudioSegment
from pydub.playback import play

#La base de données
collection = None
try:
    client = pymongo.MongoClient("localhost")
    db = client.projet1 # La base de donnée projet1
    db.create_collection("evenements", capped =True, size=5000, max=20)
except pymongo.errors.CollectionInvalid:
    print("La collection existe deja")
else:
    print("il n'y a pas de probleme de duplication de collection")
collection = db.evenements
rendezvousdb = db.rendezvous

# Fonction pour obtenir le temps actuel
def obtenir_temps():
    
    temps = datetime.now()
    temps_date = str(temps.date())
    temps_heure = '{:02d}'.format(temps.hour)
    temps_minutes = '{:02d}'.format(temps.minute)
    temps_secondes = '{:02d}'.format(temps.second)
    return [temps_heure, temps_minutes, temps_secondes, temps_date]

# Fonction pour obtenir la météo actuelle
def obtenir_meteo():
    
    owm = pyowm.OWM('ec915be5e247913eea0905035934e17b')
    city= 'Montreal'
    mng = owm.weather_manager()
    obs =mng.weather_at_place(city)
    weather = obs.weather
    status = weather.status
    temp = weather.temperature('celsius')
    return temp, status

#liste des commandes vocales
commandlist=[
u"allumer la lumière de la cuisine",
u"fermer la lumière de la cuisine",
u"allumer la lumière du salon",
u"fermer la lumière du salon",
u"ouvrir le ventilateur",
u"fermer le ventilateur",
u"peux tu jouer une chanson de",
u"musique",
u"c'est qui",
u"c'est quoi",
u"raconte moi une histoire drôle",
u"raconte moi une blague de python",
u"définition",
u"google",
u"lire pdf",
u"lire pdf page",
u"web",
u"traduire en anglais",
u"traduire en espagnol",
u"sécurité"
]

#Liste des blagues
blaguelist = ["un policier arrête une automobiliste et lui dit: vous n'aviez pas vu que le feu était rouge, l'automobiliste répond oui je l'ai vu, c'est vous que je n'ai pas vu",
              "un homme atteint d'alzheymère se heurte à sa femme en marchant dans la cuisine. Elle lui dit tu ne m'as pas vu? Il repond oui mais je ne me souviens pas où"]


# Information concernant la fonctionnalité lecture de fihiers PDF 
document = 'Document.pdf'
# Instantiation de l'objet dictionnaire pour la fonctionnalité du dictionnaire anglais
dictionary=PyDictionary()
# Instantiation de l'objet caméra pour la fonctionnalité sécurité
cam = cv2.VideoCapture(0)

# Fonction qui choisit une blague au hasard à partir d'une liste
def get_blague(liste):
    
    return random.choice(liste)

# Préparation pour la reconnaissance vocale
recognizer = sr.Recognizer()
engine =pyttsx3.init()

# Implémentation de l'API google translate
translator = googletrans.Translator()

# Connection au serveur MQTT
def get_client_mqtt():
    """
        MQTT client pour les commandes
    """
    host          = "localhost"
    port          = 1883
    clean_session = True
    client_id     = "Commande"
    user_name     = "Maherkhaznaji"
    password      = "maher123"

    client = mqtt.Client(clean_session=clean_session)
    client.connect (host, port)
    return client

# Interface Utilisateur
fen1 = customtkinter.CTk()
fen1.title("Mon Assistant Personnel Intelligent Laura")
fen1.geometry("700x450")

# Labels 

# Les séparateurs
ttk.Separator(fen1, orient=HORIZONTAL).grid(row=2, column=0, sticky="ew", pady=10)

ttk.Separator(fen1, orient=HORIZONTAL).grid(row=4, column=0, sticky="ew", pady=10)

ttk.Separator(fen1, orient=HORIZONTAL).grid(row=6, column=0, sticky="ew", pady=10)

ttk.Separator(fen1, orient=HORIZONTAL).grid(row=8, column=0, sticky="ew", pady=10)

ttk.Separator(fen1, orient=HORIZONTAL).grid(row=10, column=0, sticky="ew", pady=10)

ttk.Separator(fen1, orient=HORIZONTAL).grid(row=12, column=0, sticky="ew", pady=10)

l2= customtkinter.CTkLabel(fen1, text="Lumiere cuisine")
l2.grid(row=1, column= 0, pady=10)

l3= customtkinter.CTkLabel(fen1, text="Lumiere salon")
l3.grid(row=3, column= 0, pady=10)

l4= customtkinter.CTkLabel(fen1, text="Ventilateur")
l4.grid(row=5, column= 0, pady=10)

l6 = customtkinter.CTkLabel(fen1, text="Historique")
l6.grid(row=9, column= 0, pady=10)

label_temps = customtkinter.CTkLabel(fen1, text='')
label_temps.grid(row=13, column=0)

label_meteo = customtkinter.CTkLabel(fen1, text='')
label_meteo.grid(row=13, column=2)

label_temperature = customtkinter.CTkLabel(fen1, text='')
label_temperature.grid(row=13, column=1)

label_lumiere_cuisine = customtkinter.CTkLabel(fen1,text='OFF')
label_lumiere_cuisine.grid(row=1, column=3, padx=10)

label_lumiere_salon = customtkinter.CTkLabel(fen1,text='OFF')
label_lumiere_salon.grid(row=3, column=3, padx=10)

label_ventilateur = customtkinter.CTkLabel(fen1, text='OFF')
label_ventilateur.grid(row=5, column=3, padx=10)

label_commande_vocale = customtkinter.CTkLabel(fen1, text='Cliquer pour une commande vocale')
label_commande_vocale.grid(row=7, column=1, padx=10)

label_rendezvous = customtkinter.CTkLabel(fen1, text='Rendez-vous')
label_rendezvous.grid(row=11, column=0)

def avoir_temps():
    
    temps = datetime.now()
    temps_date = str(temps.date())
    temps_heure = '{:02d}'.format(temps.hour)
    temps_minutes = '{:02d}'.format(temps.minute)
    temps_secondes = '{:02d}'.format(temps.second)
    temps_heure = temps_heure+":"+temps_minutes+":"+temps_secondes
    return temps_date, temps_heure

# Fonction pour sauvegarder les commandes vocales dans la base de données
def save_in_db(event):
    
    date, heure = avoir_temps()
    doc = { "event": event, "date": date, "heure": heure}
    collection.insert_one(doc)

# Fonction pour sauvegarder les rendez-vous dans la base de données
def save_rendezvous(date, event):
    
    doc = {"date": date, "rendez-vous": event}
    rendezvousdb.insert_one(doc)

# Fonction du bouton pour allumer lumière cuisine
def on_btn_lumiere_cuisine_on():

    if label_lumiere_cuisine.cget("text") == "OFF":
        print("Connexion avec le broker MQTT ..")
        client_mqtt = get_client_mqtt()
        message = "ON"
        client_mqtt.publish(topic="Commande/LumiereCuisine", payload=message)
        print("Etat lumiere cuisine ON est publié via MQTT")
        time.sleep(1)
        client_mqtt.disconnect()
        save_in_db("Lumiere cuisine: ON")
        print("Etat lumiere cuisine ON est enregistré dans MongoDB")

# Fonction du bouton pour fermer lumière cuisine
def on_btn_lumiere_cuisine_off():

    if label_lumiere_cuisine.cget("text") == "ON":
        print("Connexion avec le broker MQTT ..")
        client_mqtt = get_client_mqtt()
        message = "OFF"
        client_mqtt.publish(topic="Commande/LumiereCuisine", payload=message)
        print("Etat lumiere cuisine OFF est publié via MQTT")
        time.sleep(1)
        client_mqtt.disconnect()
        save_in_db("Lumiere cuisine: OFF")
        print("Etat lumiere cuisine OFF est enregistré dans MongoDB")

# Fonction du bouton pour allumer lumière salon
def on_btn_lumiere_salon_on():

    if label_lumiere_salon.cget("text") == "OFF":
        print("Connexion avec le broker MQTT ..")
        client_mqtt = get_client_mqtt()
        message = "ON"
        client_mqtt.publish(topic="Commande/LumiereSalon", payload=message)
        print("Etat lumiere salon ON est publié via MQTT")
        time.sleep(1)
        client_mqtt.disconnect()
        save_in_db("Lumiere salon: ON")
        print("Etat lumiere salon ON est enregistré dans MongoDB")

# Fonction du bouton pour fermer lumière salon
def on_btn_lumiere_salon_off():

    if label_lumiere_salon.cget("text") == "ON":
        print("Connexion avec le broker MQTT ..")
        client_mqtt = get_client_mqtt()
        message = "OFF"
        client_mqtt.publish(topic="Commande/LumiereSalon", payload=message)
        print("Etat lumiere salon OFF est publié via MQTT")
        time.sleep(1)
        client_mqtt.disconnect()
        save_in_db("Lumiere salon: OFF")
        print("Etat lumiere salon OFF est enregistré dans MongoDB")

# Fonction du bouton pour allumer ventilateur
def on_btn_ventilateur_on():

    if label_ventilateur.cget("text") == "OFF" or label_ventilateur.cget("text") == "":
        print("Connexion avec le broker MQTT ..")
        client_mqtt = get_client_mqtt()
        message = "ON"
        client_mqtt.publish(topic="Commande/Ventilateur", payload=message)
        print("Etat Ventilateur ON est publié via MQTT")
        time.sleep(1)
        client_mqtt.disconnect()
        save_in_db("Ventilateur: ON")
        print("Etat Ventilateur ON est enregistré dans MongoDB")

# Fonction du bouton pour fermer ventilateur
def on_btn_ventilateur_off():

    if label_ventilateur.cget("text") == "ON" or label_ventilateur.cget("text") == "":
        print("Connexion avec le broker MQTT ..")
        client_mqtt = get_client_mqtt()
        message = "OFF"
        client_mqtt.publish(topic="Commande/Ventilateur", payload=message)
        print("Etat Ventilateur OFF est publié via MQTT")
        time.sleep(1)
        client_mqtt.disconnect()
        save_in_db("Ventilateur: OFF")
        print("Etat Ventilateur OFF est enregistré dans MongoDB")

# Fenètre activée par le bouton Historique
def on_btn_historique():
    
    fen_historique = customtkinter.CTkToplevel(fen1)
    fen_historique.title("Historique")
    fen_historique.geometry("800x400")

    historique = ttk.Treeview(fen_historique, show="headings", height=20, selectmode="extended")
    historique["columns"] = ("date", "hour", "event")
    historique.column("date", anchor="center")
    historique.column("hour", anchor="center")
    historique.column("event", anchor="center")
    historique.heading("date", text="Date")
    historique.heading("hour", text="Heure")
    historique.heading("event", text="Evenement")

    data_historique = collection.find()
    i = 0
    for doc in data_historique:
        i = i+1
        historique.insert("", i, values=(doc["date"], doc["heure"], doc["event"]))
    historique.pack(expand=YES, fill=BOTH)


# Fonction pour écouter le système en français
def speakFr(text):
    
    engine =pyttsx3.init()
    engine.setProperty('voice','french+f3')  #english spanish
    engine.setProperty('rate', 120)
    engine.setProperty('volume', 3)
    engine.say(text)
    engine.runAndWait()                

# Fonction pour écouter le système en anglais                
def speakEn(text):
    
    engine =pyttsx3.init()
    engine.setProperty('voice', 'english_rp+f3')
    engine.setProperty('rate', 120)
    engine.setProperty('volume', 3)
    engine.say(text)
    engine.runAndWait()                

# Fonction pour écouter le système en espagnol
def speakEs(text):
    
    engine =pyttsx3.init()
    engine.setProperty('voice', 'spanish+f3')
    engine.setProperty('rate', 120)
    engine.setProperty('volume', 3)
    engine.say(text)
    engine.runAndWait()                

# Fonction pour activer les commandes de la reconnaissance vocale
def commande_vocale_process():
    
    with sr.Microphone() as mic:
        label_commande_vocale.configure(text="Réglage du bruit ambiant... Patientez...")
        print("Réglage du bruit ambiant... Patientez...")
        recognizer.adjust_for_ambient_noise(mic, duration=1)
        label_commande_vocale.configure(text="Vous pouvez parler...")
        print("Vous pouvez parler...")
        recorded_audio = recognizer.record(mic, duration=10)
        #recorded_audio = recognizer.listen(mic)
        label_commande_vocale.configure(text="Enregistrement terminé !")
        print("Enregistrement terminé !")

    try:
        text = recognizer.recognize_google(recorded_audio, 
        language="fr-FR")       
        text =text.lower()
        text = text.replace("bonjour c'est laura que puis-je faire pour vous", '')
        print("recognized text: " + text + "")        
        (modele, score) = process.extractOne(text, commandlist)
        print("Modele : " + modele)
        if score >=50:
            label_commande_vocale.configure(text="Commande: ({})".format(text))
            #lumière de la cuisine
            if modele == "allumer la lumière de la cuisine":
                print(modele)
                print("Vous avez dit : {}".format(text))
                on_btn_lumiere_cuisine_on()
                
            if modele =="fermer la lumière de la cuisine":
                print(modele)
                print("Vous avez dit : {}".format(text))
                on_btn_lumiere_cuisine_off()
                
            #lumière du salon   
            if modele == "allumer la lumière du salon":
                print(modele)
                print("Vous avez dit : {}".format(text)) 
                on_btn_lumiere_salon_on() 

            if modele =="fermer la lumière du salon":
                print(modele)
                print("Vous avez dit : {}".format(text))
                on_btn_lumiere_salon_off()
             
            #ventilateur
            if modele == "ouvrir le ventilateur":
                print(modele)
                print("Vous avez dit : {}".format(text))
                on_btn_ventilateur_on()    
                
            if modele == "fermer le ventilateur":
                print(modele)
                print("Vous avez dit : {}".format(text))
                on_btn_ventilateur_off()
            
            # Fonctionnalités de la musique
            if modele =="peux tu jouer une chanson de":
                chanson = text.replace('peux tu jouer une chanson de', '')
                speakFr("voici la chanson")
                pywhatkit.playonyt(chanson)
                print(modele)
                print("Vous avez dit : {}".format(text))
            
            if modele == "musique":
                files = os.listdir('Musica')
                print(files)
                randompiece = random.choice(files)
                print(randompiece)
                print(modele)
                print("Vous avez dit : {}".format(text))
                song = AudioSegment.from_mp3("./Musica/" + randompiece)
                play(song)
                
            #Fonctionnalités de wikipedia 
            if modele =="c'est qui":
                wikipedia.set_lang("fr")
                person = text.replace("c'est qui", '')
                personinfo = wikipedia.summary(person, sentences = 2)
                print(personinfo)
                speakFr(personinfo)
                print(modele)
                print("Vous avez dit : {}".format(text))
                
            if modele == "c'est quoi":
                wikipedia.set_lang("fr")
                objet = text.replace("c'est quoi", '')
                objetinfo = wikipedia.summary(objet, sentences = 2)
                print(objetinfo)
                speakFr(objetinfo)
                print(modele)
                print("Vous avez dit : {}".format(text))
                
            #Fonctionnalités des histoires drôles   
            if modele =="raconte moi une histoire drôle":
                blague = get_blague(blaguelist)
                speakFr(blague)
                print(modele)
                print(blague)
                print("Vous avez dit : {}".format(text))
                
            if modele =="raconte moi une blague de python":
                speakEn(pyjokes.get_joke(language="en", category="all"))
                print(pyjokes.get_joke())
                print(modele)
                print("Vous avez dit : {}".format(text))
           
            # Fonctionnalités du dictionnaire anglais
            if modele == "définition":
                mot = text.replace("définition", '')
                lemot = dictionary.meaning(mot)
                print(lemot['Noun'][0])
                speakEn(text= lemot['Noun'][0])
                print(modele)
                print("Vous avez dit : {}".format(text))
                
            #Fonctionnalités de la lecture de fichiers pdf                  
            if modele =="lire pdf":
                book =open(document, 'rb')
                reader= PyPDF2.PdfReader(book)
                totalpages = len(reader.pages)
                for i in range(totalpages):
                    page = reader.pages[i]
                    text =page.extract_text()        
                    speakFr(text)
                print(modele)
                print(text)
                print("Vous avez dit : {}".format(text))
            
            if modele =="lire pdf page":
                book =open(document, 'rb')
                reader= PyPDF2.PdfReader(book)
                page = text.replace("lire pdf page ", '')
                lapage = reader.pages[int(page)-1]
                text = lapage.extract_text()
                speakFr(text)
                print(modele)
                print(text)
                print("Vous avez dit : {}".format(text))
            
            #Fonctionnalités de traduction de textes
            if modele =="traduire en anglais":
                translated = translator.translate(text.replace("traduire en anglais", ''), dest ='en')
                print(translated.text.replace("traduire en anglais", ''))
                speakEn(translated.text.replace("traduire en anglais", ''))
                print(modele)
                print(text)
                print("Vous avez dit : {}".format(text))
                
            if modele =="traduire en espagnol":
                translated = translator.translate(text.replace("traduire en espagnol", ''), dest ='es')
                print(translated.text.replace("traduire en espagnol", ''))
                speakEs(translated.text.replace("traduire en espagnol", ''))
                print(modele)
                print(text)
                print("Vous avez dit : {}".format(text))
            
            #Fonctionnalité de recherche Google
            if modele =="google":
                googleinfo = text.replace('google', '')
                pywhatkit.search(googleinfo)
                print(googleinfo)
                print(modele)
                print("Vous avez dit : {}".format(text))
            
            #Fonctionnalité de navigation web
            if modele =="web":
                www = 'www.'
                site = text.replace("web", '')
                web.open(site)
                print(modele)
                print(site)
                print("Vous avez dit : {}".format(text))

            save_in_db(f"{text}")
            
            #Fonctionnalité de la caméra de sécurité
            if modele =="sécurité":
                print(modele)
                print("Vous avez dit : {}".format(text))
                while cam.isOpened():
                    ret, frame1 = cam.read()
                    ret, frame2 = cam.read()
                    diff = cv2.absdiff(frame1, frame2)
                    gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
                    blur = cv2.GaussianBlur(gray, (5, 5), 0)
                    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
                    dilated = cv2.dilate(thresh, None, iterations=3)
                    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    for c in contours:
                        if cv2.contourArea(c) < 6000:
                            continue
                        x, y, w, h = cv2.boundingRect(c)
                        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        song = AudioSegment.from_mp3('alert.wav')
                        play(song)

                    if cv2.waitKey(10) == ord('q'):
                        break
                    cv2.imshow('My Cam', frame1)          
                
        if len(text.encode('utf-8'))>2 and score<50:    #si le text contient 2 lettres ou plus  
            speakFr("la commande n'est pas claire")
            label_commande_vocale.configure(text="la commande n'est pas claire")
    except sr.UnknownValueError:
        speakFr("aucune commande détectée")
        label_commande_vocale.configure(text="aucune commande détectée")

# Fonction pour enregistrer audio
def on_btn_commande_vocale():
    
    speakFr("bonjour c'est laura que puis-je faire pour vous")
    commande_vocale_thread = Thread(target=commande_vocale_process, args=())
    commande_vocale_thread.start()

#Fonctionnalité pour l'affichage des rendez-vous
def on_btn_rendezvous_add():
    
    fen_rendezvous = customtkinter.CTkToplevel(fen1)
    fen_rendezvous.title("Rendez-Vous")
    fen_rendezvous.geometry("500x300")

    cal = Calendar(fen_rendezvous, selectmode='day')
    cal.pack(expand=YES, fill=BOTH)
    description = StringVar()

    def on_btn_save_rendezvous():

        desc = description.get()
        date = cal.get_date()
        datetime_object = datetime.strptime(date, '%Y-%m-%d')
        today = datetime.now()
        if datetime_object > today:
            save_rendezvous(str(date), desc)
            fen_rendezvous.destroy()

    rendezvous_input = Entry(fen_rendezvous, textvariable=description).pack(expand=YES, fill=BOTH)
    customtkinter.CTkButton(fen_rendezvous, text="Save", command=on_btn_save_rendezvous).pack(expand=YES, fill=BOTH)

def on_btn_rendezvous_display():
    
    fen_rendezvous = customtkinter.CTkToplevel(fen1)
    fen_rendezvous.title("Rendez-Vous")
    fen_rendezvous.geometry("800x400")

    rendezvous = ttk.Treeview(fen_rendezvous, show="headings", height=20, selectmode="extended")
    rendezvous["columns"] = ("date", "rendez-vous")
    rendezvous.column("date", anchor="center")
    rendezvous.column("rendez-vous", anchor="center")
    rendezvous.heading("date", text="Date")
    rendezvous.heading("rendez-vous", text="Rendez-vous")

    data_rendezvous = rendezvousdb.find()
    i = 0
    for doc in data_rendezvous:
        i = i+1
        rendezvous.insert("", i, values=(doc["date"], doc["rendez-vous"]))
    rendezvous.pack(expand=YES, fill=BOTH)

btn_lumiere_cuisine_on = customtkinter.CTkButton(fen1, text= "ON", command = on_btn_lumiere_cuisine_on)
btn_lumiere_cuisine_on.grid(row=1, column = 1)

btn_lumiere_cuisine_off = customtkinter.CTkButton(fen1, text= "OFF", command = on_btn_lumiere_cuisine_off)
btn_lumiere_cuisine_off.grid(row=1, column = 2)

btn_lumiere_salon_on = customtkinter.CTkButton(fen1, text= "ON", command = on_btn_lumiere_salon_on)
btn_lumiere_salon_on.grid(row=3, column=1)

btn_lumiere_salon_off = customtkinter.CTkButton(fen1, text= "OFF", command = on_btn_lumiere_salon_off)
btn_lumiere_salon_off.grid(row=3, column=2)

btn_ventilateur_on = customtkinter.CTkButton(fen1, text= "ON", command = on_btn_ventilateur_on)
btn_ventilateur_on.grid(row=5, column = 1)

btn_ventilateur_off = customtkinter.CTkButton(fen1, text= "OFF", command = on_btn_ventilateur_off)
btn_ventilateur_off.grid(row=5, column = 2)

switch_var = customtkinter.StringVar(value="off")

def ventillateur_switch():
    
    valeur = switch_var.get()
    client_mqtt = get_client_mqtt()
    print(valeur)
    if valeur == "on":
        # Les boutons du ventilateur seront désactivés et envoie un message MQTT
        # pour activer le thread du contrôle automatique du ventilateur
        message = "automatic"
        btn_ventilateur_on.configure(state="disabled")
        btn_ventilateur_off.configure(state="disabled")
    else:
        message = "manual"
        btn_ventilateur_on.configure(state="normal")
        btn_ventilateur_off.configure(state="normal")
    client_mqtt.publish(topic="Commande/Ventilateur", payload=message)
    client_mqtt.disconnect()

switch_1 = customtkinter.CTkSwitch(master=fen1, text="Automatique", command=ventillateur_switch,
                                   variable=switch_var, onvalue="on", offvalue="off")
switch_1.grid(row=5, column=4)


btn_commande_vocale = customtkinter.CTkButton(fen1, text= "Commande Vocale", command = on_btn_commande_vocale)
btn_commande_vocale.grid(row=7, column = 0)

btn_historique = customtkinter.CTkButton(fen1, text= "Afficher", command = on_btn_historique)
btn_historique.grid(row=9, column = 1)

btn_rendezvous_display = customtkinter.CTkButton(fen1, text="Afficher", command=on_btn_rendezvous_display)
btn_rendezvous_display.grid(row=11, column=1)

btn_rendezvous_add = customtkinter.CTkButton(fen1, text="Ajouter", command=on_btn_rendezvous_add)
btn_rendezvous_add.grid(row=11, column=2)

def on_message_lumiere_cuisine(client, userdata, message):
    
    label_lumiere_cuisine.configure(text=message.payload.decode("utf-8") )
    if message.payload.decode("utf-8") == "ON":
        speakFr("la lumière de la cuisine est allumée")
    else:
        speakFr("la lumière de la cuisine est fermée")

def on_message_lumiere_salon(client, userdata, message):
    
    label_lumiere_salon.configure(text=message.payload.decode("utf-8") )
    if message.payload.decode("utf-8") == "ON":
        speakFr("la lumière du salon est allumée")
    else:
        speakFr("la lumière du salon est fermée")    

def on_message_ventilateur(client, userdata, message):
    
    label_ventilateur.configure(text=message.payload.decode("utf-8") )
    if message.payload.decode("utf-8") == "ON":
        speakFr("le ventilateur est ouvert")
    else:
        speakFr("le ventilateur est fermé")

def subscribe_status():
    
    host          = "localhost"
    port          = 1883
    clean_session = True
    client_id     = "Status"
    user_name     = "Maherkhaznaji"
    password      = "maher123"

    client = mqtt.Client(clean_session = clean_session)
    client.message_callback_add("Status/LumiereCuisine", on_message_lumiere_cuisine)
    client.message_callback_add("Status/LumiereSalon", on_message_lumiere_salon)
    client.message_callback_add("Status/Ventilateur", on_message_ventilateur)
    client.connect(host, port)
    client.subscribe("Status/#")
    client.loop_forever()

mqtt_thread = Thread(target=subscribe_status, args=())
mqtt_thread.start()

def show_temperature():
    
    while True:
        temps = obtenir_temps()
        label_temps.configure(text="{}:{}:{}".format(temps[0], temps[1], temps[2]))
        time.sleep(1)

temps_thread = Thread(target=show_temperature, args=())
temps_thread.start()

def show_meteo():
    
    meteo_image = PhotoImage()
    while True:
        meteo, status = obtenir_meteo()
        if status == "Clouds":
            meteo_image.configure(file="Meteo/clouds.png")
        if status == "Rain":
            meteo_image.configure(file="Meteo/rain.png")
        if status == "Clear":
            meteo_image.configure(file="Meteo/sun.png")
        if status == "Snow":
            meteo_image.configure(file="Meteo/snow.png")           
        else:
            meteo_image.configure(file="Meteo/storm.png")
        label_meteo.configure(image=meteo_image)
        label_temperature.configure(text=str(meteo['temp'])+"°C")
        time.sleep(60)

meteo_thread = Thread(target=show_meteo, args=())
meteo_thread.start()

fen1.mainloop()
