from decimal import Decimal, InvalidOperation
import re


_UNIT_TO_EXPONENT = {
    "k": 3,
    "M": 6,
    "G": 9,
}

_HUMAN_RE = re.compile(
    r"""
    ^
    \s*
    (?P<mantissa>[+-]?(?:\d+\.?\d*|\.\d+))
    \s*
    (?P<unit>k|M|G)
    a
    (?:\s*m\.?y\.?)?     # optional "m.y." or "my"
    (?:\s*ago)?           # optional "ago"
    \s*
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

_SCI_RE = re.compile(
    r"""
    ^
    \s*
    (?P<mantissa>[+-]?(?:\d+\.?\d*|\.\d+))
    [eE](?P<exponent>[+-]?\d+)
    (?:\s*(?:years?|yr|yrs?))?   # optional unit word
    \s*
    $
    """,
    re.VERBOSE,
)


class GeologicalTime:
    """A geological instant, stored as years before present (Decimal)."""

    __slots__ = ("_years",)

    def __init__(self, years):
        if isinstance(years, float):
            years = str(years)
        try:
            self._years = Decimal(years)
        except (InvalidOperation, TypeError) as exc:
            raise ValueError(f"not a valid year count: {years!r}") from exc

    @property
    def years(self) -> Decimal:
        return self._years

    @classmethod
    def from_human(cls, text: str) -> "GeologicalTime":
        match = _HUMAN_RE.match(text)
        if match is None:
            raise ValueError(f"not a human-readable geological date: {text!r}")
        mantissa = Decimal(match.group("mantissa"))
        unit_letter = match.group("unit")
        if unit_letter.upper() == "K":
            unit_letter = "k"
        elif unit_letter.upper() == "M":
            unit_letter = "M"
        elif unit_letter.upper() == "G":
            unit_letter = "G"
        exponent = _UNIT_TO_EXPONENT.get(unit_letter)
        if exponent is None:
            raise ValueError(f"unknown unit in geological date: {text!r}")
        years = mantissa * (Decimal(10) ** exponent)
        return cls(years)

    @classmethod
    def from_scientific(cls, text: str) -> "GeologicalTime":
        match = _SCI_RE.match(text)
        if match is None:
            raise ValueError(f"not scientific notation: {text!r}")
        mantissa = Decimal(match.group("mantissa"))
        exponent = Decimal(match.group("exponent"))
        years = mantissa * (Decimal(10) ** exponent)
        return cls(years)

    def to_human(self, unit: str = "auto") -> str:
        if unit == "auto":
            abs_years = abs(self._years)
            if abs_years >= Decimal(10) ** 9:
                chosen = "G"
            elif abs_years >= Decimal(10) ** 6:
                chosen = "M"
            elif abs_years >= Decimal(10) ** 3:
                chosen = "k"
            else:
                chosen = "k"
        else:
            if unit not in _UNIT_TO_EXPONENT:
                raise ValueError(
                    f"unit must be 'auto', 'k', 'M', or 'G'; got {unit!r}"
                )
            chosen = unit
        exponent = _UNIT_TO_EXPONENT[chosen]
        mantissa = self._years / (Decimal(10) ** exponent)
        return f"{_strip_decimal(mantissa)} {chosen}a"

    def to_scientific(self) -> str:
        if self._years == 0:
            return "0e0 years"
        sign = "-" if self._years < 0 else ""
        abs_val = abs(self._years)
        exponent = abs_val.ln() / Decimal(10).ln()
        exponent = exponent.to_integral_value(rounding="ROUND_FLOOR")
        mantissa = abs_val / (Decimal(10) ** exponent)
        text = f"{_strip_decimal(mantissa)}e{exponent}"
        return f"{sign}{text} years"

    def __eq__(self, other) -> bool:
        if not isinstance(other, GeologicalTime):
            return NotImplemented
        return self._years == other._years

    def __hash__(self) -> int:
        return hash(self._years)

    def __repr__(self) -> str:
        return f"GeologicalTime(years={self._years})"


def format_scientific(years) -> str:
    return GeologicalTime(years).to_scientific()


def parse_scientific(text: str) -> Decimal:
    return GeologicalTime.from_scientific(text).years


def _strip_decimal(value: Decimal) -> str:
    text = str(value)
    if "." in text and not text.endswith("."):
        if text.endswith("0"):
            stripped = text.rstrip("0")
            if stripped.endswith("."):
                return stripped[:-1]
            return stripped
    return text
