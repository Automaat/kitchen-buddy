import re
from fractions import Fraction


def scale_quantity(quantity: str | None, original_servings: int, target_servings: int) -> str | None:
    if not quantity or original_servings == target_servings:
        return quantity

    scale_factor = Fraction(target_servings, original_servings)

    pattern = r"(\d+\.?\d*|\d+/\d+)"
    matches = re.findall(pattern, quantity)

    if not matches:
        return quantity

    result = quantity
    for match in matches:
        if "/" in match:
            original_value = Fraction(match)
        else:
            original_value = Fraction(match).limit_denominator()

        scaled_value = original_value * scale_factor

        if scaled_value.denominator == 1:
            scaled_str = str(scaled_value.numerator)
        else:
            scaled_float = float(scaled_value)
            if scaled_float == int(scaled_float):
                scaled_str = str(int(scaled_float))
            else:
                scaled_str = f"{scaled_float:.2f}".rstrip("0").rstrip(".")

        result = result.replace(match, scaled_str, 1)

    return result
