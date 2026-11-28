from lifekit.cards.types import load_card_types, card_type_names, CARD_TYPES


def test_loads_five_types():
    data = load_card_types()
    assert set(data.keys()) == set(CARD_TYPES)


def test_each_has_fields():
    data = load_card_types()
    for t in CARD_TYPES:
        assert "purpose" in data[t]
        assert "comment_hint" in data[t]
        assert "coach_instruction" in data[t]


def test_names_tuple():
    assert card_type_names() == CARD_TYPES