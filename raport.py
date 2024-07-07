import numpy as np
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime, timedelta
import os



db_config = {
    'host': 'giniewicz.it',
    'user': 'team16',
    'password': '---',
    'database': 'team16'
}


con = mysql.connector.connect(**db_config)
mycursor = con.cursor()

mycursor.execute("""
SELECT  marka, COUNT(DISTINCT(id_naprawy)) as ilosc_napraw,
ROUND((COUNT(DISTINCT(id_naprawy))/1500)*100,2) AS odsetek_napraw 
FROM Pojazdy INNER JOIN Naprawy
ON Pojazdy.id_pojazdu=Naprawy.id_pojazdu
GROUP BY marka
ORDER BY ilosc_napraw DESC;
""")
result = mycursor.fetchall()

df1 = pd.DataFrame(result)
marka = df1[0][0]
ilosc_marka = df1[1][0]
procent_marka = df1[2][0]
print(df1)

sizes = []
i=0
while df1[2][i]>2.5:
    sizes.append(df1[2][i])
    i+=1
sizes.append(sum(df1[2][i:-1]))
labels = list(df1[0][0:i])
labels.append("Inne")
fig, ax = plt.subplots(figsize=(6,6))

ax.pie(sizes, labels=labels,explode=[0.05 for i in range(len(sizes))])
ax.set_title("Odsetek naprawianych marek pojazdów")
fig.savefig("./odsetek_napraw.png")

fig, ax = plt.subplots(figsize=(6,8))
ax.axis('tight')
ax.axis('off')
the_table = ax.table(cellText=df1.values,
                    rowLabels=df1.index + 1,
                    colLabels=["Marka", "Liczba napraw","Odsetek napraw"],
                    rowColours=['lightblue']*len(df1),
                    colColours=['lightblue']*len(df1.columns),
                    loc='center')
fig.savefig("./tabela_naprawy_marka.png")

mycursor.execute("""
SELECT DATE_FORMAT(n.data_przyjecia, '%Y-%m') AS miesiac, 
       COUNT(*) AS liczba_napraw
FROM Naprawy n
GROUP BY DATE_FORMAT(n.data_przyjecia, '%Y-%m');
""")
result = mycursor.fetchall()

df2 = pd.DataFrame(result)
fig, ax = plt.subplots(figsize=(15,6))

ax.bar(range(len(df2[0])),df2[1])
ax.set_xticks(range(len(df2[0])))
ax.set_xticklabels(df2[0], rotation=45, horizontalalignment='right')
ax.set_ylabel("Liczba napraw")
ax.set_title("Porównanie liczby napraw w miesiącu od 2020")
fig.savefig("./naprawy_co_miesiac.png")
naprawa_ilosc = max(df2[1])
miesiac_naprawa = df2.loc[df2[1] == naprawa_ilosc,df2.columns[0]].values[0]
width = 0.1
fig, ax = plt.subplots(figsize=(15,7))
ax.bar(np.arange(12)-0.3,df2[1][0:12],0.15)
ax.bar(np.arange(12)-0.15,df2[1][12:24],0.15)
ax.bar(np.arange(12),df2[1][24:36],0.15)
ax.bar(np.arange(12)+0.15,df2[1][36:48],0.15)
ax.bar(np.arange(len(df2[0])-48)+0.3,df2[1][48:],0.15)
ax.set_xticks(range(12))
ax.set_xticklabels(["styczeń","luty","marzec","kwiecień","maj","czerwiec","lipiec","sierpień","wrzesień","październik","listopad","grudzień"], rotation=45, horizontalalignment='right')
fig.legend(["2020","2021","2022","2023","2024"], loc="upper left",bbox_to_anchor=(0.85, 0.85))
ax.set_ylabel("Liczba napraw")
ax.set_title("Porównanie liczby napraw w danych miesiącach")
fig.savefig("./naprawy_w_miesiacach.png")

mycursor.execute("""
SELECT ks.id_pojazdu,CONCAT(p.marka,p.model), 
       ks.cena_sprzedazy - ks.cena_kupna - IFNULL(SUM(c.cena_elementow), 0) AS zysk
FROM Kupnosprzedaz ks
LEFT JOIN Naprawy n ON ks.id_pojazdu = n.id_pojazdu
LEFT JOIN Czesci c ON n.id_naprawy = c.id_naprawy
INNER JOIN Pojazdy p ON ks.id_pojazdu=p.id_pojazdu
WHERE ks.cena_sprzedazy IS NOT NULL
GROUP BY ks.id_pojazdu, ks.cena_sprzedazy, ks.cena_kupna
ORDER BY zysk DESC
LIMIT 10;
""")
result = mycursor.fetchall()

zyski = pd.DataFrame(result)
marka_zysk = zyski[1][0]
czysty_zysk = zyski[2][0]

fig, ax = plt.subplots(figsize=(6,4))
ax.axis('tight')
ax.axis('off')
the_table = ax.table(cellText=zyski.values,
                    rowLabels=zyski.index + 1,
                    colLabels=["ID pojazdu","Marka i model", "Zysk"],
                    rowColours=['lightblue']*len(zyski),
                    colColours=['lightblue']*len(zyski.columns),
                    loc='center')
fig.savefig("./tabela_zyski.png")
mycursor.execute("""
SELECT round(AVG(kwota),2) AS srednia_wyplata,rodzaj_zatrudnienia FROM Wypłata INNER JOIN Pracownicy
ON Wypłata.id_pracownika=Pracownicy.id_pracownika
GROUP BY rodzaj_zatrudnienia
ORDER BY srednia_wyplata DESC;
""")
result = mycursor.fetchall()

average = pd.DataFrame(result)
dobry_kontrakt = average[1][0]

fig, ax = plt.subplots(figsize=(6,3))
ax.axis('tight')
ax.axis('off')
the_table = ax.table(cellText=average.values,
                    rowLabels=average.index + 1,
                    colLabels=["Średnia płaca", "Rodzaj zatrudnienia"],
                    rowColours=['lightblue']*len(average),
                    colColours=['lightblue']*len(average.columns),
                    loc='center')
fig.savefig("./tabela_placa.png")


mycursor.execute("""
SELECT nazwa_usługi , COUNT(id_naprawy) AS ilosc FROM Usługi INNER JOIN Naprawy
ON Usługi.id_usługi=Naprawy.id_usługi
GROUP BY nazwa_usługi
ORDER BY ilosc DESC;
""")
result = mycursor.fetchall()
pozycja = pd.DataFrame(result)
usluga = pozycja[0][0]
liczba_uslug = pozycja[1][0]

fig, ax = plt.subplots(figsize=(6,4))
ax.axis('tight')
ax.axis('off')
the_table = ax.table(cellText=pozycja.values,
                    rowLabels=pozycja.index + 1,
                    colLabels=["Usługa", "Ilość wykonań"],
                    rowColours=['lightblue']*len(pozycja),
                    colColours=['lightblue']*len(pozycja.columns),
                    loc='center')
fig.savefig("./uslugi.png")

mycursor.execute("""
SELECT COUNT(Klienci.id_klienta) AS ilosc_klientow , miasto FROM Klienci INNER JOIN Adresy
ON Klienci.id_klienta=Adresy.id_klienta
GROUP BY miasto
ORDER BY ilosc_klientow DESC;
""")
result = mycursor.fetchall()

dfd = pd.DataFrame(result)
obywateli = max(dfd[0])
miasto = dfd.loc[dfd[0] == obywateli,dfd.columns[1]].values[0]

fig, ax = plt.subplots(figsize=(15,8))

ax.bar(range(len(dfd[1])),dfd[0])
ax.set_xticks(range(len(dfd[1])))
ax.set_xticklabels(dfd[1], rotation=45, horizontalalignment='right')
ax.set_ylabel("Liczba napraw")
ax.set_title("Porównanie liczby napraw w zaleznosci od miasta")
fig.savefig("./klienci_z_miast.png")

mycursor.execute("""
    SELECT nazwa  , COUNT(id_naprawy) as ilosc_wykorzystania_w_naprawach FROM Czesci
    GROUP BY nazwa
    ORDER BY ilosc_wykorzystania_w_naprawach DESC
    LIMIT 20;     
""")

result = mycursor.fetchall()
df5 = pd.DataFrame(result)
czesc = df5[0][0]
ilosc_czesc = df5[1][0]

fig, ax = plt.subplots(figsize=(6,5))
ax.axis('tight')
ax.axis('off')
the_table = ax.table(cellText=df5.values,
                    rowLabels=df5.index + 1,
                    colLabels=["Część", "Liczba napraw"],
                    rowColours=['lightblue']*len(df5),
                    colColours=['lightblue']*len(df5.columns),
                    loc='center')
fig.savefig("./popularne_czesci.png")


mycursor.close()
con.close()


#raport

WIDTH = 210
HEIGHT = 310

def create_title(day, pdf):  
    pdf.ln(60)
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 20)
    pdf.write(5, f"Pimp My Wheels Raport")
    pdf.ln(10)
    pdf.write(4, f'{day}')
    pdf.ln(10)
    pdf.set_font('DejaVu', '', 14)
    pdf.write(5,
    """RAPORT Z DZIAŁAŃ WARSZTATU "PIMP MY WHEELS" W LATACH 2020-2023

    WYKONANY PRZEZ:
    Bartosz Cholewa
    Bartłomiej Drzymalski
    Bartłomiej Brzozowski
    Ignacy Nowakowski
    Radosław Tertel """)
    pdf.ln(20)
    pdf.write(5, "WSTĘP")
    pdf.ln(10)
    pdf.write(5,"Niniejszy raport przedstawia szczegółową analizę działalności warsztatu mechanicznego w latach 2020-2023. "
    "Celem tego opracowania jest ocena efektywności działań, status finansowy oraz zgłebienie zleceń warsztatu w badanym okresie. "
    "Raport uwzględnia również nie tylko informacje na temat ich działalności, ale również analizę klientów dzięki której będzie można usprawnić "
    "działanie warsztatu w następnych latach.")


def create_analytics_report(day, filename="raport.pdf"):
    pdf = FPDF() 
    ''' First Page '''
    pdf.add_page()
    create_title(day, pdf)
    ''' second page'''
    pdf.add_page()
    pdf.set_font('DejaVu', '', 12)
    pdf.write(5, "PODZIAŁ NA MARKI SAMOCHODU")
    pdf.ln(10)
    pdf.write(5,"W tej sekcji raportu zbadamy którą markę samochodów nasz wartszat najczęściej naprawiał. By to sprawdzić skorzystamy z wykresu kołowego"
              " oraz by zebrać dokładniejsze informacje na ten temat użyjemy tabeli numerycznej.")
    pdf.ln(80)
    pdf.image("./odsetek_napraw.png", WIDTH/2 - 50, 50, 100, 100)
    pdf.image("./tabela_naprawy_marka.png", WIDTH/2 - 45, 140, 90, 150)
    pdf.ln(160)
    pdf.write(5,f"Jak możemy zauważyć zarówno z wykresu jak i z tabeli, najpopularniejszą marką obsługiwaną przez wartsztat była: {marka}."
              f" Była ona naprawiana aż {ilosc_marka} razy, co stanowi {procent_marka}% napraw.")
    
    """Third Page"""
    pdf.add_page()
    pdf.write(5, "PODZIAŁ NA MIESIĄCE:")
    pdf.ln(10)
    pdf.write(5, "W kolejnej sekcji zajmiemy sie analiza ilości klientów na przestrzeni lat oraz miesięcy. Do tej analizy skorzystamy z dwóch wykresów słupkowych.")
    pdf.ln(80)
    pdf.image("./naprawy_co_miesiac.png", WIDTH/2-112.5, 50, 225, 90)
    pdf.image("./naprawy_w_miesiacach.png", WIDTH/2-112.5, 150, 225, 105)
    pdf.ln(160)
    pdf.write(5,f"jak możemy przeczytać z wykresów największa liczba klientów była w miesiącu: {miesiac_naprawa} i wynosiła {naprawa_ilosc}.")
    
    """Fourth Page"""
    pdf.add_page()
    pdf.write(5, "NAJWIĘKSZE OKAZJE")
    pdf.ln(10)
    pdf.write(5,"W tej sekcji przedstawimy na jakich pojazdach nasz modelach samochodów oraz o jakim ID pojazdu nasz warsztat zarobił najwięcej.")
    pdf.image("./tabela_zyski.png", WIDTH/2 - 60, 40, 120, 120)
    pdf.ln(120)
    pdf.write(5,f"Łatwo z odczytujemy z tabeli, że jest to model: {marka_zysk} na którym zarobiliśmy {czysty_zysk} zł.")
    
    """Fifth Page"""
    pdf.add_page()
    pdf.write(5, "ZAROBKI A ZATRUDNIENIE")
    pdf.ln(10)
    pdf.write(5,"W tym dziale dowiemy się ile wynoszą średnie zarobki w zależności od umowy podpisanej przez warsztat. Dane przedstawimy za pomocą tabeli.")
    pdf.image("./tabela_placa.png", WIDTH/2-50, 55, 100, 75)
    pdf.ln(120)
    pdf.write(5,f"Najbardziej opłacalną formą zatrudnienia w tym wartsztacie jest: {dobry_kontrakt}.")
    
    """Sixth Page"""
    pdf.add_page()
    pdf.write(5, "NAJPOPULARNIEJSZE CZĘŚCI")
    pdf.ln(10)
    pdf.write(5,"Tę część raportu przeznaczymy na analizę zamówionych części przez wartsztat podczas całej jego działalności. Pozwoli nam to skuteczniej zamawiać odpowiednią"
              " ilość części w przyszłości.")
    pdf.image("./popularne_czesci.png", WIDTH/2 - 45, 40, 90, 150)
    pdf.ln(160)
    pdf.write(5,f"Jak możemy odczytać z tabeli najpopularniejszą częścią jest: {czesc} która została zamówiona {ilosc_czesc} razy.")
    
    """Seventh Page"""
    pdf.add_page()
    pdf.write(5, "NAJCZĘSTSZE USŁUGI")
    pdf.ln(10)
    pdf.write(5,"W tej sekcji zbadamy z jakich usług klieni warsztatu skorzystali najczęściej. Ta informacja pomoże w zatrudnianiu pracowników na przyszłość.")
    pdf.image("./uslugi.png", WIDTH/2 - 60, 40, 120, 120)
    pdf.ln(160)
    pdf.write(5,f"Najczęstszą usługą wykonaną przez warsztat była: {usluga}, która została wykonana aż {liczba_uslug} razy.")

    """Eighth Page"""
    pdf.add_page()
    pdf.write(5, "POCHODZENIE KLIENTÓW")
    pdf.ln(10)
    pdf.write(5,"Za pomocą wkyresu słupkowego zbadamy z jakich miast wywodzą się nasi klienci. Dzięki temu warsztat będzie mógł zadecydować, w jaki rejonie najlepiej założyć"
              "nową placówkę.")
    pdf.image("./klienci_z_miast.png",  WIDTH/2 - 100, 40, 200, 120)
    pdf.ln(160)
    pdf.write(5,f"Jak możemy odczytać z wykresu, najwięcej klientów pochodzi z rejonu miasta: {miasto} i było ich aż {obywateli}.")

    """Ninth Page"""
    pdf.add_page()
    pdf.write(5, "PODSUMOWANIE")
    pdf.ln(20)
    pdf.write(5,"W tym raporcie dokładnie przeanalizowaliśmy wiele aspektów działalności gospodarczej zakładu mechanicznego 'Pimp My Wheels'. Dzięki tym informacjom zarząd może "
              "zdecydować w jakim rejonie firma powinna się rozwijać, jakie umiejętności powinni posiadać nowi rekruci, w jaki sposób należy przeranżować inwentarz w magazynie"
              "i wiele innych cennych informacji.")
    
    pdf.output(filename)

day = (datetime.today()).strftime("%d/%m/%Y")
create_analytics_report(day)
