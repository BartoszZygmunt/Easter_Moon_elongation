import datetime
import time
from project.count_easter import wielkanoc
from project.astro import get_moon_elongation_and_illumination
from project.astro import find_full_moon_jpl


# oblicz datę Wielkanocy dla wybranych lat
for rok in range(1900, 3000):
    print(f"\033[91m______________________{rok}___________________________________\033[0m")
    miesiąc, dzień = wielkanoc(rok)
    print(f"Wielkanoc: {rok}-{miesiąc:02d}-{dzień:02d}", end="")    
    dzień_tygodnia = datetime.datetime(rok, miesiąc, dzień).strftime('%A')
    print(f" ({dzień_tygodnia})") # tylko dla sprawdzenia, czy na pewno niedziela

    # szukaj pełni księżyca przed datą Wielkanocy (obliczoną metodą nicejską) ____________________
    found = False  # zmienna pomocnicza do sprawdzenia, czy znaleziono pełnię
    start_date = datetime.datetime(rok, miesiąc, dzień, 0, 0, 0)  # w UTC
    start_date = start_date - datetime.timedelta(days=8) # zacznij 8 dni przed Wielkanocą
    
    fm_time, found = find_full_moon_jpl(start_date, search_days=8, step='15m') # szukaj pełni przez 8 dni - zakończ w sobotę przed Wielkanocą
    if not found:
        # jeśli nie znaleziono pełni, to zacznij od 8+22=30 dni przed Wielkanocą
        start_date = start_date - datetime.timedelta(days=22)
        fm_time, found = find_full_moon_jpl(start_date, search_days=22, step='15m')

    if found and fm_time:
        print(f">>> Pełnia księżyca: {fm_time.strftime('%Y-%m-%d %H:%M:%S')} UTC", end="")
        dzień_tygodnia_fm = fm_time.strftime('%A')
        print(f" ({dzień_tygodnia_fm})")
    else:
        print("Nie znaleziono pełni w zadanym przedziale. Spróbuj zmienić search_days lub step.")

    e, p = get_moon_elongation_and_illumination(rok, miesiąc, dzień)
    print(f"Elongacja: {e:.2f}°")
    print(f"Procent oświetlenia: {p:.2f}%")
    print("________________")
    # zapisz dane do pliku easter_data.txt, kolejność: 
    # data Wielkanocy, dzień tygodnia, data pełni, godzina pełni, dzień tygodnia pełni, delta dni między pełnią a Wielkanocą, elongacja, oświetlenie    
    with open(f"easter_data.txt", "a") as file:
        file.write(f"{rok}-{miesiąc:02d}-{dzień:02d}\t")
        file.write(f"{dzień_tygodnia}\t")
        if found and fm_time:
            file.write(f"{fm_time.date()}\t{fm_time.strftime('%H:%M:%S')}\t")
            file.write(f"{dzień_tygodnia_fm}\t")
            delta_days = (fm_time.date() - datetime.date(rok, miesiąc, dzień)).days
            file.write(f"{delta_days}\t")
        else:
            file.write("Nie znaleziono pełni w zadanym przedziale. Spróbuj zmienić search_days lub step.\n")
            delta_days = 0 # musi być zdefiniowane, żeby nie było błędu
        file.write(f"{e:.2f}\t") # elongacja
        file.write(f"{p:.2f}\t") # oświetlenie w procentach
    time.sleep(5) # zatrzymaj program na 5 sekund żeby nie przeciążyć serwera JPL 

    # szukaj pełni PO dacie Wielkanocy (obliczonej metodą nicejską) - od niedzieli włącznie - do porównania 
    found = False # resetuj zmienną
    start_date = datetime.datetime(rok, miesiąc, dzień, 0, 0, 0)  # w UTC - data Wielkanocy (nicejska)
    
    fm_time, found = find_full_moon_jpl(start_date, search_days=30, step='15m') # szukaj pełni przez 30 dni - cały cykl księżycowy

    if found and fm_time:
        print(f"\033[92m>>> Pełnia po WLK znaleziona ~ {fm_time.strftime('%Y-%m-%d %H:%M:%S')} UTC\033[0m", end="")
        dzień_tygodnia_fm = fm_time.strftime('%A')
        print(f"\033[92m ({dzień_tygodnia_fm})\033[0m")
    else:
        print("Nie znaleziono pełni w zadanym przedziale. Spróbuj zmienić search_days lub step.")

    # zapisz dane do pliku
    with open(f"easter_data.txt", "a") as file:
        if found and fm_time:
            file.write(f"{fm_time.strftime('%Y-%m-%d')}\t{fm_time.strftime('%H:%M:%S')}\t")
            file.write(f"{dzień_tygodnia_fm}\t")
            delta_days = (fm_time.date() - datetime.date(rok, miesiąc, dzień)).days
            file.write(f"{delta_days}\t")
        else:
            file.write("Nie znaleziono pełni w zadanym przedziale. Spróbuj zmienić search_days lub step.\t")
    time.sleep(5)

    #teraz zaproponuj korektę daty Wielkanocy, tak, żeby w niedzielę wielkanocną było najbliżej pełni księżyca
    # warunek: Wielkanoc po 21 marca
    # zaproponuj wielkanoc w niedzielę przed pełnią
    start_date = datetime.datetime(rok, miesiąc, dzień, 0, 0, 0) - datetime.timedelta(days=7)  # w UTC - data Wielkanocy (nicejska) - tydzień wcześniej
    miesiac_korekta = start_date.month
    dzien_korekta = start_date.day
    dzień_tygodnia = start_date.strftime('%A')
    # oblicz elongację i oświetlenie dla proponowanej daty
    e, p = get_moon_elongation_and_illumination(rok, miesiac_korekta, dzien_korekta)
    print(f"\033[94m{rok}-{miesiac_korekta:02d}-{dzien_korekta:02d}\t\033[0m", end="")
    print(f"\033[94m ({dzień_tygodnia})\t\033[0m")
    print(f"\033[94mElongacja: {e:.2f}°\033[0m")
    print(f"\033[94mProcent oświetlenia: {p:.2f}%\033[0m")

    # zapisz dane do pliku easter_data.txt
    with open(f"easter_data.txt", "a") as file:
        file.write(f"{rok}-{miesiac_korekta:02d}-{dzien_korekta:02d}\t")
        file.write(f"{dzień_tygodnia}\t")
        file.write(f"{e:.2f}\t") # elongacja
        file.write(f"{p:.2f}\n") # oświetlenie w procentach
    time.sleep(5) # zatrzymaj program na 5 sekund żeby nie przeciążyć serwera JPL 



