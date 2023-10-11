import re

from flask import abort

from buzuki import DoesNotExist, InvalidNote
from buzuki.utils import greeklish, unaccented


class Model:
    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.slug}'>"

    def __eq__(self, other):
        """Test instance equality by comparing slugs."""
        if isinstance(other, self.__class__):
            return self.slug == other.slug
        return False

    def get(self):
        raise NotImplementedError

    @classmethod
    def all(cls):
        raise NotImplementedError

    @classmethod
    def get_or_404(cls, *args, **kwargs):
        try:
            return cls.get(*args, **kwargs)
        except (DoesNotExist, InvalidNote):
            abort(404)

    @property
    def slug(self):
        return greeklish(self.name)

    @property
    def url(self):
        return f'/{self.__class__.__name__.lower()}s/{self.slug}/'

    @classmethod
    def search(cls, query):
        query = unaccented(query.strip())
        slug_query = re.sub(r'\s+', '_', query)
        for obj in cls.all():
            if query in unaccented(obj.name) or slug_query in obj.slug:
                yield obj
