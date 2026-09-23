"""
pyCoreGage — Medical Plugin Entry Point (medcage.py)
=====================================================
Main orchestrator that loads configuration, initializes all checker modules,
executes checks against clinical data, and produces aggregated results.

Usage:
    from medcage import MedCage
    mc = MedCage(config_path="config.json")
    mc.load_data("clinical_data.csv")
    mc.run()
    mc.save_results("output/report.json")

Author:  pyCoreGage Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core_data import (
    CoreGageConfig,
    CoreGageResult,
    CoreGageState,
    CoreGageFinding,
    CheckCategory,
    CheckStatus,
    DataSource,
    Severity,
)
from temporal_checker import TemporalChecker
from coding_checker import CodingChecker
from safety_checker import SafetyChecker
from compliance_manager import ComplianceManager

logger = logging.getLogger("pyCoreGage")


class MedCage:
    """
    Main entry point for the pyCoreGage medical plugin.

    MedCage coordinates all checker modules (temporal, coding, safety,
    compliance) and manages the overall review lifecycle:

        1. Initialize with configuration
        2. Load clinical data and medical dictionaries
        3. Run all enabled checkers
        4. Aggregate findings into CoreGageResult
        5. Export results in multiple formats
    """

    def __init__(self, config: Optional[CoreGageConfig] = None,
                 config_path: Optional[Union[str, Path]] = None):
        """
        Initialize MedCage.

        Args:
            config: CoreGageConfig instance (mutually exclusive with config_path).
            config_path: Path to JSON configuration file.
        """
        if config and config_path:
            raise ValueError("Provide either config or config_path, not both.")

        if config_path:
            self.config = CoreGageConfig.load(config_path)
        elif config:
            self.config = config
        else:
            self.config = CoreGageConfig()

        # Resolve paths relative to this module's directory
        self._base_dir = Path(__file__).parent
        self.config.dict_dir = str(Path(self.config.dict_dir).resolve()
                                   if Path(self.config.dict_dir).is_absolute()
                                   else self._base_dir / self.config.dict_dir)

        # Initialize state
        self.state = CoreGageState(config=self.config)
        self.result = CoreGageResult(config=self.config)

        # Initialize checker modules
        self._checkers: Dict[str, Any] = {}
        self._init_checkers()

        logger.info("MedCage initialized | project=%s protocol=%s",
                     self.config.project_id, self.config.protocol_id)

    # ──────────────────────────────────────────────────────────
    # Initialization
    # ──────────────────────────────────────────────────────────

    def _init_checkers(self) -> None:
        """Instantiate all checker modules based on config toggles."""
        if self.config.enable_temporal:
            self._checkers["temporal"] = TemporalChecker(
                config=self.config, state=self.state)
        if self.config.enable_coding:
            self._checkers["coding"] = CodingChecker(
                config=self.config, state=self.state)
        if self.config.enable_safety:
            self._checkers["safety"] = SafetyChecker(
                config=self.config, state=self.state)
        if self.config.enable_compliance:
            self._checkers["compliance"] = ComplianceManager(
                config=self.config, state=self.state)

    # ──────────────────────────────────────────────────────────
    # Data Loading
    # ──────────────────────────────────────────────────────────

    def load_data(self, path: Union[str, Path],
                  source: DataSource = DataSource.EDC,
                  format: str = "csv") -> None:
        """
        Load clinical data from a file.

        Args:
            path: Path to the data file.
            source: DataSource enum indicating the data type.
            format: File format ('csv', 'xlsx', 'json', 'parquet').
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Data file not found: {p}")

        # Delegate to state for storage
        self.state.set_data(source, {"path": str(p), "format": format})
        self.state.total_records += 1  # simplified; real impl counts rows
        logger.info("Loaded data: %s (source=%s, format=%s)", p.name, source.value, format)

    def load_dictionaries(self) -> None:
        """Load all medical dictionaries from the configured dict directory."""
        dict_dir = Path(self.config.dict_dir)
        if not dict_dir.exists():
            logger.warning("Dictionary directory not found: %s", dict_dir)
            return

        for subdir in dict_dir.iterdir():
            if subdir.is_dir():
                logger.info("Loading dictionary: %s", subdir.name)
                # Each subdirectory represents a dictionary type
                # e.g., meddra/, icd10/, loinc/, snomed/
                self.state.set_dictionary(subdir.name, {"path": str(subdir)})

    # ──────────────────────────────────────────────────────────
    # Execution
    # ──────────────────────────────────────────────────────────

    def run(self) -> CoreGageResult:
        """
        Execute all enabled checker modules and aggregate results.

        Returns:
            CoreGageResult with all findings and summary statistics.
        """
        self.result = CoreGageResult(config=self.config)
        self.result.started_at = time.strftime("%Y-%m-%dT%H:%M:%S")

        logger.info("Starting medical data review...")

        for name, checker in self._checkers.items():
            logger.info("Running checker: %s", name)
            try:
                findings = checker.check()
                self._collect_findings(name, findings)
                self.state.update_progress(name, len(findings))
            except Exception as e:
                logger.error("Checker %s failed: %s", name, e)
                self.result.compliance_findings.append(CoreGageFinding(
                    category=CheckCategory.COMPLIANCE,
                    severity=Severity.CRITICAL,
                    message=f"Checker {name} execution error: {e}",
                    status=CheckStatus.ERROR,
                ))

        self.result.finalize()
        logger.info("Review complete | total_findings=%d | "
                     "by_severity=%s",
                     self.result.total_findings,
                     self.result.findings_by_severity)
        return self.result

    def _collect_findings(self, module: str, findings: List[CoreGageFinding]) -> None:
        """Route findings to the appropriate result list."""
        target = {
            "temporal": self.result.temporal_findings,
            "coding": self.result.coding_findings,
            "safety": self.result.safety_findings,
            "compliance": self.result.compliance_findings,
        }.get(module)
        if target is not None:
            target.extend(findings)

    # ──────────────────────────────────────────────────────────
    # Output
    # ──────────────────────────────────────────────────────────

    def save_results(self, path: Union[str, Path],
                     format: str = "json") -> None:
        """
        Save results to a file.

        Args:
            path: Output file path.
            format: Output format ('json', 'csv', 'xlsx').
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            self.result.save(p)
        elif format == "xlsx":
            self._save_xlsx(p)
        elif format == "csv":
            self._save_csv(p)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info("Results saved to: %s", p)

    def _save_xlsx(self, path: Path) -> None:
        """Export findings to Excel workbook."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for xlsx output. Install: pip install pandas openpyxl")

        all_findings = self.result.all_findings
        if not all_findings:
            logger.warning("No findings to export.")
            return

        records = []
        for f in all_findings:
            d = f.to_dict()
            d["category"] = f.category.value
            d["severity"] = f.severity.value
            d["status"] = f.status.value
            records.append(d)

        df = pd.DataFrame(records)
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="All Findings", index=False)
            # Summary sheet
            summary = pd.DataFrame([
                {"metric": "Total Findings", "value": self.result.total_findings},
                {"metric": "Total Checks", "value": self.result.total_checks},
            ])
            sev_df = pd.DataFrame(list(self.result.findings_by_severity.items()),
                                  columns=["Severity", "Count"])
            cat_df = pd.DataFrame(list(self.result.findings_by_category.items()),
                                  columns=["Category", "Count"])
            summary.to_excel(writer, sheet_name="Summary", index=False)
            sev_df.to_excel(writer, sheet_name="By Severity", index=False)
            cat_df.to_excel(writer, sheet_name="By Category", index=False)

    def _save_csv(self, path: Path) -> None:
        """Export findings to CSV."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for csv output.")

        all_findings = self.result.all_findings
        if not all_findings:
            return

        records = [f.to_dict() for f in all_findings]
        df = pd.DataFrame(records)
        df.to_csv(path, index=False, encoding="utf-8-sig")

    def print_summary(self) -> None:
        """Print a human-readable summary to stdout."""
        r = self.result
        print("=" * 60)
        print(f"  pyCoreGage Medical Review Summary")
        print(f"  Project: {r.config.project_id}")
        print(f"  Protocol: {r.config.protocol_id}")
        print(f"  Run ID: {r.run_id}")
        print(f"  Status: {r.status}")
        print(f"  Total Findings: {r.total_findings}")
        print("-" * 60)
        print(f"  By Severity: {r.findings_by_severity}")
        print(f"  By Category: {r.findings_by_category}")
        print("=" * 60)


# ──────────────────────────────────────────────────────────────
# Convenience function
# ──────────────────────────────────────────────────────────────

def run_medical_review(config_path: Optional[str] = None,
                       data_paths: Optional[List[str]] = None,
                       output_path: Optional[str] = None,
                       output_format: str = "json") -> CoreGageResult:
    """
    One-shot convenience function to run a full medical review.

    Args:
        config_path: Path to configuration JSON.
        data_paths: List of clinical data file paths.
        output_path: Path to save results.
        output_format: Output format ('json', 'csv', 'xlsx').

    Returns:
        CoreGageResult with all findings.
    """
    mc = MedCage(config_path=config_path)
    if data_paths:
        for dp in data_paths:
            mc.load_data(dp)
    mc.load_dictionaries()
    result = mc.run()
    if output_path:
        mc.save_results(output_path, format=output_format)
    mc.print_summary()
    return result


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    result = run_medical_review(
        config_path="config.json",
        data_paths=["data/edc.csv", "data/ae.csv"],
        output_path="output/report.json",
    )
