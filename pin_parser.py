import pandas as pd
import csv


def tsv_to_list_tab(filename, indices, types=None):
    tsv_file = open(filename)
    tsv = csv.reader(tsv_file, delimiter="\t")
    columns = next(tsv)
    offset = len(columns) - 1
    data = []
    for row in tsv:
        tabs = row[offset:]
        while "" in tabs:
            tabs.remove("")
        data.append(row[:offset] + [tabs])
    # print(list[0])
    df = pd.DataFrame(data, columns=columns)
    df = df.set_index(indices)
    if types is not None:
        df = df.astype(types)
    return df


def pin_to_df(filename):
    df = tsv_to_list_tab(filename, ['SpecId'], {
        'Label': 'int8',
        'ScanNr': 'int',
        'ExpMass': 'float',
        'rank': 'int8',
        'abs_ppm': 'float',
        # 'abs_mass_diff': 'float',
        'log10_evalue': 'float',
        'hyperscore': 'float',
        'delta_hyperscore': 'float',
        'matched_ion_num': 'int8',
        # 'matched_ion_fraction': 'float',
        # 'peptide_length': 'int16',
        'ntt': 'int8',
        'nmc': 'int8',
        'charge_1': 'int8',
        'charge_2': 'int8',
        'charge_3': 'int8',
        'charge_4': 'int8',
        'charge_5': 'int8',
        'charge_6': 'int8',
        # 'charge_7': 'int8',
    })
    return df
