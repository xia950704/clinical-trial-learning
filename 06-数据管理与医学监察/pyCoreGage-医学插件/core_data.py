"""
pyCoreGage — Medical Plugin Architecture
=========================================
Core data structures: CoreGageState, CoreGageConfig, CoreGageResult.
These are the foundational types that all medical plugin modules operate on.

Author:  pyCoreGage Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# ──────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────

class Severity(Enum):
    """Severity levels for findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CheckCategory(Enum):
    """Categories of medical data checks."""
    TEMPORAL = "temporal"
    CODING = "coding"
    SAFETY = "safety"
    COMPLIANCE = "compliance"
    CONSISTENCY = "consistency"
    INTEGRITY = "integrity"


class CheckStatus(Enum):
    """Status of a single check execution."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class DataSource(Enum):
    """Supported clinical data sources."""
    EDC = "edc"
    LAB = "lab"
    ECG = "ecg"
    VITAL = "vital"
    AE = "ae"
    AE_SAE = "ae_sae"
    MED = "medication"
    DEMOGRAPHIC = "demographic"
    CONSENT = "consent"
    VISIT = "visit"
    PROTOCOL = "protocol"


# ──────────────────────────────────────────────────────────────
# Core Data Structures
# ──────────────────────────────────────────────────────────────

@dataclass
class CoreGageConfig:
    """
    Top-level configuration for the pyCoreGage medical plugin.

    Controls which checkers are enabled, severity thresholds,
    dictionary paths, output formats, and compliance rules.
    """
    # ── Identity ──
    project_id: str = ""
    protocol_id: str = ""
    version: str = "1.0.0"

    # ── Module toggles ──
    enable_temporal: bool = True
    enable_coding: bool = True
    enable_safety: bool = True
    enable_compliance: bool = True

    # ── Severity thresholds ──
    min_severity: Severity = Severity.LOW

    # ── Dictionary paths ──
    dict_dir: str = "dictionaries"
    meddra_version: str = ""
    icd10_version: str = ""
    loinc_version: str = ""

    # ── Output ──
    output_dir: str = "output"
    output_format: str = "json"  # json | csv | xlsx
    log_level: str = "INFO"

    # ── Temporal config ──
    temporal_max_gap_days: int = 365
    temporal_tolerance_days: int = 1

    # ── Safety config ──
    safety_lab_grades: List[str] = field(default_factory=lambda: ["3", "4", "5"])
    safety_vital_alerts: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # ── Compliance config ──
    compliance_regions: List[str] = field(default_factory=lambda: ["US", "EU", "CN"])
    compliance_standards: List[str] = field(default_factory=lambda: ["ICH-GCP", "FDA-21CFR11"])

    # ── Advanced ──
    parallel_workers: int = 4
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict (JSON-compatible)."""
        d = asdict(self)
        d["min_severity"] = self.min_severity.value
        d["enable_temporal"] = self.enable_temporal
        d["enable_coding"] = self.enable_coding
        d["enable_safety"] = self.enable_safety
        d["enable_compliance"] = self.enable_compliance
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CoreGageConfig":
        """Deserialize from dict."""
        d = d.copy()
        if "min_severity" in d and isinstance(d["min_severity"], str):
            d["min_severity"] = Severity(d["min_severity"])
        return cls(**d)

    def save(self, path: Union[str, Path]) -> None:
        """Save configuration to JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "CoreGageConfig":
        """Load configuration from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


@dataclass
class CoreGageFinding:
    """
    A single finding/issue detected by a checker module.

    Each finding has a unique ID, severity, category, source data reference,
    and a human-readable message.
    """
    finding_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: CheckCategory = CheckCategory.CONSISTENCY
    severity: Severity = Severity.MEDIUM
    source: str = ""
    subject_id: str = ""
    visit_id: str = ""
    form_id: str = ""
    field_name: str = ""
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: CheckStatus = CheckStatus.PENDING

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d["severity"] = self.severity.value
        d["status"] = self.status.value
        return d


@dataclass
class CoreGageResult:
    """
    Aggregated result from running all checkers.

    Contains summary statistics, per-module results, and all findings.
    """
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    config: CoreGageConfig = field(default_factory=CoreGageConfig)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""
    status: str = "running"

    # ── Per-module results ──
    temporal_findings: List[CoreGageFinding] = field(default_factory=list)
    coding_findings: List[CoreGageFinding] = field(default_factory=list)
    safety_findings: List[CoreGageFinding] = field(default_factory=list)
    compliance_findings: List[CoreGageFinding] = field(default_factory=list)

    # ── Summary ──
    total_checks: int = 0
    total_findings: int = 0
    findings_by_severity: Dict[str, int] = field(default_factory=dict)
    findings_by_category: Dict[str, int] = field(default_factory=dict)

    @property
    def all_findings(self) -> List[CoreGageFinding]:
        """All findings across all modules."""
        return (self.temporal_findings + self.coding_findings +
                self.safety_findings + self.compliance_findings)

    def finalize(self) -> None:
        """Compute summary statistics and mark complete."""
        self.completed_at = datetime.now().isoformat()
        self.status = "completed"
        all_f = self.all_findings
        self.total_checks = len(all_f)
        self.total_findings = len(all_f)
        self.findings_by_severity = {}
        self.findings_by_category = {}
        for f in all_f:
            s = f.severity.value
            self.findings_by_severity[s] = self.findings_by_severity.get(s, 0) + 1
            c = f.category.value
            self.findings_by_category[c] = self.findings_by_category.get(c, 0) + 1

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["config"] = self.config.to_dict()
        d["temporal_findings"] = [f.to_dict() for f in self.temporal_findings]
        d["coding_findings"] = [f.to_dict() for f in self.coding_findings]
        d["safety_findings"] = [f.to_dict() for f in self.safety_findings]
        d["compliance_findings"] = [f.to_dict() for f in self.compliance_findings]
        return d

    def save(self, path: Union[str, Path]) -> None:
        """Save result to JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "CoreGageResult":
        """Load result from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        config = CoreGageConfig.from_dict(d.pop("config", {}))
        result = cls(config=config, **d)
        # Reconstruct findings
        result.temporal_findings = [CoreGageFinding(**f) for f in d.get("temporal_findings", [])]
        result.coding_findings = [CoreGageFinding(**f) for f in d.get("coding_findings", [])]
        result.safety_findings = [CoreGageFinding(**f) for f in d.get("safety_findings", [])]
        result.compliance_findings = [CoreGageFinding(**f) for f in d.get("compliance_findings", [])]
        return result


@dataclass
class CoreGageState:
    """
    Runtime state of the pyCoreGage medical plugin.

    Tracks current progress, loaded data, active checkers, and intermediate results.
    """
    config: CoreGageConfig = field(default_factory=CoreGageConfig)
    result: Optional[CoreGageResult] = None

    # ── Loaded data (keyed by DataSource) ──
    data: Dict[DataSource, Any] = field(default_factory=dict)

    # ── Loaded dictionaries ──
    dictionaries: Dict[str, Any] = field(default_factory=dict)

    # ── Active checkers ──
    checkers: Dict[str, Any] = field(default_factory=dict)

    # ── Progress tracking ──
    progress: Dict[str, int] = field(default_factory=dict)
    total_records: int = 0

    # ── Cache ──
    _cache: Dict[str, Any] = field(default_factory=dict, repr=False)

    def set_data(self, source: DataSource, data: Any) -> None:
        """Load clinical data for a given source."""
        self.data[source] = data

    def get_data(self, source: DataSource) -> Any:
        """Retrieve clinical data for a given source."""
        return self.data.get(source)

    def set_dictionary(self, name: str, data: Any) -> None:
        """Load a medical dictionary."""
        self.dictionaries[name] = data

    def get_dictionary(self, name: str) -> Any:
        """Retrieve a medical dictionary."""
        return self.dictionaries.get(name)

    def cache_put(self, key: str, value: Any) -> None:
        """Store a value in the internal cache."""
        self._cache[key] = value

    def cache_get(self, key: str) -> Any:
        """Retrieve a value from the internal cache."""
        return self._cache.get(key)

    def update_progress(self, module: str, count: int) -> None:
        """Update progress for a checker module."""
        self.progress[module] = count

    def to_dict(self) -> Dict[str, Any]:
        """Serialize state (excludes raw data and cache for size)."""
        return {
            "config": self.config.to_dict(),
            "progress": self.progress,
            "total_records": self.total_records,
            "data_sources": list(self.data.keys()),
            "dictionaries_loaded": list(self.dictionaries.keys()),
        }
