# 🎵 Music Recommender Simulation

## Project Summary

Building and explaining a small music recommender system where the goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

---

## How The System Works

For my recommender system, I've selected three attributes, energy, valence, and acousticness. I find these to be the important in the general sense. It encompasses the most information about a song while relying on numbers instead of arbitrary labels. I reward songs for their closeness, where the values of a song match or almost match a user's existing preference scores. Closeness is calculatd with '1- |song_value - target|.' 1 is considered a perfect song and linearly falls off where 0 is the most distance there is. Also the closness goes both ways, so a score can be 0.1 below and above a target but still have the same weight. So, each attribute will have its closeness calculated and averaged with a weight to each. In my case, I will be giving energy 40%, valence 35% and acousticness 25%. This is the Scoring Rule. For the Ranking Rule, there's 5 steps. First we calculate the score for each song in the list. Then, we remove songs that the user has already heard or in the "seed" set. We sort by score with the highest on top. If there's a tie, we use the valence score to score for the highest between the ties. If they're the same score still, then the songs are just sorted by id. Finally we return the top K. (Ex. 3, 5, 10...)

With the definitions set, the recommender file itself need to represent the scaffolding. The UserProfile comes with its default values (except favorite_genre and favorite_mood) with some changes and additions. The likes_acoustic boolean becomes a float since we're dealing with numbers. The Song object has a wrapper object that contains the song itself, its score, the attribute scores, and the valence gap. This is added because the Ranking Rule needs the gap for tie-breaking and explain_recommendation() can then read the attribute scores without recalculating them.

Some biases that I uncovered were all based on the dataset. Energy and acousticness are inversely related. When most songs have a high energy and a low acousticness and visa versa, they carry quite a bit of the score, around 65%. Acousticness is also polarized which seperates songs. This is the opposite case with valence. As a result, it's energy and acousticness on top and valence to the side.

Compared to Spotify's recommender, the streaming platform uses more sophistacated approaches. It uses collaborative filtering, which compares users with similiar listening habits and any new songs one of them listen to, will be recommended to those that haven't. They also utlize something like the system I created where it analysis the songs themselves. But they also scan the internet for trends and uses AI systems. On top of analyzing user behavior, they also convert songs into graphs of data where clusters of similar songs can be recommended.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

   ```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

```
============================================================
RECOMMENDATIONS (top 5 per profile)
============================================================

intense_rock  (energy 0.92, valence 0.4, acousticness 0.08)
  1. Storm Runner           rock       0.963
  2. Iron Requiem           metal      0.905
  3. Night Drive Loop       synthwave  0.866
  4. Gym Hero               pop        0.859
  5. Concrete Crown         hip hop    0.857

chill_lofi  (energy 0.38, valence 0.58, acousticness 0.8)
  1. Focus Flow             lofi       0.984
  2. Library Rain           lofi       0.966
  3. Midnight Coding        lofi       0.955
  4. Hollow Pines           folk       0.952
  5. Coffee Shop Stories    jazz       0.928

happy_pop  (energy 0.8, valence 0.82, acousticness 0.2)
  1. Sunrise City           pop        0.980
  2. Fuego en la Noche      latin      0.954
  3. Rooftop Lights         indie pop  0.943
  4. Concrete Crown         hip hop    0.902
  5. Gym Hero               pop        0.893

sad_acoustic  (energy 0.25, valence 0.25, acousticness 0.95)
  1. Moonlight Reverie      classical  0.969
  2. Hollow Pines           folk       0.844
  3. Spacewalk Thoughts     ambient    0.841
  4. Library Rain           lofi       0.815
  5. Focus Flow             lofi       0.778

conflicted  (energy 0.85, valence 0.5, acousticness 0.85)
  1. Crossroads Blues       blues      0.800
  2. Night Drive Loop       synthwave  0.799
  3. Storm Runner           rock       0.781
  4. Midnight Coding        lofi       0.772
  5. Focus Flow             lofi       0.771
```

---

## Experiments You Tried

As an experment, I decided to remove energy from the equation with a Feature Removal test. Given that is has the most weight, I'm curious to see that just valence and acousticness make up for. Interestingly, there were no real surprises to the profiles, except for the conflicted profile once again. Intense Rock contained the same 5 songs with some slight differences. Night Drive Loop moves above Iron Requirem and Gym Hero drops from 4th to 5th. Chill Lofi get a replacement with Coffee Shop Stories falling out and Pulse Cathedral coming into 5th. Happy Pop has the same trend, with Pulse Cathedral coming in and Concrete Clown dropping out. For Sad Acoustic, Crossroad Blues replaces Focus Flow which makes more sense for the category now. Finally conflicted had the most change, where Crossroad Blues, Night Drive Loop, and Storm Runner falling out completely from the top 3. What I can see is that energy is doing much seperating work, valence and acousticness work well by themselves. Instead, it's more of a tie-breaker between songs of close valence and acousticness. And clearly we can see the energy makes the most of the conflicted profile.

---

## Limitations and Risks

In terms of filter bubbles and underrepresentation, a big limitation is that there's no representation. Genre and mood are both out of the picture. "Rock" is only a point in energy/valence/acousticness space. which is reflected in there being synthwave, pop, and hiphop in what's supposed to be just rock music. The song list themselves have too many genres with a thin song population, where there's 15 genres with only 1 song. Users who want some more dark song options won't get it in this dataset, only two songs have a valence below 4% with the highest average being 90%. That being said, if we used more of the features that came with a Song, things could even out. User preferences could be more specific and interactive, where there could be dislikes or skip behaviors. Energy and acousticness are basically the same thing. Loud songs are almost always not acoustic, so the system counts one preference twice. It gives that one preference 65% of the score. Each user is only one point. If someone likes both workout music and sleep music, the system picks something in the middle that fits neither. Also everyone gets the same weights. Some people care more about mood than energy, but the system can’t adjust for that. Scoring tends to favor users with middle-of-the-road tastes and those who match the dataset's patterns. There's lots of rock and lofi but energetic acoustic isn't something in the set.

---

## Reflection

[**Model Card**](model_card.md)

The biggest learning point for me would be the actual nature of music recommendation in the real world. Learning about it conceptually and then getting to make it in a small scale really helped me understand the technical setup, even if it's just a glimpse. In my brain, I thought valence and energy were a lot more seperated than they ended up being. I imagined it could measure mood and energy, but clearly this was something the needs more attributes to balance the scales, much like actual Spotify. Ai definitely helped in keeping my head straight with so many parts moving around during implementation and a sort of data expert for me to consult and see what my results were telling me. If I had more time, I would love to implement a more nusanced system including all features and some more weight changes to make everything work as accurately as possible over a broad range of users.