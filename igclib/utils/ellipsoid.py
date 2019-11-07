from math import cos

MATH_PI = 3.14159265359
MATH_E = 2.71828182846

def corrections(lat):

    c = cos(lat * MATH_PI / 180)
    c2 = 2 * c * c - 1
    c3 = 2 * c * c2 - c
    c4 = 2 * c * c3 - c2
    c5 = 2 * c * c4 - c3

    kx = 1000 * (111.41513 * c - 0.09455 * c3 + 0.00012 * c5)
    ky = 1000 * (111.13209 - 0.56605 * c2 + 0.0012 * c4)

    return kx, ky