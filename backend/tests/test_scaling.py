from app.utils import scale_quantity


class TestScaleQuantity:
    def test_returns_none_for_none_input(self):
        assert scale_quantity(None, 4, 8) is None

    def test_returns_same_for_equal_servings(self):
        assert scale_quantity("2 cups", 4, 4) == "2 cups"

    def test_returns_empty_string_unchanged(self):
        assert scale_quantity("", 2, 4) == ""

    def test_scales_integer(self):
        assert scale_quantity("2", 4, 8) == "4"

    def test_scales_decimal(self):
        result = scale_quantity("1.5", 2, 4)
        assert result == "3"

    def test_scales_fraction_individually(self):
        result = scale_quantity("1/2", 4, 8)
        assert result == "1"

    def test_scales_fraction_parts_different_ratio(self):
        result = scale_quantity("1/4", 2, 4)
        assert result == "0.5"

    def test_preserves_text_around_number(self):
        result = scale_quantity("2 cups", 4, 8)
        assert result == "4 cups"

    def test_no_numbers_returns_original(self):
        assert scale_quantity("pinch", 2, 4) == "pinch"
        assert scale_quantity("to taste", 2, 4) == "to taste"

    def test_scales_down(self):
        result = scale_quantity("4", 8, 4)
        assert result == "2"

    def test_scales_with_unit(self):
        result = scale_quantity("100 grams", 2, 4)
        assert result == "200 grams"
