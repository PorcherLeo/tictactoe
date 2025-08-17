import tkinter as tk
from tkinter import ttk
import random
import math
import time

# ======================== LOGIQUE =========================
VIDE = " "
JOUEURS = ("X", "O")

def lignes_colonnes_diagonales(board):
    for i in range(3):  # lignes
        yield [(i,0),(i,1),(i,2)]
    for j in range(3):  # colonnes
        yield [(0,j),(1,j),(2,j)]
    yield [(0,0),(1,1),(2,2)]
    yield [(2,0),(1,1),(0,2)]

def victoire(board, joueur):
    for coords in lignes_colonnes_diagonales(board):
        if all(board[r][c] == joueur for r,c in coords):
            return True, coords
    return False, None

def plateau_plein(board):
    return all(board[r][c] != VIDE for r in range(3) for c in range(3))

def coups_libres(board):
    return [(r,c) for r in range(3) for c in range(3) if board[r][c] == VIDE]

# --------- BOTS ----------
def bot_facile(board, bot, humain):
    return random.choice(coups_libres(board))

def bot_moyen(board, bot, humain):
    # 1) gagner si possible
    for r,c in coups_libres(board):
        board[r][c] = bot
        win,_ = victoire(board, bot)
        board[r][c] = VIDE
        if win: return (r,c)
    # 2) bloquer si humain gagne
    for r,c in coups_libres(board):
        board[r][c] = humain
        win,_ = victoire(board, humain)
        board[r][c] = VIDE
        if win: return (r,c)
    # 3) centre, coins, sinon random
    if board[1][1] == VIDE: return (1,1)
    for (r,c) in [(0,0),(0,2),(2,0),(2,2)]:
        if board[r][c] == VIDE: return (r,c)
    return bot_facile(board, bot, humain)

def score_terminal(board, bot, humain):
    win_bot,_ = victoire(board, bot)
    if win_bot: return 1
    win_h,_ = victoire(board, humain)
    if win_h: return -1
    if plateau_plein(board): return 0
    return None

def minimax(board, bot, humain, joueur, alpha, beta):
    s = score_terminal(board, bot, humain)
    if s is not None:
        return s, None
    best_move = None
    if joueur == bot:  # maximiser
        best = -10
        for r,c in coups_libres(board):
            board[r][c] = bot
            sc,_ = minimax(board, bot, humain, humain, alpha, beta)
            board[r][c] = VIDE
            if sc > best:
                best, best_move = sc, (r,c)
            alpha = max(alpha, sc)
            if beta <= alpha: break
        return best, best_move
    else:              # minimiser
        best = 10
        for r,c in coups_libres(board):
            board[r][c] = humain
            sc,_ = minimax(board, bot, humain, bot, alpha, beta)
            board[r][c] = VIDE
            if sc < best:
                best, best_move = sc, (r,c)
            beta = min(beta, sc)
            if beta <= alpha: break
        return best, best_move

def bot_difficile(board, bot, humain):
    _, move = minimax(board, bot, humain, bot, -10, 10)
    return move if move else bot_facile(board, bot, humain)

BOT_FNS = {"Facile": bot_facile, "Moyen": bot_moyen, "Difficile": bot_difficile}

# ======================== UI / GAMEPLAY =========================

class MorpionGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Morpion+  —  Canvas, animations & thèmes")
        self.root.geometry("540x520")
        self.root.resizable(False, False)

        self.theme = tk.StringVar(value="Clair")
        self.vs_bot = tk.BooleanVar(value=True)
        self.bot_level = tk.StringVar(value="Moyen")
        self.human_symbol = tk.StringVar(value="X")
        self.status_text = tk.StringVar(value="Prêt ? Cliquez sur une case.")
        self.score_x = 0
        self.score_o = 0
        self.score_draw = 0

        self.board = [[VIDE]*3 for _ in range(3)]
        self.current = "X"
        self.cell_size = 140
        self.margin = 20
        self.animating = False
        self.game_over = False
        self.win_coords = None
        self.confetti = []
        self.hover_cell = None

        self.colors = {
            "bg": "#fafafa",
            "grid": "#d0d0d0",
            "hover": "#2f6feb",
            "x": "#d4380d",
            "o": "#2f9e44",
            "text": "#111827",
            "win": "#f59f00",
            "confetti": ["#ff6b6b", "#ffd93d", "#6bcBef", "#b197fc", "#51cf66"],
        }

        self.build_ui()      
        self.apply_theme()
        self.draw_grid() 
        self.after_setup_start()


    # ---------- Construction UI ----------
    def build_ui(self):
        # Barre du haut
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Mode:").grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(top, text="Humain vs Bot", variable=self.vs_bot,
                        command=self.on_mode_change).grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(top, text="Niveau:").grid(row=0, column=2, sticky="e", padx=(12,0))
        self.combo_level = ttk.Combobox(top, values=list(BOT_FNS.keys()),
                                        textvariable=self.bot_level, width=10, state="readonly")
        self.combo_level.grid(row=0, column=3, sticky="w", padx=4)

        ttk.Label(top, text="Symbole humain:").grid(row=0, column=4, sticky="e", padx=(12,0))
        self.combo_sym = ttk.Combobox(top, values=["X", "O"],
                                      textvariable=self.human_symbol, width=4, state="readonly")
        self.combo_sym.grid(row=0, column=5, sticky="w", padx=4)
        self.combo_sym.bind("<<ComboboxSelected>>", lambda e: self.new_round(hard=True))

        ttk.Label(top, text="Thème:").grid(row=0, column=6, sticky="e", padx=(12,0))
        self.combo_theme = ttk.Combobox(top, values=["Clair", "Sombre"],
                                        textvariable=self.theme, width=8, state="readonly")
        self.combo_theme.grid(row=0, column=7, sticky="w")
        self.combo_theme.bind("<<ComboboxSelected>>", lambda e: self.apply_theme())

        ttk.Button(top, text="Nouvelle manche", command=lambda: self.new_round(hard=False)).grid(row=0, column=8, padx=(12,0))

        # Status + Score
        mid = ttk.Frame(self.root, padding=(10, 0, 10, 6))
        mid.pack(fill="x")
        self.status_lbl = ttk.Label(mid, textvariable=self.status_text, anchor="center")
        self.status_lbl.pack(fill="x", pady=(0,4))

        self.score_lbl = ttk.Label(mid, anchor="center")
        self.score_lbl.pack(fill="x")
        self.update_score_label()

        # Canvas
        w = h = self.margin*2 + self.cell_size*3
        self.canvas = tk.Canvas(self.root, width=w, height=h, highlightthickness=0, cursor="hand2")
        self.canvas.pack(padx=10, pady=10)

        # Boutons
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", lambda e: self.set_hover(None))

        # Grille
        self.draw_grid()

    def apply_theme(self):
        dark = self.theme.get() == "Sombre"
        self.colors = {
            "bg": "#0f1115" if dark else "#fafafa",
            "grid": "#2a2f3a" if dark else "#d0d0d0",
            "hover": "#1e90ff" if dark else "#2f6feb",
            "x": "#ff4d4f" if dark else "#d4380d",
            "o": "#40c463" if dark else "#2f9e44",
            "text": "#e6edf3" if dark else "#111827",
            "win": "#ffd43b" if dark else "#f59f00",
            "confetti": ["#ff6b6b", "#ffd93d", "#6bcBef", "#b197fc", "#51cf66"],
        }
        self.root.configure(bg=self.colors["bg"])
        self.canvas.configure(bg=self.colors["bg"])
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure(".", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("TButton", background=self.colors["bg"], foreground=self.colors["text"])
        style.configure("TCombobox", fieldbackground="#1f232a" if dark else "#ffffff",
                        background=self.colors["bg"], foreground=self.colors["text"])
        self.draw_grid(force=True)

    def after_setup_start(self):
        # Si humain choisit "O", bot peut commencer
        self.root.after(200, self.bot_turn_if_needed)

    # ---------- Helpers dessin ----------
    def cell_bounds(self, r, c):
        x0 = self.margin + c * self.cell_size
        y0 = self.margin + r * self.cell_size
        x1 = x0 + self.cell_size
        y1 = y0 + self.cell_size
        return x0, y0, x1, y1

    def draw_grid(self, force=False):
        self.canvas.delete("grid")
        # Grille
        for i in range(1,3):
            # vertical
            x = self.margin + i*self.cell_size
            self.canvas.create_line(x, self.margin, x, self.margin + 3*self.cell_size,
                                    fill=self.colors["grid"], width=3, tags="grid")
            # horizontal
            y = self.margin + i*self.cell_size
            self.canvas.create_line(self.margin, y, self.margin + 3*self.cell_size, y,
                                    fill=self.colors["grid"], width=3, tags="grid")

        if force:
            # Redessiner
            self.canvas.delete("mark")
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] in JOUEURS:
                        self.draw_mark_static(r, c, self.board[r][c])

        self.canvas.delete("winline")
        if self.win_coords:
            self.draw_win_line(self.win_coords)

    def draw_mark_static(self, r, c, sym):
        x0, y0, x1, y1 = self.cell_bounds(r, c)
        pad = 20
        if sym == "O":
            self.canvas.create_oval(x0+pad, y0+pad, x1-pad, y1-pad,
                                    outline=self.colors["o"], width=10, tags=("mark",))
        else:
            # X : deux segments
            self.canvas.create_line(x0+pad, y0+pad, x1-pad, y1-pad,
                                    fill=self.colors["x"], width=10, capstyle="round", tags=("mark",))
            self.canvas.create_line(x0+pad, y1-pad, x1-pad, y0+pad,
                                    fill=self.colors["x"], width=10, capstyle="round", tags=("mark",))

    def animate_mark(self, r, c, sym, steps=12, dur_ms=160):
        if self.animating:
            return
        self.animating = True
        x0, y0, x1, y1 = self.cell_bounds(r, c)
        pad = 20

        if sym == "O":
            oid = self.canvas.create_arc(
                x0+pad, y0+pad, x1-pad, y1-pad,
                start=0, extent=0, style="arc",
                outline=self.colors["o"], width=10, tags=("mark",)
            )
            def step(i=0):
                # on s’arrête à ~359.9 pour éviter le bug d’affichage du 360
                if i > steps:
                    # remplace l’arc par un cercle permanent
                    self.canvas.delete(oid)
                    self.canvas.create_oval(
                        x0+pad, y0+pad, x1-pad, y1-pad,
                        outline=self.colors["o"], width=10, tags=("mark",)
                    )
                    self.animating = False
                    return
                extent = 359.9 * (i/steps)
                self.canvas.itemconfig(oid, extent=extent)
                self.root.after(max(1, dur_ms//steps), step, i+1)
            step()
            return
        # --- X inchangé ---
        l1 = self.canvas.create_line(
            x0+pad, y0+pad, x0+pad, y0+pad,
            fill=self.colors["x"], width=10, capstyle="round", tags=("mark",)
        )
        l2 = self.canvas.create_line(
            x0+pad, y1-pad, x0+pad, y1-pad,
            fill=self.colors["x"], width=10, capstyle="round", tags=("mark",)
        )
        def step1(i=0):
            if i > steps:
                step2()
                return
            nx = x0+pad + (x1-pad - (x0+pad)) * (i/steps)
            ny = y0+pad + (y1-pad - (y0+pad)) * (i/steps)
            self.canvas.coords(l1, x0+pad, y0+pad, nx, ny)
            self.root.after(max(1, dur_ms//steps), step1, i+1)
        def step2(i=0):
            if i > steps:
                self.animating = False
                return
            nx = x0+pad + (x1-pad - (x0+pad)) * (i/steps)
            ny = y1-pad - (y1-pad - (y0+pad)) * (i/steps)
            self.canvas.coords(l2, x0+pad, y1-pad, nx, ny)
            self.root.after(max(1, dur_ms//steps), step2, i+1)
        step1()



    def draw_win_line(self, coords):
        # ligne sur les 3 cases gagnantes
        (r0,c0),(r1,c1),(r2,c2) = coords
        x0,y0,_,_ = self.cell_bounds(r0,c0)
        _,_,x3,y3 = self.cell_bounds(r2,c2)
        cx0 = x0 + self.cell_size/2
        cy0 = y0 + self.cell_size/2
        cx3 = x3 - self.cell_size/2
        cy3 = y3 - self.cell_size/2
        self.canvas.create_line(cx0, cy0, cx3, cy3, fill=self.colors["win"], width=8,
                                capstyle="round", tags="winline")

    def spawn_confetti(self, n=30):
        self.confetti = []
        w = self.canvas.winfo_width()
        for _ in range(n):
            x = random.randint(self.margin, self.margin + self.cell_size*3)
            y = random.randint(self.margin-40, self.margin)
            r = random.randint(3,6)
            col = random.choice(self.colors["confetti"])
            oid = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=col, outline="", tags="confetti")
            vx = random.uniform(-1.2, 1.2)
            vy = random.uniform(2.0, 3.5)
            self.confetti.append((oid, vx, vy))
        self.animate_confetti()

    def animate_confetti(self):
        alive = []
        for oid, vx, vy in self.confetti:
            x0, y0, x1, y1 = self.canvas.coords(oid)
            self.canvas.move(oid, vx, vy)
            if y1 < self.margin + self.cell_size*3 + 10:
                alive.append((oid, vx*0.99, vy*0.99 + 0.05))
            else:
                self.canvas.delete(oid)
        self.confetti = alive
        if self.game_over and self.confetti:
            self.root.after(16, self.animate_confetti)

    # ---------- Gameplay ----------
    def on_mode_change(self):
        self.new_round(hard=True)

    def update_score_label(self):
        self.score_lbl.config(text=f"Score — X: {self.score_x}   O: {self.score_o}   Égalités: {self.score_draw}")

    def set_status(self, msg):
        self.status_text.set(msg)

    def set_hover(self, cell):
        if self.hover_cell == cell:
            return
        self.hover_cell = cell
        self.canvas.delete("hover")
        if cell and not self.game_over:
            r, c = cell
            if self.board[r][c] == VIDE:
                x0,y0,x1,y1 = self.cell_bounds(r,c)
                self.canvas.create_rectangle(x0+2, y0+2, x1-2, y1-2,
                                             outline=self.colors["hover"], width=3, tags="hover")

    def on_motion(self, event):
        r = (event.y - self.margin) // self.cell_size
        c = (event.x - self.margin) // self.cell_size
        if 0 <= r < 3 and 0 <= c < 3:
            self.set_hover((int(r), int(c)))
        else:
            self.set_hover(None)

    def on_click(self, event):
        if self.animating or self.game_over:
            return
        r = (event.y - self.margin) // self.cell_size
        c = (event.x - self.margin) // self.cell_size
        if not (0 <= r < 3 and 0 <= c < 3):
            return
        r, c = int(r), int(c)
        if self.board[r][c] != VIDE:
            return
        if self.vs_bot.get() and self.current != self.human_symbol.get():
            return  # pas le tour de l'humain

        self.jouer(r, c)

    def jouer(self, r, c):
        # place et anime
        sym = self.current
        self.board[r][c] = sym
        self.animate_mark(r, c, sym)
        self.canvas.after(170, self.after_player_move)

    def after_player_move(self):
        if self.check_fin():
            return
        self.toggle()
        self.bot_turn_if_needed()

    def bot_turn_if_needed(self):
        if not self.vs_bot.get():
            self.set_status(f"À {self.current} de jouer")
            return
        humain = self.human_symbol.get()
        bot = "O" if humain == "X" else "X"
        if self.current == bot and not self.game_over:
            move = BOT_FNS[self.bot_level.get()](self.board, bot, humain)
            if move:
                r,c = move
                # petite pause pour le naturel
                self.root.after(180, lambda: self.place_bot_and_continue(r, c, bot))
        else:
            self.set_status(f"À {self.current} de jouer")

    def place_bot_and_continue(self, r, c, bot):
        if self.board[r][c] != VIDE or self.game_over:
            return
        self.board[r][c] = bot
        self.animate_mark(r, c, bot)
        self.canvas.after(170, self.after_bot_move)

    def after_bot_move(self):
        if self.check_fin():
            return
        self.toggle()
        self.set_status(f"À {self.current} de jouer")

    def toggle(self):
        self.current = "O" if self.current == "X" else "X"

    def check_fin(self):
        win, coords = victoire(self.board, self.current)
        if win:
            self.game_over = True
            self.win_coords = coords
            self.draw_grid(force=True)
            self.set_status(f"🎉 {self.current} gagne !  (Nouvelle manche pour continuer)")
            if self.current == "X":
                self.score_x += 1
            else:
                self.score_o += 1
            self.update_score_label()
            self.spawn_confetti(36)
            return True
        if plateau_plein(self.board):
            self.game_over = True
            self.set_status("🤝 Égalité.  (Nouvelle manche pour continuer)")
            self.score_draw += 1
            self.update_score_label()
            return True
        return False

    def new_round(self, hard=False):
        # hard=True réinitialise aussi qui commence selon symbole humain
        self.board = [[VIDE]*3 for _ in range(3)]
        self.game_over = False
        self.win_coords = None
        self.animating = False
        self.canvas.delete("mark")
        self.canvas.delete("winline")
        self.canvas.delete("hover")
        self.canvas.delete("confetti")
        self.draw_grid()
        if hard:
            self.current = "X"
        else:
            # on garde l'alternance: le perdant/second commence, sinon random au début
            pass
        self.set_status("Nouvelle manche !")
        # Si humain joue O, le bot commence
        humain = self.human_symbol.get()
        if humain == "O":
            self.current = "X"
        else:
            self.current = "X"
        self.root.after(200, self.bot_turn_if_needed)
        self.update_score_label()

# ======================== MAIN =========================

if __name__ == "__main__":
    random.seed()
    root = tk.Tk()
    app = MorpionGame(root)
    root.mainloop()
