import csv
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field, fields

################################
# GLOBAL VARIABLES & FUNCTIONS #
################################
DEFAULT_WEIGHTS: Dict[str, float] = {
    # "energy": 0.40,          # FEATURE-REMOVAL TEST: energy disabled
    "valence": 0.35 / 0.60,    # renormalized so weights still sum to 1.0
    "acousticness": 0.25 / 0.60,
}

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    
    Remember to convert numeric columns (id, 
    energy, tempo_bpm, valence, danceability, 
    acousticness) from strings.
    """
    print(f"Loading songs from {csv_path}...")
    int_cols = ("id",)
    float_cols = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for col in int_cols:
                row[col] = int(row[col])
            for col in float_cols:
                row[col] = float(row[col])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    
    Returns (score, reasons), where reasons is built 
    from the per-feature closeness values.
    """
    rec = Recommender([])
    user = _profile_from_dict(user_prefs)
    result = rec.score_song(user, _song_from_dict(song))
    return result.score, rec.describe_features(user, result)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    
    Returns a list of (song_dict, score, explanation), best first.
    """
    rec = Recommender([_song_from_dict(d) for d in songs])
    user = _profile_from_dict(user_prefs)
    by_id = {d["id"]: d for d in songs}
    return [
        (by_id[r.song.id], r.score, rec.explain_recommendation(user, r.song))
        for r in rec.rank(user)[:k]
    ]

def _song_from_dict(d: Dict) -> "Song":
    """Build a Song from a CSV-style dict (extra keys are ignored)."""
    return Song(**{f.name: d[f.name] for f in fields(Song)})
 
def _profile_from_dict(prefs: Dict) -> "UserProfile":
    """
    Build a UserProfile from a dict with the keys target_energy,
    target_valence, target_acousticness and, optionally, seen_song_ids.
    """
    return UserProfile(
        target_energy=prefs["target_energy"],
        target_valence=prefs["target_valence"],
        target_acousticness=prefs["target_acousticness"],
        seen_song_ids=set(prefs.get("seen_song_ids", ())),
    )

###########
# OBJECTS #
###########
@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    
    All CSV columns are kept but the system 
    only scores energy, valence, and acousticness.
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
    
######################
# SONG WRAPPER CLASS #
######################
@dataclass
class ScoreResult:
    """
    The outcome of scoring one song. Carries everything
    the ranking rule and the explanation need, so
    nothing is recomputed.
    """
    song: Song
    score: float
    feature_scores: Dict[str, float]
    valence_gap: float
    

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    
    The three target_* values (0-1) are what 
    the scoring rule measures closness against.
    """
    target_energy: float
    target_valence: float
    target_acousticness: float
    seen_song_ids: Set[int] = field(default_factory=set) # excluded when ranking

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], weights: Optional[Dict[str, float]] = None):
        self.songs = songs
        self.weights = weights if weights is not None else dict(DEFAULT_WEIGHTS)
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError(f"weights must sum to 1.0, got {sum(self.weights.values())}")        
        
    def closeness(self, song_value: float, target: float) -> float:
        """Numeric feature rule: 1 - abs(song_value - target)."""
        return 1.0 - abs(song_value - target)
    
    def score_song(self, user: UserProfile, song: Song) -> ScoreResult:
        """Scoring Rule: weighted sum of closeness for energy, valence, acousticness."""
        feature_scores = {
            # "energy": self.closeness(song.energy, user.target_energy),  # FEATURE-REMOVAL TEST
            "valence": self.closeness(song.valence, user.target_valence),
            "acousticness": self.closeness(song.acousticness, user.target_acousticness),
        }
        score = sum(self.weights[f] * c for f, c in feature_scores.items())
        return ScoreResult(
            song=song,
            score=score,
            feature_scores=feature_scores,
            valence_gap=abs(song.valence - user.target_valence),
        )
    
    def rank(self, user: UserProfile) -> List[ScoreResult]:
        """
        Ranking Rule:
        1. Drop songs whose id is in user.seen_song_ids.
        2. Score every remaining song.
        3. Sort by score (desc), then valence_gap (asc), then song.id (asc).
        """
        candidates = [s for s in self.songs if s.id not in user.seen_song_ids]
        results = [self.score_song(user, s) for s in candidates]
        # Round inside the sort key so floating-point noise (0.9000000001 vs
        # 0.9) can't stop two equal scores from tying and skipping tie-breakers.
        results.sort(key=lambda r: (-round(r.score, 6), round(r.valence_gap, 6), r.song.id))
        return results

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs from rank()."""
        return [r.song for r in self.rank(user)[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Build a short human-readable reason from the song's feature_scores."""
        result = self.score_song(user, song)
        return f"score {result.score:.2f}: " + "; ".join(self.describe_features(user, result))
    
    # Helper function for explain_recommendation()
    def describe_features(self, user: UserProfile, result: ScoreResult) -> List[str]:
        """One phrase per feature, e.g. 'energy 0.82 vs your 0.80 (close match)'."""
        targets = {
            # "energy": user.target_energy,  # FEATURE-REMOVAL TEST
            "valence": user.target_valence,
            "acousticness": user.target_acousticness,
        }
        phrases = []
        for feature, target in targets.items():
            c = result.feature_scores[feature]
            label = "close match" if c >= 0.90 else "partial match" if c >= 0.75 else "far from target"
            value = getattr(result.song, feature)
            phrases.append(f"{feature} {value:.2f} vs your {target:.2f} ({label})")
        return phrases