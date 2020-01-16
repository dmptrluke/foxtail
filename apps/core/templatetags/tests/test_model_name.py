from ..model_name import get_model_name


class DummyModel:
    pass


dummy_instance = DummyModel()


def test_model_name():
    assert get_model_name(dummy_instance) == "DummyModel"
    assert get_model_name(dummy_instance) != "IncorrectName"
