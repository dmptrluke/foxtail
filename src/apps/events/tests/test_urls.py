from django.urls import resolve, reverse


class TestEventUrls:
    """Test events URL routing."""

    # list resolves to /events/
    def test_list(self):
        assert reverse('events:list') == '/events/'
        assert resolve('/events/').view_name == 'events:list'

    # year list resolves with year param
    def test_list_year(self):
        assert reverse('events:list_year', kwargs={'year': 2019}) == '/events/2019/'
        assert resolve('/events/2019/').view_name == 'events:list_year'

    # detail resolves with year and slug
    def test_detail(self):
        assert reverse('events:detail', kwargs={'year': 2019, 'slug': 'test'}) == '/events/2019/test/'
        assert resolve('/events/2019/test/').view_name == 'events:detail'
