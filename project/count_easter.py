def wielkanoc(rok):
    """
    Oblicza datę Wielkanocy dla podanego roku.
    
    Parametr:
        rok (int): Rok, dla którego obliczana jest data Wielkanocy.
    
    Zwraca:
        tuple: Miesiąc (int) i dzień (int) Wielkanocy.
    """
    a = rok % 19
    b = rok // 100
    c = rok % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    miesiąc = (h + l - 7 * m + 114) // 31
    dzień = ((h + l - 7 * m + 114) % 31) + 1
    return miesiąc, dzień


