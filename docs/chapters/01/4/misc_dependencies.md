---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.13.7
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Misc Dependencies

## `Token`

The following object represents token values in the system. Supported operations include **add, subtract, and set** which are anologous to **credit, debit, and overwrite** in traditional book-keeping parlance.

```python
class Token(object):
    """
    Represents a token balance with common math operations to increase, decrease, and set the balance.
    """

    def __init__(self, balance: Decimal = Decimal('0'), qdecimals: Decimal = DEFAULT_QDECIMALS):
        self.balance = balance
        self.qdecimals = qdecimals

    def add(self, value: Decimal):
        self.balance += self.validate(value)

    def subtract(self, value: Decimal):
        self.balance -= self.validate(value)

    def set(self, value: Decimal):
        self.balance = self.validate(value)

    def validate(self, value) -> Decimal:
        return Decimal(str(value)).quantize(self.qdecimals)
```
