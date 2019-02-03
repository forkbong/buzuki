from elasticsearch import Elasticsearch

es = Elasticsearch()

# Tokenizers
slug_tokenizer = {
    'type': 'pattern',
    'pattern': '[_ ]',
}

# Filters
edge_ngram_filter = {
    'type': 'edge_ngram',
    'min_gram': 1,
    'max_gram': 20,
}

greek_lowercase_filter = {
    'type': 'lowercase',
    'language': 'greek',
}

greek_stemmer_filter = {
    'type': 'stemmer',
    'language': 'greek',
}

# Analyzers
greek_autocomplete_analyzer = {
    'tokenizer': 'standard',
    'filter': [
        'greek_lowercase_filter',
        'edge_ngram_filter',
    ]
}

greek_lowercase_analyzer = {
    'tokenizer': 'standard',
    'filter': [
        'greek_lowercase_filter',
    ]
}

# Unused for now
greek_stemmed_analyzer = {
    'tokenizer': 'standard',
    'filter': [
        'greek_lowercase_filter',
        'greek_stemmer_filter',
    ]
}

slug_analyzer = {
    'tokenizer': 'slug_tokenizer',
    'filter': [
        'lowercase',
        'edge_ngram_filter',
    ]
}

# Fields
greek_text_field = {
    'type': 'text',
    'analyzer': 'greek_autocomplete',
    'search_analyzer': 'greek_lowercase',
}

greeklish_text_field = {
    'type': 'text',
    'analyzer': 'slug',
    'search_analyzer': 'standard',
}

keyword_field = {
    'type': 'keyword',
}


def create_index():
    """Delete and create the `documents` index again."""
    es.indices.delete(index='*')
    body = {
        'settings': {
            'analysis': {
                'tokenizer': {
                    'slug_tokenizer': slug_tokenizer,
                },
                'filter': {
                    'edge_ngram_filter': edge_ngram_filter,
                    'greek_lowercase_filter': greek_lowercase_filter,
                    'greek_stemmer_filter': greek_stemmer_filter,
                },
                'analyzer': {
                    'greek_autocomplete': greek_autocomplete_analyzer,
                    'greek_lowercase': greek_lowercase_analyzer,
                    # Unused for now
                    'greek_stemmed': greek_stemmed_analyzer,
                    'slug': slug_analyzer,
                },
            }
        },
        'mappings': {
            'properties': {
                'name': greek_text_field,
                'body': greek_text_field,
                'slug': greeklish_text_field,
                'url': keyword_field,
            }
        },
    }
    es.indices.create(index='documents', body=body)


def index(item):
    body = {
        'name': item.name,
        'slug': item.slug,
        'url': item.url,
    }

    if hasattr(item, 'body'):
        body['body'] = item.body

    es.index(index='documents', document=body, id=item.slug)


def delete(slug):
    es.delete(index='documents', id=slug)


def search(query, extra=[]):
    """Search elasticsearch and return the first 15 results.

    Args:
        query: The search query (all words must match).
        extra: A list of extra queries (i.e. "[url:artists]" to search
               only for artists). This could allow autocompleting
               artists in song form but it isn't yet implemented.
    """
    body = {
        'from': 0,
        'size': 15,
        'query': {
            'query_string': {
                'query': ' AND '.join(query.split() + extra),
                'fields': ['name^2', 'body', 'slug^2'],
            }
        },
        '_source': ['name', 'slug', 'url']
    }
    return es.search(index='documents', body=body)
