"""
Problem 11: GPS-Based City Route Finder
Algorithm : A* Search
GUI       : tkinter + Canvas visualisation
"""

import tkinter as tk
from tkinter import messagebox, ttk
import heapq
import math
import time

# ─────────────────────────────────────────────
#  PALETTE
# ─────────────────────────────────────────────
BG         = "#0d1117"
PANEL      = "#161b22"
CARD       = "#21262d"
BORDER     = "#30363d"
ACCENT     = "#58a6ff"
ACCENT2    = "#3fb950"
WARN       = "#f78166"
GOLD       = "#e3b341"
TEXT       = "#c9d1d9"
TEXT_DIM   = "#8b949e"
NODE_CLR   = "#1f6feb"
NODE_PATH  = "#3fb950"
NODE_START = "#e3b341"
NODE_GOAL  = "#f78166"
EDGE_CLR   = "#30363d"
EDGE_PATH  = "#3fb950"
NODE_EXP   = "#8957e5"   # explored but not in final path


# ─────────────────────────────────────────────
#  A* ALGORITHM
# ─────────────────────────────────────────────
def astar(graph, heuristics, start, goal):
    """
    Returns (path, total_cost, explored_order) or (None, inf, explored)
    explored_order is the order in which nodes were POPPED from the open set.
    """
    open_heap = []          # (f, g, node)
    heapq.heappush(open_heap, (heuristics.get(start, 0), 0, start))

    came_from = {}
    g_score   = {n: math.inf for n in graph}
    g_score[start] = 0
    explored  = []
    in_open   = {start}

    while open_heap:
        f, g, current = heapq.heappop(open_heap)
        in_open.discard(current)

        if current not in explored:
            explored.append(current)

        if current == goal:
            # Reconstruct
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, g_score[goal], explored

        for neighbour, w in graph.get(current, []):
            tentative_g = g_score[current] + w
            if tentative_g < g_score.get(neighbour, math.inf):
                came_from[neighbour] = current
                g_score[neighbour]   = tentative_g
                f_new = tentative_g + heuristics.get(neighbour, 0)
                heapq.heappush(open_heap, (f_new, tentative_g, neighbour))
                in_open.add(neighbour)

    return None, math.inf, explored


# ─────────────────────────────────────────────
#  SAMPLE DATA (from assignment)
# ─────────────────────────────────────────────
SAMPLE_EDGES = [
    ("A", "B", 1), ("A", "C", 4),
    ("B", "D", 2), ("B", "E", 5),
    ("C", "D", 1),
    ("D", "F", 3),
    ("E", "F", 1),
]
SAMPLE_HEUR = {"A": 7, "B": 6, "C": 4, "D": 2, "E": 1, "F": 0}


# ─────────────────────────────────────────────
#  APP
# ─────────────────────────────────────────────
class CityRouteFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GPS City Route Finder  |  A* Algorithm")
        self.root.configure(bg=BG)
        self.root.minsize(900, 620)

        self.graph      = {}      # node -> [(neighbour, cost), …]
        self.heuristics = {}      # node -> h-value
        self.nodes      = []      # ordered list of nodes

        self.last_path     = None
        self.last_explored = []

        self._build_ui()
        self._load_sample()

    # ── UI ────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # HEADER
        hdr = tk.Frame(root, bg=BG)
        hdr.pack(fill="x", padx=20, pady=(14, 6))
        tk.Label(hdr, text="🗺  GPS CITY ROUTE FINDER",
                 font=("Courier", 18, "bold"), bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text="A* Search Algorithm",
                 font=("Courier", 10), bg=BG, fg=TEXT_DIM).pack(side="left", padx=12)

        # BODY  (left panel + right canvas+results)
        body = tk.Frame(root, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=4)

        # ── LEFT ──────────────────────────────
        left = tk.Frame(body, bg=PANEL, width=280)
        left.pack(side="left", fill="y", padx=(0, 8), pady=4)
        left.pack_propagate(False)

        self._section(left, "ADD EDGE  (undirected)")

        self.e_from = self._entry_row(left, "From :")
        self.e_to   = self._entry_row(left, "To   :")
        self.e_cost = self._entry_row(left, "Cost :")

        tk.Button(left, text="➕  Add Edge", font=("Courier", 9, "bold"),
                  bg=ACCENT2, fg=BG, relief="flat", padx=8, pady=4,
                  cursor="hand2", command=self._add_edge).pack(padx=14, pady=(2, 10))

        self._section(left, "SET HEURISTIC  h(n)")
        self.e_hnode = self._entry_row(left, "Node :")
        self.e_hval  = self._entry_row(left, "h(n) :")

        tk.Button(left, text="➕  Set Heuristic", font=("Courier", 9, "bold"),
                  bg=NODE_CLR, fg=TEXT, relief="flat", padx=8, pady=4,
                  cursor="hand2", command=self._set_heuristic).pack(padx=14, pady=(2, 10))

        self._section(left, "SEARCH")
        self.e_start = self._entry_row(left, "Start:")
        self.e_goal  = self._entry_row(left, "Goal :")

        tk.Button(left, text="🔍  Find Route  (A*)", font=("Courier", 10, "bold"),
                  bg=WARN, fg=BG, relief="flat", padx=10, pady=6,
                  cursor="hand2", command=self._run_astar).pack(padx=14, pady=(4, 6))

        sep = tk.Frame(left, bg=BORDER, height=1)
        sep.pack(fill="x", padx=14, pady=6)

        # Control buttons
        for lbl, cmd in [("📋  Load Sample", self._load_sample),
                          ("🗑   Clear All",   self._clear_all)]:
            tk.Button(left, text=lbl, font=("Courier", 9),
                      bg=CARD, fg=TEXT, relief="flat", padx=8, pady=4,
                      cursor="hand2", command=cmd).pack(padx=14, pady=3, fill="x")

        # Heuristic list
        self._section(left, "HEURISTICS  (h values)")
        self.h_listbox = tk.Listbox(left, bg=CARD, fg=ACCENT, font=("Courier", 9),
                                    relief="flat", bd=0, height=6,
                                    selectbackground=BORDER)
        self.h_listbox.pack(fill="x", padx=14, pady=(0, 8))

        # Edge list
        self._section(left, "EDGES")
        self.edge_listbox = tk.Listbox(left, bg=CARD, fg=TEXT_DIM, font=("Courier", 9),
                                       relief="flat", bd=0, height=8,
                                       selectbackground=BORDER)
        self.edge_listbox.pack(fill="x", padx=14, pady=(0, 10))

        # ── RIGHT ─────────────────────────────
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, pady=4)

        # Canvas
        canvas_frame = tk.Frame(right, bg=BORDER, padx=1, pady=1)
        canvas_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw_graph())

        # Legend
        leg = tk.Frame(right, bg=PANEL)
        leg.pack(fill="x", pady=(4, 0))
        for clr, lbl in [(NODE_START, "Start"), (NODE_GOAL, "Goal"),
                          (NODE_PATH, "Path"), (NODE_EXP, "Explored"),
                          (NODE_CLR,  "Other")]:
            dot = tk.Canvas(leg, width=12, height=12, bg=PANEL, highlightthickness=0)
            dot.pack(side="left", padx=(8, 2))
            dot.create_oval(1, 1, 11, 11, fill=clr, outline="")
            tk.Label(leg, text=lbl, font=("Courier", 8), bg=PANEL, fg=TEXT_DIM).pack(side="left")

        # Result text
        res_frame = tk.Frame(right, bg=PANEL)
        res_frame.pack(fill="x", pady=(4, 0))
        tk.Label(res_frame, text="RESULT", font=("Courier", 9, "bold"),
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w", padx=8, pady=(6, 2))
        self.result_text = tk.Text(res_frame, height=9, bg=CARD, fg=ACCENT2,
                                   font=("Courier", 9), relief="flat",
                                   state="disabled", wrap="word",
                                   insertbackground=TEXT)
        self.result_text.pack(fill="x", padx=8, pady=(0, 8))

    # ── WIDGET HELPERS ────────────────────────
    def _section(self, parent, label):
        tk.Label(parent, text=label, font=("Courier", 8, "bold"),
                 bg=PANEL, fg=TEXT_DIM).pack(anchor="w", padx=14, pady=(10, 2))

    def _entry_row(self, parent, label):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", padx=14, pady=2)
        tk.Label(row, text=label, font=("Courier", 9), bg=PANEL,
                 fg=TEXT, width=6, anchor="w").pack(side="left")
        var = tk.StringVar()
        tk.Entry(row, textvariable=var, font=("Courier", 9),
                 bg=CARD, fg=TEXT, insertbackground=TEXT,
                 relief="flat", bd=4, width=14).pack(side="left", padx=4)
        return var

    # ── GRAPH OPERATIONS ──────────────────────
    def _add_edge(self):
        frm  = self.e_from.get().strip().upper()
        to   = self.e_to.get().strip().upper()
        try:
            cost = float(self.e_cost.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Cost must be a number!", parent=self.root)
            return
        if not frm or not to:
            messagebox.showerror("Input Error", "Node names cannot be empty!", parent=self.root)
            return
        if frm == to:
            messagebox.showerror("Input Error", "Self-loops are not allowed!", parent=self.root)
            return

        for n in (frm, to):
            if n not in self.graph:
                self.graph[n] = []
                self.nodes.append(n)

        # Avoid duplicate edges
        if not any(nb == to for nb, _ in self.graph[frm]):
            self.graph[frm].append((to, cost))
            self.graph[to].append((frm, cost))

        self.e_from.set(""); self.e_to.set(""); self.e_cost.set("")
        self._refresh_lists()
        self._draw_graph()

    def _set_heuristic(self):
        node = self.e_hnode.get().strip().upper()
        try:
            val = float(self.e_hval.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "h(n) must be a number!", parent=self.root)
            return
        if not node:
            messagebox.showerror("Input Error", "Node name cannot be empty!", parent=self.root)
            return
        self.heuristics[node] = val
        self.e_hnode.set(""); self.e_hval.set("")
        self._refresh_lists()

    def _refresh_lists(self):
        self.h_listbox.delete(0, "end")
        for n, v in sorted(self.heuristics.items()):
            self.h_listbox.insert("end", f"  h({n}) = {v}")

        self.edge_listbox.delete(0, "end")
        drawn = set()
        for n in self.graph:
            for nb, c in self.graph[n]:
                key = tuple(sorted([n, nb]))
                if key not in drawn:
                    drawn.add(key)
                    self.edge_listbox.insert("end", f"  {n} ─── {nb}  (cost {c})")

    def _clear_all(self):
        self.graph = {}; self.heuristics = {}; self.nodes = []
        self.last_path = None; self.last_explored = []
        self._refresh_lists()
        self.canvas.delete("all")
        self._set_result("")

    def _load_sample(self):
        self._clear_all()
        for frm, to, cost in SAMPLE_EDGES:
            for n in (frm, to):
                if n not in self.graph:
                    self.graph[n] = []; self.nodes.append(n)
            self.graph[frm].append((to, cost))
            self.graph[to].append((frm, cost))
        self.heuristics = dict(SAMPLE_HEUR)
        self.e_start.set("A"); self.e_goal.set("F")
        self._refresh_lists()
        self._draw_graph()

    # ── A* SEARCH ─────────────────────────────
    def _run_astar(self):
        start = self.e_start.get().strip().upper()
        goal  = self.e_goal.get().strip().upper()

        if not start or not goal:
            messagebox.showerror("Error", "Enter start and goal nodes!", parent=self.root)
            return
        if start not in self.graph:
            messagebox.showerror("Error", f"Node '{start}' not in graph.", parent=self.root)
            return
        if goal not in self.graph:
            messagebox.showerror("Error", f"Node '{goal}' not in graph.", parent=self.root)
            return

        t0 = time.perf_counter()
        path, cost, explored = astar(self.graph, self.heuristics, start, goal)
        elapsed = time.perf_counter() - t0

        self.last_path     = path
        self.last_explored = explored
        self._draw_graph(start=start, goal=goal)

        if path is None:
            self._set_result(f"❌  No path found from  {start}  →  {goal}\n\n"
                             f"Nodes explored : {', '.join(explored)}")
            return

        # Cost breakdown
        lines = ["✅  OPTIMAL PATH FOUND\n",
                 "=" * 44,
                 f"🛣   Path : {' → '.join(path)}\n",
                 "💰  Cost Breakdown :"]
        total = 0
        for i in range(len(path) - 1):
            seg = next((c for n, c in self.graph[path[i]] if n == path[i+1]), 0)
            total += seg
            lines.append(f"      {path[i]} → {path[i+1]}  :  {seg}")
        lines += [f"\n🏁  Total Cost : {cost}",
                  f"⏱   Search Time : {elapsed*1000:.3f} ms",
                  f"\n🔍  Nodes Explored ({len(explored)}) : {', '.join(explored)}",
                  "\n📐  Heuristics :"]
        for n, v in sorted(self.heuristics.items()):
            if n in self.graph:
                lines.append(f"      h({n}) = {v}")

        self._set_result("\n".join(lines))

    # ── RESULT TEXT ───────────────────────────
    def _set_result(self, text):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", text)
        self.result_text.config(state="disabled")

    # ── GRAPH VISUALISATION ───────────────────
    def _draw_graph(self, start=None, goal=None):
        self.canvas.delete("all")
        if not self.nodes:
            return

        W = self.canvas.winfo_width()  or 580
        H = self.canvas.winfo_height() or 340

        cx, cy = W // 2, H // 2
        r = min(W, H) // 2 - 50

        # Arrange nodes in circle
        sorted_nodes = sorted(self.nodes)
        n = len(sorted_nodes)
        positions = {}
        for i, node in enumerate(sorted_nodes):
            angle = 2 * math.pi * i / n - math.pi / 2
            positions[node] = (cx + r * math.cos(angle),
                               cy + r * math.sin(angle))

        path_set  = set()
        path_edges = set()
        if self.last_path:
            path_set = set(self.last_path)
            for i in range(len(self.last_path) - 1):
                path_edges.add(tuple(sorted([self.last_path[i], self.last_path[i+1]])))

        explored_set = set(self.last_explored)

        # Draw edges
        drawn = set()
        for node in self.graph:
            if node not in positions:
                continue
            for nb, cost in self.graph[node]:
                if nb not in positions:
                    continue
                key = tuple(sorted([node, nb]))
                if key in drawn:
                    continue
                drawn.add(key)

                x1, y1 = positions[node]
                x2, y2 = positions[nb]
                is_path = key in path_edges
                clr = EDGE_PATH if is_path else EDGE_CLR
                wid = 3 if is_path else 1
                self.canvas.create_line(x1, y1, x2, y2, fill=clr, width=wid,
                                        smooth=True)
                mx, my = (x1+x2)/2, (y1+y2)/2
                self.canvas.create_text(mx, my, text=str(int(cost)),
                                        fill="#e3b341", font=("Courier", 8, "bold"))

        # Draw nodes
        R = 20
        for node, (x, y) in positions.items():
            if node == start:
                clr = NODE_START
            elif node == goal:
                clr = NODE_GOAL
            elif self.last_path and node in path_set:
                clr = NODE_PATH
            elif node in explored_set:
                clr = NODE_EXP
            else:
                clr = NODE_CLR

            self.canvas.create_oval(x-R, y-R, x+R, y+R,
                                    fill=clr, outline="white", width=2)
            self.canvas.create_text(x, y, text=node,
                                    fill="white", font=("Courier", 11, "bold"))

            h = self.heuristics.get(node)
            if h is not None:
                self.canvas.create_text(x, y + R + 10, text=f"h={int(h)}",
                                        fill=TEXT_DIM, font=("Courier", 7))


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = CityRouteFinder(root)
    root.mainloop()