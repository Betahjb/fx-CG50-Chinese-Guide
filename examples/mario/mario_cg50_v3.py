# mario_cg50_v3.py
# SPDX-License-Identifier: MIT
# Educational fan-made demo. No commercial ROM, audio, or extracted assets.
# Third-party names and characters are not covered by the MIT license;
# see ../../THIRD_PARTY_NOTICES.md.
# ============================================================
# fx-CG50 + PythonExtra
# Wide-screen World 1-1 style platformer V3
#
# V3 focus:
# - 384x216 full-screen CG50 presentation
# - fixed 30 Hz physics independent from rendering speed
# - faster walk/run + speed-driven running jump
# - better self-drawn animated pixel sprites
# - SMALL / SUPER / FIRE power states
# - mushroom + fire flower
# - SHIFT = run; FIRE form uses SHIFT press to shoot
# - max 2 bouncing fireballs
# - fireballs defeat Goombas
# - reduced per-frame drawing work vs V1
#
# Controls:
#   LEFT / RIGHT  Move
#   DOWN          Crouch when Super/Fire
#   EXE           Jump (hold = higher)
#   SHIFT         Run; press to shoot when Fire
#   EXIT          Quit
#
# Requires: PythonExtra with import gint
# No pygame, no third-party PC packages.
# ============================================================

import gint
import time
import gc

# ============================================================
# DISPLAY / WORLD
# ============================================================
W = 384
H = 216
TILE = 16
MAP_Y = -8
MAP_ROWS = 14
MAP_COLS = 212

# ------------------------------------------------------------
# V3 RENDER CAMERA
# Physics/map stay in the original 16x16 world coordinate system.
# Only the render layer is enlarged.
#
# Horizontal: 3/2 = 1.50x -> 384px screen shows 256 world px = 16 tiles.
# Vertical:   5/4 = 1.25x -> keeps upper blocks + ground visible on 216px.
# ------------------------------------------------------------
SCALE_X_NUM = 3
SCALE_X_DEN = 2
SCALE_Y_NUM = 5
SCALE_Y_DEN = 4

VIEW_WORLD_W = (W * SCALE_X_DEN) // SCALE_X_NUM   # 256 world px
VIEW_WORLD_Y = 56
HUD_H = 18

TILE_SW = (TILE * SCALE_X_NUM) // SCALE_X_DEN     # 24 px
TILE_SH = (TILE * SCALE_Y_NUM) // SCALE_Y_DEN     # 20 px

# 1 px = 256 fixed-point units
FP = 256

# Physics target. Rendering may be slower; accumulator keeps
# game speed close to real time even if a frame takes >33 ms.
STEP_MS = 33
MAX_CATCHUP_STEPS = 3

# ============================================================
# COLORS
# ============================================================
SKY = gint.C_RGB(11, 19, 31)
WHITE = gint.C_WHITE
BLACK = gint.C_BLACK

GROUND = gint.C_RGB(24, 13, 6)
GROUND_LIGHT = gint.C_RGB(31, 20, 10)
GROUND_DARK = gint.C_RGB(13, 7, 3)

BRICK = gint.C_RGB(25, 9, 5)
BRICK_LIGHT = gint.C_RGB(31, 17, 8)

QUESTION = gint.C_RGB(31, 21, 4)
QUESTION_LIGHT = gint.C_RGB(31, 29, 13)
USED = gint.C_RGB(18, 12, 6)

PIPE = gint.C_RGB(5, 23, 7)
PIPE_LIGHT = gint.C_RGB(13, 31, 14)
PIPE_DARK = gint.C_RGB(2, 12, 4)

RED = gint.C_RED
DARK_RED = gint.C_RGB(18, 2, 2)
BLUE = gint.C_RGB(4, 7, 24)
SKIN = gint.C_RGB(31, 23, 14)
SHOE = gint.C_RGB(12, 6, 3)

FIRE_WHITE = gint.C_RGB(31, 31, 29)
FIRE_RED = gint.C_RGB(30, 5, 3)

GOOMBA = gint.C_RGB(19, 10, 4)
GOOMBA_DARK = gint.C_RGB(10, 5, 2)

COIN = gint.C_RGB(31, 27, 3)
COIN_DARK = gint.C_RGB(26, 15, 2)

FLOWER_RED = gint.C_RGB(31, 4, 3)
FLOWER_YELLOW = gint.C_RGB(31, 25, 4)
FLOWER_GREEN = gint.C_RGB(3, 23, 6)

FIREBALL_OUTER = gint.C_RGB(31, 6, 2)
FIREBALL_INNER = gint.C_RGB(31, 28, 8)

HILL = gint.C_RGB(7, 25, 8)
CLOUD = gint.C_RGB(30, 30, 30)
FLAG = gint.C_RGB(4, 24, 7)
CASTLE = gint.C_RGB(18, 11, 7)
CASTLE_DARK = gint.C_RGB(10, 6, 4)

PIKA_YELLOW = gint.C_RGB(31, 27, 3)
PIKA_RED = gint.C_RGB(31, 4, 3)
PIKA_BROWN = gint.C_RGB(17, 9, 3)
PIKA_DARK = gint.C_RGB(4, 4, 3)
MENU_BLUE = gint.C_RGB(5, 11, 24)

# ============================================================
# TILE CODES
# ============================================================
T_EMPTY = 45   # -
T_GROUND = 88  # X
T_BRICK = 83   # S
T_QCOIN = 81   # Q
T_QPOWER = 63  # ?
T_USED = 85    # U
T_E = 69       # E
T_PL = 60      # <
T_PR = 62      # >
T_BL = 91      # [
T_BR = 93      # ]

def is_solid(ch):
    return (ch == T_GROUND or ch == T_BRICK or
            ch == T_QCOIN or ch == T_QPOWER or
            ch == T_USED or ch == T_PL or
            ch == T_PR or ch == T_BL or ch == T_BR)

# ============================================================
# LEVEL DATA
# Geometry follows the same public 1-1 tile layout used for V1.
# Art is self-drawn.
# ============================================================
LEVEL_ROWS = (
"----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",
"----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",
"----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",
"----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------",
"----------------------------------------------------------------------------------E-----------------------------------------------------------------------------------------------------------------------",
"----------------------Q---------------------------------------------------------SSSSSSSS---SSSQ--------------?-----------SSS----SQQS--------------------------------------------------------XX------------",
"-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------XXX------------",
"-------------------------------------------------------------------------------E----------------------------------------------------------------------------------------------------------XXXX------------",
"----------------------------------------------------------------S------------------------------------------------------------------------------------------------------------------------XXXXX------------",
"----------------Q---S?SQS---------------------<>---------<>------------------S?S--------------S-----SS----Q--Q--Q-----S----------SS------X--X----------XX--X------------SSQS------------XXXXXX------------",
"--------------------------------------<>------[]---------[]-----------------------------------------------------------------------------XX--XX--------XXX--XX--------------------------XXXXXXX------------",
"----------------------------<>--------[]------[]---------[]----------------------------------------------------------------------------XXX--XXX------XXXX--XXX-----<>--------------<>-XXXXXXXX------------",
"---------------------E------[]--------[]-E----[]-----E-E-[]------------------------------------E-E--------E-----------------EE-E-E----XXXX--XXXX----XXXXX--XXXX----[]---------EE---[]XXXXXXXXX--------X---",
"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX--XXXXXXXXXXXXXXX---XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX--XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
)

# ============================================================
# HELPERS
# ============================================================
def clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v

def approach(v, target, step):
    if v < target:
        v += step
        if v > target:
            v = target
    elif v > target:
        v -= step
        if v < target:
            v = target
    return v

def iabs(v):
    if v < 0:
        return -v
    return v

def aabb(ax, ay, aw, ah, bx, by, bw, bh):
    return (ax < bx + bw and ax + aw > bx and
            ay < by + bh and ay + ah > by)

# ============================================================
# PIXEL-SPRITE SYSTEM
#
# Sprites are encoded as strings then compiled ONCE into
# horizontal color runs. At runtime each run becomes one drect,
# which is much cheaper than drawing every pixel individually.
#
# Characters:
# R = red, B = blue, S = skin, K = dark/shoe
# W = white, F = fire red, Y = yellow
# . = transparent
# ============================================================
BASE_PALETTE = {
    "R": RED,
    "B": BLUE,
    "S": SKIN,
    "K": SHOE,
    "W": WHITE,
    "F": FIRE_RED,
    "Y": FIREBALL_INNER,
}

FIRE_PALETTE = {
    "R": FIRE_WHITE,
    "B": FIRE_RED,
    "S": SKIN,
    "K": SHOE,
    "W": WHITE,
    "F": FIRE_RED,
    "Y": FIREBALL_INNER,
}

# Small Mario: 16 x 22-ish visual footprint.
SMALL_STAND = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....RRRR........",
"...RRBBRR.......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"...BBBBBB.......",
"..BBB..BBB......",
"..BB....BB......",
".KKK....KKK.....",
".KK......KK.....",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

SMALL_WALK1 = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....RRRR........",
"...RRBBRR.......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"...BBBBBB.......",
"..BBB...BB......",
".BBB.....BB.....",
".KK.......KK....",
"KK.........KK...",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

SMALL_WALK2 = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....RRRR........",
"...RRBBRR.......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"...BBBBBB.......",
"...BB.BBB.......",
"..BB...BBB......",
"..KK.....KKK....",
".KK.......KK....",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

SMALL_JUMP = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....RRRR........",
"...RRBBRR.......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"..BBB.BBB.......",
".BBB...BBB......",
".KK.....BBB.....",
"KK.......KK.....",
"..........KK....",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

SMALL_SKID = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....RRRR........",
"...RRBBRR.......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"..BBBBBBB.......",
".BBB..BBB.......",
".BB....BB.......",
"KK.....KK.......",
".KK....KKK......",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

# Super / Fire Mario: 16 x 32 visual footprint.
BIG_STAND = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....SSSS........",
"....RRRR........",
"...RRRRRR.......",
"..RRRBBRRR......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"...BBBBBB.......",
"...BBBBBB.......",
"..BBB..BBB......",
"..BBB..BBB......",
"..BB....BB......",
"..BB....BB......",
".KKK....KKK.....",
".KK......KK.....",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

BIG_WALK1 = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....SSSS........",
"....RRRR........",
"...RRRRRR.......",
"..RRRBBRRR......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"...BBBBBB.......",
"...BBBBBB.......",
"..BBB...BB......",
"..BBB...BB......",
".BBB.....BB.....",
".BBB.....BB.....",
".KK.......KK....",
"KK.........KK...",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

BIG_WALK2 = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....SSSS........",
"....RRRR........",
"...RRRRRR.......",
"..RRRBBRRR......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"...BBBBBB.......",
"...BBBBBB.......",
"...BB.BBB.......",
"...BB.BBB.......",
"..BB...BBB......",
"..BB...BBB......",
"..KK.....KKK....",
".KK.......KK....",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

BIG_JUMP = (
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...SSSSSS.......",
"....SSSS........",
"....RRRR........",
"...RRRRRR.......",
"..RRRBBRRR......",
"..RRRBBRRR......",
"..RRBBBBRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"..BBB.BBB.......",
".BBB...BBB......",
".BBB...BBB......",
".KK.....BBB.....",
"KK.......BBB....",
"..........KK....",
"...........KK...",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

BIG_CROUCH = (
"................",
"................",
"................",
"................",
".....RRRR.......",
"....RRRRRR......",
"....SSSSSK......",
"...SSSSSSS......",
"...RRRRRR.......",
"..RRBBBBRR......",
"..RRBBBBRR......",
"...BBBBBB.......",
"..BBB..BBB......",
".KKK....KKK.....",
".KK......KK.....",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
"................",
)

def compile_sprite(rows):
    # Find the visible bounding box first. This removes transparent
    # padding from the art, which is essential for correct feet anchoring.
    min_x = 999
    min_y = 999
    max_x = -1
    max_y = -1

    y = 0
    while y < len(rows):
        row = rows[y]
        x = 0
        while x < len(row):
            if row[x] != ".":
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y
            x += 1
        y += 1

    if max_x < min_x:
        return ([], 1, 1)

    runs = []
    y = min_y
    while y <= max_y:
        row = rows[y]
        x = min_x

        while x <= max_x:
            ch = row[x]

            if ch == ".":
                x += 1
                continue

            x0 = x
            x += 1

            while x <= max_x and row[x] == ch:
                x += 1

            # Normalize to visible bounding box.
            runs.append((x0 - min_x, y - min_y, x - 1 - min_x, ch))

        y += 1

    return (runs, max_x - min_x + 1, max_y - min_y + 1)

SPR_SMALL_STAND = compile_sprite(SMALL_STAND)
SPR_SMALL_WALK1 = compile_sprite(SMALL_WALK1)
SPR_SMALL_WALK2 = compile_sprite(SMALL_WALK2)
SPR_SMALL_JUMP = compile_sprite(SMALL_JUMP)
SPR_SMALL_SKID = compile_sprite(SMALL_SKID)

SPR_BIG_STAND = compile_sprite(BIG_STAND)
SPR_BIG_WALK1 = compile_sprite(BIG_WALK1)
SPR_BIG_WALK2 = compile_sprite(BIG_WALK2)
SPR_BIG_JUMP = compile_sprite(BIG_JUMP)
SPR_BIG_CROUCH = compile_sprite(BIG_CROUCH)

def sx(wx, cam):
    return ((wx - cam) * SCALE_X_NUM) // SCALE_X_DEN

def sy(wy):
    return HUD_H + ((wy - VIEW_WORLD_Y) * SCALE_Y_NUM) // SCALE_Y_DEN

def scale_x(v):
    return (v * SCALE_X_NUM) // SCALE_X_DEN

def scale_y(v):
    return (v * SCALE_Y_NUM) // SCALE_Y_DEN

def draw_sprite_feet(sprite, center_world_x, feet_world_y,
                     target_world_w, target_world_h,
                     cam, facing, palette):
    # Sprite is fitted into a target visual box, but the BOTTOM of that
    # box is always exactly the player's physical feet coordinate.
    runs, sw, sh = sprite

    target_w = scale_x(target_world_w)
    target_h = scale_y(target_world_h)

    if target_w < 1:
        target_w = 1
    if target_h < 1:
        target_h = 1

    center_sx = sx(center_world_x, cam)
    left0 = center_sx - target_w // 2
    bottom = sy(feet_world_y)
    top0 = bottom - target_h + 1

    i = 0
    while i < len(runs):
        x0, yy, x1, ch = runs[i]
        color = palette[ch]

        ax0 = (x0 * target_w) // sw
        ax1 = (((x1 + 1) * target_w) // sw) - 1
        ay0 = (yy * target_h) // sh
        ay1 = (((yy + 1) * target_h) // sh) - 1

        if ax1 < ax0:
            ax1 = ax0
        if ay1 < ay0:
            ay1 = ay0

        if facing >= 0:
            left = left0 + ax0
            right = left0 + ax1
        else:
            left = left0 + (target_w - 1 - ax1)
            right = left0 + (target_w - 1 - ax0)

        top = top0 + ay0
        bottom_run = top0 + ay1

        # Cheap clipping guard.
        if right >= 0 and left < W and bottom_run >= HUD_H and top < H:
            gint.drect(left, top, right, bottom_run, color)

        i += 1

# ============================================================
# WORLD
# ============================================================
class World:
    def __init__(self):
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.camera = 0
        self.won = False

        self.map = []
        self.enemies = []
        self.items = []       # [type, x, y, target_y, dir, vy16, active, emerging]
        self.popcoins = []    # [x, y, vy16, life]

        # Exactly two fixed fireball slots:
        # [active, x_fp, y_fp, vx_fp, vy_fp, life]
        self.fireballs = [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]

        self.build_level()

        ground_y = MAP_Y + 13 * TILE
        self.player = Player(3 * TILE, ground_y)

        self.flag_x = 198 * TILE + 8

    def build_level(self):
        self.map = []
        self.enemies = []

        r = 0
        while r < MAP_ROWS:
            raw = LEVEL_ROWS[r]
            row = bytearray(MAP_COLS)

            c = 0
            while c < MAP_COLS:
                if c < len(raw):
                    ch = ord(raw[c])
                else:
                    ch = T_EMPTY

                if ch == T_E:
                    marker_bottom = MAP_Y + (r + 1) * TILE
                    self.enemies.append([
                        c * TILE + 1,       # x
                        marker_bottom - 14, # y
                        -1,                 # dir
                        0,                  # vy16
                        1,                  # active/alive
                        0,                  # squash timer
                        0                   # death flash timer
                    ])
                    ch = T_EMPTY

                row[c] = ch
                c += 1

            self.map.append(row)
            r += 1

        c = 202
        while c < MAP_COLS:
            self.map[13][c] = T_GROUND
            c += 1

    def reset_level_keep_stats(self):
        lives = self.lives
        score = self.score
        coins = self.coins

        self.camera = 0
        self.won = False
        self.items = []
        self.popcoins = []

        self.fireballs[0][0] = 0
        self.fireballs[1][0] = 0

        self.build_level()

        ground_y = MAP_Y + 13 * TILE
        self.player = Player(3 * TILE, ground_y)

        self.lives = lives
        self.score = score
        self.coins = coins

    def tile(self, c, r):
        if c < 0 or c >= MAP_COLS or r < 0 or r >= MAP_ROWS:
            return T_EMPTY
        return self.map[r][c]

    def set_tile(self, c, r, ch):
        if c >= 0 and c < MAP_COLS and r >= 0 and r < MAP_ROWS:
            self.map[r][c] = ch

    def tile_xy(self, c, r):
        return c * TILE, MAP_Y + r * TILE

    def collision_tiles(self, x, y, w, h):
        c0 = x // TILE
        c1 = (x + w - 1) // TILE
        r0 = (y - MAP_Y) // TILE
        r1 = (y + h - 1 - MAP_Y) // TILE

        if c0 < 0:
            c0 = 0
        if c1 >= MAP_COLS:
            c1 = MAP_COLS - 1
        if r0 < 0:
            r0 = 0
        if r1 >= MAP_ROWS:
            r1 = MAP_ROWS - 1

        out = []
        r = r0
        while r <= r1:
            c = c0
            while c <= c1:
                ch = self.map[r][c]
                if is_solid(ch):
                    out.append((c, r, ch))
                c += 1
            r += 1
        return out

    # --------------------------------------------------------
    # BLOCK CONTENTS
    # --------------------------------------------------------
    def hit_block(self, c, r):
        ch = self.tile(c, r)

        if ch == T_QCOIN:
            self.set_tile(c, r, T_USED)
            tx, ty = self.tile_xy(c, r)
            self.popcoins.append([tx + 8, ty - 2, -48, 22])
            self.coins += 1
            self.score += 200
            return

        if ch == T_QPOWER:
            self.set_tile(c, r, T_USED)
            tx, ty = self.tile_xy(c, r)

            if self.player.power == 0:
                # mushroom
                item_type = 0
            else:
                # fire flower
                item_type = 1

            self.items.append([
                item_type,
                tx + 1,
                ty + 2,
                ty - 15,
                1,
                0,
                1,
                1
            ])
            self.score += 100
            return

        if ch == T_BRICK:
            if self.player.power > 0:
                self.set_tile(c, r, T_EMPTY)
                self.score += 50

    # --------------------------------------------------------
    # FIREBALL SPAWN
    # --------------------------------------------------------
    def shoot_fireball(self):
        p = self.player
        if p.power != 2 or p.dead or p.finished:
            return

        slot = -1
        i = 0
        while i < 2:
            if self.fireballs[i][0] == 0:
                slot = i
                break
            i += 1

        if slot < 0:
            return

        f = self.fireballs[slot]
        f[0] = 1

        px = p.px()
        py = p.py()

        if p.facing > 0:
            f[1] = (px + 14) * FP
            f[3] = 950
        else:
            f[1] = (px - 4) * FP
            f[3] = -950

        f[2] = (py + 10) * FP
        f[4] = -300
        f[5] = 120

    # --------------------------------------------------------
    # ITEMS
    # --------------------------------------------------------
    def update_items(self):
        # Pop-up coins
        i = 0
        while i < len(self.popcoins):
            p = self.popcoins[i]
            p[1] += p[2] // 16
            p[2] += 8
            p[3] -= 1

            if p[3] <= 0:
                self.popcoins.pop(i)
            else:
                i += 1

        # Mushroom / flower
        i = 0
        while i < len(self.items):
            it = self.items[i]

            if not it[6]:
                self.items.pop(i)
                continue

            # emerging
            if it[7]:
                it[2] -= 1
                if it[2] <= it[3]:
                    it[2] = it[3]
                    it[7] = 0
                i += 1
                continue

            # Flower stays in place after emerging.
            if it[0] == 1:
                i += 1
                continue

            # Mushroom horizontal movement
            nx = it[1] + it[4]
            coll = self.collision_tiles(nx, it[2], 14, 14)

            if len(coll):
                it[4] = -it[4]
            else:
                it[1] = nx

            # Mushroom gravity
            it[5] += 6
            if it[5] > 80:
                it[5] = 80

            old_y = it[2]
            ny = old_y + (it[5] // 16)

            coll = self.collision_tiles(it[1], ny, 14, 14)
            j = 0
            while j < len(coll):
                c, r, ch = coll[j]
                tx, ty = self.tile_xy(c, r)

                if it[5] > 0 and old_y + 14 <= ty + 4:
                    ny = ty - 14
                    it[5] = 0
                    break
                j += 1

            it[2] = ny

            if it[2] > H + 40:
                it[6] = 0

            i += 1

    # --------------------------------------------------------
    # ENEMIES
    # --------------------------------------------------------
    def update_enemies(self):
        i = 0
        while i < len(self.enemies):
            e = self.enemies[i]

            if not e[4]:
                i += 1
                continue

            # activate when near screen
            if e[0] > self.camera + VIEW_WORLD_W + 50:
                i += 1
                continue

            if e[6] > 0:
                e[6] -= 1
                if e[6] <= 0:
                    e[4] = 0
                i += 1
                continue

            if e[5] > 0:
                e[5] -= 1
                if e[5] <= 0:
                    e[4] = 0
                i += 1
                continue

            nx = e[0] + e[2]
            coll = self.collision_tiles(nx, e[1], 14, 14)

            if len(coll):
                e[2] = -e[2]
            else:
                e[0] = nx

            e[3] += 7
            if e[3] > 84:
                e[3] = 84

            old_y = e[1]
            ny = old_y + (e[3] // 16)

            coll = self.collision_tiles(e[0], ny, 14, 14)
            j = 0
            while j < len(coll):
                c, r, ch = coll[j]
                tx, ty = self.tile_xy(c, r)

                if e[3] > 0 and old_y + 14 <= ty + 4:
                    ny = ty - 14
                    e[3] = 0
                    break
                j += 1

            e[1] = ny

            if e[1] > H + 50:
                e[4] = 0

            i += 1

    # --------------------------------------------------------
    # FIREBALL PHYSICS
    # --------------------------------------------------------
    def update_fireballs(self):
        i = 0
        while i < 2:
            f = self.fireballs[i]

            if not f[0]:
                i += 1
                continue

            f[5] -= 1
            if f[5] <= 0:
                f[0] = 0
                i += 1
                continue

            old_x = f[1] // FP
            old_y = f[2] // FP

            # Horizontal first
            f[1] += f[3]
            x = f[1] // FP
            y = f[2] // FP

            coll = self.collision_tiles(x, y, 5, 5)
            if len(coll):
                f[0] = 0
                i += 1
                continue

            # Gravity + vertical bounce
            f[4] += 95
            if f[4] > 900:
                f[4] = 900

            f[2] += f[4]
            x = f[1] // FP
            y = f[2] // FP

            coll = self.collision_tiles(x, y, 5, 5)
            bounced = False
            j = 0
            while j < len(coll):
                c, r, ch = coll[j]
                tx, ty = self.tile_xy(c, r)

                if f[4] > 0 and old_y + 5 <= ty + 4:
                    f[2] = (ty - 5) * FP
                    f[4] = -760
                    bounced = True
                    break
                else:
                    # hit ceiling/side-like geometry
                    f[0] = 0
                    break
                j += 1

            if not f[0]:
                i += 1
                continue

            # Enemy collision
            fx = f[1] // FP
            fy = f[2] // FP

            j = 0
            while j < len(self.enemies):
                e = self.enemies[j]
                if e[4] and e[5] <= 0 and e[6] <= 0:
                    if aabb(fx, fy, 5, 5, e[0], e[1], 14, 14):
                        e[6] = 8
                        self.score += 100
                        f[0] = 0
                        break
                j += 1

            # Off screen / pit cleanup
            fx = f[1] // FP
            fy = f[2] // FP
            if fx < self.camera - 20 or fx > self.camera + VIEW_WORLD_W + 40 or fy > H + 30:
                f[0] = 0

            i += 1

    # --------------------------------------------------------
    # WORLD UPDATE
    # --------------------------------------------------------
    def update(self, inp):
        if self.won:
            return

        self.player.update(self, inp)
        self.update_items()
        self.update_enemies()
        self.update_fireballs()

        # Dynamic camera. Mario sits left of center to show more ahead.
        px = self.player.px()
        target = px - 96

        if target < 0:
            target = 0

        max_cam = MAP_COLS * TILE - VIEW_WORLD_W
        if target > max_cam:
            target = max_cam

        if target > self.camera:
            speed = iabs(self.player.vx)

            if speed > 750:
                cam_step = 7
            elif speed > 450:
                cam_step = 5
            else:
                cam_step = 3

            delta = target - self.camera
            if delta < cam_step:
                self.camera = target
            else:
                self.camera += cam_step

        if px + 16 >= self.flag_x:
            self.won = True
            self.player.finished = True
            self.score += 1000

# ============================================================
# PLAYER
# power: 0 SMALL, 1 SUPER, 2 FIRE
# ============================================================
class Player:
    W = 14
    SMALL_H = 20
    BIG_H = 30
    CROUCH_H = 19

    # Faster than V1 for the 384-wide screen.
    WALK_MAX = 560      # 2.19 px/step
    RUN_MAX = 1040      # 4.06 px/step
    WALK_ACCEL = 34
    RUN_ACCEL = 54
    AIR_ACCEL = 23
    GROUND_DECEL = 38

    # Jump calibrated to roughly ~4.5 tiles ordinary,
    # ~5+ tiles at full running speed with held EXE.
    JUMP_IDLE = -1660
    JUMP_RUN = -1840

    GRAV_HOLD_IDLE = 64
    GRAV_HOLD_RUN = 55
    GRAV_RELEASE = 150
    GRAV_FALL = 112
    MAX_FALL = 1400
    MAX_HOLD = 12

    COYOTE = 4
    BUFFER = 5

    def __init__(self, start_x, ground_y):
        self.x = start_x * FP
        self.y = (ground_y - self.SMALL_H) * FP

        self.vx = 0
        self.vy = 0

        self.power = 0
        self.crouch = False
        self.on_ground = False
        self.dead = False
        self.finished = False

        self.facing = 1
        self.invuln = 0

        self.coyote = 0
        self.jump_buffer = 0
        self.jump_hold = 0
        self.run_jump = False

        self.anim = 0
        self.skid = False

    def stand_height(self):
        if self.power == 0:
            return self.SMALL_H
        return self.BIG_H

    def height(self):
        if self.power > 0 and self.crouch and self.on_ground:
            return self.CROUCH_H
        return self.stand_height()

    def px(self):
        return self.x // FP

    def py(self):
        y = self.y // FP
        sh = self.stand_height()
        h = self.height()

        if h != sh:
            y += sh - h

        return y

    def set_power(self, power):
        old_feet = self.py() + self.height()
        self.power = power
        self.crouch = False
        self.y = (old_feet - self.stand_height()) * FP
        self.invuln = 24

    def hurt(self, world):
        if self.invuln > 0 or self.dead or self.finished:
            return

        # SMB1 behavior: Super or Fire -> Small.
        if self.power > 0:
            self.set_power(0)
            self.invuln = 55
        else:
            self.dead = True
            self.vx = 0
            self.vy = -1500
            world.lives -= 1

    def update(self, world, inp):
        if self.finished:
            self.vx = approach(self.vx, 0, self.GROUND_DECEL)
            return

        if self.dead:
            self.vy += self.GRAV_FALL
            if self.vy > self.MAX_FALL:
                self.vy = self.MAX_FALL

            self.y += self.vy

            if self.y // FP > H + 55:
                if world.lives <= 0:
                    world.score = 0
                    world.coins = 0
                    world.lives = 3
                world.reset_level_keep_stats()
            return

        if self.invuln > 0:
            self.invuln -= 1

        left = inp[0]
        right = inp[1]
        down = inp[2]
        run = inp[3]
        jump = inp[4]
        jump_pressed = inp[5]
        b_pressed = inp[6]

        if jump_pressed:
            self.jump_buffer = self.BUFFER
        elif self.jump_buffer > 0:
            self.jump_buffer -= 1

        if b_pressed and self.power == 2:
            world.shoot_fireball()

        if self.on_ground:
            self.coyote = self.COYOTE
        elif self.coyote > 0:
            self.coyote -= 1

        direction = 0
        if right:
            direction += 1
        if left:
            direction -= 1

        self.crouch = bool(self.power > 0 and down and self.on_ground)

        if direction != 0:
            self.facing = direction

        self.skid = False

        # ----------------------------------------------------
        # HORIZONTAL
        # ----------------------------------------------------
        if direction != 0 and not self.crouch:
            max_speed = self.RUN_MAX if run else self.WALK_MAX

            if self.on_ground:
                accel = self.RUN_ACCEL if run else self.WALK_ACCEL

                if self.vx != 0 and ((self.vx > 0) != (direction > 0)):
                    accel *= 2
                    self.skid = True
            else:
                accel = self.AIR_ACCEL

            self.vx = approach(self.vx, direction * max_speed, accel)
        else:
            if self.on_ground:
                self.vx = approach(self.vx, 0, self.GROUND_DECEL)

        # ----------------------------------------------------
        # JUMP: takeoff speed determines run jump
        # ----------------------------------------------------
        can_jump = self.on_ground or self.coyote > 0

        if self.jump_buffer > 0 and can_jump and not self.crouch:
            speed = iabs(self.vx)

            # Running jump begins around fast-walk speed and
            # scales naturally because horizontal vx is retained.
            self.run_jump = (speed >= 520)

            if self.run_jump:
                self.vy = self.JUMP_RUN
            else:
                self.vy = self.JUMP_IDLE

            self.on_ground = False
            self.coyote = 0
            self.jump_buffer = 0
            self.jump_hold = 0

        if self.vy < 0:
            if jump and self.jump_hold < self.MAX_HOLD:
                self.jump_hold += 1

                if self.run_jump:
                    gravity = self.GRAV_HOLD_RUN
                else:
                    gravity = self.GRAV_HOLD_IDLE
            else:
                gravity = self.GRAV_RELEASE
        else:
            gravity = self.GRAV_FALL

        self.vy += gravity
        if self.vy > self.MAX_FALL:
            self.vy = self.MAX_FALL

        # ----------------------------------------------------
        # X COLLISION
        # ----------------------------------------------------
        self.x += self.vx

        if self.x < 0:
            self.x = 0
            self.vx = 0

        px = self.px()
        py = self.py()
        ph = self.height()

        coll = world.collision_tiles(px, py, self.W, ph)

        i = 0
        while i < len(coll):
            c, r, ch = coll[i]
            tx, ty = world.tile_xy(c, r)

            if aabb(px, py, self.W, ph, tx, ty, TILE, TILE):
                if self.vx > 0:
                    px = tx - self.W
                elif self.vx < 0:
                    px = tx + TILE

                self.x = px * FP
                self.vx = 0
            i += 1

        # ----------------------------------------------------
        # Y COLLISION
        # ----------------------------------------------------
        old_py = self.py()
        old_ph = self.height()
        old_bottom = old_py + old_ph
        old_top = old_py
        old_vy = self.vy

        self.y += self.vy

        px = self.px()
        py = self.py()
        ph = self.height()

        coll = world.collision_tiles(px, py, self.W, ph)
        landed = False

        if old_vy > 0:
            best_top = 9999

            i = 0
            while i < len(coll):
                c, r, ch = coll[i]
                tx, ty = world.tile_xy(c, r)

                if aabb(px, py, self.W, ph, tx, ty, TILE, TILE):
                    if old_bottom <= ty + 6 and ty < best_top:
                        best_top = ty
                i += 1

            if best_top != 9999:
                self.y = (best_top - self.stand_height()) * FP
                self.vy = 0
                landed = True

        elif old_vy < 0:
            best_bottom = -9999
            hit_c = -1
            hit_r = -1

            i = 0
            while i < len(coll):
                c, r, ch = coll[i]
                tx, ty = world.tile_xy(c, r)

                if aabb(px, py, self.W, ph, tx, ty, TILE, TILE):
                    bottom = ty + TILE

                    if old_top >= bottom - 7 and bottom > best_bottom:
                        best_bottom = bottom
                        hit_c = c
                        hit_r = r
                i += 1

            if hit_c >= 0:
                self.y = best_bottom * FP
                self.vy = 0
                world.hit_block(hit_c, hit_r)

        self.on_ground = landed

        # Ground stability probe
        if not self.on_ground and self.vy >= 0:
            px = self.px()
            py = self.py()
            ph = self.height()

            coll = world.collision_tiles(px, py + 1, self.W, ph)

            i = 0
            while i < len(coll):
                c, r, ch = coll[i]
                tx, ty = world.tile_xy(c, r)

                if py + ph <= ty + 1:
                    self.on_ground = True
                    self.vy = 0
                    self.y = (ty - self.stand_height()) * FP
                    break
                i += 1

        # ----------------------------------------------------
        # ITEM COLLISION
        # ----------------------------------------------------
        px = self.px()
        py = self.py()
        ph = self.height()

        i = 0
        while i < len(world.items):
            it = world.items[i]

            if it[6] and aabb(px, py, self.W, ph, it[1], it[2], 14, 15):
                if it[0] == 0:
                    # Mushroom -> Super (or keep current higher state)
                    if self.power == 0:
                        self.set_power(1)
                else:
                    self.set_power(2)

                it[6] = 0
                world.score += 1000
            i += 1

        # ----------------------------------------------------
        # ENEMY COLLISION
        # ----------------------------------------------------
        i = 0
        while i < len(world.enemies):
            e = world.enemies[i]

            if e[4] and e[5] <= 0 and e[6] <= 0:
                if aabb(px, py, self.W, ph, e[0], e[1], 14, 14):
                    if old_vy > 0 and old_bottom <= e[1] + 8:
                        e[5] = 13
                        self.vy = -1080
                        self.on_ground = False
                        world.score += 100
                    else:
                        self.hurt(world)
                        break
            i += 1

        # Pit = direct death, regardless of power state
        if self.py() > H + 30 and not self.dead:
            self.dead = True
            self.vx = 0
            self.vy = -1300
            world.lives -= 1

        # Animation clock
        if self.on_ground and iabs(self.vx) > 60:
            self.anim += 1
        else:
            self.anim = 0

# ============================================================
# INPUT
# [left, right, down, run_held, jump_held,
#  jump_pressed, b_pressed]
#
# V3 uses edge LATCHES. If an EXE/SHIFT press arrives between two
# physics steps, the edge stays remembered until physics consumes it.
# ============================================================
_prev_jump = False
_prev_b = False
_jump_latched = False
_b_latched = False

def reset_input_edges():
    global _prev_jump, _prev_b, _jump_latched, _b_latched

    gint.clearevents()
    _prev_jump = bool(gint.keydown(gint.KEY_EXE))
    _prev_b = bool(gint.keydown(gint.KEY_SHIFT))
    _jump_latched = False
    _b_latched = False

def read_input():
    global _prev_jump, _prev_b, _jump_latched, _b_latched

    gint.clearevents()

    left = bool(gint.keydown(gint.KEY_LEFT))
    right = bool(gint.keydown(gint.KEY_RIGHT))
    down = bool(gint.keydown(gint.KEY_DOWN))

    run = bool(gint.keydown(gint.KEY_SHIFT))
    jump = bool(gint.keydown(gint.KEY_EXE))

    if jump and not _prev_jump:
        _jump_latched = True

    if run and not _prev_b:
        _b_latched = True

    _prev_jump = jump
    _prev_b = run

    return [
        left,
        right,
        down,
        run,
        jump,
        _jump_latched,
        _b_latched
    ]

def consume_input_edges():
    global _jump_latched, _b_latched
    _jump_latched = False
    _b_latched = False

# ============================================================
# V3 ZOOMED RENDER LAYER
# World physics remain 16x16. Screen tiles become 24x20.
# ============================================================
def draw_ground_tile(x, y):
    gint.drect(x, y, x + TILE_SW - 1, y + TILE_SH - 1, GROUND)
    gint.drect(x, y, x + TILE_SW - 1, y + 3, GROUND_LIGHT)
    gint.dline(x, y + 10, x + TILE_SW - 1, y + 10, GROUND_DARK)

def draw_brick(x, y):
    gint.drect(x, y, x + TILE_SW - 1, y + TILE_SH - 1, BRICK)
    gint.drect(x, y, x + TILE_SW - 1, y + 3, BRICK_LIGHT)
    gint.dline(x, y + 9, x + TILE_SW - 1, y + 9, GROUND_DARK)
    gint.dline(x + 11, y, x + 11, y + 9, GROUND_DARK)

def draw_question(x, y, used):
    if used:
        gint.drect(x, y, x + TILE_SW - 1, y + TILE_SH - 1, USED)
        gint.drect(x, y, x + TILE_SW - 1, y + 3, GROUND_LIGHT)
        return

    gint.drect(x, y, x + TILE_SW - 1, y + TILE_SH - 1, QUESTION)
    gint.drect(x + 3, y + 2, x + TILE_SW - 4, y + 5, QUESTION_LIGHT)

    # Larger hand-drawn question mark.
    gint.drect(x + 9, y + 5, x + 14, y + 7, WHITE)
    gint.drect(x + 14, y + 7, x + 16, y + 10, WHITE)
    gint.drect(x + 11, y + 10, x + 14, y + 12, WHITE)
    gint.drect(x + 11, y + 15, x + 14, y + 17, WHITE)

def draw_pipe_tile(x, y, ch):
    gint.drect(x, y, x + TILE_SW - 1, y + TILE_SH - 1, PIPE)

    if ch == T_PL or ch == T_BL:
        gint.drect(x + 3, y, x + 6, y + TILE_SH - 1, PIPE_LIGHT)
    else:
        gint.drect(x + TILE_SW - 6, y, x + TILE_SW - 3, y + TILE_SH - 1, PIPE_DARK)

    if ch == T_PL or ch == T_PR:
        gint.drect(x, y, x + TILE_SW - 1, y + 3, PIPE_LIGHT)

def draw_map(world):
    cam = world.camera

    c0 = cam // TILE - 1
    c1 = (cam + VIEW_WORLD_W) // TILE + 1

    if c0 < 0:
        c0 = 0
    if c1 >= MAP_COLS:
        c1 = MAP_COLS - 1

    r = 0
    while r < MAP_ROWS:
        wy = MAP_Y + r * TILE
        y = sy(wy)

        # Entire tile row off screen.
        if y + TILE_SH >= HUD_H and y < H:
            c = c0
            while c <= c1:
                ch = world.map[r][c]

                if ch != T_EMPTY:
                    x = sx(c * TILE, cam)

                    if ch == T_GROUND:
                        draw_ground_tile(x, y)
                    elif ch == T_BRICK:
                        draw_brick(x, y)
                    elif ch == T_QCOIN or ch == T_QPOWER:
                        draw_question(x, y, False)
                    elif ch == T_USED:
                        draw_question(x, y, True)
                    elif ch == T_PL or ch == T_PR or ch == T_BL or ch == T_BR:
                        draw_pipe_tile(x, y, ch)

                c += 1

        r += 1

# ============================================================
# CHARACTER / ITEM DRAWING
# ============================================================
def choose_player_sprite(p):
    if not p.on_ground:
        if p.power == 0:
            return SPR_SMALL_JUMP
        return SPR_BIG_JUMP

    if p.crouch and p.power > 0:
        return SPR_BIG_CROUCH

    if p.skid:
        if p.power == 0:
            return SPR_SMALL_SKID
        return SPR_BIG_STAND

    speed = iabs(p.vx)

    if speed < 80:
        if p.power == 0:
            return SPR_SMALL_STAND
        return SPR_BIG_STAND

    if speed > 700:
        phase = (p.anim // 2) & 1
    else:
        phase = (p.anim // 4) & 1

    if p.power == 0:
        return SPR_SMALL_WALK1 if phase == 0 else SPR_SMALL_WALK2

    return SPR_BIG_WALK1 if phase == 0 else SPR_BIG_WALK2

def draw_player(p, cam):
    if p.invuln > 0 and ((p.invuln // 3) & 1) == 0:
        return

    # FEET ANCHOR:
    # visible sprite bottom is always exactly the physical collision feet.
    feet = p.py() + p.height()
    center_x = p.px() + p.W // 2

    if p.power == 2:
        palette = FIRE_PALETTE
    else:
        palette = BASE_PALETTE

    spr = choose_player_sprite(p)

    if p.power == 0:
        visual_w = 15
        visual_h = 20
    elif p.crouch:
        visual_w = 16
        visual_h = 19
    else:
        visual_w = 16
        visual_h = 30

    draw_sprite_feet(
        spr,
        center_x,
        feet,
        visual_w,
        visual_h,
        cam,
        p.facing,
        palette
    )

def draw_goomba(e, cam, frame):
    if not e[4]:
        return

    x = sx(e[0], cam)
    y = sy(e[1])
    ew = scale_x(14)
    eh = scale_y(14)

    if x + ew < 0 or x >= W:
        return

    if e[6] > 0:
        color = FIREBALL_INNER if (e[6] & 1) else GOOMBA
        gint.drect(x + 3, y + 2, x + ew - 4, y + eh - 3, color)
        return

    if e[5] > 0:
        gint.drect(x, y + eh // 2, x + ew - 1, y + eh - 1, GOOMBA)
        gint.drect(x + 3, y + eh - 4, x + ew - 4, y + eh - 1, GOOMBA_DARK)
        return

    gint.drect(x + 3, y + 2, x + ew - 4, y + eh - 4, GOOMBA)
    gint.drect(x, y + eh - 5, x + 6, y + eh - 1, GOOMBA_DARK)
    gint.drect(x + ew - 7, y + eh - 5, x + ew - 1, y + eh - 1, GOOMBA_DARK)

    # Eyes
    gint.drect(x + 5, y + 6, x + 7, y + 8, WHITE)
    gint.drect(x + ew - 8, y + 6, x + ew - 6, y + 8, WHITE)
    gint.dpixel(x + 7, y + 8, BLACK)
    gint.dpixel(x + ew - 8, y + 8, BLACK)

def draw_mushroom(it, cam):
    x = sx(it[1], cam)
    y = sy(it[2])
    iw = scale_x(14)
    ih = scale_y(14)

    if x + iw < 0 or x >= W:
        return

    gint.drect(x + 6, y + 8, x + iw - 7, y + ih - 1, SKIN)
    gint.drect(x + 2, y + 4, x + iw - 3, y + 10, RED)
    gint.drect(x + 5, y + 2, x + iw - 6, y + 6, RED)
    gint.drect(x + 5, y + 4, x + 8, y + 7, WHITE)
    gint.drect(x + iw - 9, y + 5, x + iw - 5, y + 8, WHITE)

def draw_flower(it, cam, frame):
    x = sx(it[1], cam)
    y = sy(it[2])
    iw = scale_x(14)
    ih = scale_y(15)

    if x + iw < 0 or x >= W:
        return

    if frame & 1:
        c1 = FLOWER_RED
        c2 = FLOWER_YELLOW
    else:
        c1 = FLOWER_YELLOW
        c2 = FLOWER_RED

    gint.drect(x + iw // 2 - 1, y + 9, x + iw // 2 + 2, y + ih - 1, FLOWER_GREEN)
    gint.drect(x + 6, y + 4, x + iw - 7, y + 11, WHITE)
    gint.drect(x + 2, y + 6, x + 7, y + 10, c1)
    gint.drect(x + iw - 8, y + 6, x + iw - 3, y + 10, c1)
    gint.drect(x + 7, y + 1, x + iw - 8, y + 5, c2)

def draw_popcoin(p, cam):
    x = sx(p[0], cam)
    y = sy(p[1])
    gint.drect(x - 3, y - 8, x + 3, y + 8, COIN)
    gint.dline(x, y - 7, x, y + 7, COIN_DARK)

def draw_fireball(f, cam, frame):
    if not f[0]:
        return

    x = sx(f[1] // FP, cam)
    y = sy(f[2] // FP)

    if frame & 1:
        gint.drect(x, y + 2, x + 7, y + 5, FIREBALL_OUTER)
        gint.drect(x + 2, y, x + 5, y + 7, FIREBALL_INNER)
    else:
        gint.drect(x + 2, y, x + 5, y + 7, FIREBALL_OUTER)
        gint.drect(x, y + 2, x + 7, y + 5, FIREBALL_INNER)

# ============================================================
# BACKGROUND / GOAL / HUD
# ============================================================
def draw_background(world):
    gint.dclear(SKY)

    # Screen-space decorative background. Deliberately cheap.
    gint.drect(22, 167, 91, 197, HILL)
    gint.drect(39, 148, 74, 197, HILL)
    gint.drect(51, 134, 63, 197, HILL)

    gint.drect(274, 176, 349, 197, HILL)
    gint.drect(294, 155, 331, 197, HILL)

    # Clouds
    gint.drect(54, 48, 91, 57, CLOUD)
    gint.drect(62, 41, 75, 57, CLOUD)
    gint.drect(77, 44, 87, 57, CLOUD)

    gint.drect(286, 67, 326, 76, CLOUD)
    gint.drect(297, 59, 310, 76, CLOUD)

def draw_goal(world):
    cam = world.camera
    ground_y = MAP_Y + 13 * TILE

    x = sx(world.flag_x, cam)

    if x > -40 and x < W + 40:
        gy = sy(ground_y)
        gint.drect(x, 37, x + 3, gy, WHITE)
        gint.drect(x + 4, 52, x + 34, 65, FLAG)

    cx = sx(204 * TILE, cam)
    cy = sy(ground_y - 48)

    if cx < W + 120 and cx + 120 > -30:
        cw = scale_x(74)
        ch = scale_y(48)

        gint.drect(cx, cy + scale_y(16), cx + cw, cy + ch + scale_y(16), CASTLE)
        gint.drect(cx, cy + scale_y(8), cx + scale_x(16), cy + scale_y(18), CASTLE)
        gint.drect(cx + scale_x(25), cy + scale_y(8),
                   cx + scale_x(41), cy + scale_y(18), CASTLE)
        gint.drect(cx + scale_x(50), cy + scale_y(8),
                   cx + scale_x(66), cy + scale_y(18), CASTLE)
        gint.drect(cx + scale_x(29), cy + scale_y(48),
                   cx + scale_x(45), cy + scale_y(64), CASTLE_DARK)

def draw_hud(world):
    # HUD is intentionally NOT zoomed with the world.
    gint.drect(0, 0, W - 1, HUD_H - 1, MENU_BLUE)

    gint.dtext(4, 1, WHITE, "MARIO " + str(world.score))
    gint.dtext(145, 1, WHITE, "1-1")
    gint.dtext(218, 1, WHITE, "C " + str(world.coins))
    gint.dtext(290, 1, WHITE, "L " + str(world.lives))

    if world.player.power == 2:
        gint.dtext(344, 1, WHITE, "F")

def draw_world(world, visual_frame):
    draw_background(world)
    draw_map(world)

    i = 0
    while i < len(world.popcoins):
        draw_popcoin(world.popcoins[i], world.camera)
        i += 1

    i = 0
    while i < len(world.items):
        it = world.items[i]

        if it[6]:
            if it[0] == 0:
                draw_mushroom(it, world.camera)
            else:
                draw_flower(it, world.camera, visual_frame)

        i += 1

    i = 0
    while i < len(world.enemies):
        draw_goomba(world.enemies[i], world.camera, visual_frame)
        i += 1

    i = 0
    while i < 2:
        draw_fireball(world.fireballs[i], world.camera, visual_frame)
        i += 1

    draw_goal(world)
    draw_player(world.player, world.camera)
    draw_hud(world)
    gint.dupdate()

# ============================================================
# MENU
# ============================================================
def wait_key_release(key):
    # Prevent the EXE used to open the script from instantly selecting menu.
    n = 0
    while n < 80:
        gint.clearevents()
        if not gint.keydown(key):
            return
        time.sleep_ms(15)
        n += 1

def show_menu():
    wait_key_release(gint.KEY_EXE)

    blink = 0

    while True:
        gint.clearevents()

        if gint.keydown(gint.KEY_EXIT):
            return False

        if gint.keydown(gint.KEY_EXE):
            wait_key_release(gint.KEY_EXE)
            reset_input_edges()
            return True

        gint.dclear(SKY)

        # Frame
        gint.drect(25, 28, 358, 169, MENU_BLUE)
        gint.drect(31, 34, 352, 163, GROUND_DARK)

        gint.dtext(82, 48, WHITE, "MARIO CG50 WIDE")
        gint.dtext(137, 73, COIN, "WORLD 1-1")

        # Tiny decorative mushroom and flower.
        gint.drect(74, 99, 89, 109, RED)
        gint.drect(78, 108, 85, 119, SKIN)
        gint.drect(77, 101, 80, 104, WHITE)
        gint.drect(85, 102, 88, 105, WHITE)

        gint.drect(288, 105, 291, 119, FLOWER_GREEN)
        gint.drect(282, 97, 297, 108, WHITE)
        gint.drect(279, 100, 284, 106, FLOWER_RED)
        gint.drect(295, 100, 300, 106, FLOWER_YELLOW)

        if (blink // 10) & 1:
            gint.dtext(125, 132, WHITE, "EXE  START")
        else:
            gint.dtext(125, 132, QUESTION_LIGHT, "EXE  START")

        gint.dtext(128, 181, WHITE, "EXIT  QUIT")
        gint.dupdate()

        blink += 1
        time.sleep_ms(30)

# ============================================================
# PIKACHU END-SCREEN PATTERN
# This is a small hand-built pixel graphic shown after clearing 1-1.
# ============================================================
PIKA_PATTERN = (
"....KK..........KK....",
"...KYYK........KYYK...",
"..KYYYYK......KYYYYK..",
"..KYYYYYK....KYYYYYK..",
".KYYYYYYYYKKYYYYYYYYK.",
"KYYYYYYYYYYYYYYYYYYYYK",
"KYYYYKYYYYYYYYYYKYYYYK",
"KYYYYKKYYYYYYYYKKYYYYK",
"KYYYYYYYYYYYYYYYYYYYYK",
"KYYRRYYYYYYYYYYYYRRYYK",
"KYYYYYYYYKKYYYYYYYYYYK",
".KYYYYYYYKKYYYYYYYYYK.",
"..KYYYYYYYYYYYYYYYYK..",
"...KYYYYYYYYYYYYYYK...",
"....KYYYYYYYYYYYYK....",
".....KYYYYYYYYYYK.....",
"....YYKYYYYYYYYKYY....",
"...YYYYYYYYYYYYYYYY...",
"...YYY..YYYYYY..YYY...",
"....KK..........KK....",
)

def draw_pika_pattern():
    cell = 5
    ph = len(PIKA_PATTERN)
    pw = len(PIKA_PATTERN[0])

    ox = (W - pw * cell) // 2
    oy = 52

    y = 0
    while y < ph:
        row = PIKA_PATTERN[y]
        x = 0

        while x < pw:
            ch = row[x]

            if ch != ".":
                if ch == "Y":
                    color = PIKA_YELLOW
                elif ch == "R":
                    color = PIKA_RED
                elif ch == "K":
                    color = PIKA_DARK
                else:
                    color = PIKA_BROWN

                sx0 = ox + x * cell
                sy0 = oy + y * cell
                gint.drect(sx0, sy0, sx0 + cell - 1, sy0 + cell - 1, color)

            x += 1

        y += 1

def show_pika_clear():
    wait_key_release(gint.KEY_EXE)
    time.sleep_ms(250)

    while True:
        gint.clearevents()

        if gint.keydown(gint.KEY_EXIT):
            return False

        if gint.keydown(gint.KEY_EXE):
            wait_key_release(gint.KEY_EXE)
            return True

        gint.dclear(MENU_BLUE)
        gint.dtext(137, 18, WHITE, "COURSE CLEAR")
        gint.dtext(145, 35, PIKA_YELLOW, "HI PIKA!")

        draw_pika_pattern()

        gint.dtext(117, 184, WHITE, "EXE  MENU")
        gint.dtext(121, 199, WHITE, "EXIT QUIT")
        gint.dupdate()

        time.sleep_ms(30)

# ============================================================
# GAME SESSION
# ============================================================
def run_game():
    world = World()
    gc.collect()
    reset_input_edges()

    last_ms = time.ticks_ms()
    accum = 0
    visual_frame = 0

    while True:
        loop_start = time.ticks_ms()

        now = loop_start
        elapsed = time.ticks_diff(now, last_ms)
        last_ms = now

        if elapsed < 0:
            elapsed = 0
        if elapsed > 100:
            elapsed = 100

        accum += elapsed

        inp = read_input()

        # EXIT from gameplay returns all the way out.
        if gint.keydown(gint.KEY_EXIT):
            return 0

        steps = 0

        while accum >= STEP_MS and steps < MAX_CATCHUP_STEPS:
            world.update(inp)

            # Edge events are consumed only AFTER a real physics update.
            if steps == 0:
                consume_input_edges()
                inp[5] = False
                inp[6] = False

            accum -= STEP_MS
            steps += 1

        draw_world(world, visual_frame)
        visual_frame += 1

        if world.won:
            return 1

        used = time.ticks_diff(time.ticks_ms(), loop_start)
        wait = STEP_MS - used

        if wait > 0:
            time.sleep_ms(wait)

# ============================================================
# APP FLOW
# ============================================================
app_running = True

while app_running:
    if not show_menu():
        break

    result = run_game()

    if result == 0:
        break

    # Finished World 1-1 -> Pikachu "HI PIKA!" graphic.
    if not show_pika_clear():
        break

    # EXE from clear screen returns to the menu.

gint.dclear(gint.C_WHITE)
gint.dtext(10, 10, gint.C_BLACK, "Game exited.")
gint.dupdate()
