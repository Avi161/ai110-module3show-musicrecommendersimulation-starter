import csv
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def load_songs(csv_path: str) -> List[Song]:
    """Load songs from a CSV file and return a list of Song dataclass instances."""
    songs: List[Song] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                songs.append(Song(
                    id=int(row["id"]),
                    title=row["title"].strip(),
                    artist=row["artist"].strip(),
                    genre=row["genre"].strip().lower(),
                    mood=row["mood"].strip().lower(),
                    energy=float(row["energy"]),
                    tempo_bpm=float(row["tempo_bpm"]),
                    valence=float(row["valence"]),
                    danceability=float(row["danceability"]),
                    acousticness=float(row["acousticness"]),
                ))
            except (ValueError, KeyError) as e:
                print(f"Skipping malformed row (id={row.get('id', '?')}): {e}")
    return songs


def score_song(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """
    Score a single song against a user profile using the weighted algorithm recipe.

    Scoring rules:
      +2.0  genre match
      +1.0  mood match
      +1.5 * (1 - |song.energy - user.target_energy|)  energy closeness
      +0.5  if user likes_acoustic and song.acousticness >= 0.5

    Returns a (score, reasons) tuple where reasons is a list of human-readable
    strings explaining each contribution to the total score.
    """
    score = 0.0
    reasons: List[str] = []

    if user.favorite_genre and song.genre == user.favorite_genre.strip().lower():
        score += 2.0
        reasons.append("genre match (+2.00)")

    if user.favorite_mood and song.mood == user.favorite_mood.strip().lower():
        score += 1.0
        reasons.append("mood match (+1.00)")

    clamped_energy = max(0.0, min(1.0, song.energy))
    energy_closeness = 1.0 - abs(clamped_energy - user.target_energy)
    energy_points = 1.5 * energy_closeness
    score += energy_points
    reasons.append(f"energy closeness (+{energy_points:.2f})")

    if user.likes_acoustic and song.acousticness >= 0.5:
        score += 0.5
        reasons.append("acoustic preference (+0.50)")

    return score, reasons


def recommend_songs(
    user: UserProfile, songs: List[Song], k: int = 5
) -> List[Tuple[Song, float, List[str]]]:
    """
    Rank all songs for a user and return the top-k with scores and reasons.

    Returns a list of (Song, score, reasons) tuples sorted highest score first.
    Ties broken by ascending song id for deterministic output.
    """
    scored = [(s, *score_song(user, s)) for s in songs]
    scored.sort(key=lambda t: (-t[1], t[0].id))
    return scored[:k]


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Song objects ranked by score for the given user."""
        return [song for song, _, _ in recommend_songs(user, self.songs, k)]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why a song was recommended."""
        score, reasons = score_song(user, song)
        if not reasons:
            return f"No strong feature matches; total score {score:.2f}."
        return f"Total {score:.2f}: " + "; ".join(reasons)
