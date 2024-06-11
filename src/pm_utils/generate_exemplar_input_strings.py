import argparse


def main():
    args = parse_args()
    run(args.inp_dump)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate exemplar input string from inp_dump"
    )
    parser.add_argument(
        "inp_dump",
        type=str,
        help='Various format of input strings (e.g., "SPIDxxx01 SPIDxxx02 SPIDxxx03")',
    )
    args = parser.parse_args()
    return args


def run(inp_dump):
    exemplar_input_str = generate_exemplar_input_str(inp_dump)
    print(exemplar_input_str)


def generate_exemplar_input_str(inp_dump, delimiter=","):
    normalized_inp_str = normalize_inp(inp_dump)
    str_list = normalized_inp_str.split()
    concatenated_str = delimiter.join(str_list)
    exemplar_input_str = "%" + concatenated_str.replace(delimiter, "%,%") + "%"
    return exemplar_input_str


def normalize_inp(inp_dump):
    # Remove leading/trailing whitespace characters
    cleaned_inp_dump = inp_dump.strip()
    lines = cleaned_inp_dump.splitlines()
    normalized_inp_str = " ".join(lines)
    return normalized_inp_str
