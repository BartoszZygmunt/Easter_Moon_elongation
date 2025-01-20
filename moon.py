from astroquery.jplhorizons import Horizons

obj = Horizons(
    id='301',           # 301 = Moon
    location='@399',    # geocentrycznie (Ziemia = 399)
    epochs={
        'start': '2030-04-18 02:00', 
        'stop':  '2030-04-18 05:00',
        'step':  '10m'
    }
)

eph = obj.ephemerides(quantities='10,43' )  # 31 = geocentric ecliptic long. & lat.
print(eph.colnames)

#odczytaj alpha_true oraz illumination
for row in eph:
    print(f"DateTime: {row['datetime_str']}, Alpha True: {row['alpha_true']}, Illumination: {row['illumination']}")


#24. ilumination 0-1
#46 elong
#48 phase angle

