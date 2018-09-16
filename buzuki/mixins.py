import re

from buzuki.utils import unaccented


class Model:
    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.slug}'>"

    @classmethod
    def search(cls, query):
        query = unaccented(query.strip())
        slug_query = re.sub(r'\s+', '_', query)
        for obj in cls.all():
            if query in unaccented(obj.name) or slug_query in obj.slug:
                yield obj
