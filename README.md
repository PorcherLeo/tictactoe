# Tic-Tac-Toe (Morpion)

Un **morpion en Python** avec interface graphique Tkinter :  
animations, IA à plusieurs niveaux de difficulté, score, thèmes clair/sombre et effets visuels 🎉

---

## Fonctionnalités
- **Trois niveaux de bot** : Facile, Moyen (bloque/gagne), Difficile (minimax avec alpha-beta).  
- **Mode 1 joueur** (vs bot) ou **2 joueurs local**.  
- **Animations** des X et O (tracés progressifs).  
- **Surbrillance** au survol des cases.  
- **Ligne de victoire** et **confettis** à l’écran.  
- **Scoreboard** (X / O / égalités).  
- **Choix du symbole** de l’humain (X ou O).  
- **Thème clair / sombre** switchable.  

---

## Installation & lancement

### Prérequis
- Python **3.10+**
- Tkinter (inclus par défaut avec Python sur la plupart des systèmes)

### Étapes
```bash
# cloner le repo
git clone https://github.com/PorcherLeo/tictactoe.git
cd tictactoe

python3 -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows

# lancer le jeu
python3 morpion_gui.py
