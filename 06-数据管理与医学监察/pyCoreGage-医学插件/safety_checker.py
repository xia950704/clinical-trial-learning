"""
pyCoreGage — Safety Checker (safety_checker.py)
=================================================
Detects safety signals and adverse events in clinical data.

Checks performed:
  1. Lab value abnormalities (Grade 3-5 per CTCAE criteria)
  2. Vital sign alerts (hypotension, tachycardia, fever, etc.)
  3. SAE (Serious Adverse Event) criteria validation
  4. Lab value trends (rapid deterioration)
  5. Drug exposure vs. AE temporal relationship
  6. Concomitant medication safety flags
  7. Missing safety data (critical labs not collected)

Author:  pyCoreGage Team
Version: 1.0.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from core_data import (
    CoreGageConfig,
    CoreGageState,
    CoreGageFinding,
    CheckCategory,
    CheckStatus,
    DataSource,
    Severity,
)

logger = logging.getLogger("pyCoreGage.safety")


@dataclass
class LabAbnormalityRule:
    """Rule for detecting lab abnormalities."""
    test_code: str
    test_name: str
    unit: str = ""
    # CTCAE-like thresholds: (low_critical, low_severe, low_moderate,
    #                         high_moderate, high_severe, high_critical)
    thresholds: Tuple[float, float, float, float, float, float] = (
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    )
    # Normal range
    normal_low: float = 0.0
    normal_high: float = 0.0


@dataclass
class VitalSignRule:
    """Rule for vital sign alerts."""
    parameter: str  # heart_rate, systolic_bp, diastolic_bp, temperature, respiratory_rate
    alert_low: float = 0.0
    alert_high: float = 0.0
    critical_low: float = 0.0
    critical_high: float = 0.0
    unit: str = ""


@dataclass
class SAECriteria:
    """SAE (Serious Adverse Event) classification criteria."""
    name: str
    description: str
    severity: Severity = Severity.HIGH


class SafetyChecker:
    """
    Checker module for safety signal detection.

    Interfaces with CoreGageState to access lab, vital sign, AE, and
    medication data, producing CoreGageFinding objects for safety concerns.
    """

    def __init__(self, config: CoreGageConfig, state: CoreGageState):
        self.config = config
        self.state = state
        self._lab_rules: List[LabAbnormalityRule] = []
        self._vital_rules: List[VitalSignRule] = []
        self._sae_criteria: List[SAECriteria] = [
            SAECriteria("death", "Resulted in death", Severity.CRITICAL),
            SAECriteria("life_threatening", "Life-threatening", Severity.CRITICAL),
            SAECriteria("hospitalization", "Required or prolonged hospitalization", Severity.HIGH),
            SAECriteria("disability", "Persistent/significant disability", Severity.HIGH),
            SAECriteria("congenital_anomaly", "Congenital anomaly/birth defect", Severity.HIGH),
            SAECriteria("important_medical_event", "Important medical event", Severity.MEDIUM),
        ]
        self._findings: List[CoreGageFinding] = []

        # Default vital sign thresholds
        self._init_default_vital_rules()

    def _init_default_vital_rules(self) -> None:
        """Initialize default vital sign alert thresholds."""
        self._vital_rules = [
            VitalSignRule("heart_rate", alert_low=50, alert_high=100,
                          critical_low=40, critical_high=150, unit="bpm"),
            VitalSignRule("systolic_bp", alert_low=90, alert_high=180,
                          critical_low=80, critical_high=200, unit="mmHg"),
            VitalSignRule("diastolic_bp", alert_low=60, alert_high=110,
                          critical_low=50, critical_high=120, unit="mmHg"),
            VitalSignRule("temperature", alert_low=36.0, alert_high=38.0,
                          critical_low=35.0, critical_high=39.5, unit="°C"),
            VitalSignRule("respiratory_rate", alert_low=12, alert_high=20,
                          critical_low=8, critical_high=30, unit="breaths/min"),
        ]

    # ──────────────────────────────────────────────────────────
    # Configuration
    # ──────────────────────────────────────────────────────────

    def add_lab_abnormality_rule(self, rule: LabAbnormalityRule) -> None:
        """Register a lab abnormality detection rule."""
        self._lab_rules.append(rule)

    def add_lab_abnormality_rules_from_list(
        self, rules: List[Dict[str, Any]]
    ) -> None:
        """Bulk-register lab abnormality rules."""
        for r in rules:
            self.add_lab_abnormality_rule(LabAbnormalityRule(**r))

    def add_vital_sign_rule(self, rule: VitalSignRule) -> None:
        """Register a vital sign alert rule."""
        self._vital_rules.append(rule)

    # ──────────────────────────────────────────────────────────
    # Core Check Methods
    # ──────────────────────────────────────────────────────────

    def check(self) -> List[CoreGageFinding]:
        """
        Run all safety checks and return findings.

        Returns:
            List of CoreGageFinding objects.
        """
        self._findings = []

        # 1. Lab value abnormalities
        self._check_lab_abnormalities()

        # 2. Vital sign alerts
        self._check_vital_signs()

        # 3. SAE criteria validation
        self._check_sae_criteria()

        # 4. Lab value deterioration trends
        self._check_lab_deterioration()

        # 5. Drug-AE temporal relationship
        self._check_drug_ae_relationship()

        # 6. Missing safety data
        self._check_missing_safety_data()

        # Filter by minimum severity
        min_sev = self.config.min_severity
        self._findings = [
            f for f in self._findings
            if self._severity_ge(f.severity, min_sev)
        ]

        logger.info("SafetyChecker: %d findings", len(self._findings))
        return self._findings

    # ──────────────────────────────────────────────────────────
    # Individual Check Implementations
    # ──────────────────────────────────────────────────────────

    def _check_lab_abnormalities(self) -> None:
        """Detect lab values outside normal/acceptable ranges."""
        labs = self.state.get_data(DataSource.LAB)
        if not labs:
            logger.debug("No lab data loaded, skipping lab abnormality check.")
            return

        # Build lookup by test_code
        rule_by_code: Dict[str, LabAbnormalityRule] = {}
        for rule in self._lab_rules:
            rule_by_code[rule.test_code.lower()] = rule

        for lab in labs:
            subject_id = lab.get("subject_id", "")
            test_code = lab.get("test_code", "").lower()
            test_value = self._parse_numeric(lab.get("test_value"))
            test_date = lab.get("test_date", "")

            if test_value is None:
                continue

            rule = rule_by_code.get(test_code)
            if not rule:
                continue  # No rule defined for this test code

            # Determine grade based on thresholds
            grade = self._classify_lab_grade(test_value, rule)
            if grade >= 3:  # Grade 3+ is clinically significant
                grade_severity = {
                    3: Severity.MEDIUM,
                    4: Severity.HIGH,
                    5: Severity.CRITICAL,
                }.get(grade, Severity.MEDIUM)

                direction = "above" if test_value > rule.normal_high else "below"
                self._findings.append(CoreGageFinding(
                    category=CheckCategory.SAFETY,
                    severity=grade_severity,
                    source="lab",
                    subject_id=subject_id,
                    field_name=test_code,
                    message=(
                        f"Lab '{rule.test_name}' value {test_value} "
                        f"is {direction} normal range — "
                        f"CTCAE Grade {grade}"
                    ),
                    details={
                        "test_value": test_value,
                        "grade": grade,
                        "normal_range": f"{rule.normal_low}-{rule.normal_high}",
                        "unit": rule.unit,
                        "test_date": test_date,
                    },
                    status=CheckStatus.FAILED,
                ))

    def _check_vital_signs(self) -> None:
        """Detect vital sign values outside acceptable ranges."""
        vitals = self.state.get_data(DataSource.VITAL)
        if not vitals:
            logger.debug("No vital sign data loaded, skipping vital sign check.")
            return

        # Build lookup by parameter
        rule_by_param: Dict[str, VitalSignRule] = {}
        for rule in self._vital_rules:
            rule_by_param[rule.parameter.lower()] = rule

        for vital in vitals:
            subject_id = vital.get("subject_id", "")
            parameter = vital.get("parameter", vital.get("vital_type", "")).lower()
            value = self._parse_numeric(vital.get("value"))
            vital_date = vital.get("vital_date", "")

            if value is None:
                continue

            rule = rule_by_param.get(parameter)
            if not rule:
                continue

            # Check critical range first
            if (rule.critical_low > 0 and value <= rule.critical_low) or \
               (rule.critical_high > 0 and value >= rule.critical_high):
                self._findings.append(CoreGageFinding(
                    category=CheckCategory.SAFETY,
                    severity=Severity.CRITICAL,
                    source="vital",
                    subject_id=subject_id,
                    field_name=parameter,
                    message=(
                        f"CRITICAL vital sign: {parameter} = {value} "
                        f"(critical range: "
                        f"{rule.critical_low if rule.critical_low > 0 else 'N/A'} - "
                        f"{rule.critical_high if rule.critical_high > 0 else 'N/A'})"
                    ),
                    details={"value": value, "parameter": parameter,
                             "vital_date": vital_date},
                    status=CheckStatus.FAILED,
                ))
            # Check alert range
            elif (rule.alert_low > 0 and value <= rule.alert_low) or \
                 (rule.alert_high > 0 and value >= rule.alert_high):
                self._findings.append(CoreGageFinding(
                    category=CheckCategory.SAFETY,
                    severity=Severity.HIGH,
                    source="vital",
                    subject_id=subject_id,
                    field_name=parameter,
                    message=(
                        f"Vital sign alert: {parameter} = {value} "
                        f"(alert range: {rule.alert_low}-{rule.alert_high})"
                    ),
                    details={"value": value, "parameter": parameter,
                             "vital_date": vital_date},
                    status=CheckStatus.FAILED,
                ))

    def _check_sae_criteria(self) -> None:
        """Validate SAE records against SAE criteria."""
        saes = self.state.get_data(DataSource.AE_SAE)
        if not saes:
            logger.debug("No SAE data loaded, skipping SAE criteria check.")
            return

        for sae in saes:
            subject_id = sae.get("subject_id", "")
            ae_term = sae.get("ae_term", sae.get("term", ""))

            # Check each SAE criterion
            for criterion in self._sae_criteria:
                field_name = criterion.name + "_flag"
                is_sae = sae.get(field_name, sae.get(criterion.name, False))

                if is_sae:
                    self._findings.append(CoreGageFinding(
                        category=CheckCategory.SAFETY,
                        severity=criterion.severity,
                        source="ae_sae",
                        subject_id=subject_id,
                        message=(
                            f"SAE '{ae_term}' meets criterion: "
                            f"'{criterion.name}' — {criterion.description}"
                        ),
                        details={"criterion": criterion.name,
                                 "description": criterion.description},
                        status=CheckStatus.FAILED,
                    ))

    def _check_lab_deterioration(self) -> None:
        """Detect rapid lab value deterioration between consecutive measurements."""
        labs = self.state.get_data(DataSource.LAB)
        if not labs:
            return

        # Group by subject and test
        grouped: Dict[Tuple[str, str], List[Dict]] = {}
        for lab in labs:
            subject_id = lab.get("subject_id", "")
            test_code = lab.get("test_code", "")
            key = (subject_id, test_code)
            grouped.setdefault(key, []).append(lab)

        for (subject_id, test_code), records in grouped.items():
            # Sort by date
            records.sort(key=lambda r: r.get("test_date", ""))

            for i in range(1, len(records)):
                prev_val = self._parse_numeric(records[i - 1].get("test_value"))
                curr_val = self._parse_numeric(records[i].get("test_value"))

                if prev_val is None or curr_val is None:
                    continue

                # Check for rapid deterioration (value worsening significantly)
                # For most labs, higher = worse for things like creatinine, bilirubin
                # Lower = worse for things like hemoglobin, platelets
                change = curr_val - prev_val
                change_pct = abs(change / prev_val) * 100 if prev_val != 0 else 0

                if change_pct > 50:  # >50% change is concerning
                    direction = "worsened" if change > 0 else "improved"
                    self._findings.append(CoreGageFinding(
                        category=CheckCategory.SAFETY,
                        severity=Severity.MEDIUM,
                        source="lab",
                        subject_id=subject_id,
                        field_name=test_code,
                        message=(
                            f"Lab '{test_code}' rapidly {direction}: "
                            f"{prev_val} → {curr_val} "
                            f"({change_pct:.1f}% change) "
                            f"between {records[i-1].get('test_date')} "
                            f"and {records[i].get('test_date')}"
                        ),
                        details={
                            "prev_value": prev_val,
                            "curr_value": curr_val,
                            "change_pct": round(change_pct, 2),
                        },
                        status=CheckStatus.FAILED,
                    ))

    def _check_drug_ae_relationship(self) -> None:
        """Check temporal relationship between drug exposure and AEs."""
        meds = self.state.get_data(DataSource.MED)
        aes = self.state.get_data(DataSource.AE)

        if not meds or not aes:
            logger.debug("Missing medication or AE data, skipping drug-AE check.")
            return

        # Build medication exposure windows per subject
        med_windows: Dict[str, List[Tuple[datetime, datetime]]] = {}
        for med in meds:
            subject_id = med.get("subject_id", "")
            start = self._parse_date(med.get("start_date"))
            stop = self._parse_date(med.get("stop_date"))
            if start:
                end = stop if stop else start + timedelta(days=365)
                med_windows.setdefault(subject_id, []).append((start, end))

        # Check each AE for temporal overlap with medication
        for ae in aes:
            subject_id = ae.get("subject_id", "")
            ae_term = ae.get("ae_term", ae.get("term", ""))
            onset = self._parse_date(ae.get("onset_date"))

            if not onset:
                continue

            windows = med_windows.get(subject_id, [])
            if not windows:
                continue

            # Check if AE onset falls within any medication window
            for start, end in windows:
                if start <= onset <= end:
                    # AE occurred during drug exposure — flag for review
                    self._findings.append(CoreGageFinding(
                        category=CheckCategory.SAFETY,
                        severity=Severity.LOW,
                        source="ae",
                        subject_id=subject_id,
                        message=(
                            f"AE '{ae_term}' onset ({onset.date()}) "
                            f"occurred during medication exposure "
                            f"({start.date()} to {end.date()})"
                        ),
                        details={"ae_term": ae_term,
                                 "onset_date": onset.date().isoformat()},
                        status=CheckStatus.PASSED,
                    ))
                    break

    def _check_missing_safety_data(self) -> None:
        """Flag subjects with missing critical safety data."""
        # Critical safety tests that should be collected
        critical_tests = self.config.safety_lab_grades  # configurable

        subjects_with_labs: Dict[str, set] = {}
        labs = self.state.get_data(DataSource.LAB)
        if labs:
            for lab in labs:
                subject_id = lab.get("subject_id", "")
                test_code = lab.get("test_code", "")
                subjects_with_labs.setdefault(subject_id, set()).add(test_code)

        # Check each subject
        all_subjects = set(subjects_with_labs.keys())
        # Also get subjects from AE data
        aes = self.state.get_data(DataSource.AE)
        if aes:
            for ae in aes:
                all_subjects.add(ae.get("subject_id", ""))

        for subject_id in all_subjects:
            collected_tests = subjects_with_labs.get(subject_id, set())
            missing_critical = [
                t for t in critical_tests
                if t not in collected_tests
            ]
            if missing_critical:
                self._findings.append(CoreGageFinding(
                    category=CheckCategory.SAFETY,
                    severity=Severity.MEDIUM,
                    source="lab",
                    subject_id=subject_id,
                    message=(
                        f"Subject {subject_id} missing critical safety labs: "
                        f"{', '.join(missing_critical)}"
                    ),
                    details={"missing_tests": missing_critical},
                    status=CheckStatus.FAILED,
                ))

    # ──────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────

    def _classify_lab_grade(self, value: float,
                            rule: LabAbnormalityRule) -> int:
        """
        Classify lab value into CTCAE-like grade (1-5).

        Thresholds: (low_critical, low_severe, low_moderate,
                     high_moderate, high_severe, high_critical)
        """
        lo_crit, lo_sev, lo_mod, hi_mod, hi_sev, hi_crit = rule.thresholds

        if value <= lo_crit or value >= hi_crit:
            return 5
        elif value <= lo_sev or value >= hi_sev:
            return 4
        elif value <= lo_mod or value >= hi_mod:
            return 3
        elif value < rule.normal_low or value > rule.normal_high:
            return 2
        return 1

    @staticmethod
    def _parse_date(value: Any) -> Optional[datetime]:
        """Parse a date string into datetime."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(value.strip(), fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def _parse_numeric(value: Any) -> Optional[float]:
        """Parse a numeric value from string."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).replace(",", "").strip())
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _severity_ge(a: Severity, b: Severity) -> bool:
        """Check if severity a >= severity b."""
        order = {Severity.INFO: 0, Severity.LOW: 1, Severity.MEDIUM: 2,
                 Severity.HIGH: 3, Severity.CRITICAL: 4}
        return order.get(a, 0) >= order.get(b, 0)
