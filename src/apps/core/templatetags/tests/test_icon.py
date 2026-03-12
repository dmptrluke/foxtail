from unittest.mock import patch

from django.test import RequestFactory

from ..icon import icon_tag


class TestIconTag:
    def _make_context(self, request_factory):
        return {'request': request_factory.get('/')}

    # icon ID is slugified into the component name
    @patch('apps.core.templatetags.icon.render_component', return_value='<svg/>')
    def test_builds_component_name(self, mock_render, request_factory: RequestFactory):
        ctx = self._make_context(request_factory)
        icon_tag(ctx, 'Arrow Right')
        mock_render.assert_called_once()
        assert mock_render.call_args[0][1] == 'icons.arrow-right'

    # colored=True adds the colored prefix to the component name
    @patch('apps.core.templatetags.icon.render_component', return_value='<svg/>')
    def test_colored_prefix(self, mock_render, request_factory: RequestFactory):
        ctx = self._make_context(request_factory)
        icon_tag(ctx, 'star', colored=True)
        assert mock_render.call_args[0][1] == 'icons.colored.star'

    # size parameter sets width and height kwargs
    @patch('apps.core.templatetags.icon.render_component', return_value='<svg/>')
    def test_size_kwargs(self, mock_render, request_factory: RequestFactory):
        ctx = self._make_context(request_factory)
        icon_tag(ctx, 'star', size=24)
        _, kwargs = mock_render.call_args
        assert kwargs['width'] == 24
        assert kwargs['height'] == 24
