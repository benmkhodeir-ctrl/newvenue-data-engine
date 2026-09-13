from newvenue.classify import classify_text


def test_new_restaurant_is_candidate():
    result = classify_text("New on-premises licence", "restaurant")
    assert result.opportunity_class == "candidate_new_venue"
    assert result.score >= 60


def test_transfer_is_low_value():
    result = classify_text("Transfer of licence", "existing hotel")
    assert result.opportunity_class == "existing_or_low_value"
    assert result.score < 50
