"""
AI 2002 - Assignment 1 - Question 7
GOOD PERFORMANCE TIME APP
AI Pathfinder - 6 Uninformed Search Algorithms with Dynamic Obstacles
"""

import pygame
import sys
import random
import time
from collections import deque
import heapq

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
WINDOW_W, WINDOW_H = 1100, 750
GRID_COLS, GRID_ROWS = 20, 18
CELL = 34
GRID_OFFSET_X = 60
GRID_OFFSET_Y = 120
PANEL_X = GRID_OFFSET_X + GRID_COLS * CELL + 20

FPS = 60
STEP_DELAY = 0.06          # seconds between algorithm steps
DYN_PROB   = 0.018          # probability a dynamic obstacle spawns per step
DLS_LIMIT  = 8             # depth limit for DLS

# Colours
BG          = (18,  18,  30)
GRID_LINE   = (40,  40,  60)
WHITE       = (230, 230, 240)
BLACK       = (0,   0,   0)
START_C     = (0,   200, 80)
TARGET_C    = (220, 50,  50)
WALL_C      = (60,  60,  80)
FRONTIER_C  = (50,  120, 240)
EXPLORED_C  = (180, 60,  200)
PATH_C      = (255, 210, 0)
DYN_WALL_C  = (220, 100, 0)
EMPTY_C     = (28,  28,  46)
BTN_NORMAL  = (40,  80,  160)
BTN_HOVER   = (60,  120, 220)
BTN_ACTIVE  = (30,  200, 110)
BTN_DIS     = (50,  50,  70)
TEXT_C      = (220, 220, 255)
PANEL_BG    = (22,  22,  40)
ACCENT      = (80,  180, 255)
WARN_C      = (255, 160, 30)
INFO_C      = (100, 220, 200)

# Movement: Up, Right, Down, Down-Right, Left, Top-Left, Top-Right, Down-Left (all 8 dirs)
DIRECTIONS = [(-1,0),(0,1),(1,0),(1,1),(0,-1),(-1,-1),(-1,1),(1,-1)]
DIR_NAMES  = ["Up","Right","Down","Down-Right","Left","Top-Left","Top-Right","Down-Left"]

ALGORITHMS = ["BFS","DFS","UCS","DLS","IDDFS","Bidirectional"]

ALG_COLORS = {
    "BFS":          (50,  160, 255),
    "DFS":          (200, 80,  200),
    "UCS":          (80,  220, 150),
    "DLS":          (255, 160, 50),
    "IDDFS":        (255, 80,  80),
    "Bidirectional":(80,  230, 230),
}

# ─────────────────────────────────────────────
#  GRID
# ─────────────────────────────────────────────
class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.walls = set()
        self.dyn_walls = set()
        self.start  = (rows-2, 1)
        self.target = (1, cols-2)

    def reset_walls(self):
        self.walls.clear()
        self.dyn_walls.clear()

    def random_walls(self, density=0.22):
        self.walls.clear()
        self.dyn_walls.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                if (r,c) in (self.start, self.target):
                    continue
                if random.random() < density:
                    self.walls.add((r,c))

    def is_blocked(self, r, c):
        return (r,c) in self.walls or (r,c) in self.dyn_walls

    def in_bounds(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols

    def neighbors(self, r, c):
        result = []
        for dr, dc in DIRECTIONS:
            nr, nc = r+dr, c+dc
            if self.in_bounds(nr, nc) and not self.is_blocked(nr, nc):
                cost = 1.4 if (dr != 0 and dc != 0) else 1.0
                result.append((nr, nc, cost))
        return result

    def spawn_dynamic(self, current_path=None):
        """Spawn a dynamic obstacle; returns True if path is blocked."""
        candidates = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r,c) not in self.walls and (r,c) not in self.dyn_walls:
                    if (r,c) != self.start and (r,c) != self.target:
                        candidates.append((r,c))
        if not candidates:
            return False
        pos = random.choice(candidates)
        self.dyn_walls.add(pos)
        if current_path and pos in current_path:
            return True
        return False


# ─────────────────────────────────────────────
#  SEARCH ALGORITHMS
# ─────────────────────────────────────────────
def reconstruct(came_from, start, target):
    path = []
    cur = target
    while cur != start:
        path.append(cur)
        cur = came_from.get(cur)
        if cur is None:
            return []
    path.append(start)
    path.reverse()
    return path

def bfs_gen(grid):
    """Yields (frontier_set, explored_set, path) step by step."""
    start, target = grid.start, grid.target
    queue = deque([start])
    came_from = {start: None}
    explored = set()
    frontier = {start}

    while queue:
        node = queue.popleft()
        frontier.discard(node)
        if node == target:
            path = reconstruct(came_from, start, target)
            yield frontier.copy(), explored.copy(), path
            return
        explored.add(node)
        for nr, nc, _ in grid.neighbors(*node):
            nxt = (nr, nc)
            if nxt not in came_from:
                came_from[nxt] = node
                queue.append(nxt)
                frontier.add(nxt)
        yield frontier.copy(), explored.copy(), []
    yield frontier.copy(), explored.copy(), []

def dfs_gen(grid):
    start, target = grid.start, grid.target
    stack = [start]
    came_from = {start: None}
    explored = set()
    frontier = {start}

    while stack:
        node = stack.pop()
        frontier.discard(node)
        if node in explored:
            yield frontier.copy(), explored.copy(), []
            continue
        if node == target:
            path = reconstruct(came_from, start, target)
            yield frontier.copy(), explored.copy(), path
            return
        explored.add(node)
        for nr, nc, _ in grid.neighbors(*node):
            nxt = (nr, nc)
            if nxt not in explored:
                came_from[nxt] = node
                stack.append(nxt)
                frontier.add(nxt)
        yield frontier.copy(), explored.copy(), []
    yield frontier.copy(), explored.copy(), []

def ucs_gen(grid):
    start, target = grid.start, grid.target
    pq = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    explored = set()
    frontier = {start}

    while pq:
        cost, node = heapq.heappop(pq)
        frontier.discard(node)
        if node == target:
            path = reconstruct(came_from, start, target)
            yield frontier.copy(), explored.copy(), path
            return
        if node in explored:
            yield frontier.copy(), explored.copy(), []
            continue
        explored.add(node)
        for nr, nc, move_cost in grid.neighbors(*node):
            nxt = (nr, nc)
            new_cost = cost + move_cost
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                came_from[nxt] = node
                heapq.heappush(pq, (new_cost, nxt))
                frontier.add(nxt)
        yield frontier.copy(), explored.copy(), []
    yield frontier.copy(), explored.copy(), []

def dls_gen(grid, limit=DLS_LIMIT):
    start, target = grid.start, grid.target
    # Iterative stack: (node, depth, path_so_far)
    stack = [(start, 0, [start])]
    explored = set()
    frontier = {start}

    while stack:
        node, depth, path = stack.pop()
        frontier.discard(node)
        if node == target:
            yield frontier.copy(), explored.copy(), path
            return
        explored.add(node)
        if depth < limit:
            for nr, nc, _ in grid.neighbors(*node):
                nxt = (nr, nc)
                if nxt not in explored:
                    stack.append((nxt, depth+1, path+[nxt]))
                    frontier.add(nxt)
        yield frontier.copy(), explored.copy(), []
    yield frontier.copy(), explored.copy(), []

def iddfs_gen(grid):
    start, target = grid.start, grid.target
    max_depth = grid.rows * grid.cols

    for limit in range(1, max_depth + 1):
        stack = [(start, 0, [start])]
        explored = set()
        frontier = {start}
        found = False

        while stack:
            node, depth, path = stack.pop()
            frontier.discard(node)
            if node == target:
                yield frontier.copy(), explored.copy(), path
                return
            explored.add(node)
            if depth < limit:
                for nr, nc, _ in grid.neighbors(*node):
                    nxt = (nr, nc)
                    if nxt not in explored:
                        stack.append((nxt, depth+1, path+[nxt]))
                        frontier.add(nxt)
            yield frontier.copy(), explored.copy(), []
    yield set(), set(), []

def bidirectional_gen(grid):
    start, target = grid.start, grid.target
    fwd_queue  = deque([start])
    bwd_queue  = deque([target])
    fwd_came   = {start: None}
    bwd_came   = {target: None}
    fwd_vis    = {start}
    bwd_vis    = {target}
    frontier   = {start, target}
    explored   = set()

    def build_path(meet):
        # forward half
        path_f = []
        cur = meet
        while cur is not None:
            path_f.append(cur)
            cur = fwd_came.get(cur)
        path_f.reverse()
        # backward half
        path_b = []
        cur = bwd_came.get(meet)
        while cur is not None:
            path_b.append(cur)
            cur = bwd_came.get(cur)
        return path_f + path_b

    while fwd_queue or bwd_queue:
        # Forward step
        if fwd_queue:
            node = fwd_queue.popleft()
            frontier.discard(node)
            explored.add(node)
            if node in bwd_vis:
                path = build_path(node)
                yield frontier.copy(), explored.copy(), path
                return
            for nr, nc, _ in grid.neighbors(*node):
                nxt = (nr, nc)
                if nxt not in fwd_vis:
                    fwd_vis.add(nxt)
                    fwd_came[nxt] = node
                    fwd_queue.append(nxt)
                    frontier.add(nxt)

        # Backward step
        if bwd_queue:
            node = bwd_queue.popleft()
            frontier.discard(node)
            explored.add(node)
            if node in fwd_vis:
                path = build_path(node)
                yield frontier.copy(), explored.copy(), path
                return
            for nr, nc, _ in grid.neighbors(*node):
                nxt = (nr, nc)
                if nxt not in bwd_vis:
                    bwd_vis.add(nxt)
                    bwd_came[nxt] = node
                    bwd_queue.append(nxt)
                    frontier.add(nxt)

        yield frontier.copy(), explored.copy(), []
    yield set(), set(), []


# ─────────────────────────────────────────────
#  BUTTON
# ─────────────────────────────────────────────
class Button:
    def __init__(self, rect, text, color=BTN_NORMAL, font=None):
        self.rect  = pygame.Rect(rect)
        self.text  = text
        self.color = color
        self.font  = font
        self.hovered  = False
        self.disabled = False

    def draw(self, surf):
        if self.disabled:
            col = BTN_DIS
        elif self.hovered:
            col = BTN_HOVER
        else:
            col = self.color
        pygame.draw.rect(surf, col, self.rect, border_radius=7)
        pygame.draw.rect(surf, ACCENT, self.rect, 2, border_radius=7)
        if self.font:
            lbl = self.font.render(self.text, True, WHITE)
            surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos) and not self.disabled

    def is_clicked(self, pos, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(pos) and
                not self.disabled)


# ─────────────────────────────────────────────
#  MAIN APP
# ─────────────────────────────────────────────
class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("GOOD PERFORMANCE TIME APP")
        self.clock  = pygame.time.Clock()

        # Fonts
        self.font_lg  = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_md  = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_sm  = pygame.font.SysFont("consolas", 13)
        self.font_xl  = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_ti  = pygame.font.SysFont("consolas", 20, bold=True)

        self.grid = Grid(GRID_ROWS, GRID_COLS)
        self.grid.random_walls()

        # State
        self.state   = "menu"   # menu | running | paused | done
        self.alg_idx = 0
        self.gen     = None
        self.frontier  = set()
        self.explored  = set()
        self.path      = []
        self.last_step = 0
        self.step_count = 0
        self.replanned  = 0
        self.message    = ""
        self.msg_timer  = 0
        self.draw_mode  = None   # None | 'wall' | 'erase'

        self._build_ui()
        self.show_menu = True

    # ── UI BUILD ──────────────────────────────
    def _build_ui(self):
        bw, bh = 200, 36
        bx = PANEL_X + 10

        # Algorithm selection buttons
        self.alg_btns = []
        for i, name in enumerate(ALGORITHMS):
            col = ALG_COLORS[name]
            btn = Button((bx, 130 + i*46, bw, 38), name,
                         color=col, font=self.font_md)
            self.alg_btns.append(btn)

        # Control buttons
        self.btn_start   = Button((bx, 430, bw, 38), "▶  START",   BTN_ACTIVE,  self.font_md)
        self.btn_pause   = Button((bx, 476, bw, 38), "⏸  PAUSE",   BTN_NORMAL,  self.font_md)
        self.btn_reset   = Button((bx, 522, bw, 38), "↺  RESET",   BTN_NORMAL,  self.font_md)
        self.btn_regen   = Button((bx, 568, bw, 38), "⊞  NEW MAZE",BTN_NORMAL,  self.font_md)
        self.btn_clear   = Button((bx, 614, bw, 38), "✕  CLEAR",   (120,40,60), self.font_md)
        self.btn_step    = Button((bx, 660, bw, 38), "⏭  STEP",    (60,60,120), self.font_md)

        self.ctrl_btns = [self.btn_start, self.btn_pause,
                          self.btn_reset, self.btn_regen,
                          self.btn_clear, self.btn_step]

    # ── DRAWING ───────────────────────────────
    def _cell_rect(self, r, c):
        x = GRID_OFFSET_X + c * CELL
        y = GRID_OFFSET_Y + r * CELL
        return pygame.Rect(x, y, CELL-1, CELL-1)

    def draw_grid(self):
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                rect = self._cell_rect(r, c)
                pos  = (r, c)

                if pos == self.grid.start:
                    col = START_C
                elif pos == self.grid.target:
                    col = TARGET_C
                elif pos in self.grid.walls:
                    col = WALL_C
                elif pos in self.grid.dyn_walls:
                    col = DYN_WALL_C
                elif pos in self.path:
                    col = PATH_C
                elif pos in self.frontier:
                    col = FRONTIER_C
                elif pos in self.explored:
                    col = EXPLORED_C
                else:
                    col = EMPTY_C

                pygame.draw.rect(self.screen, col, rect, border_radius=3)

        # Grid border
        bx = GRID_OFFSET_X - 2
        by = GRID_OFFSET_Y - 2
        bw = GRID_COLS * CELL + 2
        bh = GRID_ROWS * CELL + 2
        pygame.draw.rect(self.screen, ACCENT, (bx, by, bw, bh), 2, border_radius=4)

    def draw_panel(self):
        # Panel background
        pygame.draw.rect(self.screen, PANEL_BG,
                         (PANEL_X, 0, WINDOW_W - PANEL_X, WINDOW_H))
        pygame.draw.line(self.screen, ACCENT, (PANEL_X, 0), (PANEL_X, WINDOW_H), 2)

        bx = PANEL_X + 10

        # Title
        t = self.font_lg.render("SELECT ALGORITHM", True, ACCENT)
        self.screen.blit(t, (bx, 95))

        # Algorithm buttons
        for i, btn in enumerate(self.alg_btns):
            is_sel = (i == self.alg_idx)
            btn.draw(self.screen)
            if is_sel:
                pygame.draw.rect(self.screen, WHITE,
                                 btn.rect.inflate(4, 4), 2, border_radius=9)

        # Control buttons
        for btn in self.ctrl_btns:
            btn.draw(self.screen)

        # Stats
        stats_y = 710
        alg = ALGORITHMS[self.alg_idx]
        self.screen.blit(self.font_sm.render(f"Algo : {alg}", True, INFO_C), (bx, stats_y - 60))
        self.screen.blit(self.font_sm.render(f"Steps: {self.step_count}", True, INFO_C), (bx, stats_y - 40))
        self.screen.blit(self.font_sm.render(f"ReplanEvents: {self.replanned}", True, WARN_C), (bx, stats_y - 20))

        # Legend
        legend = [
            (START_C,    "Start"),
            (TARGET_C,   "Target"),
            (WALL_C,     "Static Wall"),
            (DYN_WALL_C, "Dynamic Wall"),
            (FRONTIER_C, "Frontier"),
            (EXPLORED_C, "Explored"),
            (PATH_C,     "Path"),
        ]
        lx, ly = GRID_OFFSET_X, GRID_OFFSET_Y + GRID_ROWS * CELL + 12
        for col, label in legend:
            pygame.draw.rect(self.screen, col, (lx, ly, 16, 16), border_radius=3)
            lbl = self.font_sm.render(label, True, TEXT_C)
            self.screen.blit(lbl, (lx + 20, ly))
            lx += lbl.get_width() + 44
            if lx > GRID_OFFSET_X + GRID_COLS * CELL - 40:
                lx = GRID_OFFSET_X
                ly += 22

    def draw_header(self):
        # Header bar
        pygame.draw.rect(self.screen, (12, 12, 24), (0, 0, WINDOW_W, 88))
        pygame.draw.line(self.screen, ACCENT, (0, 88), (WINDOW_W, 88), 2)

        title = self.font_xl.render("GOOD PERFORMANCE TIME APP", True, ACCENT)
        self.screen.blit(title, (20, 10))

        alg = ALGORITHMS[self.alg_idx]
        sub = self.font_ti.render(f"Algorithm: {alg}  |  State: {self.state.upper()}",
                                  True, ALG_COLORS[alg])
        self.screen.blit(sub, (20, 46))

        tip = self.font_sm.render("LMB: place wall   RMB: erase wall   Drag on grid",
                                  True, (120, 120, 160))
        self.screen.blit(tip, (20, 70))

    def draw_message(self):
        if self.message and time.time() < self.msg_timer:
            surf = self.font_md.render(self.message, True, WARN_C)
            x = GRID_OFFSET_X + (GRID_COLS * CELL - surf.get_width()) // 2
            y = GRID_OFFSET_Y + GRID_ROWS * CELL // 2 - 12
            bg = pygame.Surface((surf.get_width()+20, surf.get_height()+10), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 180))
            self.screen.blit(bg, (x-10, y-5))
            self.screen.blit(surf, (x, y))

    def show_message(self, msg, duration=2.5):
        self.message   = msg
        self.msg_timer = time.time() + duration

    # ── ALGORITHM RUNNER ──────────────────────
    def start_algorithm(self):
        self.frontier   = set()
        self.explored   = set()
        self.path       = []
        self.step_count = 0
        self.replanned  = 0
        self.last_step  = time.time()
        alg = ALGORITHMS[self.alg_idx]

        if alg == "BFS":
            self.gen = bfs_gen(self.grid)
        elif alg == "DFS":
            self.gen = dfs_gen(self.grid)
        elif alg == "UCS":
            self.gen = ucs_gen(self.grid)
        elif alg == "DLS":
            self.gen = dls_gen(self.grid, DLS_LIMIT)
        elif alg == "IDDFS":
            self.gen = iddfs_gen(self.grid)
        elif alg == "Bidirectional":
            self.gen = bidirectional_gen(self.grid)

        self.state = "running"

    def step_algorithm(self):
        if self.gen is None:
            return
        try:
            frontier, explored, path = next(self.gen)
            self.frontier   = frontier
            self.explored   = explored
            self.step_count += 1

            # Dynamic obstacle
            if random.random() < DYN_PROB:
                blocked = self.grid.spawn_dynamic(
                    current_path=self.path if self.path else None)
                if blocked:
                    self.replanned += 1
                    self.show_message(f"⚠ Dynamic obstacle! Re-planning... #{self.replanned}")
                    self.start_algorithm()
                    return

            if path:
                self.path  = path
                self.state = "done"
                self.gen   = None
                self.show_message(f"✔ Path found! Length: {len(path)}  Steps: {self.step_count}")

        except StopIteration:
            self.state = "done"
            self.gen   = None
            if not self.path:
                self.show_message("✘ No path found!")

    # ── EVENT HANDLING ────────────────────────
    def handle_events(self):
        mouse = pygame.mouse.get_pos()
        for btn in self.alg_btns + self.ctrl_btns:
            btn.check_hover(mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == "running":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "running"
                    elif self.state in ("menu","done"):
                        self.start_algorithm()
                if event.key == pygame.K_r:
                    self._do_reset()
                if event.key == pygame.K_n:
                    self._do_new_maze()
                if event.key == pygame.K_RIGHT and self.state == "paused":
                    self.step_algorithm()
                # Algo hotkeys 1-6
                for i in range(len(ALGORITHMS)):
                    if event.key == getattr(pygame, f"K_{i+1}", None):
                        self.alg_idx = i

            # Mouse on grid (wall painting)
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.draw_mode = 'wall'
                    elif event.button == 3:
                        self.draw_mode = 'erase'
                if self.draw_mode and self.state in ("menu","done","paused"):
                    r, c = self._grid_pos(mouse)
                    if r is not None:
                        if (r,c) not in (self.grid.start, self.grid.target):
                            if self.draw_mode == 'wall':
                                self.grid.walls.add((r,c))
                                self.grid.dyn_walls.discard((r,c))
                            else:
                                self.grid.walls.discard((r,c))
                                self.grid.dyn_walls.discard((r,c))

            if event.type == pygame.MOUSEBUTTONUP:
                self.draw_mode = None

            # Button clicks
            for i, btn in enumerate(self.alg_btns):
                if btn.is_clicked(mouse, event):
                    self.alg_idx = i

            if self.btn_start.is_clicked(mouse, event):
                self.start_algorithm()

            if self.btn_pause.is_clicked(mouse, event):
                if self.state == "running":
                    self.state = "paused"
                    self.btn_pause.text = "▶  RESUME"
                elif self.state == "paused":
                    self.state = "running"
                    self.btn_pause.text = "⏸  PAUSE"

            if self.btn_reset.is_clicked(mouse, event):
                self._do_reset()

            if self.btn_regen.is_clicked(mouse, event):
                self._do_new_maze()

            if self.btn_clear.is_clicked(mouse, event):
                self.grid.reset_walls()
                self._do_reset()

            if self.btn_step.is_clicked(mouse, event):
                if self.state == "running":
                    self.state = "paused"
                    self.btn_pause.text = "▶  RESUME"
                if self.state == "paused":
                    self.step_algorithm()

    def _grid_pos(self, mouse):
        mx, my = mouse
        c = (mx - GRID_OFFSET_X) // CELL
        r = (my - GRID_OFFSET_Y) // CELL
        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
            return r, c
        return None, None

    def _do_reset(self):
        self.frontier   = set()
        self.explored   = set()
        self.path       = []
        self.step_count = 0
        self.replanned  = 0
        self.gen        = None
        self.grid.dyn_walls.clear()
        self.state       = "menu"
        self.btn_pause.text = "⏸  PAUSE"

    def _do_new_maze(self):
        self._do_reset()
        self.grid.random_walls()

    # ── MAIN LOOP ─────────────────────────────
    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()

            # Auto-step
            if self.state == "running":
                now = time.time()
                if now - self.last_step >= STEP_DELAY:
                    self.step_algorithm()
                    self.last_step = now

            # Draw
            self.screen.fill(BG)
            self.draw_grid()
            self.draw_panel()
            self.draw_header()
            self.draw_message()

            # "Press SPACE to start" hint
            if self.state == "menu":
                hint = self.font_md.render(
                    "Select an algorithm → Press START or SPACE",
                    True, (160, 160, 200))
                hx = GRID_OFFSET_X + (GRID_COLS*CELL - hint.get_width())//2
                hy = GRID_OFFSET_Y + GRID_ROWS*CELL//2 - 10
                self.screen.blit(hint, (hx, hy))

            pygame.display.flip()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    App().run()