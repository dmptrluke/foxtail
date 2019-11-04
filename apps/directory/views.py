from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView

from .models import Character


class CharacterListView(ListView):
    model = Character
    template_name = 'character_list.html'

class CharacterView(DetailView):
    model = Character
    template_name = 'character_detail.html'


__all__ = ['CharacterListView']
