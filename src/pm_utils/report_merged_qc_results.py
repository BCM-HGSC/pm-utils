"""
Inputs a single input file 'Exemplar Merge Report'
and generates an Excel workbook with two sheets.

tab3: weekly report tab3 'Production Metrics'
tm_qc: QC data metrics with results PASS or FAIL

New TOPMed metrics be added to Exemplar LIMS merge report:
- PF_HQ_Aligned_Q20_Bases
- MEAN_INSERT_SIZE  # corrected value for Mean Insert Size (Library AVG)
- WGS_HET_SNP_Q
- WGS_HET_SNP_SENSITIVITY
"""

# First come standard libraries, in alphabetical order
import argparse
from collections import defaultdict
import re

# After a blank line, import third-party libraries
import pandas as pd

# After another blank line, import local libraries
from .utils import normalize_name
from .business import (
    decode_merge_name,
    load_merge_report,
)
from .rpt_columns import (
    rpt_merge_cols,  # input
    WKT3_COLS,
    tmqc_merge_cols,  # output
)
from .mappings import STUDY_MAPPING
from . import __version__


def main():
    args = parse_args()
    run(args.recent_merge_report, args.output_file)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "recent_merge_report",
        help="*.xlsx, input_file, usually downloaded from Exemplar LIMS",
    )
    parser.add_argument("--version", action="version",
                        version="%(prog)s {}".format(__version__))
    parser.add_argument("output_file", help="should end with .xlsx")
    args = parser.parse_args()
    return args


def run(recent_merge_report, output_file):
    rtm_sub = load_merge_report(recent_merge_report)
    qc = qc_results(rtm_sub)
    # TODO track weeks
    # will contain output for at least the last 4 weeks along with metrics
    rpt = qc[WKT3_COLS]
    tmqc = qc[tmqc_merge_cols]
    output_results(output_file, rpt, tmqc)


def qc_results(rtm_sub):
    qc = rtm_sub.loc[:].copy()  # create copy of rtm_sub
    # add qc results 'PASS' or 'FAIL'
    # Negative checks, should all be False
    n1 = qc["unique_aligned_gb"] < 90.0
    n2 = qc["aligned_bases_pct"] < 90.0
    n3 = qc["average_coverage"] < 30.0
    n4 = qc["per_ten_coverage_bases"] < 95.0
    n5 = qc["per_twenty_coverage_bases"] < 90.0
    n6 = qc["q20_bases"] < 87_000_000_000
    # Positive checks, should all be True
    p1 = qc["contamination_pct"] < 3.0
    p2 = qc["chimeric_rate"] < 5.0
    # Combined
    all_checks_good = p1 & p2 & ~(n1 | n2 | n3 | n4 | n5 | n6)
    qc["results"] = all_checks_good.map({True: "PASS", False: "FAIL"})
    return qc


def output_results(output_file, rpt, tmqc):
    with pd.ExcelWriter(output_file) as writer:
        rpt.to_excel(writer, sheet_name="tab3", index=False)
        tmqc.to_excel(writer, sheet_name="tm_qc", index=False)
