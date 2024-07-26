import sys
from pin_parser import pin_to_df


if __name__ == '__main__':
    pin_file = sys.argv[1]
    if len(sys.argv) < 2:
        print("Usage: python decoy_count.py input.pin")
    df = pin_to_df(pin_file)

    print(df['Label'].value_counts())