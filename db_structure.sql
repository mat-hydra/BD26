-- 1. Tabela: pracownicy
CREATE TABLE pracownicy (
    id_pracownika INT NOT NULL AUTO_INCREMENT,
    imie VARCHAR(100) NULL,
    nazwisko VARCHAR(100) NULL,
    pracuje_od DATE NULL,
    pracuje_do DATE NULL,
    mail VARCHAR(255) NULL,
    telefon VARCHAR(20) NULL,
    id_miasta INT NOT NULL,
    ulica VARCHAR(255) NULL,
    nr_domu VARCHAR(20) NULL,
    kod_pocztowy VARCHAR(20) NULL,
    PRIMARY KEY (id_pracownika)
) COMMENT 'tabela z informacjami o pracownikach';

-- 2. Tabela: sponsorzy
CREATE TABLE sponsorzy (
    id_sponsora INT NOT NULL AUTO_INCREMENT,
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
    id_chomika INT NOT NULL AUTO_INCREMENT,
    imie VARCHAR(100) NULL,
    plec CHAR(1) NULL,
    data_urodzenia DATE NULL,
    data_smierci DATE NULL,
    waga INT NULL COMMENT 'w gramach',
    historia TEXT NULL,
    id_rasy INT NOT NULL,
    id_sponsora INT NOT NULL,
    PRIMARY KEY (id_chomika)
) COMMENT 'tabela z informacjami o chomikach';

-- 4. Tabela: zawody
CREATE TABLE zawody (
    id_zawodow INT NOT NULL AUTO_INCREMENT,
    nazwa VARCHAR(255) NULL COMMENT 'nazwa zawodow',
    termin DATE NULL COMMENT 'termin zawodow',
    id_miasta INT NOT NULL,
    status VARCHAR(50) NULL COMMENT '"odbyte", "planowane" , "w trakcie"',
    PRIMARY KEY (id_zawodow)
) COMMENT 'tabela z informacjami o zawodach';

-- 5. Tabela: konkurencje
CREATE TABLE konkurencje (
    id_konkurencji INT NOT NULL AUTO_INCREMENT,
    nazwa VARCHAR(255) NULL,
    kategorie VARCHAR(100) NULL COMMENT '"naturalne", "formula CH"',
    charakterystyka TEXT NULL,
    PRIMARY KEY (id_konkurencji)
) COMMENT 'tabela z informacjami o konkurencjach';

-- 6. Tabela: przebieg
CREATE TABLE przebieg (
    id_przebiegu INT NOT NULL AUTO_INCREMENT,
    godzina TIME NULL COMMENT 'godzina startu dyscypliny',
    zwyciezca BOOLEAN NULL,
    czas INT NULL COMMENT 'czas trwania biegu',
    id_chomika INT NOT NULL,
    id_zawodow INT NOT NULL,
    id_konkurencji INT NOT NULL,
    PRIMARY KEY (id_przebiegu)
) COMMENT 'tabela z informacjami przebiegu zawodow';

-- 7. Tabela: substancje_zakazane
CREATE TABLE substancje_zakazane (
    id_substancji INT NOT NULL AUTO_INCREMENT,
    nazwa VARCHAR(255) NULL,
    PRIMARY KEY (id_substancji)
) COMMENT 'tabela z informacjami o substancjach zakazanych';

-- 8. Tabela: kontrola_antydopingowa
CREATE TABLE kontrola_antydopingowa (
    id_kontroli INT NOT NULL AUTO_INCREMENT,
    data_badania DATE NULL,
    id_chomika INT NOT NULL,
    id_substancji INT NULL,
    PRIMARY KEY (id_kontroli)
) COMMENT 'tabela z informacjami o dopingu';

-- 10. Tabela: finanse
CREATE TABLE finanse (
    id_transakcji INT NOT NULL AUTO_INCREMENT,
    data_transakcji DATE NOT NULL,
    kwota DECIMAL(10,2) NOT NULL,
    id_typu INT NOT NULL,
    id_chomika INT NULL,    -- NULL jeśli nie jest to rejestracja zawodnika
    uwagi TEXT,
    PRIMARY KEY (id_transakcji)
) COMMENT 'tabela z informacjami o finansowaniu';

-- 11. Tabela: wyplaty
CREATE TABLE wyplaty (
    id_wyplaty INT NOT NULL AUTO_INCREMENT,
    kwota_zl DECIMAL(10, 2) NULL,
    data_wyplaty DATE NULL,
    id_pracownika INT NOT NULL,
    PRIMARY KEY (id_wyplaty)
) COMMENT 'tabela z informacjami wypłat dla pracowników';

-- 12. Tabela: kraje
CREATE TABLE kraje (
    id_kraju INT NOT NULL AUTO_INCREMENT,
    nazwa VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_kraju)
);

-- 13. Tabela: miasta
CREATE TABLE miasta (
    id_miasta INT NOT NULL AUTO_INCREMENT,
    nazwa VARCHAR(100) NOT NULL,
    id_kraju INT NOT NULL,
    PRIMARY KEY (id_miasta)
);

-- 14. Tabela: rasa
CREATE TABLE rasa (
    id_rasy INT NOT NULL AUTO_INCREMENT,
    nazwa VARCHAR(100) NOT NULL,
    cechy VARCHAR(255) NOT NULL,
    PRIMARY KEY (id_rasy)
);

-- 15. Tabela: typ_transakcji
CREATE TABLE typ_transakcji (
    id_typu INT NOT NULL AUTO_INCREMENT,
    nazwa VARCHAR(100) NOT NULL,
    opis TEXT,
    PRIMARY KEY (id_typu)
);


-- Klucze obce
ALTER TABLE wyplaty ADD CONSTRAINT FK_pracownicy_TO_wyplaty FOREIGN KEY (id_pracownika) REFERENCES pracownicy (id_pracownika);
ALTER TABLE chomiki ADD CONSTRAINT FK_sponsorzy_TO_chomiki FOREIGN KEY (id_sponsora) REFERENCES sponsorzy (id_sponsora);
ALTER TABLE przebieg ADD CONSTRAINT FK_chomiki_TO_przebieg FOREIGN KEY (id_chomika) REFERENCES chomiki (id_chomika);
ALTER TABLE przebieg ADD CONSTRAINT FK_zawody_TO_przebieg FOREIGN KEY (id_zawodow) REFERENCES zawody (id_zawodow);
ALTER TABLE przebieg ADD CONSTRAINT FK_konkurencje_TO_przebieg FOREIGN KEY (id_konkurencji) REFERENCES konkurencje (id_konkurencji);
ALTER TABLE kontrola_antydopingowa ADD CONSTRAINT FK_chomiki_TO_kontrola_antydopingowa FOREIGN KEY (id_chomika) REFERENCES chomiki (id_chomika);
ALTER TABLE kontrola_antydopingowa ADD CONSTRAINT FK_substancje_zakazane_TO_kontrola_antydopingowa FOREIGN KEY (id_substancji) REFERENCES substancje_zakazane (id_substancji);
ALTER TABLE miasta ADD CONSTRAINT FK_kraje_TO_miasta FOREIGN KEY (id_kraju) REFERENCES kraje(id_kraju);
ALTER TABLE pracownicy ADD CONSTRAINT FK_miasta_TO_pracownicy FOREIGN KEY (id_miasta) REFERENCES miasta(id_miasta);
ALTER TABLE zawody ADD CONSTRAINT FK_miasta_TO_zawody FOREIGN KEY (id_miasta) REFERENCES miasta(id_miasta);
ALTER TABLE chomiki ADD CONSTRAINT FK_rasa_TO_chomiki FOREIGN KEY (id_rasy) REFERENCES rasa(id_rasy);
ALTER TABLE finanse ADD CONSTRAINT FK_typ_TO_finanse FOREIGN KEY (id_typu) REFERENCES typ_transakcji(id_typu);
ALTER TABLE finanse ADD CONSTRAINT FK_chomiki_TO_finanse FOREIGN KEY (id_chomika) REFERENCES chomiki(id_chomika);

