from math import floor, log10

def custom_round(x, decimals):
    # For numbers >= 1, round normally.
    if abs(x) >= 1:
        return round(x, decimals)
    else:
        # For numbers < 1, calculate the number of leading zeros after the decimal.
        # For example, with x = 0.00153, math.log10(0.00153) is about -2.815, so:
        exponent = floor(log10(abs(x)))  # e.g. -3 for 0.00153
        extra = -exponent - 1  # Number of zeros between decimal point and first significant digit.
        return round(x, decimals + extra)


# For complex numbers, round each part separately:
def custom_round_complex(z, decimals):
    return complex(custom_round(z.real, decimals),
                   custom_round(z.imag, decimals))
