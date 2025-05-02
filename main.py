from math import ceil, floor

from lxml import etree
from copy import deepcopy
from tqdm import tqdm
import base64
import struct
import re
import sys
import zlib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("-m", '--mass', action='store_true', required=False, help="Reverse m/z array")
parser.add_argument("-i", '--inten', action='store_true', required=False, help="Reverse intensity array")
parser.add_argument("--inplace", action='store_true', required=False, default=False, help="Output only reversed spectra.")


def read_mzml(path):
    tree = etree.parse(path)
    root = tree.getroot()
    return root


def get_ms_level(element):
    if element is not None:
        cv_params = element.findall(".//cvParam", namespaces=tree.getroot().nsmap)
        for cv_param in cv_params:
            if cv_param.attrib["accession"] == 'MS:1000511':
                return int(cv_param.attrib['value'])
        raise ValueError


def get_binaries(element):
    if element is not None:
        ret = []
        binaryDataArrayList = element.findall(".//binaryDataArray", namespaces=tree.getroot().nsmap)
        for binaryDataArray in binaryDataArrayList:
            binary = {'cvParams': []}
            for cv_param in binaryDataArray.findall(".//cvParam", namespaces=tree.getroot().nsmap):
                binary['cvParams'].append({
                    'accession': cv_param.attrib['accession'],
                    'name': cv_param.attrib['name'],
                    'value': cv_param.attrib['value']
                })
            binary['binaryElement'] = binaryDataArray  # Store element reference
            ret.append(binary)
        return ret


def get_encoding_and_compression(cvParams):
    data_format = None
    compression = None
    for cv_param in cvParams:
        if cv_param['accession'] == 'MS:1000521':  # 32f
            data_format = 'f'
        elif cv_param['accession'] == 'MS:1000523':  # 64d
            data_format = 'd'
        elif cv_param['accession'] == 'MS:1000574':  # zlib
            compression = True
        elif cv_param['accession'] == 'MS:1000576':  # no compression
            compression = False
    return data_format, compression


def decode_binary(text, source_format, source_compression):
    if text is not None:
        decoded_bytes = base64.b64decode(text)
        if source_compression:
            decoded_bytes = zlib.decompress(decoded_bytes)

        if source_format == 'f':
            arr_len = len(decoded_bytes) // 4
        elif source_format == 'd':
            arr_len = len(decoded_bytes) // 8

        arr = struct.unpack(source_format * arr_len, decoded_bytes)
        return arr


def encode_binary(arr, source_format, source_compression):
    if arr is not None:
        byte_array = struct.pack(source_format * len(arr), *arr)

        if source_compression:
            buff = zlib.compress(byte_array)
        else:
            buff = byte_array
        return base64.b64encode(buff)


def get_binary_elem(element):
    if element is not None:
        binary_elem = element.find(".//binary", namespaces=tree.getroot().nsmap)
        if binary_elem is not None:
            return binary_elem
    return None


def simple_reverse(arr):
    return arr[::-1]


def mass_reverse(arr):
    peak = ceil(max(arr))
    base = floor(min(arr))
    rev = []
    for mz in arr:
        rev.append((peak-mz+base))
    return rev


def update_index_and_scan(spectrum, index, scan):
    spectrum.attrib['index'] = str(index)
    id_str = spectrum.attrib['id']
    spectrum.attrib['id'] = re.sub(r'scan=\d+', f'scan={scan}', id_str)


if __name__ == "__main__":
    args = parser.parse_args()
    input_mzml = args.input_file
    output_mzml = input_mzml.replace(".mzML", "_rev.mzML")
    tree = etree.parse(input_mzml)

    for spectrum in tqdm(tree.findall(".//mzML/run/spectrumList/spectrum", namespaces=tree.getroot().nsmap)):
        index = int(spectrum.attrib['index'])
        scan_info = spectrum.attrib['id']
        scan_number = int(scan_info.split("scan=")[1])

        # Duplicate the spectrum (if not inplace)
        if not args.inplace:
            duplicate = deepcopy(spectrum)
        else:
            duplicate = spectrum

        duplicate.attrib['id'] += " rev"
        # Get MS Level
        ms_level = get_ms_level(duplicate)

        if ms_level > 1:  # Do not reverse MS1 spectra
            binaries = get_binaries(duplicate)
            for binary in binaries:
                for cv_param in binary['cvParams']:
                    if args.mass and cv_param['accession'] == 'MS:1000514':     # m/z array
                        data_format, compression = get_encoding_and_compression(binary['cvParams'])
                        binary_elem = get_binary_elem(binary['binaryElement'])
                        arr = decode_binary(binary_elem.text, data_format, compression)
                        rev = mass_reverse(arr)
                        binary_elem.text = encode_binary(rev, data_format, compression)
                    elif args.inten and cv_param['accession'] == 'MS:1000515':  # Intensity array
                        data_format, compression = get_encoding_and_compression(binary['cvParams'])
                        binary_elem = get_binary_elem(binary['binaryElement'])
                        arr = decode_binary(binary_elem.text, data_format, compression)
                        rev = simple_reverse(arr)
                        binary_elem.text = encode_binary(rev, data_format, compression)


        if not args.inplace:
            # Update indices
            update_index_and_scan(spectrum, 2 * index + 1, (2 * index + 1) + 1)
            update_index_and_scan(duplicate, 2 * index, (2 * index) + 1)

            # Add reversed/duplicated spectrum before the original
            spectrum.addprevious(duplicate)

    tree.write(output_mzml, pretty_print=True, xml_declaration=True, encoding='UTF-8')
