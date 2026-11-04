"""
Command line runner and progress tracker for the music recommender.

Run from the project folder:
    python src/main.py

Each STAGE below checks one piece of the Algorithm Recipe. Add a new stage
(or new checks) whenever you add a feature, and the exit code will be non-zero
if anything fails, so you always know the whole thing still works.
"""
import random
import sys
from pathlib import Path

from recommender import (
    Recommender, Song, UserProfile,
    load_songs, score_song, recommend_songs, DEFAULT_WEIGHTS,
    _song_from_dict,
)
from taste_profiles import TASTE_PROFILES

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"

_results = []


def stage(title: str) -> None:
    print(f"\n=== {title} ===")


def check(name: str, condition: bool, detail: str = "") -> None:
    _results.append(condition)
    print(f"  [{'PASS' if condition else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not condition else ""))


def approx(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def titles(songs) -> list:
    return [s.title for s in songs]


def profile_to_dict(p: UserProfile) -> dict:
    return {
        "target_energy": p.target_energy,
        "target_valence": p.target_valence,
        "target_acousticness": p.target_acousticness,
        "seen_song_ids": set(p.seen_song_ids),
    }


def main() -> int:
    # ------------------------------------------------------------------
    stage("1. Loading data")
    rows = load_songs(str(DATA_PATH))
    songs = [_song_from_dict(r) for r in rows]
    check("loaded 20 songs", len(rows) == 20, f"got {len(rows)}")
    check("numeric columns converted", isinstance(rows[0]["energy"], float) and isinstance(rows[0]["id"], int))
    check("ids are unique", len({s.id for s in songs}) == len(songs))
    check("all scored features are within 0-1",
          all(0 <= getattr(s, f) <= 1 for s in songs for f in DEFAULT_WEIGHTS))

    rec = Recommender(songs)

    # ------------------------------------------------------------------
    stage("2. Scoring rule")
    check("weights sum to 1", approx(sum(DEFAULT_WEIGHTS.values()), 1.0))
    check("closeness: perfect match is 1.0", approx(rec.closeness(0.7, 0.7), 1.0))
    check("closeness: symmetric above/below target",
          approx(rec.closeness(0.9, 0.8), rec.closeness(0.7, 0.8)))
    check("closeness: worst case is 0.0", approx(rec.closeness(0.0, 1.0), 0.0))

    # Hand-computed: Sunrise City vs happy_pop targets (0.80, 0.82, 0.20)
    #   0.40*0.98 + 0.35*0.98 + 0.25*0.98 = 0.98
    sunrise = next(s for s in songs if s.title == "Sunrise City")
    result = rec.score_song(TASTE_PROFILES["happy_pop"], sunrise)
    check("Sunrise City vs happy_pop = 0.980 (hand-computed)", approx(result.score, 0.98), f"got {result.score:.4f}")
    check("score stays between 0 and 1 for every profile and song",
          all(0 <= rec.score_song(p, s).score <= 1 for p in TASTE_PROFILES.values() for s in songs))

    # ------------------------------------------------------------------
    stage("3. Ranking rule")
    target = UserProfile(0.5, 0.5, 0.5)
    # A and B tie exactly on score (0.965). A has the smaller valence gap but the
    # LARGER id, so only the valence tie-break can put A first. C is identical
    # to B, so only the id tie-break can order B before C.
    tie_songs = [
        Song(3, "C", "x", "g", "m", 0.5, 100, 0.6, 0.5, 0.5),
        Song(1, "B", "x", "g", "m", 0.5, 100, 0.6, 0.5, 0.5),
        Song(2, "A", "x", "g", "m", 0.5, 100, 0.5, 0.5, 0.64),
    ]
    order = [r.song.title for r in Recommender(tie_songs).rank(target)]
    check("tie on score -> smaller valence gap first, then lowest id", order == ["A", "B", "C"], f"got {order}")

    profile = TASTE_PROFILES["chill_lofi"]
    full = [r.song.id for r in rec.rank(profile)]
    check("rank returns every song when none are seen", len(full) == len(songs))
    seen_profile = UserProfile(profile.target_energy, profile.target_valence,
                               profile.target_acousticness, seen_song_ids={full[0], full[1]})
    after = [r.song.id for r in rec.rank(seen_profile)]
    check("seen songs are removed", full[0] not in after and full[1] not in after and len(after) == len(songs) - 2)
    check("remaining order is unchanged by removal", after == full[2:])

    shuffled = songs[:]
    random.Random(0).shuffle(shuffled)
    check("same order regardless of catalog order",
          [r.song.id for r in Recommender(shuffled).rank(profile)] == full)
    check("recommend(k) returns k Song objects",
          len(rec.recommend(profile, k=3)) == 3 and all(isinstance(s, Song) for s in rec.recommend(profile, k=3)))

    # ------------------------------------------------------------------
    stage("4. Taste profiles separate listening styles")
    expectations = {
        "intense_rock": ("Storm Runner", None),
        "chill_lofi": (None, {"Focus Flow", "Library Rain", "Midnight Coding"}),
        "happy_pop": ("Sunrise City", None),
        "sad_acoustic": ("Moonlight Reverie", None),
    }
    for name, (top1, top3_set) in expectations.items():
        top = titles(rec.recommend(TASTE_PROFILES[name], k=3))
        if top1:
            check(f"{name}: #1 is {top1}", top[0] == top1, f"got {top}")
        if top3_set:
            check(f"{name}: top 3 are {sorted(top3_set)}", set(top) == top3_set, f"got {top}")
    rock_top5 = set(titles(rec.recommend(TASTE_PROFILES["intense_rock"], k=5)))
    lofi_top5 = set(titles(rec.recommend(TASTE_PROFILES["chill_lofi"], k=5)))
    check("intense_rock and chill_lofi top 5 do not overlap", rock_top5.isdisjoint(lofi_top5), f"shared: {rock_top5 & lofi_top5}")
    conflicted_best = rec.rank(TASTE_PROFILES["conflicted"])[0].score
    check("conflicted profile finds no strong match (best < 0.85)", conflicted_best < 0.85, f"best {conflicted_best:.3f}")

    # ------------------------------------------------------------------
    stage("5. Functional API matches the class")
    for name, p in TASTE_PROFILES.items():
        prefs = profile_to_dict(p)
        fn = recommend_songs(prefs, rows, k=5)
        oop = rec.rank(p)[:5]
        same = [d["id"] for d, _, _ in fn] == [r.song.id for r in oop]
        check(f"{name}: recommend_songs order == Recommender.rank", same)
    score, reasons = score_song(profile_to_dict(TASTE_PROFILES["happy_pop"]), rows[0])
    check("score_song returns (float, list of 3 reasons)", isinstance(score, float) and len(reasons) == 3)

    # ------------------------------------------------------------------
    stage("6. Explanations")
    text = rec.explain_recommendation(TASTE_PROFILES["happy_pop"], sunrise)
    check("explanation mentions score and all three features",
          text.startswith("score 0.98") and all(f in text for f in DEFAULT_WEIGHTS), text)

    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS (top 5 per profile)")
    print("=" * 60)
    for name, p in TASTE_PROFILES.items():
        print(f"\n{name}  (energy {p.target_energy}, valence {p.target_valence}, acousticness {p.target_acousticness})")
        for i, r in enumerate(rec.rank(p)[:5], 1):
            print(f"  {i}. {r.song.title:<22} {r.song.genre:<10} {r.score:.3f}")

    passed, total = sum(_results), len(_results)
    print(f"\n{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())