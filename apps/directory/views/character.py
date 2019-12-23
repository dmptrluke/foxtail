from django.views.generic import DetailView

from ..models import Character


class CharacterView(DetailView):
    model = Character
    template_name = 'character.html'


class CharacterEditView(DetailView):
    model = Character
    template_name = 'character.html'


__all__ = ["CharacterView", "CharacterEditView"]
