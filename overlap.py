from reverse_count import annotate_pairs
import sys
from pin_parser import pin_to_df


def get_pairs(df):
    paired_odd_scan_nrs = df[df['paired']]['ScanNr']
    pairs = set()

    for scan_nr in paired_odd_scan_nrs:
        pair = (scan_nr, scan_nr + 1)
        if pair[0] in df['ScanNr'].values and pair[1] in df['ScanNr'].values:
            pairs.add(pair)

    return pairs


def get_overlap(files):
    paired_scans = []

    for pin_file in files:
        df = pin_to_df(pin_file)
        df = annotate_pairs(df)
        pairs = get_pairs(df)
        paired_scans.append((pin_file, pairs))

    all_pairs = [pairs for _, pairs in paired_scans]
    overlap = set.intersection(*all_pairs)

    return overlap, paired_scans


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python overlap_count.py file1.pin file2.pin ...")
        sys.exit(1)

    pin_files = sys.argv[1:]

    overlap, paired_scans = get_overlap(pin_files)

    print(f'Overlapping pairs (ScanNr): {overlap}')
    print(f'Total overlapping pairs: {len(overlap)}')

    for file, pairs in paired_scans:
        unique_pairs = pairs - overlap
        print(f'Unique pairs in {file}: {unique_pairs}')
        print(f'Total unique pairs in {file}: {len(unique_pairs)}')