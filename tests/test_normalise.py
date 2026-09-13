from newvenue.normalise import normalise_address, parse_date


def test_normalise_address_common_variants():
    assert normalise_address("10 Example Street, Sydney NSW 2000") == "10 EXAMPLE ST SYDNEY"
    assert normalise_address("10 Example St Sydney 2000") == "10 EXAMPLE ST SYDNEY"


def test_parse_date():
    assert parse_date("13/09/2026") == "2026-09-13"
