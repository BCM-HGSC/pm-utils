#!/usr/bin/env python

"""
Combines Exemplar merge report with new 90X metrics report
(from R&D group) and generates an Excel workbook with two sheets.

tab3: weekly report tab3 'Production Metrics'
tmqc: QC data metrics with results PASS or FAIL
"""

# First come standard libraries, in alphabetical order.
import argparse
from collections import defaultdict
import re

# After a blank line, import third-party libraries.
import pandas as pd

# After another blank line, import local libraries.
from report_merged_qc_results import normalize_name


# for input files
RTM_COLS = [
    "merge_name",
    "merge_finished_date",
    "results_path",
    "unique_aligned_bases",  # internal qc only
    "duplicate_bases",  # internal qc only
    "aligned_bases_pct",  # internal qc only
    "average_coverage",
    "chimeric_rate",  # internal qc only
    "per_ten_coverage_bases",
    "per_twenty_coverage_bases",
    "q20_bases",
    "contamination_rate",
    "mean_insert_size",
    "pf_hq_aligned_q20_bases",
    "wgs_het_snp_q",
    "wgs_het_snp_sensitivity",
]

NM_COLS = [
    "sample_id",
    "samples",
    "per_sixty_coverage_bases",
    "per_seventy_coverage_bases",
]

# for output files
WKT3_COLS = [
    "sample_id",
    "collection",
    "pf_hq_aligned_q20_bases",
    "mean_insert_size",
    "average_coverage",
    "wgs_het_snp_q",
    "wgs_het_snp_sensitivity",
    "per_ten_coverage_bases",
    "per_twenty_coverage_bases",
    "q20_bases",
    "contamination_pct",
]

TMQC_COLS = [
    # weekly_report
    "sample_id",
    "collection",
    "pf_hq_aligned_q20_bases",
    "mean_insert_size",
    "average_coverage",
    "wgs_het_snp_q",
    "wgs_het_snp_sensitivity",
    "per_ten_coverage_bases",
    "per_twenty_coverage_bases",
    "per_sixty_coverage_bases",
    "per_seventy_coverage_bases",
    "q20_bases",
    "contamination_pct",
    # internal qc only
    "unique_aligned_gb",
    "aligned_bases_pct",
    "chimeric_rate",
    "merge_name",
    "merge_finished_date",
    "results_path",
    "results",
]

# map abbrev (from merge_name in input report) to the Study/Cohort name
COLLECTION_LIST = [
    ("Legacy", "TOPMed Control"),
    ("TMHASC", "Harvard SCD"),
    ("TMCGVC", "Causal Genetic Variants of Cardiomyopathy"),
    ("TMGCUC", "Genetic Causes of Unexplained Cardiomyopathies"),
    ("TMREDS", "Sickle Cell Disease REDS III"),
]


def main():
    args = parse_args()
    run(args.recent_merge_report, args.new_90x_metrics_file, args.output_file)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "recent_merge_report", help="*.xlsx, usually generated by QC group"
    )
    parser.add_argument(
        "new_90x_metrics_file", help="*.xlsx, usually generated by R&D group"
    )
    parser.add_argument("output_file", help="should end with .xlsx")
    args = parser.parse_args()
    return args


def run(recent_merge_report, new_90x_metrics_file, output_file):
    rtm_sub = load_merge_report(recent_merge_report)
    nm_sub = load_metrics(new_90x_metrics_file)
    m = merge_qc_results(rtm_sub, nm_sub)
    # TODO track weeks
    # will contain output for at least the last 4 weeks along with metrics
    wkt3 = m[WKT3_COLS]
    tmqc = m[TMQC_COLS]
    output_results(output_file, wkt3, tmqc)


def load_merge_report(recent_merge_report):
    rtm = pd.read_excel(recent_merge_report, sheet_name="table ref")

    # normalize column names
    d1 = {c: normalize_name(c) for c in rtm.columns}
    rtm.rename(columns=d1, inplace=True)

    # use loc to avoid warning message
    rtm_sub = rtm.loc[:, RTM_COLS]

    # extract abbrev from merge_name
    cid = rtm_sub["merge_name"].str.split("_", n=5, expand=True)[2]
    # add default value using defaultdict
    d2 = defaultdict(lambda: None)
    d2.update(COLLECTION_LIST)
    # add a column 'collection'
    rtm_sub["collection"] = cid.map(d2)

    # extract sample_id from merge_name
    sid = rtm_sub["merge_name"].str.split("_", n=5, expand=True)[3]
    rtm_sub["sample_id"] = sid

    # convert contamination_rate to contamination_pct
    rtm_sub["contamination_pct"] = rtm_sub["contamination_rate"] * 100

    # pandas broadcasting operation
    rtm_sub["unique_aligned_gb"] = (
        rtm_sub["unique_aligned_bases"]
    ) / 1_000_000_000

    return rtm_sub


def load_metrics(new_90x_metrics_file):
    # new metrics from R&D group; will not be pushed to Exemplar LIMS
    nm = pd.read_excel(new_90x_metrics_file, sheet_name="_90x")
    d2 = {c: normalize_name(c) for c in nm.columns}
    nm.rename(columns=d2, inplace=True)
    # convert 60x coverage
    nm["per_sixty_coverage_bases"] = nm["pct_of_bases_with_60x_coverage"] * 100
    # convert 70x coverage
    nm["per_seventy_coverage_bases"] = (
        nm["pct_of_bases_with_70x_coverage"] * 100
    )
    nm_sub = nm.loc[:, NM_COLS]
    return nm_sub


def merge_qc_results(rtm_sub, nm_sub):
    m = pd.merge(
        rtm_sub, nm_sub, how="outer", left_on="sample_id", right_on="sample_id"
    )
    # add qc results 'PASS' or 'FAIL'
    # Negative checks, should all be False
    n1 = m["unique_aligned_gb"] < 90.0
    n2 = m["aligned_bases_pct"] < 90.0
    n3 = m["average_coverage"] < 90.0  # 90x metrics
    n4 = m["per_ten_coverage_bases"] < 95.0
    n5 = m["per_twenty_coverage_bases"] < 90.0
    n6 = m["per_sixty_coverage_bases"] < 95.0  # 90x metrics
    n7 = m["per_seventy_coverage_bases"] < 90.0  # 90x metrics
    n8 = m["q20_bases"] < 205_000_000_000  # 90x metrics
    # Positive checks, should all be True
    p1 = m["contamination_pct"] < 3.0
    p2 = m["chimeric_rate"] < 5.0
    # Combined
    all_checks_good = p1 & p2 & ~(n1 | n2 | n3 | n4 | n5 | n6 | n7 | n8)
    m["results"] = all_checks_good.map({True: "PASS", False: "FAIL"})
    return m


def output_results(output_file, wkt3, tmqc):
    with pd.ExcelWriter(output_file) as writer:
        wkt3.to_excel(writer, sheet_name="tab3", index=False)
        tmqc.to_excel(writer, sheet_name="tm_qc", index=False)


if __name__ == "__main__":
    main()
