# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



