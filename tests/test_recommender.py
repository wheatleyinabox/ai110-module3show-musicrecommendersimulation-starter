import random
from pathlib import Path

import pytest

from src.recommender import (
    Song, UserProfile, Recommender, DEFAULT_WEIGHTS,
    load_songs, score_song, recommend_songs, _song_from_dict,
)
from src.taste_profiles import TASTE_PROFILES

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


########################
# HELPERS AND FIXTUREs #
########################
def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def titles(songs):
    return [s.title for s in songs]


def profile_to_dict(p: UserProfile) -> dict:
    return {
        "target_energy": p.target_energy,
        "target_valence": p.target_valence,
        "target_acousticness": p.target_acousticness,
        "seen_song_ids": set(p.seen_song_ids),
    }


@pytest.fixture(scope="module")
def rows():
    return load_songs(str(DATA_PATH))


@pytest.fixture(scope="module")
def songs(rows):
    return [_song_from_dict(r) for r in rows]


@pytest.fixture(scope="module")
def rec(songs):
    return Recommender(songs)


@pytest.fixture(scope="module")
def sunrise(songs):
    return next(s for s in songs if s.title == "Sunrise City")


##########################
# ORIGINAL STARTER TESTS #
##########################
def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        target_energy=0.92,
        target_valence=0.40,
        target_acousticness=0.08,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        target_energy=0.38,
        target_valence=0.58,
        target_acousticness=0.80,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


################
# LOADING DATA #
################
class TestLoadingData:
    def test_loads_20_songs(self, rows):
        assert len(rows) == 20

    def test_numeric_columns_converted(self, rows):
        assert isinstance(rows[0]["id"], int)
        assert isinstance(rows[0]["energy"], float)

    def test_ids_are_unique(self, songs):
        assert len({s.id for s in songs}) == len(songs)

    def test_scored_features_within_0_to_1(self, songs):
        for s in songs:
            for feature in DEFAULT_WEIGHTS:
                assert 0 <= getattr(s, feature) <= 1, f"{s.title}.{feature}"


################
# SCORING RULE #
################
class TestScoringRule:
    def test_weights_sum_to_1(self):
        assert sum(DEFAULT_WEIGHTS.values()) == pytest.approx(1.0)

    def test_weights_that_do_not_sum_to_1_are_rejected(self):
        with pytest.raises(ValueError):
            Recommender([], weights={"energy": 0.5, "valence": 0.5, "acousticness": 0.5})

    def test_closeness_perfect_match_is_1(self, rec):
        assert rec.closeness(0.7, 0.7) == pytest.approx(1.0)

    def test_closeness_is_symmetric_around_target(self, rec):
        assert rec.closeness(0.9, 0.8) == pytest.approx(rec.closeness(0.7, 0.8))

    def test_closeness_worst_case_is_0(self, rec):
        assert rec.closeness(0.0, 1.0) == pytest.approx(0.0)

    def test_sunrise_city_vs_happy_pop_hand_computed(self, rec, sunrise):
        # 0.40*0.98 + 0.35*0.98 + 0.25*0.98 = 0.98
        result = rec.score_song(TASTE_PROFILES["happy_pop"], sunrise)
        assert result.score == pytest.approx(0.98)

    @pytest.mark.parametrize("profile_name", list(TASTE_PROFILES))
    def test_scores_stay_between_0_and_1(self, rec, songs, profile_name):
        profile = TASTE_PROFILES[profile_name]
        for s in songs:
            assert 0 <= rec.score_song(profile, s).score <= 1


################
# RANKING RULE #
################
class TestRankingRule:
    def test_tie_on_score_uses_valence_gap_then_id(self):
        target = UserProfile(0.5, 0.5, 0.5)
        # A and B tie exactly on score (0.965). A has the smaller valence gap but
        # the LARGER id, so only the valence tie-break can put A first. C is
        # identical to B, so only the id tie-break can order B before C.
        tie_songs = [
            Song(3, "C", "x", "g", "m", 0.5, 100, 0.6, 0.5, 0.5),
            Song(1, "B", "x", "g", "m", 0.5, 100, 0.6, 0.5, 0.5),
            Song(2, "A", "x", "g", "m", 0.5, 100, 0.5, 0.5, 0.64),
        ]
        order = [r.song.title for r in Recommender(tie_songs).rank(target)]
        assert order == ["A", "B", "C"]

    def test_rank_returns_every_song_when_none_seen(self, rec, songs):
        assert len(rec.rank(TASTE_PROFILES["chill_lofi"])) == len(songs)

    def test_seen_songs_are_removed_and_order_otherwise_unchanged(self, rec, songs):
        p = TASTE_PROFILES["chill_lofi"]
        full = [r.song.id for r in rec.rank(p)]
        seen = UserProfile(p.target_energy, p.target_valence, p.target_acousticness,
                           seen_song_ids={full[0], full[1]})
        after = [r.song.id for r in rec.rank(seen)]
        assert full[0] not in after and full[1] not in after
        assert after == full[2:]

    def test_order_is_independent_of_catalog_order(self, rec, songs):
        p = TASTE_PROFILES["chill_lofi"]
        expected = [r.song.id for r in rec.rank(p)]
        shuffled = songs[:]
        random.Random(0).shuffle(shuffled)
        assert [r.song.id for r in Recommender(shuffled).rank(p)] == expected

    def test_recommend_returns_k_song_objects(self, rec):
        result = rec.recommend(TASTE_PROFILES["chill_lofi"], k=3)
        assert len(result) == 3
        assert all(isinstance(s, Song) for s in result)


############################################
# TASTE PROFILES SEPARATE LISENTING STYLES #
############################################
class TestTasteProfiles:
    @pytest.mark.parametrize("profile_name, expected_top", [
        ("intense_rock", "Storm Runner"),
        ("happy_pop", "Sunrise City"),
        ("sad_acoustic", "Moonlight Reverie"),
    ])
    def test_top_recommendation(self, rec, profile_name, expected_top):
        assert titles(rec.recommend(TASTE_PROFILES[profile_name], k=1)) == [expected_top]

    def test_chill_lofi_top_3_are_the_lofi_songs(self, rec):
        top3 = set(titles(rec.recommend(TASTE_PROFILES["chill_lofi"], k=3)))
        assert top3 == {"Focus Flow", "Library Rain", "Midnight Coding"}

    def test_intense_rock_and_chill_lofi_top_5_do_not_overlap(self, rec):
        rock = set(titles(rec.recommend(TASTE_PROFILES["intense_rock"], k=5)))
        lofi = set(titles(rec.recommend(TASTE_PROFILES["chill_lofi"], k=5)))
        assert rock.isdisjoint(lofi)

    def test_conflicted_profile_finds_no_strong_match(self, rec):
        assert rec.rank(TASTE_PROFILES["conflicted"])[0].score < 0.85


#####################################
# FUNCTIONAL API MATCEHES THE CLASS #
#####################################
class TestFunctionalApi:
    @pytest.mark.parametrize("profile_name", list(TASTE_PROFILES))
    def test_recommend_songs_order_matches_recommender(self, rec, rows, profile_name):
        p = TASTE_PROFILES[profile_name]
        functional = [d["id"] for d, _, _ in recommend_songs(profile_to_dict(p), rows, k=5)]
        oop = [r.song.id for r in rec.rank(p)[:5]]
        assert functional == oop

    def test_score_song_returns_score_and_three_reasons(self, rows):
        score, reasons = score_song(profile_to_dict(TASTE_PROFILES["happy_pop"]), rows[0])
        assert isinstance(score, float)
        assert len(reasons) == 3


################
# EXPLANATIONS #
################
class TestExplanations:
    def test_explanation_mentions_score_and_all_three_features(self, rec, sunrise):
        text = rec.explain_recommendation(TASTE_PROFILES["happy_pop"], sunrise)
        assert text.startswith("score 0.98")
        for feature in DEFAULT_WEIGHTS:
            assert feature in text