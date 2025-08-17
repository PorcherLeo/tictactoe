from typing import List, Tuple, Optional
import random

VIDE = " "
JOUEURS = ("X", "O")

Plateau = List[List[str]]

def nouveau_plateau() -> Plateau:
    return [[VIDE for _ in range(3)] for _ in range(3)]

def print_plateau(p: Plateau) -> None:
    print("   0   1   2")
    for i, row in enumerate(p):
        print(f"{i}  {row[0]} | {row[1]} | {row[2]}")
        if i < 2:
            print("  ---+---+---")

def lignes_colonnes_diagonales(p: Plateau):
    for i in range(3):  # lignes
        yield p[i]
    for j in range(3):  # colonnes
        yield [p[0][j], p[1][j], p[2][j]]
    yield [p[0][0], p[1][1], p[2][2]]      # diagonales
    yield [p[2][0], p[1][1], p[0][2]]

def victoire(p: Plateau, joueur: str) -> bool:
    return any(all(c == joueur for c in ligne) for ligne in lignes_colonnes_diagonales(p))

def plateau_plein(p: Plateau) -> bool:
    return all(c != VIDE for row in p for c in row)

def coups_libres(p: Plateau) -> List[Tuple[int,int]]:
    return [(r, c) for r in range(3) for c in range(3) if p[r][c] == VIDE]

def demander_coup(p: Plateau, joueur: str) -> Tuple[int,int]:
    while True:
        move = input(f"Joueur {joueur}, (ligne colonne) : ").strip().split()
        if len(move) != 2 or not all(m.isdigit() for m in move): print("Format invalide. Ex: 1 2"); continue
        r, c = map(int, move)
        if not (0 <= r <= 2 and 0 <= c <= 2): print("Indices 0..2 uniquement."); continue
        if p[r][c] != VIDE: print("Case déjà prise."); continue
        return r, c

# -----------------------------
# BOT FACILE : choix aléatoire
# -----------------------------
def bot_facile(p: Plateau, symbole_bot: str, symbole_humain: str) -> Tuple[int,int]:
    return random.choice(coups_libres(p))

# ----------------------------------------
# BOT MOYEN : gagner, bloquer, puis greedy
# ----------------------------------------
def bot_moyen(p: Plateau, symbole_bot: str, symbole_humain: str) -> Tuple[int,int]:
    # 1) Si je peux gagner en 1 coup, je le prends
    for r, c in coups_libres(p):
        p[r][c] = symbole_bot
        if victoire(p, symbole_bot):
            p[r][c] = VIDE
            return (r, c)
        p[r][c] = VIDE
    # 2) Sinon, si l'humain peut gagner au prochain, je bloque
    for r, c in coups_libres(p):
        p[r][c] = symbole_humain
        if victoire(p, symbole_humain):
            p[r][c] = VIDE
            return (r, c)
        p[r][c] = VIDE
    # 3) Sinon, on privilégie centre, coins, puis random
    if p[1][1] == VIDE: 
        return (1,1)
    for (r,c) in [(0,0),(0,2),(2,0),(2,2)]:
        if p[r][c] == VIDE:
            return (r,c)
    return bot_facile(p, symbole_bot, symbole_humain)

# --------------------------------
# BOT DIFFICILE : minimax + alphaβ
# --------------------------------
def score_terminal(p: Plateau, bot: str, humain: str) -> Optional[int]:
    if victoire(p, bot):   return 1
    if victoire(p, humain):return -1
    if plateau_plein(p):   return 0
    return None

def minimax(p: Plateau, bot: str, humain: str, joueur_actuel: str, alpha: int, beta: int) -> Tuple[int, Optional[Tuple[int,int]]]:
    # Retourne (score, coup)
    s = score_terminal(p, bot, humain)
    if s is not None:
        return s, None

    best_move = None
    if joueur_actuel == bot:
        best_score = -10
        for r, c in coups_libres(p):
            p[r][c] = bot
            sc, _ = minimax(p, bot, humain, humain, alpha, beta)
            p[r][c] = VIDE
            if sc > best_score:
                best_score, best_move = sc, (r, c)
            alpha = max(alpha, sc)
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = 10
        for r, c in coups_libres(p):
            p[r][c] = humain
            sc, _ = minimax(p, bot, humain, bot, alpha, beta)
            p[r][c] = VIDE
            if sc < best_score:
                best_score, best_move = sc, (r, c)
            beta = min(beta, sc)
            if beta <= alpha:
                break
        return best_score, best_move

def bot_difficile(p: Plateau, symbole_bot: str, symbole_humain: str) -> Tuple[int,int]:
    _, move = minimax(p, symbole_bot, symbole_humain, symbole_bot, -10, 10)
    return move if move else random.choice(coups_libres(p))

# -------------------------
# Boucle de jeu avec un bot
# -------------------------
def choisir_bot() -> str:
    while True:
        c = input("Choisis la difficulté du bot (facile/moyen/difficile) : ").strip().lower()
        if c in ("facile","moyen","difficile"): return c
        print("Réponse invalide.")

def jouer_vs_bot():
    p = nouveau_plateau()
    humain = input("Tu joues X ou O ? ").strip().upper()
    if humain not in JOUEURS:
        humain = "X"
    bot = "O" if humain == "X" else "X"
    niveau = choisir_bot()

    bot_fn = {"facile": bot_facile, "moyen": bot_moyen, "difficile": bot_difficile}[niveau]

    joueur = "X"  # X commence toujours
    while True:
        print_plateau(p)
        if joueur == humain:
            r, c = demander_coup(p, humain)
        else:
            r, c = bot_fn(p, bot, humain)
            print(f"(bot {niveau}) joue {r} {c}")
        p[r][c] = joueur

        if victoire(p, joueur):
            print_plateau(p)
            msg = "Tu as gagné !" if joueur == humain else f"Le bot {niveau} gagne !"
            print("🏁", msg)
            break
        if plateau_plein(p):
            print_plateau(p)
            print("🤝 Égalité.")
            break
        joueur = "O" if joueur == "X" else "X"

if __name__ == "__main__":
    random.seed()  # pour varier le bot facile/moyen
    jouer_vs_bot()
