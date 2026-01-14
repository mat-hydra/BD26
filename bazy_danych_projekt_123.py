import pandas as pd
import random
from sqlalchemy import create_engine, text
from faker import Faker
from datetime import datetime, timedelta

# KONFIGURACJA
CONN_STR = "mysql+mysqldb://root:@localhost/Baza"
fake = Faker('pl_PL')

# 1. STRUKTURA BAZY
SQL_STRUCTURE = """
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS wyplaty, finanse, kontrola_antydopingowa, substancje_zakazane, 
przebieg, konkurencje, zawody, rejestracja_chomika, chomiki, sponsorzy, pracownicy;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Tabela: pracownicy
CREATE TABLE pracownicy (
  id_pracownika INT NOT NULL,
  imie VARCHAR(100) NULL,
  nazwisko VARCHAR(100) NULL,
  pracuje_od DATE NULL,
  pracuje_do DATE NULL,
  mail VARCHAR(255) NULL,
  telefon VARCHAR(20) NULL,
  adres VARCHAR(255) NULL,
  miasto VARCHAR(100) NULL,
  PRIMARY KEY (id_pracownika)
) COMMENT 'tabela z informacjami o pracownikach';

-- 2. Tabela: sponsorzy
CREATE TABLE sponsorzy (
  id_sponsora INT NOT NULL,
  nazwa VARCHAR(255) NULL,
  wspolpraca_od DATE NULL,
  wspolpraca_do DATE NULL,
  opis TEXT NULL,
  telefon VARCHAR(20) NULL,
  mail VARCHAR(255) NULL,
  PRIMARY KEY (id_sponsora)
) COMMENT 'tabela z informacjami o sponsorach';

-- 3. Tabela: chomiki
CREATE TABLE chomiki (
  id_chomika INT NOT NULL,
  imie VARCHAR(100) NULL,
  plec CHAR(1) NULL,
  data_urodzenia DATE NULL,
  waga INT NULL COMMENT 'w gramach',
  historia TEXT NULL,
  rasa VARCHAR(100) NULL,
  id_sponsora INT NOT NULL,
  PRIMARY KEY (id_chomika)
) COMMENT 'tabela z informacjami o chomikach';

-- 4. Tabela: zawody
CREATE TABLE zawody (
  id_zawodow INT NOT NULL,
  nazwa VARCHAR(255) NULL COMMENT 'nazwa zawodow',
  termin DATE NULL COMMENT 'termin zawodow',
  panstwo VARCHAR(100) NULL,
  miasto VARCHAR(100) NULL,
  status VARCHAR(50) NULL COMMENT '"odbyte", "planowane" , "w trakcie"',
  PRIMARY KEY (id_zawodow)
) COMMENT 'tabela z informacjami o zawodach';

-- 5. Tabela: konkurencje
CREATE TABLE konkurencje (
  id_konkurencji INT NOT NULL,
  nazwa VARCHAR(255) NULL,
  kategorie VARCHAR(100) NULL COMMENT '"naturalne", "formula CH"',
  charakterystyka TEXT NULL,
  PRIMARY KEY (id_konkurencji)
) COMMENT 'tabela z informacjami o konkurencjach';

-- 6. Tabela: przebieg
CREATE TABLE przebieg (
  id_przebiegu INT NOT NULL,
  godzina TIME NULL COMMENT 'godzina startu dyscypliny',
  zwyciezca BOOLEAN NULL,
  czas TIMESTAMP NULL COMMENT 'czas trwania biegu',
  id_chomika INT NOT NULL,
  id_zawodow INT NOT NULL,
  id_konkurencji INT NOT NULL,
  PRIMARY KEY (id_przebiegu)
) COMMENT 'tabela z informacjami przebiegu zawodow';

-- 7. Tabela: substancje_zakazane
CREATE TABLE substancje_zakazane (
  id_substancji INT NOT NULL,
  nazwa VARCHAR(255) NULL,
  PRIMARY KEY (id_substancji)
) COMMENT 'tabela z informacjami o substancjach zakazanych';

-- 8. Tabela: kontrola_antydopingowa
CREATE TABLE kontrola_antydopingowa (
  id_kontroli INT NOT NULL,
  data_badania DATE NULL,
  id_chomika INT NOT NULL,
  id_substancji INT NULL,
  PRIMARY KEY (id_kontroli)
) COMMENT 'tabela z informacjami o dopingu';

-- 9. Tabela: rejestracja_chomika
CREATE TABLE rejestracja_chomika (
  wpisowe DECIMAL(10, 2) NULL,
  zaksiegowane BOOLEAN NULL,
  id_chomika INT NOT NULL,
  PRIMARY KEY (id_chomika)
) COMMENT 'tabela z informacjami o rejestracji chomików w federacji';

-- 10. Tabela: finanse
CREATE TABLE finanse (
  id_transakcji INT NOT NULL,
  tytul VARCHAR(255) NULL,
  dane_transakcji TEXT NULL,
  data DATE NULL,
  dochod DECIMAL(10, 2) NULL,
  id_chomika INT NOT NULL,
  PRIMARY KEY (id_transakcji)
) COMMENT 'tabela z informacjami o finansowaniu';

-- 11. Tabela: wyplaty
CREATE TABLE wyplaty (
  id_wyplaty INT NOT NULL,
  kwota_zl DECIMAL(10, 2) NULL,
  data_wypłaty DATE NULL,
  id_pracownika INT NOT NULL,
  PRIMARY KEY (id_wyplaty)
) COMMENT 'tabela z informacjami wypłat dla pracowników';

-- Klucze obce
ALTER TABLE wyplaty ADD CONSTRAINT FK_pracownicy_TO_wyplaty FOREIGN KEY (id_pracownika) REFERENCES pracownicy (id_pracownika);
ALTER TABLE chomiki ADD CONSTRAINT FK_sponsorzy_TO_chomiki FOREIGN KEY (id_sponsora) REFERENCES sponsorzy (id_sponsora);
ALTER TABLE przebieg ADD CONSTRAINT FK_chomiki_TO_przebieg FOREIGN KEY (id_chomika) REFERENCES chomiki (id_chomika);
ALTER TABLE przebieg ADD CONSTRAINT FK_zawody_TO_przebieg FOREIGN KEY (id_zawodow) REFERENCES zawody (id_zawodow);
ALTER TABLE przebieg ADD CONSTRAINT FK_konkurencje_TO_przebieg FOREIGN KEY (id_konkurencji) REFERENCES konkurencje (id_konkurencji);
ALTER TABLE kontrola_antydopingowa ADD CONSTRAINT FK_chomiki_TO_kontrola_antydopingowa FOREIGN KEY (id_chomika) REFERENCES chomiki (id_chomika);
ALTER TABLE kontrola_antydopingowa ADD CONSTRAINT FK_substancje_zakazane_TO_kontrola_antydopingowa FOREIGN KEY (id_substancji) REFERENCES substancje_zakazane (id_substancji);
ALTER TABLE rejestracja_chomika ADD CONSTRAINT FK_chomiki_TO_rejestracja_chomika FOREIGN KEY (id_chomika) REFERENCES chomiki (id_chomika);
ALTER TABLE finanse ADD CONSTRAINT FK_rejestracja_chomika_TO_finanse FOREIGN KEY (id_chomika) REFERENCES rejestracja_chomika (id_chomika);
"""

# 2. DANE OSOBOWE
def pobierz_dane_osobowe():
    try:
        df_im = pd.read_csv('imiona.csv')
        df_naz = pd.read_csv('nazwiska.csv')
        imiona = df_im.iloc[:, 0].dropna().tolist()
        nazwiska = df_naz.iloc[:, 0].dropna().tolist()
        return imiona, nazwiska
    except:
        return [], []

IMIONA, NAZWISKA = pobierz_dane_osobowe()

def losuj_osobe():
    if IMIONA and NAZWISKA:
        return random.choice(IMIONA).title(), random.choice(NAZWISKA).title()
    return fake.first_name(), fake.last_name()

# 3. GENERATORY DANYCH

def gen_pracownicy(n=5):
    dane = []
    for i in range(1, n + 1):
        im, naz = losuj_osobe()
        dane.append({
            'id_pracownika': i,
            'imie': im, 
            'nazwisko': naz,
            'pracuje_od': fake.date_between(start_date='-5y', end_date='-1y'),
            'pracuje_do': None,
            'mail': f"{im[:3].lower()}{naz.lower()}@federacja.pl",
            'telefon': fake.phone_number(),
            'adres': fake.address(),
            'miasto': fake.city()
        })
    return pd.DataFrame(dane)

def gen_sponsorzy(n=10):
    dane = []
    for i in range(1, n + 1):
        dane.append({
            'id_sponsora': i,
            'nazwa': fake.company(),
            'wspolpraca_od': fake.date_between(start_date='-4y', end_date='-2y'),
            'wspolpraca_do': fake.date_between(start_date='today', end_date='+2y'),
            'opis': fake.bs(),
            'telefon': fake.phone_number(),
            'mail': fake.company_email()
        })
    return pd.DataFrame(dane)

def gen_chomiki(n=60, max_sponsor=10):
    dane = []
    rasy = ['Syryjski', 'Dżungarski', 'Roborowskiego']
    for i in range(1, n + 1):
        dane.append({
            'id_chomika': i,
            'imie': fake.first_name(),
            'plec': random.choice(['M', 'K']),
            'data_urodzenia': fake.date_between(start_date='-2y', end_date='-2m'),
            'waga': random.randint(30, 150),
            'historia': fake.sentence(),
            'rasa': random.choice(rasy),
            'id_sponsora': random.randint(1, max_sponsor)
        })
    return pd.DataFrame(dane)

def gen_zawody(n=15):
    dane = []
    for i in range(1, n+1):
        dane.append({
            'id_zawodow': i,
            'nazwa': f"Grand Prix {fake.city()}",
            'termin': fake.date_between(start_date='-2y', end_date='today'),
            'panstwo': 'Polska',
            'miasto': fake.city(),
            'status': 'odbyte'
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
    for i in range(1, n+1):
        zawody = df_zawody.sample(1).iloc[0]
        chomik = df_chomiki.sample(1).iloc[0]
        
        # data zawodów musi być późniejsza niż data urodzin chomika
        if zawody['termin'] < chomik['data_urodzenia']:
            continue
            
        dane.append({
            'id_przebiegu': i,
            'godzina': fake.time(),
            'zwyciezca': random.choice([True, False, False]),
            'czas': datetime.now(),
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

def gen_kontrola(n=20, max_chomik=60):
    dane = []
    for i in range(1, n+1):
        dane.append({
            'id_kontroli': i,
            'data_badania': fake.date_this_year(),
            'id_chomika': random.randint(1, max_chomik),
            'id_substancji': random.choice([None, 1, 2])
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
        for m in range(6):
            dane.append({
                'id_wyplaty': id_counter,
                'kwota_zl': random.randint(4300, 8500),
                'data_wypłaty': datetime.now().date() - timedelta(days=30*m),
                'id_pracownika': pracownik['id_pracownika']
            })
            id_counter += 1
    return pd.DataFrame(dane)

# 4. URUCHOMIENIE

def main():
    engine = create_engine(CONN_STR)

    with engine.connect() as conn:

        for stmt in SQL_STRUCTURE.split(';'):
            if stmt.strip():
                conn.execute(text(stmt))
        conn.commit()
    
    # Generowanie danych

    df_prac = gen_pracownicy(5)
    df_prac.to_sql('pracownicy', engine, if_exists='append', index=False)
    
    df_spon = gen_sponsorzy(10)
    df_spon.to_sql('sponsorzy', engine, if_exists='append', index=False)
    
    df_chom = gen_chomiki(60, 10)
    df_chom.to_sql('chomiki', engine, if_exists='append', index=False)
    
    df_zaw = gen_zawody(15)
    df_zaw.to_sql('zawody', engine, if_exists='append', index=False)
    
    df_konk = gen_konkurencje()
    df_konk.to_sql('konkurencje', engine, if_exists='append', index=False)
    
    df_przeb = gen_przebieg(200, df_zaw, df_chom, len(df_konk))
    df_przeb.to_sql('przebieg', engine, if_exists='append', index=False)
    
    df_subs = gen_substancje()
    df_subs.to_sql('substancje_zakazane', engine, if_exists='append', index=False)
    
    df_kontr = gen_kontrola(20, 60)
    df_kontr.to_sql('kontrola_antydopingowa', engine, if_exists='append', index=False)
    
    df_rej = gen_rejestracja(df_chom)
    df_rej.to_sql('rejestracja_chomika', engine, if_exists='append', index=False)
    
    df_fin = gen_finanse(df_rej)
    df_fin.to_sql('finanse', engine, if_exists='append', index=False)
    
    df_wyp = gen_wyplaty(df_prac)
    df_wyp.to_sql('wyplaty', engine, if_exists='append', index=False)

if __name__ == "__main__":
    main()