# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

VibeFlow v1.0

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

For my recommender system, I've selected three attributes, energy, valence, and acousticness. I find these to be the important in the general sense. It encompasses the most information about a song while relying on numbers instead of arbitrary labels. I reward songs for their closeness, where the values of a song match or almost match a user's existing preference scores. Closeness is calculatd with '1- |song_value - target|.' 1 is considered a perfect song and linearly falls off where 0 is the most distance there is. Also the closness goes both ways, so a score can be 0.1 below and above a target but still have the same weight. So, each attribute will have its closeness calculated and averaged with a weight to each. In my case, I will be giving energy 40%, valence 35% and acousticness 25%. This is the Scoring Rule. For the Ranking Rule, there's 5 steps. First we calculate the score for each song in the list. Then, we remove songs that the user has already heard or in the "seed" set. We sort by score with the highest on top. If there's a tie, we use the valence score to score for the highest between the ties. If they're the same score still, then the songs are just sorted by id. Finally we return the top K. (Ex. 3, 5, 10...)

With the definitions set, the recommender file itself need to represent the scaffolding. The UserProfile comes with its default values (except favorite_genre and favorite_mood) with some changes and additions. The likes_acoustic boolean becomes a float since we're dealing with numbers. The Song object has a wrapper object that contains the song itself, its score, the attribute scores, and the valence gap. This is added because the Ranking Rule needs the gap for tie-breaking and explain_recommendation() can then read the attribute scores without recalculating them.

Some biases that I uncovered were all based on the dataset. Energy and acousticness are inversely related. When most songs have a high energy and a low acousticness and visa versa, they carry quite a bit of the score, around 65%. Acousticness is also polarized which seperates songs. This is the opposite case with valence. As a result, it's energy and acousticness on top and valence to the side.

Compared to Spotify's recommender, the streaming platform uses more sophistacated approaches. It uses collaborative filtering, which compares users with similiar listening habits and any new songs one of them listen to, will be recommended to those that haven't. They also utlize something like the system I created where it analysis the songs themselves. But they also scan the internet for trends and uses AI systems. On top of analyzing user behavior, they also convert songs into graphs of data where clusters of similar songs can be recommended.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
