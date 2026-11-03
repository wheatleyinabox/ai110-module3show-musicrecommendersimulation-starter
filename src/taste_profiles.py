from typing import Dict

from recommender import UserProfile

# Each profile is a "target point" in (energy, valence, acousticness) space.
# The Recommender scores songs by closeness to this point, so profiles only
# need to sit far apart on the axes that separate the listening styles.
#
#   energy       0 = calm      -> 1 = intense
#   valence      0 = dark/sad  -> 1 = bright/happy
#   acousticness 0 = electric  -> 1 = acoustic

TASTE_PROFILES: Dict[str, UserProfile] = {
    # Loud, aggressive, electric, slightly dark.
    "intense_rock": UserProfile(
        target_energy=0.92,
        target_valence=0.40,
        target_acousticness=0.08,
    ),
    # Quiet, neutral-warm, organic/mellow.
    "chill_lofi": UserProfile(
        target_energy=0.38,
        target_valence=0.58,
        target_acousticness=0.80,
    ),
    # Upbeat, bright, polished/electric.
    "happy_pop": UserProfile(
        target_energy=0.80,
        target_valence=0.82,
        target_acousticness=0.20,
    ),
    # Very quiet, dark, fully acoustic.
    "sad_acoustic": UserProfile(
        target_energy=0.25,
        target_valence=0.25,
        target_acousticness=0.95,
    ),
    # Edge case for testing: high energy AND high acousticness, which the
    # catalog barely contains. Used to check how the scorer behaves when
    # preferences conflict.
    "conflicted": UserProfile(
        target_energy=0.85,
        target_valence=0.50,
        target_acousticness=0.85,
    ),
}