"""
pyCoreGage — Compliance Manager (compliance_manager.py)
========================================================
Validates clinical data against regulatory compliance standards.

Supported standards:
  - ICH-GCP E6(R2): International Council for Harmonisation Good Clinical Practice
  - FDA 21 CFR Part 11: Electronic Records, Electronic Signatures
  - FDA 21 CFR Part 50: Protection of Human Subjects
  - FDA 21 CFR Part 54: Clinical Trial Reporting
  - EMA Guideline on GCP: European Medicines Agency
  - NMPA GCP: China National Medical Products Administration
  - GDPR: General Data Protection Regulation (EU)
  - HIPAA: Health Insurance Portability and Accountability Act (US)

Checks performed:
  1. Informed consent completeness and timing
  2. Protocol deviation tracking
  3. Data integrity (ALCOA+ principles)
  4. Audit trail completeness
  5. Electronic signature compliance
  6. Data privacy and anonymization
  7. Regulatory submission readiness

Author:  pyCoreGage Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from core_data import (
    CoreGageConfig,
    CoreGageState,
    CoreGageFinding,
    CheckCategory,
    CheckStatus,
    DataSource,
    Severity,
)

logger = logging.getLogger("pyCoreGage.compliance")


class ComplianceStandard(Enum):
    """Regulatory compliance standards."""
    ICH_GCP = "ICH-GCP"
    FDA_21CFR11 = "FDA-21CFR11"
    FDA_21CFR50 = "FDA-21CFR50"
    FDA_21CFR54 = "FDA-21CFR54"
    EMA_GCP = "EMA-GCP"
    NMPA_GCP = "NMPA-GCP"
    GDPR = "GDPR"
    HIPAA = "HIPAA"


class ALCOA_Principle(Enum):
    """ALCOA+ data integrity principles."""
    ATTRIBUTABLE = "attributable"
    LEGIBLE = "legible"
    CONTIMPOURANEOUS = "contemporaneous"
    ORIGINAL = "original"
    ACCURATE = "accurate"
    COMPLETE = "complete"
    CONSISTENT = "consistent"
    ENDURING = "enduring"
    AVAILABLE = "available"


@dataclass
class ComplianceRule:
    """Single compliance validation rule."""
    rule_id: str
    name: str
    standard: ComplianceStandard
    description: str
    severity: Severity = Severity.HIGH
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolDeviation:
    """Protocol deviation record."""
    deviation_id: str
    subject_id: str
    visit_id: str
    description: str
    category: str  # minor, major, critical
    detected_date: str
    resolved: bool = False
    resolution_date: Optional[str] = None


class ComplianceManager:
    """
    Checker module for regulatory compliance validation.

    Interfaces with CoreGageState to access clinical data and produces
    CoreGageFinding objects for compliance violations.
    """

    def __init__(self, config: CoreGageConfig, state: CoreGageState):
        self.config = config
        self.state = state
        self._compliance_rules: List[ComplianceRule] = []
        self._findings: List[CoreGageFinding] = []
        self._deviations: List[ProtocolDeviation] = []

        # Initialize default compliance rules
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialize default compliance validation rules."""
        self._compliance_rules = [
            # ── ICH-GCP Rules ──
            ComplianceRule(
                rule_id="ICH-GCP-001",
                name="Informed Consent Before Any Study Procedure",
                standard=ComplianceStandard.ICH_GCP,
                description="Written informed consent must be obtained before any "
                            "study-specific procedures are performed.",
                severity=Severity.CRITICAL,
            ),
            ComplianceRule(
                rule_id="ICH-GCP-002",
                name="Informed Consent Documentation Complete",
                standard=ComplianceStandard.ICH_GCP,
                description="Informed consent form must include all required elements "
                            "(purpose, procedures, risks, benefits, alternatives).",
                severity=Severity.HIGH,
            ),
            ComplianceRule(
                rule_id="ICH-GCP-003",
                name="Protocol Deviation Reporting",
                standard=ComplianceStandard.ICH_GCP,
                description="All protocol deviations must be documented and reported.",
                severity=Severity.HIGH,
            ),
            ComplianceRule(
                rule_id="ICH-GCP-004",
                name="Source Data Verification",
                standard=ComplianceStandard.ICH_GCP,
                description="Source data must be available for verification and "
                            "consistent with EDC entries.",
                severity=Severity.HIGH,
            ),
            ComplianceRule(
                rule_id="ICH-GCP-005",
                name="Investigator Qualification",
                standard=ComplianceStandard.ICH_GCP,
                description="Investigator must be qualified by education, training, "
                            "and experience to conduct the trial.",
                severity=Severity.HIGH,
            ),

            # ── FDA 21 CFR Part 11 Rules ──
            ComplianceRule(
                rule_id="FDA-21CFR11-001",
                name="Electronic Signature Requirements",
                standard=ComplianceStandard.FDA_21CFR11,
                description="Electronic signatures must be linked to their respective "
                            "electronic records and include signature components.",
                severity=Severity.HIGH,
            ),
            ComplianceRule(
                rule_id="FDA-21CFR11-002",
                name="Audit Trail Integrity",
                standard=ComplianceStandard.FDA_21CFR11,
                description="Audit trails must capture creation, modification, and "
                            "deletion of electronic records.",
                severity=Severity.HIGH,
            ),
            ComplianceRule(
                rule_id="FDA-21CFR11-003",
                name="System Access Controls",
                standard=ComplianceStandard.FDA_21CFR11,
                description="System must have appropriate access controls and "
                            "authentication mechanisms.",
                severity=Severity.MEDIUM,
            ),

            # ── GDPR Rules ──
            ComplianceRule(
                rule_id="GDPR-001",
                name="Personal Data Minimization",
                standard=ComplianceStandard.GDPR,
                description="Only personal data necessary for the trial purpose "
                            "should be collected and processed.",
                severity=Severity.MEDIUM,
            ),
            ComplianceRule(
                rule_id="GDPR-002",
                name="Data Subject Rights",
                standard=ComplianceStandard.GDPR,
                description="Data subjects must be informed of their rights to access, "
                            "rectification, and erasure of personal data.",
                severity=Severity.MEDIUM,
            ),

            # ── HIPAA Rules ──
            ComplianceRule(
                rule_id="HIPAA-001",
                name="PHI Protection",
                standard=ComplianceStandard.HIPAA,
                description="Protected Health Information must be safeguarded against "
                            "unauthorized disclosure.",
                severity=Severity.HIGH,
            ),
        ]

    # ──────────────────────────────────────────────────────────
    # Configuration
    # ──────────────────────────────────────────────────────────

    def add_compliance_rule(self, rule: ComplianceRule) -> None:
        """Register a compliance validation rule."""
        self._compliance_rules.append(rule)

    def add_compliance_rules_from_list(
        self, rules: List[Dict[str, Any]]
    ) -> None:
        """Bulk-register compliance rules from a list of dicts."""
        for r in rules:
            if "standard" in r and isinstance(r["standard"], str):
                r["standard"] = ComplianceStandard(r["standard"])
            if "severity" in r and isinstance(r["severity"], str):
                r["severity"] = Severity(r["severity"])
            self.add_compliance_rule(ComplianceRule(**r))

    def add_protocol_deviation(self, deviation: ProtocolDeviation) -> None:
        """Register a protocol deviation."""
        self._deviations.append(deviation)

    # ──────────────────────────────────────────────────────────
    # Core Check Methods
    # ──────────────────────────────────────────────────────────

    def check(self) -> List[CoreGageFinding]:
        """
        Run all compliance checks and return findings.

        Returns:
            List of CoreGageFinding objects.
        """
        self._findings = []

        # 1. Informed consent validation
        self._check_informed_consent()

        # 2. Protocol deviation tracking
        self._check_protocol_deviations()

        # 3. Data integrity (ALCOA+)
        self._check_data_integrity()

        # 4. Electronic signature compliance
        self._check_electronic_signatures()

        # 5. Audit trail completeness
        self._check_audit_trail()

        # 6. Data privacy checks
        self._check_data_privacy()

        # 7. Apply registered compliance rules
        self._apply_compliance_rules()

        # Filter by minimum severity
        min_sev = self.config.min_severity
        self._findings = [
            f for f in self._findings
            if self._severity_ge(f.severity, min_sev)
        ]

        logger.info("ComplianceManager: %d findings", len(self._findings))
        return self._findings

    # ──────────────────────────────────────────────────────────
    # Individual Check Implementations
    # ──────────────────────────────────────────────────────────

    def _check_informed_consent(self) -> None:
        """Validate informed consent completeness and timing."""
        consents = self.state.get_data(DataSource.CONSENT)
        visits = self.state.get_data(DataSource.VISIT)

        if not consents:
            logger.debug("No consent data loaded, skipping consent check.")
            return

        # Required consent elements per ICH-GCP
        required_elements = [
            "study_purpose",
            "procedures",
            "risks",
            "benefits",
            "alternatives",
            "confidentiality",
            "compensation",
            "contact_information",
            "voluntary_participation",
            "right_to_withdraw",
        ]

        for consent in consents:
            subject_id = consent.get("subject_id", "")
            consent_date = self._parse_date(consent.get("consent_date"))
            consent_version = consent.get("consent_version", "")

            # Check required elements
            missing_elements = []
            for element in required_elements:
                if not consent.get(element, False):
                    missing_elements.append(element)

            if missing_elements:
                self._findings.append(CoreGageFinding(
                    category=CheckCategory.COMPLIANCE,
                    severity=Severity.HIGH,
                    source="consent",
                    subject_id=subject_id,
                    message=(
                        f"Informed consent missing required elements: "
                        f"{', '.join(missing_elements)}"
                    ),
                    details={"missing_elements": missing_elements,
                             "consent_version": consent_version},
                    status=CheckStatus.FAILED,
                ))

            # Check consent date vs. first visit
            if consent_date and visits:
                subject_visits = [
                    v for v in visits
                    if v.get("subject_id") == subject_id
                ]
                if subject_visits:
                    first_visit_date = min(
                        self._parse_date(v.get("visit_date")) or
                        datetime.max for v in subject_visits
                    )
                    if consent_date > first_visit_date:
                        self._findings.append(CoreGageFinding(
                            category=CheckCategory.COMPLIANCE,
                            severity=Severity.CRITICAL,
                            source="consent",
                            subject_id=subject_id,
                            message=(
                                f"Consent date ({consent_date.date()}) is after "
                                f"first visit ({first_visit_date.date()}) — "
                                f"ICH-GCP violation"
                            ),
                            status=CheckStatus.FAILED,
                        ))

    def _check_protocol_deviations(self) -> None:
        """Track and flag unresolved protocol deviations."""
        for deviation in self._deviations:
            if not deviation.resolved:
                self._findings.append(CoreGageFinding(
                    category=CheckCategory.COMPLIANCE,
                    severity={
                        "critical": Severity.CRITICAL,
                        "major": Severity.HIGH,
                        "minor": Severity.MEDIUM,
                    }.get(deviation.category.lower(), Severity.MEDIUM),
                    source="protocol",
                    subject_id=deviation.subject_id,
                    visit_id=deviation.visit_id,
                    message=(
                        f"Unresolved protocol deviation: "
                        f"'{deviation.description}' "
                        f"(category: {deviation.category})"
                    ),
                    details={
                        "deviation_id": deviation.deviation_id,
                        "category": deviation.category,
                        "detected_date": deviation.detected_date,
                    },
                    status=CheckStatus.FAILED,
                ))

    def _check_data_integrity(self) -> None:
        """Validate data integrity against ALCOA+ principles."""
        # Check each data source for ALCOA+ compliance
        for source, data in self.state.data.items():
            if not isinstance(data, list):
                continue

            for record in data:
                subject_id = record.get("subject_id", "")

                # Check for attributable (who entered the data)
                if not record.get("entered_by") and not record.get("user_id"):
                    self._findings.append(CoreGageFinding(
                        category=CheckCategory.COMPLIANCE,
                        severity=Severity.MEDIUM,
                        source=source.value,
                        subject_id=subject_id,
                        message=(
                            f"ALCOA+ violation: Data not attributable — "
                            f"missing 'entered_by' or 'user_id' field"
                        ),
                        details={"principle": "attributable"},
                        status=CheckStatus.FAILED,
                    ))

                # Check for contemporaneous (date of entry)
                if not record.get("entry_date") and not record.get("timestamp"):
                    self._findings.append(CoreGageFinding(
                        category=CheckCategory.COMPLIANCE,
                        severity=Severity.MEDIUM,
                        source=source.value,
                        subject_id=subject_id,
                        message=(
                            f"ALCOA+ violation: Data not contemporaneous — "
                            f"missing 'entry_date' or 'timestamp' field"
                        ),
                        details={"principle": "contemporaneous"},
                        status=CheckStatus.FAILED,
                    ))

                # Check for complete (required fields)
                required_fields = record.get("_required_fields", [])
                for rf in required_fields:
                    if not record.get(rf):
                        self._findings.append(CoreGageFinding(
                            category=CheckCategory.COMPLIANCE,
                            severity=Severity.MEDIUM,
                            source=source.value,
                            subject_id=subject_id,
                            field_name=rf,
                            message=(
                                f"ALCOA+ violation: Incomplete data — "
                                f"required field '{rf}' is empty"
                            ),
                            details={"principle": "complete"},
                            status=CheckStatus.FAILED,
                        ))

    def _check_electronic_signatures(self) -> None:
        """Validate electronic signature compliance (FDA 21 CFR Part 11)."""
        # Check consent records for e-signature
        consents = self.state.get_data(DataSource.CONSENT)
        if not consents:
            return

        for consent in consents:
            subject_id = consent.get("subject_id", "")

            # Check for electronic signature components
            has_signature = bool(
                consent.get("signature") or consent.get("electronic_signature")
            )
            has_signature_date = bool(
                consent.get("signature_date") or consent.get("signature_timestamp")
            )
            has_signature_type = bool(
                consent.get("signature_type") or consent.get("signature_meaning")
            )

            if has_signature:
                if not has_signature_date:
                    self._findings.append(CoreGageFinding(
                        category=CheckCategory.COMPLIANCE,
                        severity=Severity.HIGH,
                        source="consent",
                        subject_id=subject_id,
                        message=(
                            "Electronic signature missing date/timestamp "
                            "(FDA 21 CFR Part 11 violation)"
                        ),
                        details={"principle": "electronic_signature"},
                        status=CheckStatus.FAILED,
                    ))
                if not has_signature_type:
                    self._findings.append(CoreGageFinding(
                        category=CheckCategory.COMPLIANCE,
                        severity=Severity.MEDIUM,
                        source="consent",
                        subject_id=subject_id,
                        message=(
                            "Electronic signature missing type/meaning "
                            "(FDA 21 CFR Part 11 violation)"
                        ),
                        details={"principle": "electronic_signature"},
                        status=CheckStatus.FAILED,
                    ))

    def _check_audit_trail(self) -> None:
        """Validate audit trail completeness."""
        # Check if audit trail data is available
        audit_data = self.state.get_data(DataSource.EDC)
        if not audit_data:
            return

        for record in audit_data:
            subject_id = record.get("subject_id", "")

            # Check for audit trail fields
            has_audit = bool(
                record.get("audit_trail") or record.get("change_history") or
                record.get("version_history")
            )

            if not has_audit:
                self._findings.append(CoreGageFinding(
                    category=CheckCategory.COMPLIANCE,
                    severity=Severity.MEDIUM,
                    source="edc",
                    subject_id=subject_id,
                    message=(
                        "Audit trail not available for this record "
                        "(FDA 21 CFR Part 11 requirement)"
                    ),
                    details={"principle": "audit_trail"},
                    status=CheckStatus.FAILED,
                ))

    def _check_data_privacy(self) -> None:
        """Check data privacy compliance (GDPR/HIPAA)."""
        # Check for PHI/PII in data fields
        pii_patterns = {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "address": r"\b\d+\s+[A-Za-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b",
        }

        for source, data in self.state.data.items():
            if not isinstance(data, list):
                continue

            for record in data:
                subject_id = record.get("subject_id", "")

                for field_name, value in record.items():
                    if not isinstance(value, str):
                        continue

                    for pii_type, pattern in pii_patterns.items():
                        if re.search(pattern, value, re.IGNORECASE):
                            self._findings.append(CoreGageFinding(
                                category=CheckCategory.COMPLIANCE,
                                severity=Severity.HIGH,
                                source=source.value,
                                subject_id=subject_id,
                                field_name=field_name,
                                message=(
                                    f"Potential PII detected in field '{field_name}': "
                                    f"{pii_type} pattern found"
                                ),
                                details={"pii_type": pii_type},
                                status=CheckStatus.FAILED,
                            ))

    def _apply_compliance_rules(self) -> None:
        """Apply registered compliance validation rules."""
        for rule in self._compliance_rules:
            if not rule.enabled:
                continue

            # Each rule can have custom check logic
            # For now, rules are informational — actual checks are done
            # by the dedicated methods above
            pass

    # ──────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        """Parse a date string into datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y",
                        "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(value.strip(), fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _severity_ge(a: Severity, b: Severity) -> bool:
        """Check if severity a >= severity b."""
        order = {Severity.INFO: 0, Severity.LOW: 1, Severity.MEDIUM: 2,
                 Severity.HIGH: 3, Severity.CRITICAL: 4}
        return order.get(a, 0) >= order.get(b, 0)

    # ──────────────────────────────────────────────────────────
    # Reporting
    # ──────────────────────────────────────────────────────────

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Generate a compliance summary report."""
        by_standard: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}

        for f in self._findings:
            # Extract standard from rule_id if available
            rule_id = f.details.get("rule_id", "")
            standard = rule_id.split("-")[0] if rule_id else "general"
            by_standard[standard] = by_standard.get(standard, 0) + 1

            sev = f.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "total_findings": len(self._findings),
            "by_standard": by_standard,
            "by_severity": by_severity,
            "deviations_tracked": len(self._deviations),
            "unresolved_deviations": sum(
                1 for d in self._deviations if not d.resolved
            ),
        }
