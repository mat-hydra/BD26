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

