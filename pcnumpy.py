import numpy as np
import random
import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[3])
print(voices[1])
engine.setProperty('rate', 30)
# Set volume 0-1
engine.setProperty('volume', 0.1)
engine.say("bonjour")
engine.runAndWait()


rev =[1,3,5,7,9,11]
def moyenne(liste):
    return sum(liste)/len(liste)
print(moyenne(rev))
print(np.mean(rev))
revenu_array= np.array(rev)
print(revenu_array.size)
print(revenu_array.shape)
print(revenu_array.ndim)
print(np.append(revenu_array,12))
print(revenu_array[(revenu_array > 5) & (revenu_array < 11)])
print(revenu_array.shape)
print(revenu_array.mean())
print(revenu_array.max())
print(revenu_array.min())
print(revenu_array.argmin())
print(revenu_array.argmax())
print(revenu_array.sum())
# ordonner par ordre croissant :
revenu_array.sort()
print('revenu',revenu_array)

numbers = [1, 2, 3]
letters = ['a', 'b', 'c']
zipped = zip(numbers, letters)
print('f', zipped)  # Holds an iterator object
# test
print(list(zipped))
print(list(zip(range(5), range(100))))
letters = ['a', 'b', 'c']
numbers = [0, 1, 2]
for l, n in zip(letters, numbers):
    print(f'Letter: {l}')
    print(f'Number: {n}')
blaguelist = ['raconte moi une histoire drole un',
              'raconte moi une histoire drole deux',
              'raconte moi une histoire drole toi',
              'raconte moi une histoire drole ma',
              'raconte moi une histoire drole ta']
def get_blague(liste):
    return random.choice(liste)
ac = get_blague(blaguelist)
print(ac)
