import logging
import math
from pathlib import Path

import yaml
from flask import current_app as app

from buzuki import cache_utils
from buzuki.cache_utils import get_related as get_related_cache
from buzuki.playlists import get_selected_playlist
from buzuki.sessions import Session
from buzuki.utils import get_latest_songs


def _calculate_distances(directory):
    """Calculate distances for each song pair in Sessions."""
    distances = {}
    for path in directory.iterdir():
        data = Session(path.name, directory=directory).songs
        for i, song_left in enumerate(data[:-1]):
            slug_left = song_left['slug']
            for j, song_right in enumerate(data[i + 1:i + 21], start=i + 1):
                slug_right = song_right['slug']
                if slug_left == slug_right:
                    continue

                value = distances.setdefault(slug_left, {})
                value.setdefault(slug_right, []).append(j - i)

                value = distances.setdefault(slug_right, {})
                value.setdefault(slug_left, []).append(j - i)

    return distances


def _calculate_scores(distances):
    """Normalize distances to scores and calculate C and m."""
    max_distance = 0
    for song_left, songs in distances.items():
        for song_right, values in songs.items():
            max_distance = max(max_distance, max(values))

    # Map possible distances to a line using a function
    # f, such that f(1) = 10 and f(max_distance) = 1.
    a = -9 / (max_distance - 1)
    b = 10 - a

    def f(x: int) -> float:
        return a * x + b

    len_all = 0
    sum_all = 0
    num = 0
    for song_left, songs in distances.items():
        for song_right, values in songs.items():
            normalized_values = [f(value) for value in values]
            songs[song_right] = normalized_values
            len_all += len(normalized_values)
            sum_all += sum(normalized_values)
            num += 1

    C = sum_all / len_all
    m = len_all / num

    print("max_distance:", max_distance)
    print("C:", C)
    print("m:", m)

    return distances, C, math.ceil(m)


def _bayesian_weighting(scores, C, m):
    """Calculate average scores of song pairs using a bayes estimator.

    Score is calculated as W = (R*v + C*m) / (v + m), where:

    W = Weighted score
    R = Average score for the song pair as a number from 1 to 10
    v = Number of scores for the song pair
    m = Weight given to the prior estimate (average number of scores per pair)
    C = The mean score across the whole pool

    See:
    https://www.startpage.com/do/metasearch.pl?query=bayesian%20weighting
    https://en.wikipedia.org/wiki/Bayes_estimator#Practical_example_of_Bayes_estimators
    """
    average_scores = {}
    for song_left, songs in scores.items():
        average_scores[song_left] = {}
        for song_right, values in songs.items():
            v = len(values)  # Number of scores
            R = sum(values) / v  # Average
            W = (R * v + C * m) / (v + m)  # Weighted average
            average_scores[song_left][song_right] = W

    return average_scores


def _sorted_dict(data):
    """Return dict `data` sorted by value, descending."""
    return dict(sorted(data.items(), key=lambda kv: -kv[1]))


def _related(average_scores):
    """Return related songs for each song sorted by average descending."""
    return {
        song: _sorted_dict(scores)
        for song, scores in sorted(average_scores.items())
    }


def generate_related():
    """Analyze sessions and generate related songs."""
    directory: Path = app.config['DIR'] / 'sessions'
    distances = _calculate_distances(directory)
    scores, C, m = _calculate_scores(distances)
    average_scores = _bayesian_weighting(scores, C, m)
    related = _related(average_scores)
    path = app.config['DIR'] / 'related.yml'
    data = yaml.safe_dump(related, allow_unicode=True, sort_keys=False)
    path.write_text(data)


def logged_in():
    from flask import session

    return session.get('logged_in')


def combine(score_list):
    combined = {}
    for scores, weight in score_list:
        for slug, score in scores.items():
            combined[slug] = combined.get(slug, 0) + weight * score

    return _sorted_dict(combined)


def get_related(slug):
    """Get a list of related songs for the given song."""
    logging.debug(f"Getting related for {slug}")

    if logged_in():
        sequence = [song['slug'] for song in Session.get().songs]
    else:
        sequence = get_latest_songs()

    if sequence and sequence[-1] == slug:
        del sequence[-1]

    assert not sequence or sequence[-1] != slug

    logging.debug("Got latest song sequence")

    previous_songs = [slug]
    if len(sequence) > 0:
        previous_songs.append(sequence[-1])
    if len(sequence) > 1:
        previous_songs.append(sequence[-2])

    score_list = []
    for slug in previous_songs:
        related = get_related_cache(slug)
        if related is not None:
            score_list.append(related)

    len_score_list = len(score_list)
    logging.debug(f"Found {len_score_list} of {len(previous_songs)}")
    if len_score_list == 0:
        return None
    elif len_score_list == 1:
        score_list[0] = (score_list[0], 1)
    elif len_score_list == 2:
        score_list[0] = (score_list[0], 0.7)
        score_list[1] = (score_list[1], 0.3)
    elif len_score_list:
        score_list[0] = (score_list[0], 0.5)
        score_list[1] = (score_list[1], 0.3)
        score_list[2] = (score_list[2], 0.2)

    related = combine(score_list)
    logging.debug("Combined scores")

    related = [slug for slug in related if slug not in sequence]
    logging.debug("Filtered out played")

    # If a playlist is selected and the given song is in
    # the playlist, filter out songs that aren't in it.
    playlist = get_selected_playlist()
    if playlist and slug in playlist:
        related = [slug for slug in related if slug in playlist]
        logging.debug("Filtered out not in playlist")

    cached_songs = cache_utils.get_songs()
    return [{
        'name': cached_songs[slug]['name'],
        'slug': slug,
    } for slug in related[:15]]
