# geological-time

Converts between human-readable geological dates (`2.5 Ma`, `4.54 Ga`) and scientific notation (`2.5e6 years`). Standard library only.

## Usage

```python
from geological_time import GeologicalTime, format_scientific, parse_scientific

# Human -> scientific
gt = GeologicalTime.from_human("4.54 Ga")
print(gt.to_scientific())   # 4.54e9 years

# Scientific -> human
gt2 = GeologicalTime.from_scientific("2.5e6 years")
print(gt2.to_human())       # 2.5 Ma

# Convenience functions
print(format_scientific(2500000))          # 2.5e6 years
print(parse_scientific("2.5e6 years"))      # Decimal('2500000')
```

## Why

Geological papers mix two notations for the same quantity. `2.5 Ma` reads well in prose; `2.5e6` is what code wants. Doing the conversion by hand (`2.5 * 1e6`) invites floating-point drift and unit confusion (is `M` mega or milli?). This library resolves both: the unit letter is fixed to SI annum conventions (`ka`, `Ma`, `Ga`), and values are held as `Decimal` so `4.54e9` survives a round trip unchanged.

The trade-off: there is no sub-ka unit. Anything under 1000 years renders as a fractional `ka` (e.g. `0.5 ka`). If you need year-level precision for Holocene events, use `to_scientific()` instead.

## Edge cases

- Zero is valid and means "now" in both notations.
- Negative values are accepted in scientific notation (a future date, nonsensical geologically but mathematically consistent).
- Unknown units like `Ta` raise `ValueError`.
- The word "ago" is accepted and ignored — it carries no information the magnitude doesn't.

## Exports

- `GeologicalTime` — the main class. Methods: `from_human`, `from_scientific`, `to_human`, `to_scientific`. Property: `years` (Decimal).
- `format_scientific(years)` — shortcut for `GeologicalTime(years).to_scientific()`.
- `parse_scientific(text)` — shortcut returning the Decimal year count.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

