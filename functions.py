import pandas as pd
import random
from faker import Faker


fake = Faker('pl_PL')

# dane osoobowe
def pobierz_dane_osobowe():
    try:
        df_imionam = pd.read_csv('datasets/imiona_m.csv')
        df_nazwiskam = pd.read_csv('datasets/nazwiska_m.csv')
        df_imionak = pd.read_csv('datasets/imiona_k.csv')
        df_nazwiskak = pd.read_csv('datasets/nazwiska_k.csv')
        imionam = df_imionam.iloc[:, 0].dropna().tolist()
        nazwiskam = df_nazwiskam.iloc[:, 0].dropna().tolist()
        imionak = df_imionak.iloc[:, 0].dropna().tolist()
        nazwiskak = df_nazwiskak.iloc[:, 0].dropna().tolist()
        return imionam, nazwiskam, imionak, nazwiskak
    except:
        print('Błąd ładowania data setów')

IMIONAM, NAZWISKAM, IMIONAK, NAZWISKAK = pobierz_dane_osobowe()

def losuj_osobe():
    plec = random.choice(['M', 'K'])

    if plec == 'M' and IMIONAM and NAZWISKAM:
        return random.choice(IMIONAM).title(), random.choice(NAZWISKAM).title(), 'M'
    elif plec == 'K' and IMIONAK and NAZWISKAK:
        return random.choice(IMIONAK).title(), random.choice(NAZWISKAK).title(), "K"



def czas_konkurencji(id_konkurencji):
    if id_konkurencji == 1:    # Sprint 50cm
        return random.randint(4, 12)
    elif id_konkurencji == 2:  # Skok przez płotki
        return random.randint(8, 20)
    elif id_konkurencji == 3:  # Chomiczy Maraton (422cm)
        return random.randint(180, 400)
    elif id_konkurencji == 4:  # Półmaraton (211cm)
        return random.randint(80, 180)
    elif id_konkurencji == 5:  # Wspinaczka
        return random.randint(15, 50)
    elif id_konkurencji == 6:  # Kołowrotek (wytrzymałość)
        return random.randint(60, 600)
    elif id_konkurencji == 7:  # Grand Prix Formuły Ch (3 okrążenia)
        return random.randint(40, 120)
    else:
        return random.randint(30, 90) # bezpiecznik