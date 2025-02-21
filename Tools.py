from math import floor, log10

def round_sig(x, sig=3):
    if x == 0:
        return 0
    digits = sig - int(floor(log10(abs(x)))) - 1
    return round(x, digits)


def round_sig_complex(z, sig=3):
    return complex(round_sig(z.real, sig), round_sig(z.imag, sig-1))
