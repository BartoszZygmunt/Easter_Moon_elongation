import datetime
import numpy as np
import math as math
from astroquery.jplhorizons import Horizons

# 1. Funkcja parsująca daty z JPL Horizons w różnych formatach
def parse_horizons_datetime(dt_str):
    """
    Przykładowy parser ciągów dat i czasu z Horizons (kolumna datetime_str).
    Usuwamy ewentualne sufiksy i próbujemy kilka popularnych formatów.
    """
    # Usuwamy ewentualne "UTC", "UT", "TDB"
    dt_str = dt_str.replace(' UTC', '').replace(' UT', '').replace(' TDB', '')
    
    formats = [
        '%Y-%b-%d %H:%M:%S.%f',
        '%Y-%b-%d %H:%M:%S',
        '%Y-%b-%d %H:%M',
        '%Y-%b-%d %H',
        '%Y-%b-%d'
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(dt_str, fmt)
        except ValueError:
            pass
    # jeśli nic się nie udało:
    raise ValueError(f"Could not parse date string from Horizons: {dt_str}")


# 2. Pomocnicza funkcja do normalizacji kąta w stopniach
def normalize_angle(angle_deg):
    """ Zwraca kąt w zakresie [0, 360). """
    return angle_deg % 360.0


# 3. Funkcja pobierająca współrzędne ekliptyczne obiektu (Słońce / Księżyc) z JPL Horizons
def get_ecliptic_longitudes(object_id, start_time, stop_time, step='1h'):
    """
    Pobiera z JPL Horizons (astroquery) efemerydy obiektu o ID = object_id ('10' = Słońce, '301' = Księżyc)
    w przedziale [start_time, stop_time] co 'step' (np. '1h', '30m').
    Zwraca (lista_czasów_datetime, numpy_tablica_długości_eklipt.).
    """

    # Tworzymy obiekt Horizons bez id_type (aby uniknąć ostrzeżeń o deprecacji):
    obj = Horizons(
        id=object_id,
        location='500@399',  # geocentryczne efemerydy
        epochs={
            'start': start_time.strftime('%Y-%m-%d %H:%M'),
            'stop':  stop_time.strftime('%Y-%m-%d %H:%M'),
            'step':  step
        }
        # id_type=None  # domyślnie tak czy inaczej
    )

    # quantities='31' -> geocentryczna długość i szerokość ekliptyczna
    # eph = obj.ephemerides()
    eph = obj.ephemerides(quantities='31')
    # print(eph)
    
    times = []
    ecl_lons = []
    # ilum = []

    for row in eph:
        dt_str = row['datetime_str']   # Np. '2024-Dec-22 00:00:00.0000 UTC'
        dt_parsed = parse_horizons_datetime(dt_str)
        lon = float(row['ObsEclLon'])  # Długość ekliptyczna w stopniach
        times.append(dt_parsed)
        ecl_lons.append(lon)

        # ilum.append(float(row['illumination']))  # Oświetlenie w procentach
    
    return times, np.array(ecl_lons)


# Funkcja pomocnicza do zamiany kąta na przedział [-180, +180)
def to_signed_angle(deg):
    return ((deg + 180) % 360) - 180

# 4. Główna funkcja szukająca momentu pełni (elongacja = 180°) - 
def find_full_moon_jpl(start_date, search_days=5, step='20m'):
    """
    Szuka momentu pełni w okolicy 'start_date' (datetime, UTC),
    w ciągu 'search_days' dni do przodu, z rozdzielczością 'step'.
    Zwraca (moment_pelni_datetime, czy_znaleziono).
    """

    stop_date = start_date + datetime.timedelta(days=search_days)

    # Pobieramy Słońce (id='10') i Księżyc (id='301')
    sun_times, sun_lons = get_ecliptic_longitudes('10',  start_date, stop_date, step)
    moon_times, moon_lons = get_ecliptic_longitudes('301', start_date, stop_date, step)

    # Zakładamy, że listy czasów pokrywają się indeksowo (to samo step, ten sam interwał).
    if len(sun_times) != len(moon_times):
        raise ValueError("Liczba próbek z Horizons różni się dla Słońca i Księżyca.")
    
    elongations = []
    # illuminations = []
    for i in range(len(sun_times)):
        diff = normalize_angle(moon_lons[i] - sun_lons[i])
        elongations.append(diff)
        # illuminations.append(illum[i]) 

    # Szukamy miejsca, gdzie elongacja przechodzi przez 180° (lub jest równa)
    best_time = None
    found = False

    for i in range(len(elongations) - 1):
        e1 = elongations[i]
        e2 = elongations[i+1]

        # 1. Jeśli w którejś próbce jest dokładnie 180
        if abs(e1 - 180.0) < 1e-9:
            best_time = sun_times[i]
            found = True
            break
        if abs(e2 - 180.0) < 1e-9:
            best_time = sun_times[i+1]
            found = True
            break

        # 2. Jeśli pomiędzy e1 a e2 elongacja "przeszła" z <180 do >180 (lub odwrotnie),
        #    używamy "signed angles" by uniknąć fałszywego przejścia przy 0°
        sa1 = to_signed_angle(e1 - 180.0)
        sa2 = to_signed_angle(e2 - 180.0)

        if (e1 > 350 and e2 < 10) or (e2 > 350 and e1 < 10):
            continue # pomiń, bo to okolice 0° (nów), a nie 180° (pełnia)


        if sa1 * sa2 < 0:
            # mamy rzeczywiste przecięcie okolic 180°
            frac = abs(sa1) / (abs(sa1) + abs(sa2))
            dt1 = sun_times[i]
            dt2 = sun_times[i+1]

            total_s = (dt2 - dt1).total_seconds()
            delta_s = total_s * frac
            best_time = dt1 + datetime.timedelta(seconds=delta_s)
            found = True
            break

    return best_time, found




def get_moon_elongation_and_illumination(year: int, month: int, day: int):
    """
    Zwraca kąt elongacji (stopnie, w zakresie 0–180) oraz procent oświetlenia
    tarczy Księżyca w danym dniu (UTC północ), bazując na efemerydach JPL Horizons.

    Parametry:
    -----------
    year, month, day : int
        Data (rok, miesiąc, dzień) w UTC.

    Zwraca:
    -----------
    (elong_deg, illum_percent) : (float, float)
        - elong_deg: kąt między Słońcem a Księżycem (0° = nów, 180° = pełnia).
        - illum_percent: przybliżony procent oświetlenia tarczy Księżyca.
    """

    # 1. Definiujemy datę (UTC) w formacie rozpoznawalnym przez Horizons
    date_str = f"'{year}-{month:02d}-{day:02d} 00:00'" # północ w dniu podanym

    # 2. Pobieramy efemerydy Słońca (id='10') i Księżyca (id='301') dla obserwatora '@399' (geocentrycznie)
    sun_obj = Horizons(id='10', location='@399', epochs=date_str)
    moon_obj = Horizons(id='301', location='@399', epochs=date_str)

    # Zwracamy np. długość ekliptyczną z quantities='31' (ObsEclLon)
    sun_eph = sun_obj.ephemerides(quantities='31')
    moon_eph = moon_obj.ephemerides(quantities='31')

    # 3. Odczytujemy geocentryczną długość ekliptyczną
    sun_lon = float(sun_eph[0]['ObsEclLon'])   # w stopniach
    moon_lon = float(moon_eph[0]['ObsEclLon']) # w stopniach

    # 4. Elongacja = różnica w długościach, znormalizowana do 0–360
    raw_elong = (moon_lon - sun_lon) % 360.0

    # Dla Księżyca typowo używamy przedziału 0–180, bo powyżej 180° można uznać za "180 - (kąt)", 
    # pełnia występuje przy 180°. Wybieramy "mniejszy łuk":
    if raw_elong > 180.0:
        elong_deg = 360.0 - raw_elong
    else:
        elong_deg = raw_elong

    # 5. Obliczamy uproszczony procent oświetlenia 
    #    (zakładając, że phase_angle ~ elongacja)
    theta_rad = math.radians(elong_deg)
    illum_fraction = (1.0 - math.cos(theta_rad)) / 2.0
    illum_percent = illum_fraction * 100.0

    return elong_deg, illum_percent



