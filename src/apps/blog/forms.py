from django.forms import (
    DateTimeField,
    DateTimeInput,
    HiddenInput,
    ImageField,
    ModelForm,
    Textarea,
)

from csp_helpers.mixins import CSPFormMixin
from markdownfield.widgets import MDEWidget
from taggit.forms import TagField

from apps.core.widgets import CroppedImageWidget

from .models import Author, Comment, Post


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': Textarea(attrs={'rows': 4})}


class PostForm(CSPFormMixin, ModelForm):
    tags = TagField(required=False, help_text='Comma-separated list of tags.')
    image = ImageField(required=False, widget=CroppedImageWidget(aspect_ratio=2, ppoi_field='image_ppoi'))
    live_as_of = DateTimeField(
        required=False,
        label='Publish Date',
        help_text='Required when status is "Available after Publish Date".',
        widget=DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'slug',
            'author',
            'description',
            'text',
            'allow_comments',
            'publish_status',
            'live_as_of',
            'image',
            'image_ppoi',
        ]
        widgets = {
            'description': Textarea(attrs={'rows': 3}),
            'text': MDEWidget(),
            'image_ppoi': HiddenInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = Author.objects.all()
        self.fields['author'].required = False
        if user and hasattr(user, 'blog_author'):
            self.fields['author'].initial = user.blog_author
        if self.instance and self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()
