from ..model_name import get_model_name


class _DummyModel:
    pass


class TestGetModelName:
    # returns the class name of the given object
    def test_returns_class_name(self):
        assert get_model_name(_DummyModel()) == '_DummyModel'
