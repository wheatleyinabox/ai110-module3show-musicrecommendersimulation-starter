# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

VibeFlow v1.0

---

## 2. Intended Use

It’s a content-based recommender. You tell it your target energy, valence (how happy or dark) and acousticness, and it ranks songs by how closely they match, skipping songs you’ve already heard. It assumes your taste is one fixed point, that those three features are enough to describe taste, that all users weigh them the same way, and that being close in either direction is equally good. It doesn’t learn from behavior like skips or replays. With only 20 songs, hand-written taste profiles and hard-coded test expectations, this is clearly a classroom exploration project rather than something built for real users. It’s a good model for learning how scoring and ranking work, but it isn’t ready to serve real listeners.

---

## 3. How the Model Works

For my recommender system, I've selected three attributes, energy, valence, and acousticness. I find these to be the important in the general sense. It encompasses the most information about a song while relying on numbers instead of arbitrary labels. I reward songs for their closeness, where the values of a song match or almost match a user's existing preference scores. Closeness is calculatd with '1- |song_value - target|.' 1 is considered a perfect song and linearly falls off where 0 is the most distance there is. Also the closness goes both ways, so a score can be 0.1 below and above a target but still have the same weight. So, each attribute will have its closeness calculated and averaged with a weight to each. In my case, I will be giving energy 40%, valence 35% and acousticness 25%. This is the Scoring Rule. For the Ranking Rule, there's 5 steps. First we calculate the score for each song in the list. Then, we remove songs that the user has already heard or in the "seed" set. We sort by score with the highest on top. If there's a tie, we use the valence score to score for the highest between the ties. If they're the same score still, then the songs are just sorted by id. Finally we return the top K. (Ex. 3, 5, 10...)

With the definitions set, the recommender file itself need to represent the scaffolding. The UserProfile comes with its default values (except favorite_genre and favorite_mood) with some changes and additions. The likes_acoustic boolean becomes a float since we're dealing with numbers. The Song object has a wrapper object that contains the song itself, its score, the attribute scores, and the valence gap. This is added because the Ranking Rule needs the gap for tie-breaking and explain_recommendation() can then read the attribute scores without recalculating them.

Some biases that I uncovered were all based on the dataset. Energy and acousticness are inversely related. When most songs have a high energy and a low acousticness and visa versa, they carry quite a bit of the score, around 65%. Acousticness is also polarized which seperates songs. This is the opposite case with valence. As a result, it's energy and acousticness on top and valence to the side.

Compared to Spotify's recommender, the streaming platform uses more sophistacated approaches. It uses collaborative filtering, which compares users with similiar listening habits and any new songs one of them listen to, will be recommended to those that haven't. They also utlize something like the system I created where it analysis the songs themselves. But they also scan the internet for trends and uses AI systems. On top of analyzing user behavior, they also convert songs into graphs of data where clusters of similar songs can be recommended.

---

## 4. Data

The dataset uses 20 songs, with 20 unique ids. Each has a title, artist, genre, mood and five numeric features: energy, tempo, valence, danceability and acousticness. There are 17 genres, but they’re very uneven. Lofi has 3 songs and pop has 2. The other 15 (rock, metal, jazz, classical, folk, blues, latin, edm, r&b, reggae, country, hip hop, synthwave, ambient and indie pop) have one each. Moods are similar: 16 in total, with chill at 3, happy and intense at 2 each, and 13 moods like angry, romantic and nostalgic appearing only once. With one song per genre or mood, the system can’t tell whether it likes the genre or just that one song. Only two artists appear more than once (Neon Echo and LoRoom, 2 songs each). 

---

## 5. Strengths

The system gets the basics right. Scores are easy to understand: each feature is scored by how close the song is to what you want, then combined with fixed weights. Your tests show it separates different tastes well. Rock, lofi, pop and sad-acoustic profiles each get sensible top picks, and the rock and lofi top 5 lists don’t overlap at all. It also behaves predictably. Ties are broken the same way every time, the order doesn’t depend on how the catalog is arranged, and removing seen songs doesn’t scramble the rest. Even the “conflicted” profile behaves sensibly: it finds no strong match, and its best score stays low, which is the honest answer. The explanations are also a plus, since each recommendation says how close it was on each feature.

---

## 6. Limitations and Bias

In terms of filter bubbles and underrepresentation, a big limitation is that there's no representation. Genre and mood are both out of the picture. "Rock" is only a point in energy/valence/acousticness space. which is reflected in there being synthwave, pop, and hiphop in what's supposed to be just rock music. The song list themselves have too many genres with a thin song population, where there's 15 genres with only 1 song. Users who want some more dark song options won't get it in this dataset, only two songs have a valence below 4% with the highest average being 90%. That being said, if we used more of the features that came with a Song, things could even out. User preferences could be more specific and interactive, where there could be dislikes or skip behaviors. Energy and acousticness are basically the same thing. Loud songs are almost always not acoustic, so the system counts one preference twice. It gives that one preference 65% of the score. Each user is only one point. If someone likes both workout music and sleep music, the system picks something in the middle that fits neither. Also everyone gets the same weights. Some people care more about mood than energy, but the system can’t adjust for that. Scoring tends to favor users with middle-of-the-road tastes and those who match the dataset's patterns. There's lots of rock and lofi but energetic acoustic isn't something in the set.

---

## 7. Evaluation

The user profiles used to test out the system exist in 5 categories: Intense Rock (High energy, decent valence, low acousticness), Chill Lofi (High acousticness, decent valence, minimal acousticness), Happy Pop (High energy, high valence, minimal acousticness), Sad Acoustic (minimal energy and valence, high acousticness), and Conflicted songs (decent valence). The last being an edge case that adds a higher energy and acousticness since it's lacking in the existing profiles. Seeing how the system handles conflicting songs.

The recommendations are actually pretty accurate to what I expected in the profiles, with the oddballs in the conflicted profile. The only thing that surprises me is the Intense Rock profile. With a dataset of rock scarcity, it's interesting how the more pop songs ended up on the list. I assume it's being weight more on energy that anything else, which make sense based on the definition. Given the lists, I think there's a good diversity, without too much overlap between at most one song noticable repeating.

As an experment, I decided to remove energy from the equation with a Feature Removal test. Given that is has the most weight, I'm curious to see that just valence and acousticness make up for. Interestingly, there were no real surprises to the profiles, except for the conflicted profile once again. Intense Rock contained the same 5 songs with some slight differences. Night Drive Loop moves above Iron Requirem and Gym Hero drops from 4th to 5th. Chill Lofi get a replacement with Coffee Shop Stories falling out and Pulse Cathedral coming into 5th. Happy Pop has the same trend, with Pulse Cathedral coming in and Concrete Clown dropping out. For Sad Acoustic, Crossroad Blues replaces Focus Flow which makes more sense for the category now. Finally conflicted had the most change, where Crossroad Blues, Night Drive Loop, and Storm Runner falling out completely from the top 3. What I can see is that energy is doing much seperating work, valence and acousticness work well by themselves. Instead, it's more of a tie-breaker between songs of close valence and acousticness. And clearly we can see the energy makes the most of the conflicted profile.

---

## 8. Future Work

The biggest gains would come from using more of the data. Genre and mood could add a small bonus, and tempo and danceability could help separate songs that otherwise look identical. Users could set their own weights, or you could drop or merge energy and acousticness, since they mostly measure the same thing. For diversity, the top 5 could be limited to one song per artist or genre, so lofi fans don’t see three near-identical tracks. For complex tastes, a user could have several profiles, like “workout” and “study”, or a range instead of a single target point. Explanations could also say why a song ranks above the next one, for example “it beat song X because its mood was closer”, and could be written in plain sentences instead of numbers. Finally, a bigger catalog with more dark and high-energy acoustic songs would fix a lot of the gaps on its own.

---

## 9. Personal Reflection

The biggest learning point for me would be the actual nature of music recommendation in the real world. Learning about it conceptually and then getting to make it in a small scale really helped me understand the technical setup, even if it's just a glimpse. In my brain, I thought valence and energy were a lot more seperated than they ended up being. I imagined it could measure mood and energy, but clearly this was something the needs more attributes to balance the scales, much like actual Spotify. Ai definitely helped in keeping my head straight with so many parts moving around during implementation and a sort of data expert for me to consult and see what my results were telling me. If I had more time, I would love to implement a more nusanced system including all features and some more weight changes to make everything work as accurately as possible over a broad range of users.