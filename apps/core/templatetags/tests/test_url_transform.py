from ..url_transform import url_transform


def test_basic_transform(request_factory):
    context = {
        'request': request_factory.get("/accounts/")
    }
    transformation = {
        'page': 1
    }

    transformed = url_transform(context, **transformation)

    assert transformed == 'page=1'


def test_replace_transform(request_factory):
    context = {
        'request': request_factory.get("/accounts/?page=1")
    }
    transformation = {
        'page': 2
    }

    transformed = url_transform(context, **transformation)

    assert transformed == 'page=2'


def test_merge_transform(request_factory):
    context = {
        'request': request_factory.get("/accounts/?page=2")
    }
    transformation = {
        'view': 'list'
    }

    transformed = url_transform(context, **transformation)

    assert transformed == 'page=2&view=list'


def test_clear_transform(request_factory):
    context = {
        'request': request_factory.get("/accounts/?page=2&view=list")
    }
    transformation = {
        'view': None
    }

    transformed = url_transform(context, **transformation)

    assert transformed == 'page=2'
