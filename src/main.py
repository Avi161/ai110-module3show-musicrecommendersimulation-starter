"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

from src.recommender import UserProfile, load_songs, recommend_songs

# Four distinct taste profiles for testing — including one adversarial edge case
PROFILES = [
    ("High-Energy Pop Fan",   UserProfile("pop",  "happy",   0.85, False)),
    ("Chill Lofi Studier",    UserProfile("lofi", "chill",   0.35, True)),
    ("Deep Intense Rock",     UserProfile("rock", "intense", 0.90, False)),
    ("Adversarial: Happy-Sad Pop", UserProfile("pop",  "sad",  0.90, False)),
]


def main() -> None:
    songs = load_songs("data/songs.csv")
    if not songs:
        print("No songs loaded — check data/songs.csv path.")
        return

    print(f"Loaded {len(songs)} songs.\n")

    for name, user in PROFILES:
        print(f"{'=' * 60}")
        print(f"Profile: {name}")
        print(
            f"  genre={user.favorite_genre}  mood={user.favorite_mood}  "
            f"energy={user.target_energy}  acoustic={user.likes_acoustic}"
        )
        print()
        results = recommend_songs(user, songs, k=5)
        for rank, (song, score, reasons) in enumerate(results, start=1):
            print(
                f"  {rank}. [{score:5.2f}] {song.title} — {song.artist}"
                f"  ({song.genre} / {song.mood})"
            )
            print(f"         because: {'; '.join(reasons)}")
        print()


if __name__ == "__main__":
    main()
