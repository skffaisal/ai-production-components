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
from presidio_anonymizer.operators import Operator, OperatorType


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
# CUSTOM ANONYMIZATION OPERATORS
# ============================================================

class EmailTagOperator(Operator):
    """
    Example custom anonymization operator.

    Transforms:
        john@example.com

    Into:
        [email:john@example.com]
    """

    def operate(
        self,
        text: str,
        params: dict | None = None,
    ) -> str:
        return f"[email:{text}]"

    def validate(
        self,
        params: dict | None = None,
    ) -> None:
        pass

    def operator_name(self) -> str:
        return "email_tag"

    def operator_type(self) -> OperatorType:
        return OperatorType.Anonymize

# ============================================================
# ANONYMIZATION POLICY
# ============================================================

ANONYMIZATION_OPERATORS = {
    # --------------------------------------------------------
    # REPLACE
    # --------------------------------------------------------
    "PERSON": OperatorConfig(
        "replace",
        {
            "new_value": "[PERSON]",
        },
    ),

    "EMAIL_ADDRESS": OperatorConfig(
        "replace",
        {
            "new_value": "[EMAIL]",
        },
    ),

    "EMPLOYEE_ID": OperatorConfig(
        "replace",
        {
            "new_value": "[EMPLOYEE_ID]",
        },
    ),

    # --------------------------------------------------------
    # MASK
    # --------------------------------------------------------
    "PHONE_NUMBER": OperatorConfig(
        "mask",
        {
            "chars_to_mask": 7,
            "masking_char": "*",
            "from_end": True,
        },
    ),

    # --------------------------------------------------------
    # REDACT
    # --------------------------------------------------------
    "CREDIT_CARD": OperatorConfig(
        "redact",
        {},
    ),

    # --------------------------------------------------------
    # HASH
    # --------------------------------------------------------
    "IBAN_CODE": OperatorConfig(
        "hash",
        {
            "hash_type": "sha256",
        },
    ),

    # --------------------------------------------------------
    # ENCRYPT
    # --------------------------------------------------------
    #
    # Encryption requires appropriate encryption parameters
    # and key-management strategy. Configure this only when
    # your application actually needs reversible protection.
    #
    # Keep the section here as a production reference rather
    # than enabling it blindly.
    #
    # "PERSON": OperatorConfig(
    #     "encrypt",
    #     {
    #         # encryption parameters depend on the
    #         # Presidio encryption operator configuration
    #     },
    # ),

    # --------------------------------------------------------
    # CUSTOM OPERATOR
    # --------------------------------------------------------
    #
    # Enable this when the application requires a custom
    # transformation.
    #
    "EMAIL_ADDRESS": OperatorConfig(
        "email_tag",
        {},
    ),

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------
    "DEFAULT": OperatorConfig(
        "replace",
        {
            "new_value": "[REDACTED]",
        },
    ),
}


# ============================================================
# GUARDRAIL POLICY
# ============================================================

POLICY_ALLOW = "ALLOW"
POLICY_REDACT = "REDACT"
POLICY_MASK = "MASK"
POLICY_BLOCK = "BLOCK"


ENTITY_POLICIES = {
    "PERSON": POLICY_REDACT,
    "EMAIL_ADDRESS": POLICY_REDACT,
    "PHONE_NUMBER": POLICY_MASK,
    "CREDIT_CARD": POLICY_BLOCK,
    "IBAN_CODE": POLICY_BLOCK,
    "EMPLOYEE_ID": POLICY_REDACT,
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
        self._register_custom_anonymizers()

    def _register_custom_recognizers(self) -> None:
        """
        Register application-specific Presidio recognizers.
        """

        self._analyzer.registry.add_recognizer(
            EmployeeIdRecognizer()
        )

    def _register_custom_anonymizers(self) -> None:

        self._anonymizer.add_anonymizer(

            EmailTagOperator
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

            if result.score < threshold:
                continue

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
    
    # ============================================================
    # POLICY EVALUATION
    # ============================================================

    def evaluate_policy(
        self,
        entities: tuple[DetectedEntity, ...],
    ) -> str:
        if not entities:
            return POLICY_ALLOW

        decisions = {
            ENTITY_POLICIES.get(
                entity.entity_type,
                POLICY_ALLOW,
            )
            for entity in entities
        }

        if POLICY_BLOCK in decisions:
            return POLICY_BLOCK

        if POLICY_REDACT in decisions:
            return POLICY_REDACT

        if POLICY_MASK in decisions:
            return POLICY_MASK

        return POLICY_ALLOW

    # ============================================================
# GUARDRAIL PROCESSING
# ============================================================

    def process(
        self,
        text: str,
        *,
        language: str = "en",
    ) -> GuardrailResult:
        if not text:
            return GuardrailResult(
            allowed=True,
            action=POLICY_ALLOW,
            original_text=text,
            text=text,
            entities=(),
            metadata={},
            )

        entities = self.detect(
            text,
            language=language,
        )

        action = self.evaluate_policy(entities)

    # --------------------------------------------------------
    # BLOCK
    # --------------------------------------------------------
        if action == POLICY_BLOCK:
            return GuardrailResult(
            allowed=False,
            action=POLICY_BLOCK,
            original_text=text,
            text="",
            entities=entities,
            metadata={
                "reason": "blocked_entity_detected",
            },
        )

    # --------------------------------------------------------
    # ALLOW
    # --------------------------------------------------------
        if action == POLICY_ALLOW:
            return GuardrailResult(
            allowed=True,
            action=POLICY_ALLOW,
            original_text=text,
            text=text,
            entities=entities,
            metadata={},
        )

    # --------------------------------------------------------
    # REDACT / MASK
    # --------------------------------------------------------
        sanitized_text = self.anonymize(
            text,
            language=language,
        )

        return GuardrailResult(
        allowed=True,
        action=action,
        original_text=text,
        text=sanitized_text,
        entities=entities,
        metadata={
            "entities_sanitized": len(entities),
        },
    )


if __name__ == "__main__":
    guardrail = PIIGuardrail()

    text = """
Employee ID: EMP-123456
Name: John Smith
Email: john.smith@example.com
Phone: +1 415-555-0132
Credit Card: 4111 1111 1111 1111
IBAN: GB82WEST12345698765432
Some unknown sensitive value: SECRET-ABC-999
"""

    # results = guardrail.detect(text)

    # for entity in results:
    #     print(
    #         f"{entity.entity_type}: "
    #         f"{entity.text!r} "
    #         f"(score={entity.score:.2f})"
    #     )

    # print(guardrail.anonymize(text))
#     entities = guardrail.detect(
#     "Hello, how are you?"
# )

#     decision = guardrail.evaluate_policy(entities)

#     print(decision)

    # result = guardrail.process(
    # "What is the capital of India?"
    # )

    # print(result)
    print(
    guardrail.process(
        "My name is John Smith."
    )
)

    print(
    guardrail.process(
        "Call me at +1 415-555-0132."
    )
)

    print(
    guardrail.process(
        "My card is 4111 1111 1111 1111."
    )
)