from buzuki.songs import Song


def SongFactory(**kwargs):
    return Song(
        name=kwargs.get('name', 'name'),
        artist=kwargs.get('artist', 'artist'),
        link=kwargs.get('link', 'link'),
        scale=kwargs.get('scale', 'scale'),
        rhythm=kwargs.get('rhythm', 'rhythm'),
        body=kwargs.get('body', 'body'),
    )
