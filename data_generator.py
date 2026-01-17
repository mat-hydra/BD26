import pandas as pd
import random
from sqlalchemy import create_engine, text
from faker import Faker
from datetime import datetime, timedelta
import functions

# KONFIGURACJA
CONN_STR = "mysql+mysqlconnector://root:@localhost/MWFC"
fake = Faker('pl_PL')

# 1. STRUKTURA BAZY
f = open("db_structure.sql", 'r', encoding='utf-8')

SQL_STRUCTURE = f.read()


# 3. GENERATORY DANYCH

# 3.1 tabele niezależne

def gen_kraje(n=5):
    dane = []
    for i in range(1, n + 1):
        dane.append({
            'id_kraju': i,
            'nazwa': fake.unique.country()
        })
    return pd.DataFrame(dane)


def gen_rasa():
    dane = [
        {'id_rasy': 1, 'nazwa': 'Syryjski', 'cechy': fake.bs()},
        {'id_rasy': 2, 'nazwa': 'Dżungarski', 'cechy': fake.bs()},
        {'id_rasy': 3, 'nazwa': 'Roborowskiego', 'cechy': fake.bs()},
        {'id_rasy': 4, 'nazwa': 'Campbella', 'cechy': fake.bs()},
        {'id_rasy': 5, 'nazwa': 'Chiński', 'cechy': fake.bs()}
    ]
    return pd.DataFrame(dane)


def gen_typ_transakcji():
    dane = [
        {'id_typu': 1, 'nazwa': 'Opłata rejestracyjna', 'opis': 'Jednorazowa opłata wpisowa za  chomika do federacji'},
        {'id_typu': 2, 'nazwa': 'Zakup Merchu', 'opis': 'Sprzedaż oficjalnych gadżetów federacji'},
        {'id_typu': 3, 'nazwa': 'Bilet wstępu', 'opis': 'Bilet na trybuny'},
        {'id_typu': 4, 'nazwa': 'Inne'}
    ]
    return pd.DataFrame(dane)


def gen_sponsorzy(n=10):
    dane = []
    for i in range(1, n + 1):
        dane.append({
            'id_sponsora': i,
            'nazwa': fake.company(),
            'wspolpraca_od': fake.date_between(start_date='-5y', end_date='-2y'),
            'wspolpraca_do': fake.date_between(start_date='today', end_date='+2y'),
            'opis': fake.catch_phrase(),
            'telefon': fake.phone_number(),
            'mail': fake.company_email()
        })
    return pd.DataFrame(dane)


def gen_konkurencje():
    lista = [
        {'id_konkurencji': 1, 'nazwa': 'Sprint', 'kategorie': 'formula CH', 'charakterystyka': 'Bieg na 5m'},
        {'id_konkurencji': 2, 'nazwa': 'Kołowrotek', 'kategorie': 'naturalne', 'charakterystyka': 'Dystans w 1min'},
        {'id_konkurencji': 3, 'nazwa': 'Labirynt', 'kategorie': 'formula CH', 'charakterystyka': 'Czas wyjścia'}
    ]
    return pd.DataFrame(lista)


def gen_substancje():
    return pd.DataFrame([
        {'id_substancji': 1, 'nazwa': 'Słonecznik modyfikowany'},
        {'id_substancji': 2, 'nazwa': 'Kofeina gryzoniowa'}
    ])


# 3.2 tabele 1st

def gen_miasta(df_kraje, miasta_na_kraj=3):
    dane = []
    id_miasta = 1
    for _, kraj in df_kraje.iterrows():
        # każdy kraj => kilka miast
        for _ in range(miasta_na_kraj):
            dane.append({
                'id_miasta': id_miasta,
                'nazwa': fake.city(),
                'id_kraju': kraj['id_kraju']
            })
            id_miasta += 1
    return pd.DataFrame(dane)


def gen_chomiki(n=60, max_sponsor=10, df_rasy=None):
    dane = []

    dzisiaj = datetime.now().date()


    wagi_ras = {
        1: (80, 150),  # Syryjski
        2: (18, 45),   # Dżungarski
        3: (16, 26),   # Roborowskiego
        4: (20, 40),   # Campbella
        5: (25, 45)    # Chiński
    }


    for i in range(1, n + 1):
        im, _, plec = functions.losuj_osobe()
        urodzenie = fake.date_between(start_date='-7y', end_date='-6m')

        smierc = None
        # wiecej niż 3 lata => nie żyje
        if dzisiaj - urodzenie > timedelta(days=3 * 365):
            # śnierć między 3 miesiącem a 3 rokiem życia
            start_s = urodzenie + timedelta(days=180)
            koniec_s = urodzenie + timedelta(days=3 * 365)
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

        wylosowana_rasa = df_rasy.sample(1).iloc[0]
        id_rasy = int(wylosowana_rasa['id_rasy'])
        min_w, max_w = wagi_ras.get(id_rasy, (30, 100))
        waga = random.randint(min_w, max_w)

        dane.append({
            'id_chomika': i,
            'imie': im,
            'plec': plec,
            'data_urodzenia': urodzenie,
            'data_smierci': smierc,
            'waga': waga,
            'historia': fake.sentence(),
            'id_rasy': id_rasy,
            'id_sponsora': random.randint(1, max_sponsor)
        })
    return pd.DataFrame(dane)


# 3.3 tabele 2st
def gen_pracownicy(n=40, df_miasta=None):
    dane = []
    start_federacji = datetime.now() - timedelta(days=5 * 365)

    for i in range(1, n + 1):
        im, naz, _ = functions.losuj_osobe()

        # zatrudnienia w ciągu ostatnich 5 lat
        data_zatrudnienia = fake.date_between(start_date=start_federacji, end_date='-1y')
        data_zwolnienia = None
        # pewnosc 3 aktualnych pracownikow i 50% szans na odejście kolejnych
        if i <= 3:
            czy_odszedl = False
        else:
            czy_odszedl = random.random() < 0.5

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
            'id_miasta': df_miasta.sample(1).iloc[0]['id_miasta'],
            'ulica': fake.street_name(),
            'nr_domu': fake.building_number(),
            'kod_pocztowy': fake.postcode()
        })
    df = pd.DataFrame(dane)

    # Walidacja ilości
    pracujacy_obecnie = df[df['pracuje_do'].isna()]
    if len(pracujacy_obecnie) < 3:
        return gen_pracownicy(n)

    return df


def gen_zawody(n=15, df_miasta=None):
    dane = []

    for i in range(1, n + 1):
        miasto = df_miasta.sample(1).iloc[0]
        data = fake.date_between(start_date='-5y', end_date='+1y')
        if data > datetime.now().date():
            status = "planowane"
        elif data == datetime.now().date():
            status = "w trakcie"
        else:
            status = "odbyte"

        dane.append({
            'id_zawodow': i,
            'nazwa': f"Grand Prix {miasto['nazwa']}",
            'termin': data,
            'id_miasta': miasto['id_miasta'],
            'status': status
        })
    return pd.DataFrame(dane)


def gen_wyplaty(df_pracownicy):
    dane = []
    id_counter = 1
    for _, pracownik in df_pracownicy.iterrows():
        start = pracownik['pracuje_od']
        koniec = pracownik['pracuje_do'] if pracownik['pracuje_do'] else datetime.now().date()

        # comiesieczna wyplata(min. minimalna krajowa)
        aktualna_data = start + timedelta(days=30)
        while aktualna_data <= koniec:
            dane.append({
                'id_wyplaty': id_counter,
                'kwota_zl': random.randint(4806, 8500),
                'data_wyplaty': aktualna_data,
                'id_pracownika': pracownik['id_pracownika']
            })
            id_counter += 1
            aktualna_data += timedelta(days=30)  # Kolejny miesiąc pracy
    return pd.DataFrame(dane)


def gen_finanse(df_chomiki, n_trans=100):
    dane = []
    id_counter = 1
    # rejestracja kazdego chomika
    for _, chomik in df_chomiki.iterrows():
        dane.append({
            'id_transakcji': id_counter,
            'data_transakcji': chomik['data_urodzenia'],
            'kwota': 50.00,
            'id_typu': 1,
            'id_chomika': chomik['id_chomika'],
            'uwagi': f"Wpisowe: {chomik['imie']}"
        })
        id_counter += 1

    # bilety i merch
    for i in range(n_trans):
        typ = random.choice([2, 3])  # 2 = merch, 3 = bilet

        if typ == 2:  # merch
            kwota = random.randint(10, 200) + random.randint(0, 99) / 100  # cena merch rand
            uwagi = "Zakup gadżetów federacji"
        else:  # bilety
            kwota = random.randint(10, 40) + random.randint(0, 99) / 100  # cena biletow rand
            uwagi = "Bilet wstępu na zawody"

        dane.append({
            'id_transakcji': id_counter,
            'data_transakcji': fake.date_this_year(),
            'kwota': kwota,
            'id_typu': typ,
            'id_chomika': None,
            'uwagi': uwagi
        })
        id_counter += 1
    return pd.DataFrame(dane)


def gen_przebieg(n=200, df_zawody=None, df_chomiki=None, df_konkurencje=None):
    dane = []

    df_odbyte = df_zawody[df_zawody['status'] == 'odbyte']

    for _, zawody in df_odbyte.iterrows():
        termin = zawody['termin']
        zyjace_chomiki = df_chomiki[
            (df_chomiki['data_urodzenia'] + timedelta(days=30) < termin)
            & ((df_chomiki['data_smierci'] > termin) | (df_chomiki['data_smierci'].isna()))
            ]

        if zyjace_chomiki.empty:
            continue

        for _ in range(3, len(zyjace_chomiki) // 5):
            chomik = zyjace_chomiki.sample(1).iloc[0]

            id_konk = random.randint(1, len(df_konkurencje))

            # Zróżnicowanie czasu zw wzg. na konkurencje
            if id_konk == 1:  # Sprint
                czas = random.randint(10, 25)
            elif id_konk == 2:  # Kołowrotek - stały czas testu
                czas = 60
            else:  # Labirynt
                czas = random.randint(30, 120)

            dane.append({
                'id_przebiegu': len(dane) + 1,
                'godzina': fake.time(),
                'zwyciezca': random.choice([True, False, False]),
                'czas': czas,
                'id_chomika': chomik['id_chomika'],
                'id_zawodow': zawody['id_zawodow'],
                'id_konkurencji': id_konk
            })

    return pd.DataFrame(dane)


def gen_kontrola(n=20, df_chomiki=None, df_substancje=None):
    dane = []
    dzisiaj = datetime.now().date()

    for i in range(1, n + 1):
        chomik = df_chomiki.sample(1).iloc[0]

        start_zycia = chomik['data_urodzenia']
        koniec_zycia = chomik['data_smierci'] if chomik['data_smierci'] else dzisiaj

        if random.random() < 0.2:
            substancja = df_substancje.sample(1).iloc[0]['id_substancji']
        else:
            substancja = None

        dane.append({
            'id_kontroli': i,
            'data_badania': fake.date_between(start_date=start_zycia, end_date=koniec_zycia),
            'id_chomika': chomik['id_chomika'],
            'id_substancji': substancja
        })
    return pd.DataFrame(dane)


# 4. URUCHOMIENIE

def main():
    if not SQL_STRUCTURE:
        return

    # połączenie z hostem db
    engine = create_engine(CONN_STR)

    print("Tworzenia struktury bazy danych...")
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        istniejace_tabele = [row[0] for row in result]

        # nadpisywanie tabel, wyłaczenie FK
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

        for tabela in istniejace_tabele:
            conn.execute(text(f'DROP TABLE IF EXISTS {tabela};'))

        # instrukcje sql, nowa generacja dancyh
        for stmt in SQL_STRUCTURE.split(';'):
            if stmt.strip():
                conn.execute(text(stmt))

        conn.commit()
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    # Generowanie danych

    ilosc_chomikow = 60

    df_kraje = gen_kraje()
    df_kraje.to_sql('kraje', engine, if_exists='append', index=False)

    df_rasy = gen_rasa()
    df_rasy.to_sql('rasa', engine, if_exists='append', index=False)

    df_typ_transakcji = gen_typ_transakcji()
    df_typ_transakcji.to_sql('typ_transakcji', engine, if_exists='append', index=False)

    df_spon = gen_sponsorzy(10)
    df_spon.to_sql('sponsorzy', engine, if_exists='append', index=False)

    df_konkurencje = gen_konkurencje()
    df_konkurencje.to_sql('konkurencje', engine, if_exists='append', index=False)

    df_substancje = gen_substancje()
    df_substancje.to_sql('substancje_zakazane', engine, if_exists='append', index=False)

    df_miasta = gen_miasta(df_kraje)
    df_miasta.to_sql('miasta', engine, if_exists='append', index=False)

    df_chomiki = gen_chomiki(ilosc_chomikow, 10, df_rasy)
    df_chomiki.to_sql('chomiki', engine, if_exists='append', index=False)

    df_pracownicy = gen_pracownicy(10, df_miasta)
    df_pracownicy.to_sql('pracownicy', engine, if_exists='append', index=False)

    df_zawody = gen_zawody(15, df_miasta)
    df_zawody.to_sql('zawody', engine, if_exists='append', index=False)

    df_wyplaty = gen_wyplaty(df_pracownicy)
    df_wyplaty.to_sql('wyplaty', engine, if_exists='append', index=False)

    df_finanse = gen_finanse(df_chomiki)
    df_finanse.to_sql('finanse', engine, if_exists='append', index=False)

    df_przebieg = gen_przebieg(200, df_zawody, df_chomiki, df_konkurencje)
    df_przebieg.to_sql('przebieg', engine, if_exists='append', index=False)

    df_kontrola = gen_kontrola(20, df_chomiki, df_substancje)
    df_kontrola.to_sql('kontrola_antydopingowa', engine, if_exists='append', index=False)


if __name__ == "__main__":
    main()
