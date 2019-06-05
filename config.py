# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
from pi3d_font import Font

TEXTS_FONTS = ["sans", "sans", "mono", "mono"]
TEXT_RESOLUTION = 0.5
CODEPOINTS = list(range(32, 126)) + list(range(160,255)) + ['ʒ', '~', 'ä']
FONTS = {
    "sans": Font('fonts/leaguegothic.ttf', color=(127,127,127,255), shadow=(0,0,0,127), shadow_radius=0, background_color=(0,0,0,0), font_size=int(170*TEXT_RESOLUTION), offset_y=0.015, codepoints=CODEPOINTS),
    "mono": Font('fonts/freemono.ttf', color=(127,127,127,255), shadow=(0,0,0,127), shadow_radius=0, background_color=(0,0,0,0), font_size=int(200*TEXT_RESOLUTION), offset_y=-0.005, codepoints=CODEPOINTS)
}
