from OnePy.event_engine import EventEngine


def test_event_engine():
    test_engine = EventEngine()

    assert test_engine.is_empty() is True

    test_engine.put(1)

    assert test_engine.is_empty() is False

    obj = test_engine.get()

    assert obj == 1
    assert test_engine.is_empty() is True


if __name__ == "__main__":
    test_event_engine()
