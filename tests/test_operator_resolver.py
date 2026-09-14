from newvenue.operator_resolver import Evidence, resolve_operator


def test_independent_sources_can_resolve_operator():
    evidence = [
        Evidence("Example Hospitality", "source-one", "planning_application", address="10 Test St Sydney", venue_name="Example Bar", evidence_text="Example Hospitality proposes Example Bar", named_person="Alex Example"),
        Evidence("Example Hospitality", "source-two", "official_operator", address="10 Test St Sydney", venue_name="Example Bar", evidence_text="Example Hospitality Example Bar"),
    ]
    result = resolve_operator(evidence, address="10 Test St Sydney", venue_name="Example Bar")
    assert result.operator_name == "Example Hospitality"
    assert result.confidence in {"confirmed", "strong"}
    assert result.named_person == "Alex Example"


def test_tenancy_conflict_prevents_easy_false_match():
    evidence = [Evidence("Wrong Operator", "source-one", "directory", address="10 Test St Sydney", tenancy="Shop 2", venue_name="Example Bar")]
    result = resolve_operator(evidence, address="10 Test St Sydney", tenancy="Shop 1", venue_name="Example Bar")
    assert result.operator_name is None
    assert result.confidence == "unknown"


def test_weak_search_result_stays_unknown():
    evidence = [Evidence("Possible Operator", "source-one", "search_result", address="10 Test St Sydney")]
    result = resolve_operator(evidence, address="10 Test St Sydney")
    assert result.operator_name is None
    assert result.confidence == "unknown"


def test_competing_operators_need_margin():
    evidence = [
        Evidence("Operator One", "source-one", "directory", address="10 Test St Sydney", venue_name="Example Bar"),
        Evidence("Operator Two", "source-two", "directory", address="10 Test St Sydney", venue_name="Example Bar"),
    ]
    result = resolve_operator(evidence, address="10 Test St Sydney", venue_name="Example Bar")
    assert result.operator_name is None
    assert result.confidence == "unknown"
