"""Phone number intelligence module — dependency: phonenumbers."""

from dataclasses import dataclass, field
from typing import Optional

import phonenumbers
from phonenumbers import geocoder, carrier, timezone as pn_timezone


@dataclass
class PhoneIntel:
    raw: str
    valid: bool = False
    possible: bool = False
    e164: Optional[str] = None
    international: Optional[str] = None
    national: Optional[str] = None
    country_code: Optional[int] = None
    region_code: Optional[str] = None
    location: Optional[str] = None
    carrier_name: Optional[str] = None
    line_type: Optional[str] = None
    timezones: list = field(default_factory=list)
    error: Optional[str] = None


_NUMBER_TYPES = {
    phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed line",
    phonenumbers.PhoneNumberType.MOBILE: "Mobile",
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed line or mobile",
    phonenumbers.PhoneNumberType.TOLL_FREE: "Toll free",
    phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium rate",
    phonenumbers.PhoneNumberType.SHARED_COST: "Shared cost",
    phonenumbers.PhoneNumberType.VOIP: "VoIP",
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal number",
    phonenumbers.PhoneNumberType.PAGER: "Pager",
    phonenumbers.PhoneNumberType.UAN: "UAN",
    phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
    phonenumbers.PhoneNumberType.UNKNOWN: "Unknown",
}


def analyze_phone(raw_number: str, default_region: str = "US") -> PhoneIntel:
    """Analyze a phone number and return a fully populated PhoneIntel object.

    Args:
        raw_number: phone number, with or without a country code (+1...).
        default_region: two-letter ISO region used when the number doesn't start with '+'.
    """
    result = PhoneIntel(raw=raw_number)
    try:
        parsed = phonenumbers.parse(raw_number, default_region)
    except phonenumbers.NumberParseException as exc:
        result.error = str(exc)
        return result

    result.valid = phonenumbers.is_valid_number(parsed)
    result.possible = phonenumbers.is_possible_number(parsed)
    result.e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    result.international = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
    )
    result.national = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.NATIONAL
    )
    result.country_code = parsed.country_code
    result.region_code = phonenumbers.region_code_for_number(parsed)
    result.location = geocoder.description_for_number(parsed, "en") or None
    result.carrier_name = carrier.name_for_number(parsed, "en") or None
    result.line_type = _NUMBER_TYPES.get(
        phonenumbers.number_type(parsed), "Unknown"
    )
    result.timezones = list(pn_timezone.time_zones_for_number(parsed))
    return result
