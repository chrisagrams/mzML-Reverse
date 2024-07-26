import sys

from pin_parser import pin_to_df


def original_or_reverse(scan_num):
    return 'original' if scan_num % 2 == 0 else 'reversed'


def annotate_pairs(df):
    df['is_reversed'] = df['ScanNr'].apply(original_or_reverse)
    df['paired'] = (df['ScanNr'] % 2 == 1) & (df['ScanNr'] + 1).isin(df['ScanNr'])
    paired_odd_scan_nrs = df[df['paired']]['ScanNr']
    df.loc[df['ScanNr'].isin(paired_odd_scan_nrs + 1), 'paired'] = True
    return df


if __name__ == '__main__':
    pin_file = sys.argv[1]
    out_file = pin_file.replace(".pin", "_annotated.csv")

    if len(sys.argv) < 2:
        print("Usage: python reverse_count.py input.pin")
    df = pin_to_df(pin_file)

    annotate_pairs(df)

    num_pairs = df['paired'].sum() // 2

    total_numbers = len(df)
    percentage_pairs = (num_pairs / total_numbers) * 100

    print(f'Total pairs: {num_pairs}')
    print(f'Percentage of pairs: {percentage_pairs:.2f}%')
    print(df)
    df.to_csv(out_file)