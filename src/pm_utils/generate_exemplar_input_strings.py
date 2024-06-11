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


def generate_exemplar_input_str(inp_dump):
    unique_strs = sorted(set(inp_dump.split()))
    pattern_list = [f"%{item}%" for item in unique_strs]
    exemplar_input_str = ",".join(pattern_list)
    return exemplar_input_str
