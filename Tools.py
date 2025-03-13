from math import floor, log10
import numpy as np
import os
import pandas as pd

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


def to_csv(data, name: str):
    data_str = np.array(
    [[f"{val.real:.6f} + {val.imag:.6f}j" for val in row] for row in data])
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", name + ".csv")
    np.savetxt(desktop_path, data_str, delimiter=",", fmt="%s")


def read_excel():
    main_dir = os.path.dirname(os.path.realpath(__file__))
    dir = os.path.join(main_dir, r"Excel_Files\example6_9.xlsx")

    dataframe = pd.read_excel(dir)
    dataframe = dataframe.fillna(0)  # converts all NaN values to 0
    n = len(dataframe) - 1
    data = []

    for i in range(n):
        data.append(dataframe.iloc[i+1, 2:7])
    
    #  this line of code converts the string literals in data into properly formatted complex strings
    data = [[val.replace(" ", "").replace("j", "") + "j" if isinstance(val, str) else val for val in row] for row in data]
    data = np.array(data, dtype=complex)  # converts data into a numpy array with complex entries

    return data


def compare(Ybus, pwrworld):
    Ybus = np.round(Ybus, 2)
    print("Ybus = ", '\n', Ybus, '\n')
    print("pwrworld = ", '\n', pwrworld, '\n')
    diff = Ybus - pwrworld
    print("difference = ", '\n', diff, '\n')


def read_jacobian(M):
        csv_J1 = np.zeros((M, M), dtype=float)
        csv_J2 = np.zeros((M, M), dtype=float)
        csv_J3 = np.zeros((M, M), dtype=float)
        csv_J4 = np.zeros((M, M), dtype=float)

        main_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(main_dir, r"Excel_Files\fivepowerbusystem_flatstart_jacobian_matrix.csv")

        df = pd.read_csv(file_path, header=None, skiprows=3, dtype=str)
        df = df.apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)

        start_row = 0
        start_col = 4
        shift = M + 1

        for idx, (i, j) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
            row_idx = start_row + i * shift
            col_idx = start_col + j * shift
            matrix = df.iloc[row_idx:row_idx + M, col_idx:col_idx + M].to_numpy(dtype=float)

            if idx == 0:
                csv_J1 = matrix
            elif idx == 1:
                csv_J2 = matrix
            elif idx == 2:
                csv_J3 = matrix
            else:
                csv_J4 = matrix

        return csv_J1, csv_J2, csv_J3, csv_J4


def display_jacobian(jacobian):
    for i, j in enumerate(jacobian, 1):
        print(f"csv_J{i} =\n", j, "\n")