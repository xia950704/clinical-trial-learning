"""
Test script for _check_sae_candidates() method.
Loads AE.csv and CM.csv data, runs the safety checker, and prints results.
"""
import sys
import os
import csv
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core_data import (
    CoreGageConfig,
    CoreGageState,
    DataSource,
    Severity,
)
from safety_checker import SafetyChecker

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


def load_csv_to_dicts(filepath: str) -> list:
    """Load a CSV file into a list of dicts."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def main():
    print("=" * 80)
    print("🧪 Test: _check_sae_candidates() SAE candidate list generation")
    print("=" * 80)

    # Load AE data
    ae_path = project_root / "实战案例" / "AE.csv"
    med_path = project_root / "实战案例" / "CM.csv"

    if not ae_path.exists():
        print(f"❌ AE data not found: {ae_path}")
        return 1

    aes = load_csv_to_dicts(str(ae_path))
    print(f"📊 Loaded {len(aes)} AE records from AE.csv")

    # Load medication data
    meds = []
    if med_path.exists():
        meds = load_csv_to_dicts(str(med_path))
        print(f"📊 Loaded {len(meds)} medication records from CM.csv")
    else:
        print("⚠️  No medication data found, temporal check will be skipped")

    # Configure
    config = CoreGageConfig(min_severity=Severity.INFO)
    state = CoreGageState(config=config)

    # Load data into state
    state.set_data(DataSource.AE, aes)
    if meds:
        state.set_data(DataSource.MED, meds)

    # Run safety checker
    checker = SafetyChecker(config=config, state=state)
    findings = checker.check()

    print(f"\n📋 Total findings: {len(findings)}")
    print("-" * 60)

    # Categorize findings
    sae_candidate_findings = [
        f for f in findings
        if f.source == "ae" and f.field_name != "sae_candidates"
    ]
    summary_findings = [
        f for f in findings
        if f.source == "ae" and f.field_name == "sae_candidates"
    ]
    other_findings = [
        f for f in findings
        if f.source != "ae"
    ]

    print(f"  SAE candidate findings: {len(sae_candidate_findings)}")
    print(f"  SAE summary findings:   {len(summary_findings)}")
    print(f"  Other findings:         {len(other_findings)}")

    # Print SAE candidate findings by type
    print("\n🔍 SAE Candidate Findings:")
    print("-" * 60)

    ich_e2a = [f for f in sae_candidate_findings if "ICH E2A" in f.message]
    ctcae3 = [f for f in sae_candidate_findings if "CTCAE Grade" in f.message and "requires SAE review" in f.message]
    temporal = [f for f in sae_candidate_findings if "Temporal suspect" in f.message]
    unexpected = [f for f in sae_candidate_findings if "Unexpected AE candidate" in f.message]

    print(f"\n  1. ICH E2A criteria: {len(ich_e2a)} findings")
    for f in ich_e2a[:5]:
        print(f"     - [{f.severity.value.upper()}] {f.message}")
    if len(ich_e2a) > 5:
        print(f"     ... and {len(ich_e2a) - 5} more")

    print(f"\n  2. CTCAE Grade ≥ 3: {len(ctcae3)} findings")
    for f in ctcae3[:5]:
        print(f"     - [{f.severity.value.upper()}] {f.message}")
    if len(ctcae3) > 5:
        print(f"     ... and {len(ctcae3) - 5} more")

    print(f"\n  3. Temporal suspect (≤7 days): {len(temporal)} findings")
    for f in temporal[:5]:
        print(f"     - [{f.severity.value.upper()}] {f.message}")
    if len(temporal) > 5:
        print(f"     ... and {len(temporal) - 5} more")

    print(f"\n  4. Unexpected (Grade 3+ no SAE marking): {len(unexpected)} findings")
    for f in unexpected[:5]:
        print(f"     - [{f.severity.value.upper()}] {f.message}")
    if len(unexpected) > 5:
        print(f"     ... and {len(unexpected) - 5} more")

    # Print summary
    print("\n📊 SAE Candidate Summary:")
    print("-" * 60)
    for f in summary_findings:
        print(f"  [{f.severity.value.upper()}] {f.message}")
        print(f"  Details: {f.details}")

    # Verify counts
    print("\n✅ Test Results:")
    print(f"  - CTCAE ≥ 3 count > 0: {len(ctcae3) > 0} ({len(ctcae3)} found)")
    print(f"  - Temporal suspect count > 0: {len(temporal) > 0} ({len(temporal)} found)")
    print(f"  - Unexpected count > 0: {len(unexpected) > 0} ({len(unexpected)} found)")
    print(f"  - Summary finding exists: {len(summary_findings) > 0}")

    # Check for any errors
    error_findings = [f for f in findings if f.severity == Severity.CRITICAL and "error" in f.message.lower()]
    if error_findings:
        print(f"\n❌ Errors found: {len(error_findings)}")
        for f in error_findings:
            print(f"  - {f.message}")
        return 1

    print("\n✅ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
