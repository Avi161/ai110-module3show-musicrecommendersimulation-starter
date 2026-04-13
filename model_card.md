# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 0.1**

---

## 2. Intended Use

VibeFinder 0.1 is a classroom simulation of a content-based music recommender. Given a user's stated preferences for genre, mood, energy level, and acoustic taste, it selects and ranks the top five most similar songs from a small curated catalog.

- **What it does:** suggests 5 songs per query from a 22-song CSV catalog.
- **Who it is for:** educational exploration only — not for real users or production deployment.
- **What it assumes:** the user can accurately describe their own taste in four parameters, and that those parameters capture enough of "vibe" to be useful. It does not learn from behavior; it only uses what the user explicitly provides.
- **What it is NOT for:** replacing real recommendation services, handling large catalogs, personalizing over time, or making decisions about what music is "good."

---

## 3. How the Model Works

Think of VibeFinder as a judging panel that gives each song a score out of 5 and picks the winners.

For every song in the catalog, the system asks four questions:

1. **Does the genre match?** If yes, award 2 points. Genre is weighted highest because it usually determines the broadest "feel" of a track.
2. **Does the mood match?** If yes, award 1 point. Mood matters but is secondary — a happy pop song is still better than a sad jazz track for a pop fan.
3. **How close is the song's energy to what the user wants?** Energy is a number between 0 (very calm) and 1 (very intense). The closer the song is to the user's target, the more points it gets — up to 1.5 for a perfect match.
4. **Is the song acoustic if the user likes acoustic tracks?** If yes, award 0.5 bonus points.

Once every song has a score, the system sorts them from highest to lowest and returns the top five, along with a plain-English breakdown of why each song ranked where it did.

---

## 4. Data

- **Catalog size:** 22 songs (10 original starter tracks + 12 added for diversity).
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop.
- **Moods represented:** happy, chill, intense, relaxed, moody, focused, sad.
- **Features per song:** genre, mood, energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1). Of these, only genre, mood, energy, and acousticness are currently used in scoring.
- **What was added:** rock/intense variety (Broken Satellites, Iron Sky, Voltage Rush), pop/sad tracks (Blue Monday Feels, Empty Rooms) to enable adversarial testing, plus ambient/relaxed, jazz/chill, lofi/intense, indie pop/chill, and synthwave/sad entries to widen coverage.
- **Missing musical taste:** no hip-hop, classical, country, R&B, metal, or electronic sub-genres. The catalog skews toward a narrow Western indie/pop/lofi taste window. Mood labels (e.g., "intense," "chill") are assigned subjectively by the dataset author — two people might label the same track differently.

---

## 5. Strengths

- **Works well for users with clear, catalog-matching preferences.** The "Chill Lofi Studier" profile (lofi/chill/energy=0.35) produced a perfect 5.0 top result (Library Rain), which matched intuition exactly. When a user's genre and mood exist well in the catalog, the system is reliably useful.
- **Transparent reasoning.** Every recommendation comes with a reasons list (e.g., "genre match (+2.00); energy closeness (+1.47)"). Users can immediately understand why a song appeared and whether to trust the suggestion. This is an advantage over black-box systems.
- **Deterministic and debuggable.** The same inputs always produce the same outputs in the same order. No randomness, no hidden state. Easy to audit and explain.
- **Handles adversarial inputs gracefully.** The "Happy-Sad Pop" profile (genre=pop, mood=sad) correctly surfaced pop/sad tracks after the catalog was expanded, demonstrating that the algorithm degrades sensibly — it doesn't crash or return nonsense, it just falls back to the strongest matching feature.

---

## 6. Limitations and Bias

- **Genre dominance.** The +2.0 genre bonus outweighs the maximum possible energy score (1.5) and mood bonus (1.0) combined. A genre match guarantees the top positions almost regardless of energy or mood. Users who want "anything chill" without naming a specific genre receive noticeably weaker results.
- **Small catalog creates filter bubbles.** With only 22 songs across 7 genres, users asking for rock/intense will receive the same 4 tracks every time. Diversity of recommendations is limited by diversity of data, not algorithm sophistication.
- **No collaborative signal.** The system treats every user in isolation. Real recommenders benefit from "people like you also liked…" patterns. Without this, VibeFinder cannot discover that a classical fan might love certain ambient tracks.
- **Mood labels are subjective and unverified.** Someone assigned "moody" to Night Drive Loop. Another person might call it "nostalgic" or "energetic." Subjective labels encoded as objective features propagate the labeler's perspective into every recommendation.
- **Single user shape.** One `UserProfile` cannot represent mixed-context taste (e.g., high-energy for workouts, low-energy for study). The system always applies the same preferences regardless of context.
- **No artist diversity logic.** If three songs by Neon Echo all score highly, all three appear together in the top five. A production system would penalize repeated artists to improve variety.

---

## 7. Evaluation

Four user profiles were tested; `pytest` was used for automated coverage of the core ranking contract.

| Profile | Key result | Observation |
|---|---|---|
| High-Energy Pop Fan | Sunrise City, Golden Haze top-ranked | Correct; both are pop/happy/high-energy |
| Chill Lofi Studier | Library Rain scores perfect 5.0 | Correct; lofi/chill/acoustic/low-energy exact match |
| Deep Intense Rock | 4 rock/intense songs in top 4 | Correct; rock catalog coverage was thin until songs were added |
| Adversarial: Happy-Sad Pop | pop/sad tracks ranked first | Correct after catalog expansion; demonstrates genre dominance over mood |

**Surprises:**
- Removing the acoustic preference component barely shifted the Lofi Studier's top 2 results — those songs had such strong genre+mood+energy matches that the acoustic bonus was nearly invisible.
- The "Deep Intense Rock" profile's #5 slot (Last Train Out, rock/chill) felt like a stretch — the system ran out of rock/intense songs and fell back to genre-match-only. This is an honest reflection of catalog depth, not a bug.
- The adversarial profile showed that even when the system cannot satisfy both genre and mood, it doesn't hallucinate or produce random results — it transparently falls back to the strongest available feature.

**Automated tests:** `pytest` covers two cases: that `Recommender.recommend` returns songs sorted by score (pop/happy song ranked first for a pop/happy user) and that `explain_recommendation` returns a non-empty string. Both pass.

---

## 8. Future Work

1. **Collaborative filtering layer.** Track which songs users skip, save, or replay. Use this to find "users like you" and surface songs outside the user's stated genre that similar users enjoyed. This is how Spotify's Discover Weekly discovers unexpected favorites.
2. **Diversity penalty (Maximal Marginal Relevance).** After scoring, penalize a song's rank if an artist already appears in the top results. This prevents the top five from being monopolized by two artists with a similar catalog.
3. **Richer feature vector with learned weights.** Add tempo range preference, valence (positivity), and danceability to the scoring. Instead of hand-tuning weights (2.0, 1.0, 1.5, 0.5), use a small set of user-rated songs to fit weights automatically — turning the "algorithm recipe" into a personalized model.
4. **Session-aware profiles.** Allow users to describe multiple contexts ("gym mode," "study mode") and switch between them without restarting. Store preference histories so the profile improves over time.

---

## 9. Personal Reflection

Building VibeFinder made something abstract concrete: a recommendation is just a sorted list of scores, and a score is just a weighted sum of feature comparisons. There is no taste, no understanding — just arithmetic. What surprised me most was how much the choice of weights shapes the outcome. Changing the genre bonus from 2.0 to 1.0 in Experiment 2 completely reshuffled the rankings for the High-Energy Pop Fan profile, bumping synthwave tracks above mood-mismatched pop tracks. That sensitivity showed how real-world systems — even "neutral" ones — silently encode the designer's assumptions about what matters. If I set genre weight high, pop dominates; if energy weight were highest, calm-but-genre-matched songs would get buried. None of those choices are wrong technically, but they all have consequences for whose music gets heard. Working through these tradeoffs in a small, transparent system made it much easier to imagine where the same dynamics play out — invisibly — at Spotify scale.
