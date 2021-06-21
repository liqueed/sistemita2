"""Módulo de validaciones."""

from django.core.exceptions import ValidationError

from sistemita.core.utils.strings import MESSAGE_ONLY_NUMBERS


def validate_is_number(value):
    """Returns is value is a digit.

    Args:
        value (int|string): Value to validate
    Raises:
        ValidationError: If value is not a digit
    """
    value = str(value)
    if not value.isdigit():
        raise ValidationError(MESSAGE_ONLY_NUMBERS)
