from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field

################################
# GLOBAL VARIABLES & FUNCTIONS #
################################
DEFAULT_WEIGHTS: Dict[str, float] = {
    "energy": 0.40,
    "valence": 0.35,
    "acousticness": 0.25,
}

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    
    Remember to convert numeric columns (id, 
    energy, tempo_bpm, valence, danceability, 
    acousticness) from strings.

    """
    # TODO: Implement CSV loading logic
    print(f"Loading songs from {csv_path}...")
    return []

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    
    Returns (score, reasons), where reasons is built 
    from the per-feature closeness values.
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    return []

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    
    Returns a list of (song_dict, score, explanation), best first.
    """
    # TODO: Implement scoring and ranking logic
    # Expected return format: (song_dict, score, explanation)
    return []

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
        
    def closeness(self, song_value: float, target: float) -> float:
        """Numeric feature rule: 1 abs(song_value - target)."""
        raise NotImplementedError
    
    def score_song(self, user: UserProfile, song: Song) -> ScoreResult:
        """Scoring Rule: weighted sum of closeness for energy, valence, acousticness."""
        raise NotImplementedError
    
    def rank(self, user: UserProfile) -> List[ScoreResult]:
        """
        Ranking Rule:
        1. Drop songs whose id is in user.seen_song_ids.
        2. Score every remaining song.
        3. Sort by score (desc), then valence_gap (asc), then song.id (asc).
        """
        raise NotImplementedError

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs from rank()."""
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Build a short human-readable reason from the song's feature_scores."""
        return "Explanation placeholder"