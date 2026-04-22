"""
Problem 1: Interactive Game AI - Tic-Tac-Toe
Algorithms: Minimax & Alpha-Beta Pruning
GUI: tkinter
"""

import tkinter as tk
from tkinter import messagebox
import time
import math

# ─────────────────────────────────────────────
#  COLORS & CONSTANTS
# ─────────────────────────────────────────────
BG         = "#0f0e17"
PANEL      = "#1a1a2e"
CARD       = "#16213e"
ACCENT_RED = "#e94560"
ACCENT_GRN = "#4ecca3"
ACCENT_YLW = "#f5a623"
TEXT_DIM   = "#a8b2d8"
TEXT_LIGHT = "#fffffe"
CELL_BG    = "#1a1a2e"
CELL_HOV   = "#0f3460"

WINNING_COMBOS = [
    (0,1,2),(3,4,5),(6,7,8),   # rows
    (0,3,6),(1,4,7),(2,5,8),   # cols
    (0,4,8),(2,4,6)            # diags
]

# ─────────────────────────────────────────────
#  MINIMAX (no pruning)
# ─────────────────────────────────────────────
def minimax(board, depth, is_max, nodes):
    nodes[0] += 1
    w = winner(board)
    if w == "O": return 10 - depth
    if w == "X": return depth - 10
    if all(c != "" for c in board): return 0

    if is_max:
        best = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                best = max(best, minimax(board, depth+1, False, nodes))
                board[i] = ""
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                best = min(best, minimax(board, depth+1, True, nodes))
                board[i] = ""
        return best

# ─────────────────────────────────────────────
#  MINIMAX WITH ALPHA-BETA PRUNING
# ─────────────────────────────────────────────
def minimax_ab(board, depth, is_max, alpha, beta, nodes):
    nodes[0] += 1
    w = winner(board)
    if w == "O": return 10 - depth
    if w == "X": return depth - 10
    if all(c != "" for c in board): return 0

    if is_max:
        best = -math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                val = minimax_ab(board, depth+1, False, alpha, beta, nodes)
                board[i] = ""
                best = max(best, val)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
        return best
    else:
        best = math.inf
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                val = minimax_ab(board, depth+1, True, alpha, beta, nodes)
                board[i] = ""
                best = min(best, val)
                beta = min(beta, best)
                if beta <= alpha:
                    break
        return best

# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────
def winner(board):
    for a, b, c in WINNING_COMBOS:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

def best_move(board, algo):
    nodes = [0]
    best_score = -math.inf
    move = -1
    t0 = time.perf_counter()

    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            if algo == "minimax":
                score = minimax(board, 0, False, nodes)
            else:
                score = minimax_ab(board, 0, False, -math.inf, math.inf, nodes)
            board[i] = ""
            if score > best_score:
                best_score = score
                move = i

    elapsed = time.perf_counter() - t0
    return move, elapsed, nodes[0]

def compare_from_empty():
    """Run both algos from a completely empty board and collect stats."""
    results = {}
    for algo in ("minimax", "minimax_ab"):
        nodes = [0]
        board = [""] * 9
        t0 = time.perf_counter()
        for i in range(9):
            board[i] = "O"
            if algo == "minimax":
                minimax(board, 0, False, nodes)
            else:
                minimax_ab(board, 0, False, -math.inf, math.inf, nodes)
            board[i] = ""
        elapsed = time.perf_counter() - t0
        results[algo] = (elapsed, nodes[0])
    return results


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Tic-Tac-Toe  |  Minimax vs Alpha-Beta")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.board = [""] * 9
        self.game_active = False
        self.algo_var = tk.StringVar(value="alphabeta")

        # Per-game stat accumulators
        self.mm_stats  = {"time": None, "nodes": None}
        self.ab_stats  = {"time": None, "nodes": None}

        self._build_ui()
        self._update_stats_display()

    # ── UI BUILD ───────────────────────────────
    def _build_ui(self):
        root = self.root

        # ── HEADER ──
        hdr = tk.Frame(root, bg=BG)
        hdr.pack(pady=(18, 4))
        tk.Label(hdr, text="TIC-TAC-TOE  AI", font=("Courier", 22, "bold"),
                 bg=BG, fg=ACCENT_RED).pack()
        tk.Label(hdr, text="Minimax  vs  Alpha-Beta Pruning",
                 font=("Courier", 10), bg=BG, fg=TEXT_DIM).pack()

        # ── ALGORITHM SELECTOR ──
        algo_bar = tk.Frame(root, bg=PANEL, pady=6)
        algo_bar.pack(fill="x", padx=24, pady=(6, 0))
        tk.Label(algo_bar, text="AI Algorithm:", font=("Courier", 10, "bold"),
                 bg=PANEL, fg=TEXT_LIGHT).pack(side="left", padx=12)
        for val, lbl, clr in [("minimax", "Minimax", ACCENT_RED),
                               ("alphabeta", "Alpha-Beta Pruning", ACCENT_GRN)]:
            tk.Radiobutton(algo_bar, text=lbl, variable=self.algo_var, value=val,
                           bg=PANEL, fg=clr, selectcolor=CARD,
                           activebackground=PANEL, font=("Courier", 10),
                           command=self._on_algo_change).pack(side="left", padx=10)

        # ── STATUS LABEL ──
        self.status_var = tk.StringVar(value="Press  [ NEW GAME ]  to start")
        self.status_lbl = tk.Label(root, textvariable=self.status_var,
                                   font=("Courier", 12, "bold"),
                                   bg=BG, fg=ACCENT_YLW)
        self.status_lbl.pack(pady=10)

        # ── BOARD ──
        board_outer = tk.Frame(root, bg=ACCENT_RED, padx=3, pady=3)
        board_outer.pack(padx=30)
        board_inner = tk.Frame(board_outer, bg=ACCENT_RED)
        board_inner.pack()

        self.btns = []
        for i in range(9):
            r, c = divmod(i, 3)
            btn = tk.Button(board_inner, text="", font=("Courier", 38, "bold"),
                            width=3, height=1,
                            bg=CELL_BG, fg=TEXT_LIGHT,
                            relief="flat", bd=0,
                            activebackground=CELL_HOV,
                            cursor="hand2",
                            command=lambda idx=i: self._human_move(idx))
            btn.grid(row=r, column=c, padx=2, pady=2, ipadx=8, ipady=4)
            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=CELL_HOV) if b["state"]=="normal" else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=CELL_BG))
            self.btns.append(btn)

        # ── STATS PANEL ──
        stats_outer = tk.Frame(root, bg=PANEL)
        stats_outer.pack(fill="x", padx=24, pady=12)
        tk.Label(stats_outer, text="PERFORMANCE STATS",
                 font=("Courier", 9, "bold"), bg=PANEL, fg=TEXT_DIM).pack(pady=(8,4))

        cols = tk.Frame(stats_outer, bg=PANEL)
        cols.pack(fill="x", padx=10, pady=(0,8))

        # Minimax card
        mm_card = tk.Frame(cols, bg=CARD, relief="flat", bd=0)
        mm_card.pack(side="left", expand=True, fill="both", padx=6)
        tk.Label(mm_card, text="Minimax", font=("Courier", 10, "bold"),
                 bg=CARD, fg=ACCENT_RED).pack(pady=(8,2))
        self.mm_time_lbl = tk.Label(mm_card, text="Time : —",
                                    font=("Courier", 9), bg=CARD, fg=TEXT_DIM)
        self.mm_time_lbl.pack()
        self.mm_nodes_lbl = tk.Label(mm_card, text="Nodes : —",
                                     font=("Courier", 9), bg=CARD, fg=TEXT_DIM)
        self.mm_nodes_lbl.pack(pady=(0,8))

        # Alpha-Beta card
        ab_card = tk.Frame(cols, bg=CARD, relief="flat", bd=0)
        ab_card.pack(side="left", expand=True, fill="both", padx=6)
        tk.Label(ab_card, text="Alpha-Beta", font=("Courier", 10, "bold"),
                 bg=CARD, fg=ACCENT_GRN).pack(pady=(8,2))
        self.ab_time_lbl = tk.Label(ab_card, text="Time : —",
                                    font=("Courier", 9), bg=CARD, fg=TEXT_DIM)
        self.ab_time_lbl.pack()
        self.ab_nodes_lbl = tk.Label(ab_card, text="Nodes : —",
                                     font=("Courier", 9), bg=CARD, fg=TEXT_DIM)
        self.ab_nodes_lbl.pack(pady=(0,8))

        # ── CONTROL BUTTONS ──
        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(pady=(0, 18))

        tk.Button(ctrl, text="  NEW GAME  ", font=("Courier", 11, "bold"),
                  bg=ACCENT_RED, fg=TEXT_LIGHT, relief="flat",
                  padx=14, pady=7, cursor="hand2",
                  command=self._new_game).pack(side="left", padx=8)

        tk.Button(ctrl, text="  COMPARE BOTH  ", font=("Courier", 11, "bold"),
                  bg=ACCENT_GRN, fg=BG, relief="flat",
                  padx=14, pady=7, cursor="hand2",
                  command=self._compare).pack(side="left", padx=8)

    # ── GAME LOGIC ─────────────────────────────
    def _new_game(self):
        self.board = [""] * 9
        self.game_active = True
        for btn in self.btns:
            btn.config(text="", bg=CELL_BG, fg=TEXT_LIGHT,
                       state="normal", font=("Courier", 38, "bold"))
        self.status_var.set("Your turn  ✕  (Human)")
        self.mm_stats = {"time": None, "nodes": None}
        self.ab_stats = {"time": None, "nodes": None}
        self._update_stats_display()

    def _on_algo_change(self):
        if not self.game_active:
            self._update_stats_display()

    def _human_move(self, idx):
        if not self.game_active or self.board[idx]:
            return
        self.board[idx] = "X"
        self.btns[idx].config(text="✕", fg=ACCENT_RED)

        w = winner(self.board)
        if w:
            self._end_game("You Win! 🎉", "X")
            return
        if all(c for c in self.board):
            self._end_game("Draw  🤝", None)
            return

        self.status_var.set("AI thinking…")
        self.root.update()
        self._ai_move()

    def _ai_move(self):
        algo = self.algo_var.get()
        move, elapsed, nodes = best_move(self.board, algo)

        if algo == "minimax":
            self.mm_stats = {"time": elapsed * 1000, "nodes": nodes}
        else:
            self.ab_stats = {"time": elapsed * 1000, "nodes": nodes}
        self._update_stats_display()

        if move == -1:
            self._end_game("Draw  🤝", None)
            return

        self.board[move] = "O"
        self.btns[move].config(text="○", fg=ACCENT_GRN)

        w = winner(self.board)
        if w:
            self._end_game("AI Wins! 🤖", "O")
            return
        if all(c for c in self.board):
            self._end_game("Draw  🤝", None)
            return

        self.status_var.set("Your turn  ✕  (Human)")

    def _end_game(self, msg, win_player):
        self.game_active = False
        self.status_var.set(msg)
        if win_player:
            color = ACCENT_RED if win_player == "X" else ACCENT_GRN
            for a, b, c in WINNING_COMBOS:
                if self.board[a] == self.board[b] == self.board[c] == win_player:
                    for idx in (a, b, c):
                        self.btns[idx].config(bg=color)
        for btn in self.btns:
            btn.config(state="disabled")

    def _update_stats_display(self):
        def fmt_time(v):
            return f"Time  : {v:.3f} ms" if v is not None else "Time  : —"
        def fmt_nodes(v):
            return f"Nodes : {v:,}" if v is not None else "Nodes : —"

        self.mm_time_lbl.config(text=fmt_time(self.mm_stats["time"]))
        self.mm_nodes_lbl.config(text=fmt_nodes(self.mm_stats["nodes"]))
        self.ab_time_lbl.config(text=fmt_time(self.ab_stats["time"]))
        self.ab_nodes_lbl.config(text=fmt_nodes(self.ab_stats["nodes"]))

    def _compare(self):
        self.status_var.set("Benchmarking both algorithms…")
        self.root.update()
        res = compare_from_empty()

        mm_t, mm_n = res["minimax"]
        ab_t, ab_n = res["minimax_ab"]

        self.mm_stats = {"time": mm_t * 1000, "nodes": mm_n}
        self.ab_stats = {"time": ab_t * 1000, "nodes": ab_n}
        self._update_stats_display()

        speedup   = mm_t / ab_t if ab_t > 0 else float("inf")
        node_red  = (1 - ab_n / mm_n) * 100 if mm_n > 0 else 0
        winner_lbl = "Alpha-Beta is FASTER ✅" if ab_t < mm_t else "Both are equal"

        messagebox.showinfo(
            "Algorithm Comparison (Fresh Board)",
            f"{'='*42}\n"
            f"  Minimax (no pruning)\n"
            f"    Time  : {mm_t*1000:.3f} ms\n"
            f"    Nodes : {mm_n:,}\n\n"
            f"  Alpha-Beta Pruning\n"
            f"    Time  : {ab_t*1000:.3f} ms\n"
            f"    Nodes : {ab_n:,}\n"
            f"{'='*42}\n"
            f"  Speed-up    : {speedup:.1f}× faster\n"
            f"  Node reduction : {node_red:.1f}% fewer\n\n"
            f"  {winner_lbl}"
        )
        self.status_var.set("Benchmark done — press New Game to play")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()