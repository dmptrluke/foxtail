import factory
from faker import Faker as FakerLib

fake = FakerLib()


class TaggedModelFactory(factory.django.DjangoModelFactory):
    """Abstract base factory for models using django-taggit."""

    class Meta:
        abstract = True

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.tags.add(*extracted)
        else:
            self.tags.add(fake.word(), fake.word())
