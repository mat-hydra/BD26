import pandas as pd
import random
from sqlalchemy import create_engine, text
from faker import Faker
from datetime import datetime, timedelta

# KONFIGURACJA
CONN_STR = "mysql+mysqlconnector://root:@localhost/MWFC"
fake = Faker('pl_PL')

# 1. STRUKTURA BAZY
f = open("db_structure.sql", 'r', encoding='utf-8')

SQL_STRUCTURE = f.read()

# 2. DANE OSOBOWE
def pobierz_dane_osobowe():
    try:
        df_imionam = pd.read_csv('imiona_m.csv')
        df_nazwiskam = pd.read_csv('nazwiska_m.csv')
        df_imionak = pd.read_csv('imiona_k.csv')
        df_nazwiskak = pd.read_csv('nazwiska_k.csv')
        imionam = df_imionam.iloc[:, 0].dropna().tolist()
        nazwiskam = df_nazwiskam.iloc[:, 0].dropna().tolist()
        imionak = df_imionak.iloc[:, 0].dropna().tolist()
        nazwiskak = df_nazwiskak.iloc[:, 0].dropna().tolist()
        return imionam, nazwiskam, imionak, nazwiskak
    except:
        return [], [], [], []

IMIONAM, NAZWISKAM, IMIONAK, NAZWISKAK = pobierz_dane_osobowe()

def losuj_osobe():
    plec = random.choice(['M', 'K'])
    
    if plec == 'M' and IMIONAM and NAZWISKAM:
        return random.choice(IMIONAM).title(), random.choice(NAZWISKAM).title(), 'M'
    elif plec == 'K' and IMIONAK and NAZWISKAK:
        return random.choice(IMIONAK).title(), random.choice(NAZWISKAK).title(), "K"

# 3. GENERATORY DANYCH

def gen_pracownicy(n=40):
    dane = []
    start_federacji = datetime.now() - timedelta(days=5*365)
    
    for i in range(1, n + 1):
        im, naz, _ = losuj_osobe()
        
        # zatrudnienia w ciągu ostatnich 5 lat
        data_zatrudnienia = fake.date_between(start_date=start_federacji, end_date='-1y')
        
        # 50% szans, że pracownik już nie pracuje
        czy_odszedl = random.random() < 0.5
        data_zwolnienia = None
        
        if czy_odszedl:
            # Data zwolnienia>dacie zatrudnienia
            data_zwolnienia = fake.date_between(start_date=data_zatrudnienia, end_date='today')
        
        dane.append({
            'id_pracownika': i,
            'imie': im,
            'nazwisko': naz,
            'pracuje_od': data_zatrudnienia,
            'pracuje_do': data_zwolnienia,
            'mail': f"{im[:3].lower()}{naz.lower()}@federacja.pl",
            'telefon': fake.phone_number()[:20],
            'adres': fake.address().replace('\n', ', '),
            'miasto': fake.city()
        })
    
    df = pd.DataFrame(dane)
    
    # Walidacja ilości
    pracujacy_obecnie = df[df['pracuje_do'].isna()]
    if len(pracujacy_obecnie) < 3:
        return gen_pracownicy(n)
        
    return df

def gen_sponsorzy(n=10):
    dane = []
    for i in range(1, n + 1):
        dane.append({
            'id_sponsora': i,
            'nazwa': fake.company(),
            'wspolpraca_od': fake.date_between(start_date='-5y', end_date='-2y'),
            'wspolpraca_do': fake.date_between(start_date='today', end_date='+2y'),
            'opis': fake.bs(),
            'telefon': fake.phone_number(),
            'mail': fake.company_email()
        })
    return pd.DataFrame(dane)

def gen_chomiki(n=60, max_sponsor=10):
    dane = []
    rasy = ['Syryjski', 'Dżungarski', 'Roborowskiego']
    dzisiaj = datetime.now().date()
    
    for i in range(1, n + 1):
        im, _, plec = losuj_osobe()
        urodzenie = fake.date_between(start_date='-7y', end_date='-6m')
        
        smierc = None
        # wiecej niż 3 lata => nie żyje
        if dzisiaj - urodzenie > timedelta(days=3*365):
            # śnierć między 3 miesiącem a 3 rokiem życia
            start_s = urodzenie + timedelta(days=180)
            koniec_s = urodzenie + timedelta(days=3*365)
            smierc = fake.date_between(start_date=start_s, end_date=koniec_s)
        else:
            # 20% śmiertelności
            if random.random() < 0.2:
                start_s = urodzenie + timedelta(days=180)
                # starsze niż 6 miesięcy
                if start_s < dzisiaj:
                    smierc = fake.date_between(start_date=start_s, end_date='today')
                else:
                    smierc = None
        dane.append({
            'id_chomika': i,
            'imie': im,
            'plec': plec,
            'data_urodzenia': urodzenie,
            'data_smierci': smierc,
            'waga': random.randint(30, 150),
            'historia': fake.sentence(),
            'rasa': random.choice(rasy),
            'id_sponsora': random.randint(1, max_sponsor)
        })
    return pd.DataFrame(dane)

def gen_zawody(n=15):
    dane = []
    
    for i in range(1, n+1):
        miasto = fake.city()
        data = fake.date_between(start_date='-5y', end_date='+1y')
        if data > datetime.now().date():
            status = "planowane"
        elif data == datetime.now().date():
            status = "w trakcie"
        else:
            status = "odbyte"
        
        dane.append({
            'id_zawodow': i,
            'nazwa': f"Grand Prix {miasto}",
            'termin': data,
            'panstwo': 'Polska',
            'miasto': miasto,
            'status': status
        })
    return pd.DataFrame(dane)

def gen_konkurencje():
    lista = [
        {'id_konkurencji': 1, 'nazwa': 'Sprint', 'kategorie': 'formula CH', 'charakterystyka': 'Bieg na 5m'},
        {'id_konkurencji': 2, 'nazwa': 'Kołowrotek', 'kategorie': 'naturalne', 'charakterystyka': 'Dystans w 1min'},
        {'id_konkurencji': 3, 'nazwa': 'Labirynt', 'kategorie': 'formula CH', 'charakterystyka': 'Czas wyjścia'}
    ]
    return pd.DataFrame(lista)

def gen_przebieg(n=200, df_zawody=None, df_chomiki=None, max_konk=3):
    dane = []

    df_odbyte = df_zawody[df_zawody['status'] == 'odbyte']
    
    # Zabezpieczenie na wypadek braku odbytych zawodów
    for i in range(1, n+1):
        zawody = df_odbyte.sample(1).iloc[0] 
        chomik = df_chomiki.sample(1).iloc[0]
        termin_zawodow = zawody['termin']
        
        # data zawodów musi być późniejsza niż data urodzin chomika
        if zawody['termin'] < chomik['data_urodzenia']:
            continue
        
        if chomik['data_smierci'] and termin_zawodow > chomik['data_smierci']:
            continue
        
        id_konk = random.randint(1, max_konk)
        
        # Zróżnicowanie czasu zw wzg. na konkurencje
        if id_konk == 1:    # Sprint
            czas = random.randint(10, 25)
        elif id_konk == 2:  # Kołowrotek - stały czas testu
            czas = 60
        else:   # Labirynt
            czas = random.randint(30, 120)
                
        dane.append({
            'id_przebiegu': i,
            'godzina': fake.time(),
            'zwyciezca': random.choice([True, False, False]),
            'czas': czas,
            'id_chomika': chomik['id_chomika'],
            'id_zawodow': zawody['id_zawodow'],
            'id_konkurencji': random.randint(1, max_konk)
        })
    return pd.DataFrame(dane)

def gen_substancje():
    return pd.DataFrame([
        {'id_substancji': 1, 'nazwa': 'Słonecznik modyfikowany'},
        {'id_substancji': 2, 'nazwa': 'Kofeina gryzoniowa'}
    ])

def gen_kontrola(n=20, df_chomiki=None, max_chomik=60):
    dane = []
    dzisiaj = datetime.now().date()
    
    for i in range(1, n + 1):
        chomik = df_chomiki.sample(1).iloc[0]
        
        start_zycia = chomik['data_urodzenia']
        koniec_zycia = chomik['data_smierci'] if chomik['data_smierci'] else dzisiaj
        
        if random.random() < 0.2:
            substancja = random.choice([1, 2])
        else:
            substancja = None

        dane.append({
            'id_kontroli': i,
            'data_badania': fake.date_between(start_date=start_zycia, end_date=koniec_zycia),
            'id_chomika': chomik['id_chomika'],
            'id_substancji': substancja
        })
    return pd.DataFrame(dane)

def gen_rejestracja(df_chomiki):
    dane = []
    for _, chomik in df_chomiki.iterrows():
        dane.append({
            'id_chomika': chomik['id_chomika'],
            'wpisowe': 50.00,
            'zaksiegowane': True
        })
    return pd.DataFrame(dane)

def gen_finanse(df_rejestracja):
    dane = []
    id_counter = 1
    for _, reg in df_rejestracja.iterrows():
        dane.append({
            'id_transakcji': id_counter,
            'tytul': 'Opłata wpisowa',
            'dane_transakcji': f'Wpłata ID {reg["id_chomika"]}',
            'data': fake.date_this_year(),
            'dochod': reg['wpisowe'],
            'id_chomika': reg['id_chomika']
        })
        id_counter += 1
    return pd.DataFrame(dane)

def gen_wyplaty(df_pracownicy):
    dane = []
    id_counter = 1
    for _, pracownik in df_pracownicy.iterrows():
        start = pracownik['pracuje_od']
        koniec = pracownik['pracuje_do'] if pracownik['pracuje_do'] else datetime.now().date()
        
        # Generuj wypłaty co miesiąc od daty zatrudnienia
        aktualna_data = start + timedelta(days=30)
        while aktualna_data <= koniec:
            dane.append({
                'id_wyplaty': id_counter,
                'kwota_zl': random.randint(4300, 8500), # Powyżej płacy minimalnej
                'data_wypłaty': aktualna_data,
                'id_pracownika': pracownik['id_pracownika']
            })
            id_counter += 1
            aktualna_data += timedelta(days=30) # Kolejny miesiąc pracy
    return pd.DataFrame(dane)

# 4. URUCHOMIENIE

def main():
    if not SQL_STRUCTURE:
        return

    # Inicjalizacja połączenia z XAMPP
    engine = create_engine(CONN_STR)

    print("Rozpoczynanie tworzenia struktury bazy danych...")
    with engine.connect() as conn:
        # Wyłączenie kluczy obcych na czas przebudowy
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        tabele = ['wyplaty', 'finanse', 'rejestracja_chomika', 'kontrola_antydopingowa', 
                  'przebieg', 'chomiki', 'zawody', 'konkurencje', 'sponsorzy', 
                  'pracownicy', 'substancje_zakazane']
        
        for tabela in tabele:
            conn.execute(text(f"DROP TABLE IF EXISTS {tabela};"))
        
        # Wykonywanie instrukcji z pliku SQL (tworzenie od nowa)
        for stmt in SQL_STRUCTURE.split(';'):
            if stmt.strip():
                conn.execute(text(stmt))
        
        conn.commit()
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    # Generowanie danych

    ilosc_chomikow = 60

    df_prac = gen_pracownicy(10)
    df_prac.to_sql('pracownicy', engine, if_exists='append', index=False)
    
    df_spon = gen_sponsorzy(10)
    df_spon.to_sql('sponsorzy', engine, if_exists='append', index=False)
    
    df_chom = gen_chomiki(ilosc_chomikow, 10)
    df_chom.to_sql('chomiki', engine, if_exists='append', index=False)
    
    df_zaw = gen_zawody(15)
    df_zaw.to_sql('zawody', engine, if_exists='append', index=False)
    
    df_konk = gen_konkurencje()
    df_konk.to_sql('konkurencje', engine, if_exists='append', index=False)
    
    df_przeb = gen_przebieg(200, df_zaw, df_chom, len(df_konk))
    df_przeb.to_sql('przebieg', engine, if_exists='append', index=False)
    
    df_subs = gen_substancje()
    df_subs.to_sql('substancje_zakazane', engine, if_exists='append', index=False)
    
    df_kontr = gen_kontrola(20, df_chom)
    df_kontr.to_sql('kontrola_antydopingowa', engine, if_exists='append', index=False)
    
    df_rej = gen_rejestracja(df_chom)
    df_rej.to_sql('rejestracja_chomika', engine, if_exists='append', index=False)
    
    df_fin = gen_finanse(df_rej)
    df_fin.to_sql('finanse', engine, if_exists='append', index=False)
    
    df_wyp = gen_wyplaty(df_prac)
    df_wyp.to_sql('wyplaty', engine, if_exists='append', index=False)

if __name__ == "__main__":
    main()