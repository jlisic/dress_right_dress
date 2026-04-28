#!/usr/bin/env python3
"""
USAF Drill & Ceremony Command Simulator
Based on AFMAN 36-2203 — Drill and Ceremonies

A timed quiz game where players select the correct drill command
for various formation scenarios. Difficulty scales by leadership level.
"""

import pygame
import sys
import random
import math
import time

# ---------------------------------------------------------------------------
# INITIALISATION
# ---------------------------------------------------------------------------
pygame.init()

WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("USAF Drill & Ceremony — Command Simulator")

clock = pygame.time.Clock()
FPS = 60

# ---------------------------------------------------------------------------
# COLOURS  (Air-Force-blue palette)
# ---------------------------------------------------------------------------
C_BG           = (12, 18, 30)
C_PANEL        = (18, 28, 48)
C_PANEL_LIGHT  = (26, 40, 66)
C_AF_BLUE      = (0, 75, 135)
C_AF_BLUE_LT   = (0, 100, 170)
C_AF_GOLD      = (200, 170, 80)
C_AF_GOLD_DIM  = (140, 120, 60)
C_WHITE        = (225, 230, 240)
C_TEXT         = (190, 200, 215)
C_TEXT_DIM     = (110, 120, 140)
C_GREEN        = (40, 185, 100)
C_GREEN_DIM    = (25, 110, 60)
C_RED          = (210, 55, 55)
C_RED_DIM      = (140, 35, 35)
C_AMBER        = (220, 170, 40)
C_HIGHLIGHT    = (50, 130, 210)
C_PERSON       = (100, 160, 220)
C_PERSON_DIM   = (60, 95, 140)
C_GROUND       = (20, 32, 55)
C_GRID         = (30, 45, 70)
C_ARROW        = (220, 180, 60)

# ---------------------------------------------------------------------------
# FONTS
# ---------------------------------------------------------------------------
FONT_TITLE   = pygame.font.SysFont("consolas", 36, bold=True)
FONT_HEAD    = pygame.font.SysFont("consolas", 22, bold=True)
FONT_BODY    = pygame.font.SysFont("consolas", 17)
FONT_BODY_B  = pygame.font.SysFont("consolas", 17, bold=True)
FONT_SMALL   = pygame.font.SysFont("consolas", 14)
FONT_TINY    = pygame.font.SysFont("consolas", 12)
FONT_BIG     = pygame.font.SysFont("consolas", 48, bold=True)
FONT_CMD     = pygame.font.SysFont("consolas", 20, bold=True)

# ---------------------------------------------------------------------------
# DIFFICULTY LEVELS
# ---------------------------------------------------------------------------
LEVELS = [
    {"id": "element",   "label": "Element Leader",       "time": 14, "pts": 10,  "icon": "◆"},
    {"id": "flight",    "label": "Flight Commander",     "time": 10, "pts": 20,  "icon": "◆◆"},
    {"id": "squadron",  "label": "Squadron Commander",   "time": 7,  "pts": 35,  "icon": "★"},
    {"id": "group",     "label": "Group Commander",      "time": 5,  "pts": 50,  "icon": "★★"},
    {"id": "wing",      "label": "Wing Commander",       "time": 3,  "pts": 75,  "icon": "★★★"},
]

# ---------------------------------------------------------------------------
# SCENARIO DATA  (based on AFMAN 36-2203)
# ---------------------------------------------------------------------------
SCENARIOS = [
    # ── FACING MOVEMENTS ──────────────────────────────────────────
    {
        "cat": "Facing Movements",
        "situation": "Formation is at ATTENTION facing NORTH.\nYou need the formation facing EAST.",
        "correct": "Right, FACE",
        "options": ["Right, FACE", "Left, FACE", "About, FACE", "Column Right, MARCH"],
        "explain": "RIGHT FACE rotates each member 90 deg clockwise.\nExecuted on the left heel and right toe.",
        "type": "standing", "facing": "N", "target": "E",
    },
    {
        "cat": "Facing Movements",
        "situation": "Formation is at ATTENTION facing NORTH.\nYou need the formation facing WEST.",
        "correct": "Left, FACE",
        "options": ["Left, FACE", "Right, FACE", "About, FACE", "Column Left, MARCH"],
        "explain": "LEFT FACE rotates each member 90 deg counter-clockwise.\nExecuted on the left heel and right toe.",
        "type": "standing", "facing": "N", "target": "W",
    },
    {
        "cat": "Facing Movements",
        "situation": "Formation is at ATTENTION facing NORTH.\nYou need the formation facing SOUTH.",
        "correct": "About, FACE",
        "options": ["About, FACE", "Right, FACE", "Left, FACE", "To the Rear, MARCH"],
        "explain": "ABOUT FACE rotates each member 180 deg.\nPlace right toe behind left heel, then pivot.",
        "type": "standing", "facing": "N", "target": "S",
    },
    # ── PRESENT / ORDER ARMS ──────────────────────────────────────
    {
        "cat": "Honors & Salutes",
        "situation": "Formation is at ATTENTION.\nThe National Anthem is about to play.\nYou must render a salute.",
        "correct": "Present, ARMS",
        "options": ["Present, ARMS", "Hand, SALUTE", "Order, ARMS", "Parade, REST"],
        "explain": "PRESENT ARMS directs the formation to render\nthe hand salute simultaneously.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Honors & Salutes",
        "situation": "Formation is rendering a salute.\nThe National Anthem has ended.\nYou need to terminate the salute.",
        "correct": "Order, ARMS",
        "options": ["Order, ARMS", "Present, ARMS", "At Ease", "Parade, REST"],
        "explain": "ORDER ARMS terminates the hand salute.\nArms return sharply to the side.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Honors & Salutes",
        "situation": "Formation is marching in Pass-in-Review.\nThe reviewing officer is on the RIGHT.\nYou need to render honors.",
        "correct": "Eyes, RIGHT",
        "options": ["Eyes, RIGHT", "DRESS RIGHT, DRESS", "Present, ARMS", "Right, FACE"],
        "explain": "EYES RIGHT turns all heads (except right flank)\nto the right to render honors to a reviewing officer.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Honors & Salutes",
        "situation": "Formation completed Eyes Right.\nYou need heads to return to front.",
        "correct": "Ready, FRONT",
        "options": ["Ready, FRONT", "ATTENTION", "Eyes, FRONT", "Order, ARMS"],
        "explain": "READY FRONT returns heads and arms to the\nposition of attention after Eyes Right.",
        "type": "standing", "facing": "N", "target": "N",
    },
    # ── REST POSITIONS ────────────────────────────────────────────
    {
        "cat": "Rest Positions",
        "situation": "Formation is at ATTENTION.\nYou want a modified rest — silent, in place,\nhands clasped behind back.",
        "correct": "Parade, REST",
        "options": ["Parade, REST", "AT EASE", "REST", "Fall Out"],
        "explain": "PARADE REST: left foot moves 12 inches left,\nhands clasped behind the back. Remain silent.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Rest Positions",
        "situation": "Formation is at PARADE REST.\nAllow them to relax and move in place,\nbut remain silent.",
        "correct": "AT EASE",
        "options": ["AT EASE", "REST", "Fall Out", "Parade, REST"],
        "explain": "AT EASE: members may move but keep right foot\nin place and remain silent.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Rest Positions",
        "situation": "Formation is at PARADE REST.\nAllow them to relax, move, AND talk,\nbut stay near formation.",
        "correct": "REST",
        "options": ["REST", "AT EASE", "Fall Out", "DISMISSED"],
        "explain": "REST: members may talk and move but keep right\nfoot in place. Most relaxed in-formation position.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Rest Positions",
        "situation": "Formation is at REST / AT EASE.\nYou need them back to the position of attention.",
        "correct": "Flight, ATTENTION",
        "options": ["Flight, ATTENTION", "FALL IN", "Ready, FRONT", "Present, ARMS"],
        "explain": "Calling the unit to ATTENTION returns all\nmembers from any rest position to attention.",
        "type": "standing", "facing": "N", "target": "N",
    },
    # ── FORMATION COMMANDS ────────────────────────────────────────
    {
        "cat": "Formation",
        "situation": "Personnel are in the assembly area.\nYou need to form the flight into ranks and files.",
        "correct": "FALL IN",
        "options": ["FALL IN", "Fall Out", "ATTENTION", "Open Ranks, MARCH"],
        "explain": "FALL IN forms the unit. Members immediately assume\nattention in their assigned positions.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Formation",
        "situation": "You need to inspect the ranks.\nCreate extra space between ranks for inspection.",
        "correct": "Open Ranks, MARCH",
        "options": ["Open Ranks, MARCH", "Close Ranks, MARCH", "Extend, MARCH", "DRESS RIGHT, DRESS"],
        "explain": "OPEN RANKS MARCH spreads ranks apart.\n1st rank: 2 paces fwd, 2nd: 1 pace, 3rd: stays, 4th: 2 back.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Formation",
        "situation": "Inspection is complete. Ranks are open.\nReturn to normal interval.",
        "correct": "Close Ranks, MARCH",
        "options": ["Close Ranks, MARCH", "Open Ranks, MARCH", "FALL IN", "DRESS RIGHT, DRESS"],
        "explain": "CLOSE RANKS MARCH returns the formation to\nnormal interval after Open Ranks.",
        "type": "standing", "facing": "N", "target": "N",
    },
    {
        "cat": "Formation",
        "situation": "Formation is at ATTENTION.\nYou want members to align right to dress the formation.",
        "correct": "DRESS RIGHT, DRESS",
        "options": ["DRESS RIGHT, DRESS", "Ready, FRONT", "Eyes, RIGHT", "Right, FACE"],
        "explain": "DRESS RIGHT DRESS: all except right flank turn\nheads right and extend left arm to check alignment.",
        "type": "standing", "facing": "N", "target": "N",
    },
    # ── MARCHING ──────────────────────────────────────────────────
    {
        "cat": "Marching",
        "situation": "Formation is at ATTENTION.\nBegin marching forward at quick time\n(120 steps/min, 24-inch step).",
        "correct": "Forward, MARCH",
        "options": ["Forward, MARCH", "Quick Time, MARCH", "Half Step, MARCH", "Double Time, MARCH"],
        "explain": "FORWARD MARCH initiates marching at quick time.\n120 steps per minute, 24-inch step length.",
        "type": "marching", "facing": "N", "target": "N",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching at quick time.\nYou need to halt the formation.",
        "correct": "Flight, HALT",
        "options": ["Flight, HALT", "STOP", "Mark Time, MARCH", "Quick Time, HALT"],
        "explain": "HALT stops all marching movement.\nMembers halt in two counts after command.",
        "type": "marching", "facing": "N", "target": "N",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching at quick time.\nReduce to a 15-inch step to slow the march.",
        "correct": "Half Step, MARCH",
        "options": ["Half Step, MARCH", "Mark Time, MARCH", "Slow Time, MARCH", "Change Step, MARCH"],
        "explain": "HALF STEP MARCH reduces step to 15 inches\nwhile maintaining 120-step cadence.",
        "type": "marching", "facing": "N", "target": "N",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching forward.\nYou need them to march in place without advancing.",
        "correct": "Mark Time, MARCH",
        "options": ["Mark Time, MARCH", "Half Step, MARCH", "In Place, HALT", "Change Step, MARCH"],
        "explain": "MARK TIME MARCH: march in place, alternating\nfeet, lifting each foot 2 inches off the ground.",
        "type": "marching", "facing": "N", "target": "N",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching forward in column.\nExecute a 90-degree turn to the RIGHT.",
        "correct": "Column Right, MARCH",
        "options": ["Column Right, MARCH", "Right, FACE", "Right Flank, MARCH", "Eyes, RIGHT"],
        "explain": "COLUMN RIGHT MARCH changes direction 90 deg right.\nLead element pivots; trailing elements pivot at same point.",
        "type": "marching", "facing": "N", "target": "E",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching forward in column.\nExecute a 90-degree turn to the LEFT.",
        "correct": "Column Left, MARCH",
        "options": ["Column Left, MARCH", "Left, FACE", "Left Flank, MARCH", "Counter, MARCH"],
        "explain": "COLUMN LEFT MARCH changes direction 90 deg left.\nLead element pivots; trailing elements follow.",
        "type": "marching", "facing": "N", "target": "W",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching forward.\nYou need them to reverse direction (180 deg)\nwhile continuing to march.",
        "correct": "To the Rear, MARCH",
        "options": ["To the Rear, MARCH", "About, FACE", "Counter, MARCH", "Column Right, MARCH"],
        "explain": "TO THE REAR MARCH reverses direction 180 deg\nwhile continuing to march. Given on the right foot.",
        "type": "marching", "facing": "N", "target": "S",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching at quick time.\nIncrease to double time (180 steps/min, 30-inch step).",
        "correct": "Double Time, MARCH",
        "options": ["Double Time, MARCH", "Quick Time, MARCH", "Forward, MARCH", "Half Step, MARCH"],
        "explain": "DOUBLE TIME MARCH increases to 180 steps/min\nand a 30-inch step. Essentially a jog.",
        "type": "marching", "facing": "N", "target": "N",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching at double time.\nReturn to quick time (120 steps/min).",
        "correct": "Quick Time, MARCH",
        "options": ["Quick Time, MARCH", "Forward, MARCH", "Half Step, MARCH", "Flight, HALT"],
        "explain": "QUICK TIME MARCH returns cadence to 120 steps/min\nfrom double time.",
        "type": "marching", "facing": "N", "target": "N",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching and you notice\nmembers are out of step.\nYou need them to change step to regain cadence.",
        "correct": "Change Step, MARCH",
        "options": ["Change Step, MARCH", "Mark Time, MARCH", "Half Step, MARCH", "Quick Time, MARCH"],
        "explain": "CHANGE STEP MARCH: on the right foot, place left\nbehind right, then step off again with the left.",
        "type": "marching", "facing": "N", "target": "N",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching in column and you need each\nelement to simultaneously turn 90 deg RIGHT\nwhile continuing to march.",
        "correct": "Right Flank, MARCH",
        "options": ["Right Flank, MARCH", "Column Right, MARCH", "Right, FACE", "Eyes, RIGHT"],
        "explain": "RIGHT FLANK MARCH: all members simultaneously\npivot 90 deg right on the ball of the right foot.",
        "type": "marching", "facing": "N", "target": "E",
    },
    {
        "cat": "Marching",
        "situation": "Formation is marching in column and you need each\nelement to simultaneously turn 90 deg LEFT\nwhile continuing to march.",
        "correct": "Left Flank, MARCH",
        "options": ["Left Flank, MARCH", "Column Left, MARCH", "Left, FACE", "Eyes, LEFT"],
        "explain": "LEFT FLANK MARCH: all members simultaneously\npivot 90 deg left on the ball of the left foot.",
        "type": "marching", "facing": "N", "target": "W",
    },
]

# ---------------------------------------------------------------------------
# DIRECTION HELPERS
# ---------------------------------------------------------------------------
DIR_ANGLES = {"N": 270, "E": 0, "S": 90, "W": 180}  # pygame degrees (0=right)
DIR_LABELS = {"N": "NORTH", "E": "EAST", "S": "SOUTH", "W": "WEST"}

def angle_rad(direction):
    return math.radians(DIR_ANGLES.get(direction, 270))

# ---------------------------------------------------------------------------
# DRAWING HELPERS
# ---------------------------------------------------------------------------
def draw_rounded_rect(surf, rect, color, radius=8, border=0, border_color=None):
    """Draw a rounded rectangle."""
    r = pygame.Rect(rect)
    if border > 0 and border_color:
        pygame.draw.rect(surf, border_color, r, border_radius=radius)
        inner = r.inflate(-border * 2, -border * 2)
        pygame.draw.rect(surf, color, inner, border_radius=max(radius - border, 0))
    else:
        pygame.draw.rect(surf, color, r, border_radius=radius)

def draw_text_wrapped(surf, text, font, color, rect, line_spacing=4):
    """Draw multiline text within a rect (splits on \\n)."""
    lines = text.split("\n")
    y = rect.y
    for line in lines:
        ts = font.render(line, True, color)
        surf.blit(ts, (rect.x, y))
        y += font.get_height() + line_spacing
    return y

def draw_text_centered(surf, text, font, color, cx, cy):
    ts = font.render(text, True, color)
    surf.blit(ts, (cx - ts.get_width() // 2, cy - ts.get_height() // 2))

def lerp_color(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))

# ---------------------------------------------------------------------------
# FORMATION RENDERER
# ---------------------------------------------------------------------------
def draw_formation(surf, rect, scenario, phase="question", elapsed=0):
    """Draw a top-down formation diagram inside 'rect'."""
    x, y, w, h = rect
    # Ground
    pygame.draw.rect(surf, C_GROUND, rect, border_radius=6)
    pygame.draw.rect(surf, C_GRID, rect, 1, border_radius=6)

    # Grid lines (subtle)
    for gx in range(x + 30, x + w, 30):
        pygame.draw.line(surf, (25, 38, 62), (gx, y + 4), (gx, y + h - 4), 1)
    for gy in range(y + 30, y + h, 30):
        pygame.draw.line(surf, (25, 38, 62), (x + 4, gy), (x + w - 4, gy), 1)

    cx, cy = x + w // 2, y + h // 2
    facing = scenario.get("facing", "N")
    target = scenario.get("target", "N")
    is_marching = scenario.get("type") == "marching"

    # Compass rose
    compass_x, compass_y = x + w - 30, y + 25
    for d, dx, dy in [("N", 0, -14), ("S", 0, 14), ("E", 14, 0), ("W", -14, 0)]:
        col = C_AF_GOLD if d == facing else C_TEXT_DIM
        draw_text_centered(surf, d, FONT_TINY, col, compass_x + dx, compass_y + dy)

    # Draw people in formation (4 ranks x 4 files)
    ranks, files = 4, 4
    spacing_x, spacing_y = 28, 24
    off_x = cx - (files - 1) * spacing_x // 2
    off_y = cy - (ranks - 1) * spacing_y // 2

    # Direction arrow (shows current facing)
    ang = angle_rad(facing)
    arrow_len = 18
    arrow_cx, arrow_cy = cx, off_y - 30
    ax2 = arrow_cx + math.cos(ang) * arrow_len
    ay2 = arrow_cy + math.sin(ang) * arrow_len
    pygame.draw.line(surf, C_ARROW, (arrow_cx, arrow_cy), (ax2, ay2), 2)
    # arrowhead
    for side in [-0.5, 0.5]:
        hx = ax2 - math.cos(ang + side) * 7
        hy = ay2 - math.sin(ang + side) * 7
        pygame.draw.line(surf, C_ARROW, (ax2, ay2), (hx, hy), 2)

    # If correct answer shown, draw target arrow too
    if phase == "result" and target != facing:
        ang2 = angle_rad(target)
        tx2 = arrow_cx + math.cos(ang2) * arrow_len
        ty2 = arrow_cy + math.sin(ang2) * arrow_len
        pulse = 0.5 + 0.5 * math.sin(elapsed * 4)
        col = lerp_color(C_GREEN_DIM, C_GREEN, pulse)
        pygame.draw.line(surf, col, (arrow_cx, arrow_cy), (tx2, ty2), 3)
        for side in [-0.5, 0.5]:
            hx = tx2 - math.cos(ang2 + side) * 7
            hy = ty2 - math.sin(ang2 + side) * 7
            pygame.draw.line(surf, col, (tx2, ty2), (hx, hy), 3)

    # Draw members
    for r in range(ranks):
        for f in range(files):
            px = off_x + f * spacing_x
            py = off_y + r * spacing_y
            # Leader marker
            is_leader = (r == 0 and f == 0)
            col = C_AF_GOLD if is_leader else C_PERSON
            rad = 7 if is_leader else 5

            if is_marching:
                bob = math.sin(elapsed * 6 + f * 0.5 + r * 0.3) * 2
                py += bob

            pygame.draw.circle(surf, col, (int(px), int(py)), rad)
            pygame.draw.circle(surf, (255, 255, 255, 60), (int(px), int(py)), rad, 1)

            # Facing tick on each person
            pa = angle_rad(facing)
            tx = px + math.cos(pa) * (rad + 3)
            ty = py + math.sin(pa) * (rad + 3)
            pygame.draw.line(surf, col, (px, py), (int(tx), int(ty)), 2)

    # Marching indicator
    if is_marching:
        label = "▶ MARCHING"
        ts = FONT_TINY.render(label, True, C_AF_GOLD)
        surf.blit(ts, (x + 10, y + h - 20))
    else:
        label = "■ STANDING"
        ts = FONT_TINY.render(label, True, C_TEXT_DIM)
        surf.blit(ts, (x + 10, y + h - 20))

    # Category tag
    cat = scenario.get("cat", "")
    ct = FONT_TINY.render(cat.upper(), True, C_AF_BLUE_LT)
    surf.blit(ct, (x + 10, y + 8))


# ---------------------------------------------------------------------------
# BUTTON CLASS
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, rect, text, key_label=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.key_label = key_label
        self.hovered = False
        self.state = "normal"  # normal, correct, wrong

    def draw(self, surf, font):
        if self.state == "correct":
            bg, border = C_GREEN_DIM, C_GREEN
        elif self.state == "wrong":
            bg, border = C_RED_DIM, C_RED
        elif self.hovered:
            bg, border = C_PANEL_LIGHT, C_AF_BLUE_LT
        else:
            bg, border = C_PANEL, C_AF_BLUE
        draw_rounded_rect(surf, self.rect, bg, 6, 2, border)

        # Key label
        if self.key_label:
            kx = self.rect.x + 14
            ky = self.rect.centery
            draw_rounded_rect(surf, (kx - 10, ky - 11, 22, 22), C_AF_BLUE, 4)
            draw_text_centered(surf, self.key_label, FONT_SMALL, C_WHITE, kx + 1, ky)
            tx = kx + 22
        else:
            tx = self.rect.x + 12
        ts = font.render(self.text, True, C_WHITE)
        surf.blit(ts, (tx, self.rect.centery - ts.get_height() // 2))

    def check_click(self, pos):
        return self.rect.collidepoint(pos)


# ---------------------------------------------------------------------------
# GAME STATE
# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.state = "menu"  # menu, playing, result, summary
        self.level_idx = 0
        self.score = 0
        self.round_num = 0
        self.total_rounds = 10
        self.correct_count = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []         # list of (scenario, chosen, correct_bool)
        self.scenario = None
        self.options_btns = []
        self.timer_start = 0
        self.timer_total = 10
        self.chosen = None
        self.result_time = 0
        self.shuffled_scenarios = []
        self.menu_buttons = []
        self.next_btn = None
        self.summary_btn = None
        self._build_menu()
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                       random.uniform(0.3, 1.0)) for _ in range(60)]

    # -- Menu ---------------------------------------------------------------
    def _build_menu(self):
        self.menu_buttons = []
        bw, bh = 320, 52
        start_y = 340
        for i, lv in enumerate(LEVELS):
            bx = WIDTH // 2 - bw // 2
            by = start_y + i * (bh + 10)
            label = f"{lv['icon']}  {lv['label']}  ({lv['time']}s)"
            self.menu_buttons.append(Button((bx, by, bw, bh), label))

    def start_game(self, level_idx):
        self.level_idx = level_idx
        self.score = 0
        self.round_num = 0
        self.correct_count = 0
        self.streak = 0
        self.best_streak = 0
        self.history = []
        self.shuffled_scenarios = random.sample(SCENARIOS, min(self.total_rounds, len(SCENARIOS)))
        self.state = "playing"
        self._next_round()

    def _next_round(self):
        if self.round_num >= self.total_rounds:
            self.state = "summary"
            self._build_summary()
            return
        self.scenario = self.shuffled_scenarios[self.round_num]
        self.chosen = None
        self.timer_start = time.time()
        self.timer_total = LEVELS[self.level_idx]["time"]
        opts = list(self.scenario["options"])
        random.shuffle(opts)
        self._build_option_buttons(opts)

    def _build_option_buttons(self, opts):
        self.options_btns = []
        bw, bh = 380, 48
        bx = WIDTH - bw - 40
        by_start = 440
        keys = ["1", "2", "3", "4"]
        for i, opt in enumerate(opts):
            by = by_start + i * (bh + 10)
            self.options_btns.append(Button((bx, by, bw, bh), opt, keys[i]))

    # -- Choosing -----------------------------------------------------------
    def choose(self, opt_text):
        if self.chosen is not None:
            return
        self.chosen = opt_text
        correct = (opt_text == self.scenario["correct"])
        if correct:
            pts = LEVELS[self.level_idx]["pts"]
            # Time bonus
            elapsed = time.time() - self.timer_start
            remaining = max(0, self.timer_total - elapsed)
            bonus = int(remaining / self.timer_total * pts * 0.5)
            self.score += pts + bonus
            self.correct_count += 1
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        else:
            self.streak = 0
        self.history.append((self.scenario, opt_text, correct))
        # Colour buttons
        for btn in self.options_btns:
            if btn.text == self.scenario["correct"]:
                btn.state = "correct"
            elif btn.text == opt_text and not correct:
                btn.state = "wrong"
        self.state = "result"
        self.result_time = time.time()
        self.next_btn = Button((WIDTH - 220, HEIGHT - 60, 180, 42), "NEXT  ▶", "N")

    def timeout(self):
        if self.chosen is not None:
            return
        self.chosen = "__TIMEOUT__"
        self.history.append((self.scenario, None, False))
        self.streak = 0
        for btn in self.options_btns:
            if btn.text == self.scenario["correct"]:
                btn.state = "correct"
        self.state = "result"
        self.result_time = time.time()
        self.next_btn = Button((WIDTH - 220, HEIGHT - 60, 180, 42), "NEXT  ▶", "N")

    def advance(self):
        self.round_num += 1
        self.state = "playing"
        self._next_round()

    # -- Summary ------------------------------------------------------------
    def _build_summary(self):
        self.summary_btn = Button((WIDTH // 2 - 120, HEIGHT - 80, 240, 48), "RETURN TO MENU")

    def return_to_menu(self):
        self.state = "menu"
        self._build_menu()


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
def main():
    game = Game()
    start_time = time.time()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = time.time()
        elapsed_global = now - start_time
        mx, my = pygame.mouse.get_pos()

        # -- Events ---------------------------------------------------------
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if game.state == "menu":
                    for i, btn in enumerate(game.menu_buttons):
                        if btn.check_click((mx, my)):
                            game.start_game(i)
                elif game.state == "playing":
                    for btn in game.options_btns:
                        if btn.check_click((mx, my)):
                            game.choose(btn.text)
                elif game.state == "result":
                    if game.next_btn and game.next_btn.check_click((mx, my)):
                        game.advance()
                elif game.state == "summary":
                    if game.summary_btn and game.summary_btn.check_click((mx, my)):
                        game.return_to_menu()

            elif ev.type == pygame.KEYDOWN:
                if game.state == "playing":
                    key_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
                               pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2, pygame.K_KP4: 3}
                    if ev.key in key_map:
                        idx = key_map[ev.key]
                        if idx < len(game.options_btns):
                            game.choose(game.options_btns[idx].text)
                elif game.state == "result":
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_n):
                        game.advance()
                elif game.state == "summary":
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game.return_to_menu()
                elif game.state == "menu":
                    key_map = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4}
                    if ev.key in key_map and key_map[ev.key] < len(LEVELS):
                        game.start_game(key_map[ev.key])

        # -- Timer check ----------------------------------------------------
        if game.state == "playing" and game.chosen is None:
            elapsed = now - game.timer_start
            if elapsed >= game.timer_total:
                game.timeout()

        # -- Hover updates --------------------------------------------------
        if game.state == "menu":
            for btn in game.menu_buttons:
                btn.hovered = btn.rect.collidepoint(mx, my)
        elif game.state == "playing":
            for btn in game.options_btns:
                btn.hovered = btn.rect.collidepoint(mx, my)
        elif game.state == "result" and game.next_btn:
            game.next_btn.hovered = game.next_btn.rect.collidepoint(mx, my)
        elif game.state == "summary" and game.summary_btn:
            game.summary_btn.hovered = game.summary_btn.rect.collidepoint(mx, my)

        # ==================================================================
        # DRAWING
        # ==================================================================
        screen.fill(C_BG)

        # Starfield
        for sx, sy, sb in game.stars:
            bright = int(40 + 30 * math.sin(elapsed_global * sb + sx * 0.01))
            pygame.draw.circle(screen, (bright, bright, bright + 15), (sx, sy), 1)

        # Top bar
        pygame.draw.rect(screen, C_PANEL, (0, 0, WIDTH, 54))
        pygame.draw.line(screen, C_AF_BLUE, (0, 54), (WIDTH, 54), 2)
        title_s = FONT_HEAD.render("USAF DRILL & CEREMONY — COMMAND SIMULATOR", True, C_AF_GOLD)
        screen.blit(title_s, (20, 15))
        ref_s = FONT_TINY.render("REF: AFMAN 36-2203", True, C_TEXT_DIM)
        screen.blit(ref_s, (WIDTH - ref_s.get_width() - 16, 20))

        # ── MENU ──────────────────────────────────────────────────
        if game.state == "menu":
            # Emblem placeholder
            cx = WIDTH // 2
            pygame.draw.circle(screen, C_AF_BLUE, (cx, 170), 60, 3)
            pygame.draw.circle(screen, C_AF_GOLD_DIM, (cx, 170), 50, 2)
            draw_text_centered(screen, "USAF", FONT_HEAD, C_AF_GOLD, cx, 158)
            draw_text_centered(screen, "D&C", FONT_BODY_B, C_AF_BLUE_LT, cx, 182)

            draw_text_centered(screen, "SELECT YOUR POSITION", FONT_HEAD, C_WHITE, cx, 270)
            draw_text_centered(screen, "Higher rank = less time to respond", FONT_SMALL, C_TEXT_DIM, cx, 296)

            for i, btn in enumerate(game.menu_buttons):
                btn.draw(screen, FONT_BODY_B)
                # Difficulty pips
                pips = i + 1
                for p in range(pips):
                    px = btn.rect.right + 14 + p * 14
                    py = btn.rect.centery
                    col = lerp_color(C_GREEN, C_RED, i / 4.0)
                    pygame.draw.rect(screen, col, (px, py - 4, 8, 8), border_radius=2)

            draw_text_centered(screen, "Press 1-5 or click to select", FONT_SMALL, C_TEXT_DIM, cx, HEIGHT - 40)

        # ── PLAYING / RESULT ──────────────────────────────────────
        elif game.state in ("playing", "result"):
            sc = game.scenario
            lv = LEVELS[game.level_idx]

            # HUD bar
            hud_y = 66
            draw_rounded_rect(screen, (12, hud_y, WIDTH - 24, 36), C_PANEL, 4)
            # Level
            lv_s = FONT_SMALL.render(f"{lv['icon']}  {lv['label'].upper()}", True, C_AF_GOLD)
            screen.blit(lv_s, (22, hud_y + 9))
            # Round
            rd_s = FONT_SMALL.render(f"ROUND {game.round_num + 1}/{game.total_rounds}", True, C_TEXT)
            screen.blit(rd_s, (280, hud_y + 9))
            # Score
            sc_s = FONT_SMALL.render(f"SCORE: {game.score}", True, C_WHITE)
            screen.blit(sc_s, (480, hud_y + 9))
            # Streak
            if game.streak > 0:
                stk_s = FONT_SMALL.render(f"STREAK: {game.streak}", True, C_AMBER)
                screen.blit(stk_s, (640, hud_y + 9))
            # Correct count
            cc_s = FONT_SMALL.render(f"{game.correct_count}/{game.round_num + (1 if game.state == 'result' else 0)} CORRECT", True, C_GREEN)
            screen.blit(cc_s, (820, hud_y + 9))

            # Timer
            if game.state == "playing":
                elapsed = now - game.timer_start
                remaining = max(0, game.timer_total - elapsed)
                pct = remaining / game.timer_total
            else:
                pct = 0
                remaining = 0

            timer_x, timer_w = 30, WIDTH - 60
            timer_y = 112
            timer_h = 8
            pygame.draw.rect(screen, C_PANEL_LIGHT, (timer_x, timer_y, timer_w, timer_h), border_radius=4)
            bar_col = C_GREEN if pct > 0.4 else C_AMBER if pct > 0.15 else C_RED
            if pct > 0:
                pygame.draw.rect(screen, bar_col, (timer_x, timer_y, int(timer_w * pct), timer_h), border_radius=4)
            # Timer text
            t_str = f"{remaining:.1f}s"
            t_surf = FONT_SMALL.render(t_str, True, bar_col)
            screen.blit(t_surf, (timer_x + timer_w + 8, timer_y - 2))

            # Left column: Formation diagram + Situation
            form_rect = (30, 134, 300, 240)
            draw_formation(screen, form_rect, sc,
                           "result" if game.state == "result" else "question",
                           elapsed_global)

            # Situation box
            sit_y = 390
            draw_rounded_rect(screen, (30, sit_y, 440, 160), C_PANEL, 6, 1, C_AF_BLUE)
            sit_label = FONT_TINY.render("SITUATION", True, C_AF_BLUE_LT)
            screen.blit(sit_label, (44, sit_y + 8))
            draw_text_wrapped(screen, sc["situation"], FONT_BODY, C_WHITE,
                              pygame.Rect(44, sit_y + 28, 410, 120))

            cat_label = FONT_TINY.render(f"CATEGORY: {sc['cat'].upper()}", True, C_TEXT_DIM)
            screen.blit(cat_label, (44, sit_y + 140))

            # Prompt
            if game.state == "playing":
                prompt = "SELECT THE CORRECT COMMAND:"
                prompt_col = C_AMBER
            elif game.chosen == "__TIMEOUT__":
                prompt = "⏱  TIME'S UP!"
                prompt_col = C_RED
            elif game.history[-1][2]:
                prompt = "✓  CORRECT!"
                prompt_col = C_GREEN
            else:
                prompt = "✗  INCORRECT"
                prompt_col = C_RED
            ps = FONT_HEAD.render(prompt, True, prompt_col)
            screen.blit(ps, (WIDTH - 420, 400))

            # Option buttons
            for btn in game.options_btns:
                btn.draw(screen, FONT_CMD)

            # Result explanation
            if game.state == "result":
                ex_y = 134
                draw_rounded_rect(screen, (350, ex_y, WIDTH - 390, 160), C_PANEL, 6, 1, C_GREEN_DIM)
                ex_label = FONT_TINY.render("EXPLANATION  (AFMAN 36-2203)", True, C_GREEN)
                screen.blit(ex_label, (364, ex_y + 8))
                correct_s = FONT_BODY_B.render(f"Answer: {sc['correct']}", True, C_GREEN)
                screen.blit(correct_s, (364, ex_y + 28))
                draw_text_wrapped(screen, sc["explain"], FONT_SMALL, C_TEXT,
                                  pygame.Rect(364, ex_y + 52, WIDTH - 420, 100))

                if game.history[-1][2]:
                    pts = LEVELS[game.level_idx]["pts"]
                    elapsed_r = game.history[-1][0]  # doesn't matter, just show base
                    pts_s = FONT_SMALL.render(f"+{pts} pts", True, C_AF_GOLD)
                    screen.blit(pts_s, (364, ex_y + 135))

                game.next_btn.draw(screen, FONT_BODY_B)
                hint_s = FONT_TINY.render("Press ENTER or N", True, C_TEXT_DIM)
                screen.blit(hint_s, (WIDTH - 220, HEIGHT - 24))

            # Key hints
            if game.state == "playing":
                hint_s = FONT_TINY.render("Press 1-4 or click", True, C_TEXT_DIM)
                screen.blit(hint_s, (WIDTH - 200, HEIGHT - 24))

        # ── SUMMARY ───────────────────────────────────────────────
        elif game.state == "summary":
            cx = WIDTH // 2
            lv = LEVELS[game.level_idx]
            pct = game.correct_count / game.total_rounds * 100

            draw_text_centered(screen, "AFTER ACTION REPORT", FONT_TITLE, C_AF_GOLD, cx, 100)
            draw_text_centered(screen, f"{lv['icon']}  {lv['label']}", FONT_HEAD, C_AF_BLUE_LT, cx, 145)

            # Stats panel
            panel_w, panel_h = 500, 260
            px = cx - panel_w // 2
            py = 175
            draw_rounded_rect(screen, (px, py, panel_w, panel_h), C_PANEL, 8, 2, C_AF_BLUE)

            stats = [
                ("FINAL SCORE", str(game.score), C_AF_GOLD),
                ("CORRECT", f"{game.correct_count} / {game.total_rounds}  ({pct:.0f}%)", C_GREEN if pct >= 70 else C_AMBER),
                ("BEST STREAK", str(game.best_streak), C_AMBER),
                ("TIMER", f"{lv['time']}s per question", C_TEXT),
            ]
            for i, (label, value, col) in enumerate(stats):
                sy = py + 26 + i * 56
                ls = FONT_SMALL.render(label, True, C_TEXT_DIM)
                screen.blit(ls, (px + 30, sy))
                vs = FONT_HEAD.render(value, True, col)
                screen.blit(vs, (px + 30, sy + 20))

            # Grade
            if pct >= 90:
                grade, gcol = "OUTSTANDING", C_GREEN
            elif pct >= 80:
                grade, gcol = "EXCELLENT", C_AF_GOLD
            elif pct >= 70:
                grade, gcol = "SATISFACTORY", C_AMBER
            elif pct >= 50:
                grade, gcol = "NEEDS IMPROVEMENT", C_RED
            else:
                grade, gcol = "UNSATISFACTORY", C_RED
            draw_text_centered(screen, grade, FONT_TITLE, gcol, cx, py + panel_h + 40)

            # History scroll
            hy = py + panel_h + 80
            draw_text_centered(screen, "QUESTION REVIEW", FONT_SMALL, C_TEXT_DIM, cx, hy)
            hy += 22
            visible = min(len(game.history), 6)
            for i in range(visible):
                sc_item, chosen, was_correct = game.history[i]
                icon = "✓" if was_correct else "✗"
                icol = C_GREEN if was_correct else C_RED
                row_s = FONT_SMALL.render(
                    f"  {icon}  Q{i + 1}: {sc_item['correct']}" +
                    ("" if was_correct else f"  (you: {chosen if chosen else 'TIMEOUT'})"),
                    True, icol)
                screen.blit(row_s, (cx - 240, hy + i * 22))

            if len(game.history) > visible:
                more = FONT_TINY.render(f"... and {len(game.history) - visible} more", True, C_TEXT_DIM)
                screen.blit(more, (cx - 40, hy + visible * 22 + 4))

            game.summary_btn.draw(screen, FONT_BODY_B)

        # Bottom line
        pygame.draw.line(screen, C_AF_BLUE, (0, HEIGHT - 2), (WIDTH, HEIGHT - 2), 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()