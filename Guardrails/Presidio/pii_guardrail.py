"""
Production PII Guardrail
========================

Reusable PII detection and sanitization component built on Microsoft Presidio.

Design goals:
- Keep Presidio implementation details inside this module.
- Expose a stable application-facing interface.
- Return structured results instead of raw Presidio objects.
- Separate detection from policy decisions.
- Keep configuration explicit and testable.

This file intentionally contains the complete component so it can later
be split into multiple modules without changing the public interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from presidio_anonymizer import AnonymizerEngine

from types import MappingProxyType

from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
)
from presidio_anonymizer.entities import OperatorConfig


# ============================================================
# Result Models
# ============================================================


@dataclass(frozen=True, slots=True)
class DetectedEntity:
    """
    Application-level representation of a detected entity.

    We intentionally do not expose Presidio's RecognizerResult directly.
    """

    entity_type: str
    start: int
    end: int
    score: float
    text: str


@dataclass(frozen=True, slots=True)
class GuardrailResult:
    """
    Stable result returned by the PII guardrail.
    """

    allowed: bool
    action: str
    original_text: str
    text: str
    entities: tuple[DetectedEntity, ...]
    metadata: dict[str, Any]


# ============================================================
# Detection Policy
# ============================================================

# Minimum confidence required for an entity to be accepted by
# our application-level guardrail.
#
# These are intentionally explicit rather than relying on
# Presidio's internal defaults.
#
# IMPORTANT:
# These values are policy starting points, not universal truths.
# They must eventually be validated against our application's
# evaluation dataset.
DEFAULT_ENTITY_THRESHOLDS: dict[str, float] = {
    "PERSON": 0.85,
    "EMAIL_ADDRESS": 0.90,
    "PHONE_NUMBER": 0.70,
    "CREDIT_CARD": 0.90,
    "IBAN_CODE": 0.90,
    "IP_ADDRESS": 0.90,
    "LOCATION": 0.85,
    "DATE_TIME": 0.85,
    "URL": 0.90,
}

# Prevent accidental mutation of the global policy at runtime.
ENTITY_THRESHOLDS = MappingProxyType(DEFAULT_ENTITY_THRESHOLDS)



# ============================================================
# Custom Recognizers
# ============================================================

EMPLOYEE_ID_PATTERN = Pattern(
    name="employee_id_pattern",
    regex=r"\b\d{6}\b",
    score=0.05, 
    # regex=r"\bEMP-\d{6}\b", this can be used if known 
    # score=0.95,
)

"""
here initially setting the score low, then it tries to undestand the context by 

                "employee",
                "employee id",
                "employee number",
                "staff id",
                "staff number",

and the score increase based on what the input contains
"""


class EmployeeIdRecognizer(PatternRecognizer):
    """
    Recognizes employee IDs based on a numeric pattern plus context.

    Example:
        Employee ID: 123456
        Employee number: 987654
    """

    def __init__(self) -> None:
        super().__init__(
            supported_entity="EMPLOYEE_ID",
            patterns=[EMPLOYEE_ID_PATTERN],
            context=[
                "employee",
                "employee id",
                "employee number",
                "staff id",
                "staff number",
            ],
        )



# ============================================================
# ANONYMIZATION POLICY
# ============================================================

ANONYMIZATION_OPERATORS = {
    "PERSON": OperatorConfig(
        "replace",
        {"new_value": "[PERSON]"},
    ),
    "EMAIL_ADDRESS": OperatorConfig(
        "replace",
        {"new_value": "[EMAIL]"},
    ),
    "PHONE_NUMBER": OperatorConfig(
        "mask",
        {
            "chars_to_mask": 13,
            "masking_char": "*",
            "from_end": True,
        },
    ),
    "CREDIT_CARD": OperatorConfig(
        "redact",
        {},
    ),
    "EMPLOYEE_ID": OperatorConfig(
        "replace",
        {"new_value": "[EMPLOYEE_ID]"},
    ),
    "DEFAULT": OperatorConfig(
        "replace",
        {"new_value": "[REDACTED]"},
    ),
}

# ============================================================
# PII Guardrail
# ============================================================


class PIIGuardrail:
    """
    Production-facing PII guardrail.

    Presidio-specific implementation details remain inside this class.
    """

    def __init__(self) -> None:
        self._analyzer = AnalyzerEngine()
        self._anonymizer = AnonymizerEngine()

        self._register_custom_recognizers()

    def _register_custom_recognizers(self) -> None:
        """
        Register application-specific Presidio recognizers.
        """

        self._analyzer.registry.add_recognizer(
            EmployeeIdRecognizer()
        )

    def detect(
        self,
        text: str,
        *,
        language: str = "en",
    ) -> tuple[DetectedEntity, ...]:
        """
        Detect PII entities and apply application-level confidence policy.

        Presidio performs the detection.
        This method applies our production acceptance threshold.
        """

        if not text:
            return ()

        results = self._analyzer.analyze(
            text=text,
            language=language,
        )

        detected_entities: list[DetectedEntity] = []

        for result in results:
            threshold = ENTITY_THRESHOLDS.get(
                result.entity_type,
                0.90, # if the above entity type not found , using 0.90 as threshold
            )

            # if result.score < threshold:
                # continue

            detected_entities.append(
                DetectedEntity(
                    entity_type=result.entity_type,
                    start=result.start,
                    end=result.end,
                    score=result.score,
                    text=text[result.start : result.end],
                )
            )

        return tuple(detected_entities)

    def anonymize(
        self,
        text: str,
        *,
        language: str = "en",
    ) -> str:
        if not text:
            return ""

        results = self._analyzer.analyze(
            text=text,
            language=language,
        )

        return self._anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=ANONYMIZATION_OPERATORS,
        ).text


if __name__ == "__main__":
    guardrail = PIIGuardrail()

    text = (
    "Contact John Smith at john.smith@example.com or 9343774053 "
    "or 4111 1111 1111 1111."
    )

    # results = guardrail.detect(text)

    # for entity in results:
    #     print(
    #         f"{entity.entity_type}: "
    #         f"{entity.text!r} "
    #         f"(score={entity.score:.2f})"
    #     )

    print(guardrail.anonymize(text))