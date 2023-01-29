from playsound import playsound
import random
import os

'''
On doit toujours mentioner la path du dossier ou les fichiers musiques trouvent
'''
path = ""
files = os.listdir(path)
d = random.choice(files)
playsound("path" + d)
