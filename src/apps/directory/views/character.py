from django.views.generic import DetailView

from ..models import Character


class CharacterView(DetailView):
    model = Character


class CharacterEditView(DetailView):
    model = Character


__all__ = ["CharacterView", "CharacterEditView"]
