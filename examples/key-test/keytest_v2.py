# SPDX-License-Identifier: MIT
"""Minimal multi-key input test for fx-CG50 + PythonExtra.

Copy this file to the calculator, open it from PythonExtra > FILES,
then press EXE. Hold LEFT/RIGHT, SHIFT and EXE to test input.
Press EXIT to quit.
"""

import gint
import time


while not gint.keydown(gint.KEY_EXIT):
    left = gint.keydown(gint.KEY_LEFT)
    right = gint.keydown(gint.KEY_RIGHT)
    run = gint.keydown(gint.KEY_SHIFT)
    jump = gint.keydown(gint.KEY_EXE)

    gint.dclear(gint.C_WHITE)
    gint.dtext(12, 12, gint.C_BLACK, "PythonExtra key test")
    gint.dtext(12, 42, gint.C_BLACK, "LEFT:  " + str(int(left)))
    gint.dtext(12, 62, gint.C_BLACK, "RIGHT: " + str(int(right)))
    gint.dtext(12, 82, gint.C_BLACK, "SHIFT: " + str(int(run)))
    gint.dtext(12, 102, gint.C_BLACK, "EXE:   " + str(int(jump)))

    if right and run and jump:
        gint.dtext(12, 138, gint.C_RED, "RIGHT + SHIFT + EXE")

    gint.dtext(12, 190, gint.C_BLACK, "EXIT: quit")
    gint.dupdate()
    time.sleep_ms(50)


gint.dclear(gint.C_WHITE)
gint.dtext(12, 12, gint.C_BLACK, "Key test exited.")
gint.dupdate()
