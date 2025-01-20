import datetime
import time
from project.count_easter import wielkanoc
from project.astro import find_full_moon_jpl


for rok in range(2000, 2100):
    miesiąc, dzień = wielkanoc(rok)
    start_date = datetime.datetime(rok, 3, 21, 0, 0, 0)  # w UTC
    # sprawdż czy to jest poniedziałek
    if start_date.weekday() == 6:
        # to jest poniedziałek
        # Napisz w konsole, że to jest niedziela
        print(f"{rok} - {start_date.date()} to niedziela: {start_date.strftime('%A')}")

        fm_time, found = find_full_moon_jpl(start_date, search_days=1, step='15m')
        if found and fm_time:
            # znaleziono pełnię w dniu 21 marca
            print(f" i jest pełnia: {fm_time.date()}")
            # teraz sprawdź, czy kolejna pełnia będzie w niedzielę
            #szukaj pełni za 29 dni przez 1 dzień
            start_date = fm_time + datetime.timedelta(days=29)
            fm_time, found = find_full_moon_jpl(start_date, search_days=1, step='15m')
            if found and fm_time:
                # znaleziono pełnie
                print(f" kolejna pełnia: {fm_time.date()}")
                # napisz dzień tygodnia
                print(f" dzień tygodnia: {fm_time.strftime('%A')}")
                # zapisz to do pliku easter_data.txt
                
        else:
            print(f"{rok} - \n")    
            
        time.sleep(0.5) 