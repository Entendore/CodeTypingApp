import math
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ListProperty
from kivy.graphics import Color, Line, Ellipse
from theme import ACCENT

class VectorIcon(Widget):
    """Renders crisp, themeable vector icons using Kivy canvas instructions."""
    icon = StringProperty('home')
    icolor = ListProperty(ACCENT)

    def __init__(self, icon='home', color=None, **kw):
        kw.setdefault('size_hint', (None, None))
        kw.setdefault('size', (24, 24))
        super().__init__(**kw)
        self.icon = icon
        self.icolor = list(color or ACCENT)
        self.bind(pos=self._redraw, size=self._redraw, icon=self._redraw, icolor=self._redraw)

    def _redraw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(*self.icolor)
            cx, cy = self.center_x, self.center_y
            s = min(self.width, self.height) * 0.82
            lw = max(1.4, s / 11)
            fn = getattr(self, f'_draw_{self.icon}', None)
            if fn: fn(cx, cy, s, lw)

    def _draw_home(self, cx, cy, s, lw):
        Line(points=[cx-s*.42,cy+s*.08, cx,cy+s*.45, cx+s*.42,cy+s*.08], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.32,cy+s*.08, cx-s*.32,cy-s*.38, cx+s*.32,cy-s*.38, cx+s*.32,cy+s*.08], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.09,cy-s*.38, cx-s*.09,cy-s*.12, cx+s*.09,cy-s*.12, cx+s*.09,cy-s*.38], width=lw*.7, cap='round', joint='round')

    def _draw_keyboard(self, cx, cy, s, lw):
        Line(rounded_rectangle=(cx-s*.48,cy-s*.35,s*.96,s*.7,3), width=lw)
        kw, kh, gap = s*.12, s*.1, s*.04
        for r in range(2):
            for c in range(4):
                kx = cx - s*.32 + c*(kw+gap); ky = cy + s*.12 - r*(kh+gap)
                Line(rounded_rectangle=(kx,ky,kw,kh,1), width=lw*.6)
        Line(rounded_rectangle=(cx-s*.18,cy-s*.24,s*.36,kh,2), width=lw*.6)

    def _draw_trophy(self, cx, cy, s, lw):
        Line(points=[cx-s*.32,cy+s*.45, cx-s*.22,cy-s*.02, cx+s*.22,cy-s*.02, cx+s*.32,cy+s*.45], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.32,cy+s*.45, cx+s*.32,cy+s*.45], width=lw)
        Line(points=[cx-s*.32,cy+s*.35, cx-s*.46,cy+s*.28, cx-s*.42,cy+s*.12, cx-s*.32,cy+s*.12], width=lw*.7, cap='round')
        Line(points=[cx+s*.32,cy+s*.35, cx+s*.46,cy+s*.28, cx+s*.42,cy+s*.12, cx+s*.32,cy+s*.12], width=lw*.7, cap='round')
        Line(points=[cx,cy-s*.02, cx,cy-s*.22], width=lw)
        Line(points=[cx-s*.18,cy-s*.22, cx+s*.18,cy-s*.22], width=lw, cap='round')
        Line(points=[cx-s*.05,cy+s*.28, cx+s*.05,cy+s*.18, cx+s*.12,cy+s*.28], width=lw*.5, cap='round', joint='round')

    def _draw_code(self, cx, cy, s, lw):
        Line(points=[cx-s*.18,cy+s*.35, cx-s*.42,cy, cx-s*.18,cy-s*.35], width=lw, cap='round', joint='round')
        Line(points=[cx+s*.18,cy-s*.35, cx+s*.42,cy, cx+s*.18,cy+s*.35], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.06,cy+s*.22, cx+s*.06,cy-s*.22], width=lw*.7, cap='round')

    def _draw_star(self, cx, cy, s, lw):
        pts = []
        for i in range(10):
            a = math.pi/2 + i * math.pi/5; r = s*.45 if i%2==0 else s*.2
            pts += [cx + r*math.cos(a), cy + r*math.sin(a)]
        pts += pts[:2]; Line(points=pts, width=lw, cap='round', joint='round')

    def _draw_bolt(self, cx, cy, s, lw):
        Line(points=[cx+s*.08,cy+s*.45, cx-s*.15,cy+s*.04, cx+s*.08,cy+s*.04, cx-s*.12,cy-s*.45], width=lw, cap='round', joint='round')

    def _draw_flame(self, cx, cy, s, lw):
        pts_out = []
        for i in range(20):
            t = i / 19; a = math.pi * t; r = s*.4 * (1 - .3*math.sin(a*3))
            px = cx + r * math.sin(a) * .7; py = cy - s*.35 + s*.7 * t; pts_out += [px, py]
        Line(points=pts_out, width=lw, cap='round')
        pts_in = []
        for i in range(12):
            t = i / 11; a = math.pi * t; r = s*.15 * (1 - .2*math.sin(a*2))
            px = cx + r * math.sin(a) * .6; py = cy - s*.15 + s*.35 * t; pts_in += [px, py]
        Line(points=pts_in, width=lw*.6, cap='round')

    def _draw_chart(self, cx, cy, s, lw):
        Line(points=[cx-s*.4,cy-s*.4, cx-s*.4,cy+s*.4, cx+s*.4,cy+s*.4], width=lw, cap='round')
        bw = s*.14
        for i, h in enumerate([.35, .6, .45, .8]):
            bx = cx-s*.3 + i*(bw+s*.06); by = cy-s*.4; bh = s*.7*h
            Line(rounded_rectangle=(bx,by,bw,bh,2), width=lw*.7)

    def _draw_plus(self, cx, cy, s, lw):
        Line(points=[cx,cy-s*.35, cx,cy+s*.35], width=lw, cap='round')
        Line(points=[cx-s*.35,cy, cx+s*.35,cy], width=lw, cap='round')

    def _draw_refresh(self, cx, cy, s, lw):
        Line(circle=(cx, cy, s*.32, 45, 315), width=lw, cap='round')
        ax = cx + s*.32*math.cos(math.radians(315)); ay = cy + s*.32*math.sin(math.radians(315))
        Line(points=[ax,ay, ax+s*.12,ay+s*.08, ax+s*.04,ay-s*.1], width=lw*.8, cap='round', joint='round')
        ax2 = cx + s*.32*math.cos(math.radians(45)); ay2 = cy + s*.32*math.sin(math.radians(45))
        Line(points=[ax2,ay2, ax2-s*.12,ay2-s*.08, ax2-s*.04,ay2+s*.1], width=lw*.8, cap='round', joint='round')

    def _draw_arrow_right(self, cx, cy, s, lw):
        Line(points=[cx-s*.3,cy, cx+s*.2,cy], width=lw, cap='round')
        Line(points=[cx+s*.05,cy+s*.2, cx+s*.3,cy, cx+s*.05,cy-s*.2], width=lw, cap='round', joint='round')

    def _draw_trash(self, cx, cy, s, lw):
        Line(points=[cx-s*.28,cy+s*.38, cx-s*.22,cy-s*.12, cx+s*.22,cy-s*.12, cx+s*.28,cy+s*.38], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.38,cy+s*.38, cx+s*.38,cy+s*.38], width=lw, cap='round')
        Line(points=[cx-s*.12,cy-s*.12, cx-s*.08,cy-s*.35, cx+s*.08,cy-s*.35, cx+s*.12,cy-s*.12], width=lw*.8, cap='round', joint='round')
        for dx in [-.08, .08]: Line(points=[cx+s*dx,cy-s*.02, cx+s*dx,cy+s*.28], width=lw*.5, cap='round')

    def _draw_check(self, cx, cy, s, lw):
        Line(points=[cx-s*.3,cy+s*.02, cx-s*.08,cy-s*.22, cx+s*.32,cy+s*.32], width=lw*1.2, cap='round', joint='round')

    def _draw_target(self, cx, cy, s, lw):
        Line(circle=(cx,cy,s*.38), width=lw); Line(circle=(cx,cy,s*.2), width=lw*.7)
        Ellipse(pos=(cx-s*.06,cy-s*.06), size=(s*.12,s*.12))

    def _draw_sparkle(self, cx, cy, s, lw):
        for a in [0, math.pi/2, math.pi, 3*math.pi/2]:
            x1 = cx + s*.06*math.cos(a+math.pi/2); y1 = cy + s*.06*math.sin(a+math.pi/2)
            x2 = cx + s*.38*math.cos(a); y2 = cy + s*.38*math.sin(a)
            x3 = cx - s*.06*math.cos(a+math.pi/2); y3 = cy - s*.06*math.sin(a+math.pi/2)
            Line(points=[x1,y1, x2,y2, x3,y3], width=lw, cap='round', joint='round')

    def _draw_dice(self, cx, cy, s, lw):
        Line(rounded_rectangle=(cx-s*.35,cy-s*.35,s*.7,s*.7,5), width=lw)
        ds = s*.055
        for dx,dy in [(-.15,.15),(.15,.15),(0,0),(-.15,-.15),(.15,-.15)]:
            Ellipse(pos=(cx+s*dx-ds,cy+s*dy-ds), size=(ds*2,ds*2))

    def _draw_clock(self, cx, cy, s, lw):
        Line(circle=(cx,cy,s*.38), width=lw)
        Line(points=[cx,cy, cx,cy+s*.22], width=lw, cap='round')
        Line(points=[cx,cy, cx+s*.16,cy+s*.06], width=lw*.8, cap='round')

    def _draw_hash(self, cx, cy, s, lw):
        Line(points=[cx-s*.12,cy+s*.35, cx+s*.12,cy-s*.35], width=lw, cap='round')
        Line(points=[cx+s*.12,cy+s*.35, cx-s*.12,cy-s*.35], width=lw, cap='round')
        Line(points=[cx-s*.32,cy+s*.1, cx+s*.32,cy+s*.1], width=lw, cap='round')
        Line(points=[cx-s*.32,cy-s*.1, cx+s*.32,cy-s*.1], width=lw, cap='round')

    def _draw_play(self, cx, cy, s, lw):
        # FIX: Removed rogue `cx, cy` positional arguments and properly closed the triangle loop
        Line(points=[cx-s*.18,cy+s*.3, cx-s*.18,cy-s*.3, cx+s*.28,cy, cx-s*.18,cy+s*.3],
             width=lw, cap='round', joint='round')

    def _draw_close(self, cx, cy, s, lw):
        Line(points=[cx-s*.25,cy+s*.25, cx+s*.25,cy-s*.25], width=lw, cap='round')
        Line(points=[cx+s*.25,cy+s*.25, cx-s*.25,cy-s*.25], width=lw, cap='round')