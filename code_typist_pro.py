# ═══════════════════════════════════════════════════════════════
#  Code Typist Pro  —  Single-file Kivy application
# ═══════════════════════════════════════════════════════════════

import math
import time
import random
import sqlite3
from datetime import datetime, date

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import escape_markup
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty, ListProperty,
)
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse


# ─── THEME ───────────────────────────────────────────────────
def hex_to_rgba(h, alpha=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16)/255.0 for i in (0, 2, 4)) + (alpha,)

BG_DARK    = hex_to_rgba('#0b0d1a')
BG_MAIN    = hex_to_rgba('#12142a')
BG_CARD    = hex_to_rgba('#1a1d3a')
BG_INPUT   = hex_to_rgba('#161833')
BG_HOVER   = hex_to_rgba('#22254a')
ACCENT     = hex_to_rgba('#6c5ce7')
ACCENT_L   = hex_to_rgba('#a29bfe')
ACCENT_D   = hex_to_rgba('#4834d4')
SUCCESS    = hex_to_rgba('#00e676')
ERROR      = hex_to_rgba('#ff5252')
WARNING    = hex_to_rgba('#ffab40')
INFO       = hex_to_rgba('#40c4ff')
TEXT_P     = hex_to_rgba('#eceff1')
TEXT_S     = hex_to_rgba('#90a4ae')
TEXT_M     = hex_to_rgba('#546e7a')
BORDER     = hex_to_rgba('#26294a')
GLOW       = hex_to_rgba('#6c5ce7', 0.15)

C_ACCENT   = '#6c5ce7'; C_ACCENT_L = '#a29bfe'; C_SUCCESS  = '#00e676'
C_ERROR    = '#ff5252'; C_WARNING  = '#ffab40'; C_TEXT_P   = '#eceff1'
C_TEXT_M   = '#546e7a'; C_TEXT_S   = '#90a4ae'; C_INFO     = '#40c4ff'

RAD = [10]; RAD_LG = [16]; RAD_SM = [6]
PAD = [15, 20]; PAD_LG = [25, 30]


# ─── VECTOR ICONS ───────────────────────────────────────────
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
        Line(points=[cx-s*.18,cy+s*.3, cx-s*.18,cy-s*.3, cx+s*.28,cy, cx-s*.18,cy+s*.3],
             width=lw, cap='round', joint='round')

    def _draw_close(self, cx, cy, s, lw):
        Line(points=[cx-s*.25,cy+s*.25, cx+s*.25,cy-s*.25], width=lw, cap='round')
        Line(points=[cx+s*.25,cy+s*.25, cx-s*.25,cy-s*.25], width=lw, cap='round')

    def _draw_footprints(self, cx, cy, s, lw):
        # Simple footprint icon: two oval shapes offset
        Line(ellipse=(cx-s*.1, cy+s*.05, s*.18, s*.25), width=lw)
        Line(ellipse=(cx+s*.1, cy-s*.15, s*.15, s*.2), width=lw)


# ─── DATABASE ────────────────────────────────────────────────
DEFAULT_SNIPPETS = [
    ("Python","Hello World",'print("Hello, World!")',"easy"),
    ("Python","Variable Swap","a, b = b, a","easy"),
    ("Python","List Comprehension","squares = [x**2 for x in range(10)]","easy"),
    ("Python","For Loop","for i in range(5):\n    print(i)","easy"),
    ("Python","If-Else","if score >= 90:\n    grade = 'A'\nelse:\n    grade = 'B'","easy"),
    ("Python","Function","def add(a, b):\n    return a + b","easy"),
    ("Python","Dict Iteration","for k, v in data.items():\n    print(f'{k}: {v}')","medium"),
    ("Python","Try-Except","try:\n    result = 10 / x\nexcept ZeroDivisionError:\n    print('Error')","medium"),
    ("Python","Class","class Dog:\n    def __init__(self, name):\n        self.name = name","medium"),
    ("Python","Decorator","def timer(func):\n    def wrapper(*args):\n        return func(*args)\n    return wrapper","hard"),
    ("JavaScript","Console Log",'console.log("Hello, World!");',"easy"),
    ("JavaScript","Arrow Function","const add = (a, b) => a + b;","easy"),
    ("JavaScript","Array Map","const doubled = nums.map(n => n * 2);","easy"),
    ("JavaScript","Async","async function fetchData(url) {\n    const res = await fetch(url);\n    return res.json();\n}","hard"),
    ("C","Hello World",'#include <stdio.h>\nint main() {\n    printf("Hello!");\n    return 0;\n}',"easy"),
    ("C","Pointer Swap","void swap(int *a, int *b) {\n    int temp = *a;\n    *a = *b;\n    *b = temp;\n}","medium"),
    ("Java","Hello World",'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello!");\n    }\n}',"easy"),
    ("Java","ArrayList",'ArrayList<String> list = new ArrayList<>();\nlist.add("Hello");',"medium"),
    ("Rust","Function",'fn greet(name: &str) -> String {\n    format!("Hello, {}!", name)\n}',"medium"),
    ("Go","Hello World",'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello!")\n}',"easy"),
    ("SQL","Select","SELECT * FROM users\nWHERE age > 18;","easy"),
]

DEFAULT_ACHIEVEMENTS = [
    ("First Steps","Complete your first snippet","footprints"),
    ("Speed Demon","Reach 40 WPM","bolt"),
    ("Lightning Fingers","Reach 80 WPM","bolt"),
    ("Perfectionist","Get 100% accuracy","target"),
    ("Streak Starter","3-day streak","flame"),
    ("Week Warrior","7-day streak","flame"),
    ("Ten Down","Complete 10 snippets","chart"),
    ("Hard Mode","Complete a hard snippet","trophy"),
    ("Combo King","50-character combo","sparkle"),
    ("Polyglot","3+ languages","code"),
]


class Database:
    def __init__(self):
        self.path = 'code_typist_pro.db'
        conn = sqlite3.connect(self.path); c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS snippets (id INTEGER PRIMARY KEY AUTOINCREMENT, language TEXT, title TEXT, code TEXT, difficulty TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY CHECK (id=1), total_xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1, current_streak INTEGER DEFAULT 0, best_wpm REAL DEFAULT 0, total_snippets INTEGER DEFAULT 0, session_count INTEGER DEFAULT 0, last_active DATE)')
        c.execute('CREATE TABLE IF NOT EXISTS achievements (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, icon TEXT, unlocked INTEGER DEFAULT 0, unlocked_at TIMESTAMP)')
        c.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, language TEXT, wpm REAL, accuracy REAL, xp_earned INTEGER, combo_max INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        c.execute('INSERT OR IGNORE INTO user_stats (id) VALUES (1)')
        if c.execute('SELECT COUNT(*) FROM snippets').fetchone()[0]==0:
            c.executemany('INSERT INTO snippets VALUES (NULL,?,?,?,?)', DEFAULT_SNIPPETS)
        if c.execute('SELECT COUNT(*) FROM achievements').fetchone()[0]==0:
            c.executemany('INSERT INTO achievements VALUES (NULL,?,?,?,0,NULL)', DEFAULT_ACHIEVEMENTS)
        conn.commit(); conn.close()

    def execute(self, q, p=(), fetch=False):
        conn = sqlite3.connect(self.path); conn.row_factory = sqlite3.Row
        c = conn.cursor(); c.execute(q, p)
        res = [dict(r) for r in c.fetchall()] if fetch else None
        if not fetch: conn.commit()
        conn.close(); return res

    def get_stats(self): return (self.execute('SELECT * FROM user_stats WHERE id=1', fetch=True) or [{}])[0]
    def update_stats(self, **kw): [self.execute(f'UPDATE user_stats SET {k}=? WHERE id=1',(v,)) for k,v in kw.items()]
    def get_snippets(self, lang=None, diff=None):
        q,p='SELECT * FROM snippets WHERE 1=1',[]
        if lang: q+=' AND language=?'; p.append(lang)
        if diff: q+=' AND difficulty=?'; p.append(diff)
        return self.execute(q,p,True)
    def add_snippet(self,l,t,c,d): self.execute('INSERT INTO snippets (language,title,code,difficulty) VALUES (?,?,?,?)',(l,t,c,d))
    def delete_snippet(self,i): self.execute('DELETE FROM snippets WHERE id=?',(i,))
    def get_achievements(self): return self.execute('SELECT * FROM achievements', fetch=True)
    def unlock_achievement(self,i): self.execute('UPDATE achievements SET unlocked=1, unlocked_at=? WHERE id=?',(datetime.now().isoformat(),i))
    def add_history(self,l,w,a,x,c): self.execute('INSERT INTO history (language,wpm,accuracy,xp_earned,combo_max) VALUES (?,?,?,?,?)',(l,w,a,x,c))
    def get_history(self): return self.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT 10', fetch=True)
    def get_completed_languages(self): return [r['language'] for r in self.execute('SELECT DISTINCT language FROM history', fetch=True)]
    def update_streak(self):
        r = self.execute('SELECT last_active, current_streak FROM user_stats WHERE id=1', fetch=True)[0]
        today = str(date.today())
        if r['last_active']==today: return
        ns = r['current_streak']+1 if r['last_active']==str(date.fromtimestamp(time.time()-86400)) else 1
        self.execute('UPDATE user_stats SET last_active=?, current_streak=? WHERE id=1',(today,ns))


db = Database()


# ─── GAME LOGIC ──────────────────────────────────────────────
def xp_for_level(l): return sum(i*100 for i in range(1,l))
def calc_level(xp):
    lv=1
    while xp_for_level(lv+1)<=xp: lv+=1
    return lv
def xp_to_next(l): return l*100
def calc_xp(d,w,a,c): return {'easy':20,'medium':40,'hard':60}.get(d,30)+max(0,int(w-20))+(15 if a==100 else 0)+c//10

def check_achievements(s,w,a,d,c):
    new,langs = [],db.get_completed_languages()
    for ach in db.get_achievements():
        if ach['unlocked']: continue
        n=ach['name']; ok=False
        if n=="First Steps" and s['total_snippets']>=1: ok=True
        elif n=="Speed Demon" and w>=40: ok=True
        elif n=="Lightning Fingers" and w>=80: ok=True
        elif n=="Perfectionist" and a==100: ok=True
        elif n=="Streak Starter" and s['current_streak']>=3: ok=True
        elif n=="Week Warrior" and s['current_streak']>=7: ok=True
        elif n=="Ten Down" and s['total_snippets']>=10: ok=True
        elif n=="Hard Mode" and d=='hard': ok=True
        elif n=="Combo King" and c>=50: ok=True
        elif n=="Polyglot" and len(langs)>=3: ok=True
        if ok: db.unlock_achievement(ach['id']); new.append(ach)
    return new


# ─── UI COMPONENTS ──────────────────────────────────────────
class IconBadge(Widget):
    def __init__(self, icon='home', bg=ACCENT, fg=TEXT_P, badge_size=36, **kw):
        kw.setdefault('size_hint', (None, None)); kw.setdefault('size', (badge_size, badge_size))
        super().__init__(**kw)
        self._bg = list(bg); self._fg = list(fg); self._icon = icon
        self._vec = VectorIcon(icon=icon, color=fg, size=(badge_size*.55, badge_size*.55))
        self.add_widget(self._vec); self.bind(pos=self._layout, size=self._layout)

    def _layout(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg); RoundedRectangle(pos=self.pos, size=self.size, radius=[9])
        self._vec.center = self.center

    def set_icon(self, icon): self._icon = icon; self._vec.icon = icon
    def set_colors(self, bg=None, fg=None):
        if bg: self._bg = list(bg)
        if fg: self._fg = list(fg); self._vec.icolor = list(fg)
        self._layout()


class AppCard(BoxLayout):
    def __init__(self, radius=RAD, bg=BG_CARD, border_color=None, accent_top=None, **kw):
        self._radius = radius; self._bg = list(bg); self._border = border_color; self._accent = accent_top
        super().__init__(**kw); self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg); RoundedRectangle(pos=self.pos, size=self.size, radius=self._radius)
            if self._accent:
                Color(*self._accent); h = 3
                RoundedRectangle(pos=(self.x, self.y+self.height-h), size=(self.width, h), radius=[self._radius[0], self._radius[0], 0, 0])
            if self._border:
                Color(*self._border); Line(rounded_rectangle=(*self.pos, *self.size, *self._radius), width=1.0)


class AppButton(Button):
    def __init__(self, text="", icon=None, bg=ACCENT, fg=TEXT_P, radius=RAD, **kw):
        super().__init__(**kw)
        self.text = text; self._bg = list(bg); self._fg = list(fg); self._radius = radius; self._icon_name = icon
        self.background_color = (0,0,0,0); self.color = fg; self.background_normal = ''; self.background_down = ''
        self.padding = [20, 10]; self.bind(state=self._draw, pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        bg = self._bg if self.state == 'normal' else [min(c+.12,1) for c in self._bg[:3]]+[1]
        with self.canvas.before:
            Color(*bg); RoundedRectangle(pos=self.pos, size=self.size, radius=self._radius)
            Color(1,1,1,.04); RoundedRectangle(pos=(self.x, self.y+self.height-1), size=(self.width, 1), radius=[0])


class AppInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = (0,0,0,0); self.foreground_color = TEXT_P; self.cursor_color = ACCENT_L
        self.padding = [15, 12, 15, 12]; self.bind(pos=self._draw, size=self._draw, focus=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear(); border = ACCENT if self.focus else BORDER
        with self.canvas.before:
            Color(*BG_INPUT); RoundedRectangle(pos=self.pos, size=self.size, radius=RAD)
            Color(*border); Line(rounded_rectangle=(*self.pos, *self.size, *RAD), width=1.0)
            if self.focus:
                Color(*GLOW); RoundedRectangle(pos=(self.x-2, self.y-2), size=(self.width+4, self.height+4), radius=[12])


class CodeInput(AppInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'tab': self.insert_text('    '); return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)


class AppSpinner(Spinner):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = (0,0,0,0); self.color = TEXT_P; self.background_normal = ''
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_INPUT); RoundedRectangle(pos=self.pos, size=self.size, radius=RAD)
            Color(*BORDER); Line(rounded_rectangle=(*self.pos, *self.size, *RAD), width=1.0)
            Color(*TEXT_M); ax = self.x + self.width - 22; ay = self.center_y
            Line(points=[ax-5,ay+3, ax,ay-3, ax+5,ay+3], width=1.2, cap='round', joint='round')


class CodeDisplay(Label):
    target = StringProperty(""); typed = StringProperty("")
    def __init__(self, **kw):
        super().__init__(**kw); self.markup = True; self.bind(texture_size=self._update_height)
    def _update_height(self, inst, val): self.height = val[1]
    def on_target(self, *a): self._refresh()
    def on_typed(self, *a): self._refresh()

    def _refresh(self):
        res = ""
        for i, char in enumerate(self.target):
            e = escape_markup(char)
            if char == '\n': res += '\n'; continue
            if char == '\t': res += '    '; continue
            if i < len(self.typed):
                res += f'[color={C_SUCCESS}]{e}[/color]' if self.typed[i]==char else f'[color={C_ERROR}]{e}[/color]'
            elif i == len(self.typed): res += f'[color={C_TEXT_P}][u]{e}[/u][/color]'
            else: res += f'[color={C_TEXT_M}]{e}[/color]'
        self.text = res


class XPBar(Widget):
    progress = NumericProperty(0)
    def __init__(self, **kw):
        super().__init__(**kw); self.size_hint_y = None; self.height = 10
        self.bind(pos=self._draw, size=self._draw, progress=self._draw)
    def _draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(*BG_DARK); RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
            if self.progress > 0:
                fw = max(self.width * self.progress, 8)
                Color(*ACCENT); RoundedRectangle(pos=self.pos, size=(fw, self.height), radius=[5])
                Color(*ACCENT_L); RoundedRectangle(pos=self.pos, size=(fw, 3), radius=[5,5,0,0])
    def set_data(self, cur, need): self.progress = min(cur / max(need, 1), 1.0)


class NavButton(BoxLayout):
    is_active = BooleanProperty(False)
    def __init__(self, icon='home', label='Home', **kw):
        super().__init__(orientation='horizontal', spacing=12, size_hint_y=None, height=46, **kw)
        self._icon_name = icon; self._label_text = label; self.padding = [8, 5]
        self.badge = IconBadge(icon=icon, bg=BG_CARD, fg=TEXT_M, badge_size=30)
        self.lbl = Label(text=label, font_size='13sp', color=TEXT_S, halign='left', valign='middle')
        self.lbl.bind(size=self.lbl.setter('text_size'))
        self.add_widget(self.badge); self.add_widget(self.lbl)
        self.bind(is_active=self._update, pos=self._update, size=self._update)

    def _update(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_active:
                Color(*ACCENT); RoundedRectangle(pos=(self.x, self.y+4), size=(3, self.height-8), radius=[2])
                Color(*hex_to_rgba('#6c5ce7', 0.12)); RoundedRectangle(pos=(self.x+3, self.y+2), size=(self.width-3, self.height-4), radius=[8])
        if self.is_active:
            self.badge.set_colors(bg=ACCENT, fg=TEXT_P); self.lbl.color = TEXT_P; self.lbl.bold = True
        else:
            self.badge.set_colors(bg=BG_CARD, fg=TEXT_M); self.lbl.color = TEXT_S; self.lbl.bold = False


class AchievementPopup(ModalView):
    def __init__(self, achievement, **kw):
        super().__init__(**kw)
        self.size_hint = (None, None); self.size = (420, 130); self.auto_dismiss = True; self.background = ''; self.background_color = (0,0,0,0)
        layout = AppCard(orientation='horizontal', padding=[20,15], spacing=18, radius=RAD_LG, border_color=ACCENT)
        badge = IconBadge(icon='sparkle', bg=ACCENT, fg=TEXT_P, badge_size=48)
        vbox = BoxLayout(orientation='vertical', spacing=2)
        t = Label(text="Achievement Unlocked!", font_size='10sp', color=ACCENT, size_hint_y=None, height=16, halign='left')
        n = Label(text=achievement['name'], font_size='16sp', bold=True, color=TEXT_P, halign='left', size_hint_y=None, height=24)
        d = Label(text=achievement['description'], font_size='12sp', color=TEXT_S, halign='left')
        for l in [t,n,d]: l.bind(size=l.setter('text_size'))
        vbox.add_widget(t); vbox.add_widget(n); vbox.add_widget(d)
        layout.add_widget(badge); layout.add_widget(vbox); self.add_widget(layout)
        Clock.schedule_once(self.dismiss, 3.5)


# ─── ACHIEVEMENTS SCREEN ────────────────────────────────────
class AchievementsScreen(Screen):
    def on_enter(self, *a): self.refresh()

    def refresh(self):
        achs = db.get_achievements()
        unlocked = sum(1 for a in achs if a['unlocked'])
        self.count_label.text = f"{unlocked} / {len(achs)} Unlocked"
        self.grid.clear_widgets()
        for a in achs:
            icon_name = a['icon'] if a['icon'] else 'star'
            bg = ACCENT if a['unlocked'] else hex_to_rgba('#ffffff',0.04)
            fg = TEXT_P if a['unlocked'] else TEXT_M
            border = ACCENT if a['unlocked'] else BORDER
            card = AppCard(orientation='vertical', padding=14, spacing=4, size_hint_y=None, height=155, radius=RAD, border_color=border, accent_top=ACCENT if a['unlocked'] else None)
            badge = IconBadge(icon=icon_name, bg=bg, fg=fg, badge_size=40)
            badge.size_hint = (None, None); badge.size = (40, 40)
            badge_container = BoxLayout(size_hint_y=None, height=48); badge_container.add_widget(badge)
            card.add_widget(badge_container)
            tc = TEXT_P if a['unlocked'] else TEXT_M
            card.add_widget(Label(text=a['name'], font_size='13sp', bold=True, color=tc, size_hint_y=None, height=22))
            card.add_widget(Label(text=a['description'], font_size='11sp', color=TEXT_S, size_hint_y=None, height=18))
            if a['unlocked']: card.add_widget(Label(text=f"Unlocked {a['unlocked_at'][:10]}", font_size='10sp', color=SUCCESS, size_hint_y=None, height=16))
            self.grid.add_widget(card)


# ─── DASHBOARD SCREEN ───────────────────────────────────────
class DashboardScreen(Screen):
    def on_enter(self, *a): self.refresh()

    def refresh(self):
        s = db.get_stats(); lv = calc_level(s.get('total_xp',0))
        self.level_val.text = str(lv)
        self.streak_val.text = f"{s.get('current_streak',0)}"
        self.wpm_val.text = f"{s.get('best_wpm',0):.0f}"
        self.total_val.text = str(s.get('total_snippets',0))
        xp_in = s.get('total_xp',0) - xp_for_level(lv)
        self.xp_bar.set_data(xp_in, xp_to_next(lv))
        self.xp_label.text = f"Level {lv}  ·  {xp_in} / {xp_to_next(lv)} XP"

        self.hist_box.clear_widgets()
        for h in db.get_history():
            row = AppCard(radius=RAD_SM, bg=BG_INPUT, spacing=10, size_hint_y=None, height=42, padding=[12,6])
            diff_col = SUCCESS if h.get('accuracy',0)>=95 else (WARNING if h.get('accuracy',0)>=80 else ERROR)
            row.add_widget(Label(text=h['language'], color=ACCENT, size_hint_x=0.18, font_size='12sp', bold=True))
            row.add_widget(Label(text=f"{h['wpm']:.0f} WPM", color=TEXT_P, size_hint_x=0.2, font_size='12sp'))
            row.add_widget(Label(text=f"{h['accuracy']:.1f}%", color=diff_col, size_hint_x=0.15, font_size='12sp'))
            row.add_widget(Label(text=f"+{h['xp_earned']} XP", color=WARNING, size_hint_x=0.15, font_size='12sp'))
            row.add_widget(Label(text=h['timestamp'][:10] if h['timestamp'] else "", color=TEXT_M, size_hint_x=0.22, font_size='11sp'))
            self.hist_box.add_widget(row)

        langs = ['All'] + sorted(set(s['language'] for s in db.get_snippets()))
        self.lang_spin.values = langs
        if self.lang_spin.text not in langs: self.lang_spin.text = 'All'

    def start_practice(self):
        d = self.diff_spin.text; l = self.lang_spin.text
        self.manager.get_screen('practice').set_filter(d if d!="All" else None, l if l!="All" else None)
        self.manager.current = 'practice'


# ─── PRACTICE SCREEN ────────────────────────────────────────
class PracticeScreen(Screen):
    target_text = StringProperty(""); typed_text = StringProperty("")
    current_snippet = None; start_time = None; elapsed = 0.0
    max_combo = 0; session_count = 0; completed = False

    def on_enter(self, *a):
        if not self.current_snippet: self.load_random()
        self.input_field.focus = True

    def set_filter(self, diff, lang):
        self.diff_spin.text = diff or "All"; self.lang_spin.text = lang or "All"
        self.load_random()

    def load_random(self):
        d = self.diff_spin.text if self.diff_spin.text!="All" else None
        l = self.lang_spin.text if self.lang_spin.text!="All" else None
        snips = db.get_snippets(l, d)
        if not snips: self.info_label.text = "No snippets found. Change filters or add new ones."; return
        self.current_snippet = random.choice(snips); self.reset()

    def reset(self):
        if not self.current_snippet: return
        self.completed=False; self.start_time=None; self.elapsed=0.0; self.max_combo=0
        Clock.unschedule(self.tick)
        s = self.current_snippet
        self.info_label.text = f"[color={C_ACCENT}]{s['language']}[/color]  ·  [color={C_WARNING}]{s['difficulty'].upper()}[/color]  ·  {s['title']}"
        self.target_text = s['code']; self.typed_text = ""
        self.code_display.target = self.target_text; self.code_display.typed = ""
        self.input_field.text = ""; self.timer_label.text = "0:00"
        self.wpm_label.text = "0"; self.acc_label.text = "100%"; self.combo_label.text = "x0"
        self.input_field.focus = True

    def on_text_change(self, inst, val):
        if self.completed or not self.current_snippet: return
        self.typed_text = val; self.code_display.typed = val
        if self.start_time is None and len(val)>0:
            self.start_time = time.time(); Clock.schedule_interval(self.tick, 0.1)
        target = self.target_text; clen = min(len(val), len(target))
        correct = cur_combo = combo = 0
        for i in range(clen):
            if val[i]==target[i]: correct+=1; cur_combo+=1; combo=max(combo,cur_combo)
            else: cur_combo=0
        self.max_combo = max(self.max_combo, combo)
        if self.start_time and self.elapsed>0:
            self.wpm_label.text = f"{(len(val)/5)/(self.elapsed/60):.0f}"
        if len(val)>0:
            acc = correct/len(val)*100; self.acc_label.text = f"{acc:.1f}%"
            self.acc_label.color = SUCCESS if acc>=95 else (WARNING if acc>=80 else ERROR)
        ct = f"x{cur_combo}"
        if cur_combo>=50: ct += "  🔥🔥"
        elif cur_combo>=25: ct += "  🔥"
        elif cur_combo>=10: ct += "  ✨"
        self.combo_label.text = ct
        if len(val)>=len(target): self.complete()

    def tick(self, dt):
        if self.start_time:
            self.elapsed = time.time()-self.start_time
            m,s = int(self.elapsed)//60, int(self.elapsed)%60
            self.timer_label.text = f"{m}:{s:02d}"

    def complete(self):
        self.completed=True; Clock.unschedule(self.tick)
        if self.start_time: self.elapsed=time.time()-self.start_time
        target=self.target_text; typed=self.typed_text[:len(target)]
        correct=sum(1 for i in range(len(target)) if i<len(typed) and typed[i]==target[i])
        accuracy=correct/len(target)*100 if target else 0
        wpm=(len(target)/5)/(self.elapsed/60) if self.elapsed>0 else 0
        xp=calc_xp(self.current_snippet['difficulty'],wpm,accuracy,self.max_combo)

        db.update_streak(); stats=db.get_stats()
        new_xp=stats.get('total_xp',0)+xp; new_lv=calc_level(new_xp); self.session_count+=1
        db.update_stats(total_xp=new_xp, level=new_lv,
                        best_wpm=max(stats.get('best_wpm',0),wpm),
                        total_snippets=stats.get('total_snippets',0)+1,
                        session_count=self.session_count)
        db.add_history(self.current_snippet['language'],wpm,accuracy,xp,self.max_combo)
        new_achs=check_achievements(db.get_stats(),wpm,accuracy,self.current_snippet['difficulty'],self.max_combo)
        lv=calc_level(new_xp); xp_in=new_xp-xp_for_level(lv)

        popup = ModalView(size_hint=(None,None), size=(500,480), auto_dismiss=False, background='', background_color=(0,0,0,0))
        card = AppCard(orientation='vertical', padding=PAD_LG, spacing=18, radius=RAD_LG, border_color=ACCENT)
        card.size_hint=(None,None); card.size=(500,480)

        hdr = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=50)
        hdr.add_widget(IconBadge(icon='check', bg=SUCCESS, fg=TEXT_P, badge_size=44))
        vbox_h = BoxLayout(orientation='vertical')
        vbox_h.add_widget(Label(text="Snippet Complete!", font_size='24sp', bold=True, color=TEXT_P, halign='left', size_hint_y=None, height=30))
        vbox_h.add_widget(Label(text=self.current_snippet['language']+" · "+self.current_snippet['title'], font_size='12sp', color=TEXT_S, halign='left', size_hint_y=None, height=18))
        for l in [vbox_h.children[1], vbox_h.children[0]]: l.bind(size=l.setter('text_size'))
        hdr.add_widget(vbox_h); card.add_widget(hdr)

        grid = GridLayout(cols=4, spacing=12, size_hint_y=None, height=110)
        for ico, txt, val, col in [('bolt','WPM',f"{wpm:.0f}",ACCENT_L),('target','Accuracy',f"{accuracy:.1f}%",SUCCESS),('sparkle','Combo',f"x{self.max_combo}",WARNING),('star','XP',f"+{xp}",ACCENT)]:
            vbox = BoxLayout(orientation='vertical', spacing=4)
            badge = IconBadge(icon=ico, bg=hex_to_rgba('#ffffff',0.06), fg=col, badge_size=32)
            badge.size_hint = (None, None); badge.size = (32,32); badge.pos_hint = {'center_x': 0.5}
            vbox.add_widget(badge)
            vbox.add_widget(Label(text=val, font_size='22sp', bold=True, color=col, size_hint_y=None, height=30))
            vbox.add_widget(Label(text=txt, font_size='10sp', color=TEXT_S, size_hint_y=None, height=16))
            grid.add_widget(vbox)
        card.add_widget(grid)

        card.add_widget(Label(text=f"Level {lv}  ·  {xp_in}/{xp_to_next(lv)} XP", font_size='12sp', color=TEXT_S, size_hint_y=None, height=20))
        bar = XPBar(size_hint_y=None, height=10); bar.set_data(xp_in, xp_to_next(lv)); card.add_widget(bar)

        btn_row = BoxLayout(spacing=12, size_hint_y=None, height=48)
        btn_retry = AppButton(text="Retry", icon='refresh', bg=BG_INPUT, radius=RAD)
        btn_next = AppButton(text="Next Snippet", icon='arrow_right', bg=ACCENT, radius=RAD)
        btn_row.add_widget(btn_retry); btn_row.add_widget(btn_next)
        card.add_widget(btn_row); popup.add_widget(card)

        btn_retry.bind(on_release=lambda x: (popup.dismiss(), self.reset()))
        btn_next.bind(on_release=lambda x: (popup.dismiss(), self.load_random()))
        popup.open()
        for a in new_achs: AchievementPopup(a).open()


# ─── SNIPPETS SCREEN ────────────────────────────────────────
class SnippetsScreen(Screen):
    def on_enter(self, *a): self.refresh()

    def refresh(self):
        lang = self.lang_spin.text; diff = self.diff_spin.text
        langs = ['All']+sorted(set(s['language'] for s in db.get_snippets()))
        self.lang_spin.values = langs
        if self.lang_spin.text not in langs: self.lang_spin.text = 'All'
        snippets = db.get_snippets(lang if lang!="All" else None, diff if diff!="All" else None)
        self.grid.clear_widgets()
        for s in snippets:
            diff_col = SUCCESS if s['difficulty']=='easy' else (WARNING if s['difficulty']=='medium' else ERROR)
            card = AppCard(orientation='vertical', padding=14, spacing=6, size_hint_y=None, height=115, radius=RAD, accent_top=diff_col)
            row1 = BoxLayout(spacing=8, size_hint_y=None, height=24)
            badge = IconBadge(icon='code', bg=hex_to_rgba('#ffffff',0.06), fg=ACCENT, badge_size=22)
            badge.size_hint = (None,None); badge.size = (22,22); row1.add_widget(badge)
            row1.add_widget(Label(text=s['language'], color=ACCENT, font_size='11sp', size_hint_x=0.15, bold=True))
            row1.add_widget(Label(text=s['difficulty'].upper(), color=diff_col, font_size='10sp', size_hint_x=0.12, bold=True))
            row1.add_widget(Label(text=s['title'], color=TEXT_P, font_size='14sp', bold=True, size_hint_x=0.5))
            del_btn = AppButton(text="Delete", icon='trash', bg=hex_to_rgba('#ff5252',0.15), fg=ERROR, radius=RAD_SM, size_hint_x=None, width=60)
            del_btn.bind(on_release=lambda btn, sid=s['id']: (db.delete_snippet(sid), self.refresh()))
            row1.add_widget(del_btn); card.add_widget(row1)
            prev = s['code'][:80].replace('\n',' ↵ ')+("..." if len(s['code'])>80 else "")
            card.add_widget(Label(text=prev, font_size='11sp', color=TEXT_M, halign='left', valign='top'))
            self.grid.add_widget(card)

    def show_add_popup(self):
        popup = ModalView(size_hint=(None,None), size=(500,480), auto_dismiss=False, background='', background_color=(0,0,0,0))
        card = AppCard(orientation='vertical', padding=PAD_LG, spacing=12, radius=RAD_LG, border_color=ACCENT)
        card.size_hint=(None,None); card.size=(500,480)

        hdr = BoxLayout(orientation='horizontal', spacing=12, size_hint_y=None, height=40)
        hdr.add_widget(IconBadge(icon='plus', bg=ACCENT, fg=TEXT_P, badge_size=36))
        hdr.add_widget(Label(text="Add New Snippet", font_size='20sp', bold=True, color=TEXT_P))
        card.add_widget(hdr)

        card.add_widget(Label(text="Language", font_size='11sp', color=TEXT_S, size_hint_y=None, height=16, halign='left'))
        langs = sorted(set(s['language'] for s in db.get_snippets()))
        lang_spin = AppSpinner(text="Python", values=langs, size_hint_y=None, height=40); card.add_widget(lang_spin)

        card.add_widget(Label(text="Title", font_size='11sp', color=TEXT_S, size_hint_y=None, height=16, halign='left'))
        title_in = AppInput(multiline=False, size_hint_y=None, height=40, hint_text="e.g. Binary Search"); card.add_widget(title_in)

        card.add_widget(Label(text="Code", font_size='11sp', color=TEXT_S, size_hint_y=None, height=16, halign='left'))
        code_in = AppInput(multiline=True, hint_text="Paste code here..."); card.add_widget(code_in)

        card.add_widget(Label(text="Difficulty", font_size='11sp', color=TEXT_S, size_hint_y=None, height=16, halign='left'))
        diff_spin = AppSpinner(text="medium", values=["easy","medium","hard"], size_hint_y=None, height=40); card.add_widget(diff_spin)

        add_btn = AppButton(text="Add Snippet", icon='plus', bg=ACCENT, radius=RAD, size_hint_y=None, height=48); card.add_widget(add_btn)

        def do_add(inst):
            t,c = title_in.text.strip(), code_in.text.strip()
            if t and c: db.add_snippet(lang_spin.text,t,c,diff_spin.text); popup.dismiss(); self.refresh()
            else: title_in.hint_text = "Required!"
        add_btn.bind(on_release=do_add)
        popup.add_widget(card); popup.open()


# ─── MAIN APP ───────────────────────────────────────────────
class CodeTypistApp(App):
    def build(self):
        Window.clearcolor = BG_MAIN
        sm = ScreenManager(transition=SlideTransition(duration=0.2))

        # ── DASHBOARD ──────────────────────────────────────
        dash = DashboardScreen(name='dashboard')
        d_box = BoxLayout(orientation='vertical', padding=[35,25], spacing=16)
        hdr = BoxLayout(size_hint_y=None, height=45)
        hdr.add_widget(Label(text="Dashboard", font_size='26sp', bold=True, halign='left', color=TEXT_P))
        hdr.children[0].bind(size=hdr.children[0].setter('text_size')); d_box.add_widget(hdr)

        top_grid = GridLayout(cols=4, spacing=12, size_hint_y=None, height=115)
        stat_defs = [('level_val', 'star', 'Level', ACCENT), ('streak_val', 'flame', 'Streak', WARNING), ('wpm_val', 'bolt', 'Best WPM', INFO), ('total_val', 'chart', 'Completed', SUCCESS)]
        for attr, ico, txt, col in stat_defs:
            vbox = AppCard(orientation='vertical', padding=14, spacing=4, radius=RAD, accent_top=col)
            badge_row = BoxLayout(size_hint_y=None, height=34)
            badge = IconBadge(icon=ico, bg=hex_to_rgba('#ffffff',0.06), fg=col, badge_size=30)
            badge.size_hint = (None,None); badge.size = (30,30)
            badge_row.add_widget(badge); badge_row.add_widget(Label(text=txt, font_size='11sp', color=TEXT_S))
            vbox.add_widget(badge_row); val = Label(text="0", font_size='28sp', bold=True, color=col); vbox.add_widget(val)
            setattr(dash, attr, val); top_grid.add_widget(vbox)
        d_box.add_widget(top_grid)

        xp_box = BoxLayout(orientation='vertical', spacing=4, size_hint_y=None, height=28)
        dash.xp_label = Label(text="", font_size='11sp', color=TEXT_S, halign='left', size_hint_y=None, height=14)
        dash.xp_label.bind(size=dash.xp_label.setter('text_size')); dash.xp_bar = XPBar()
        xp_box.add_widget(dash.xp_label); xp_box.add_widget(dash.xp_bar); d_box.add_widget(xp_box)

        qs = AppCard(orientation='horizontal', padding=[14,10], spacing=12, size_hint_y=None, height=52, radius=RAD)
        qs_badge = IconBadge(icon='play', bg=ACCENT, fg=TEXT_P, badge_size=32)
        qs_badge.size_hint = (None,None); qs_badge.size = (32,32); qs.add_widget(qs_badge)
        qs.add_widget(Label(text="Quick Start", font_size='14sp', bold=True, color=TEXT_P, size_hint_x=0.15))
        dash.diff_spin = AppSpinner(text="All", values=["All","easy","medium","hard"], size_hint_x=0.18)
        dash.lang_spin = AppSpinner(text="All", values=["All","Python"], size_hint_x=0.18)
        start_btn = AppButton(text="Start Practice", icon='keyboard', bg=ACCENT, radius=RAD, size_hint_x=0.35)
        start_btn.bind(on_release=lambda x: dash.start_practice())
        qs.add_widget(dash.diff_spin); qs.add_widget(dash.lang_spin); qs.add_widget(start_btn); d_box.add_widget(qs)

        d_box.add_widget(Label(text="Recent Activity", font_size='15sp', bold=True, color=TEXT_P, size_hint_y=None, height=28, halign='left'))
        hist_scroll = ScrollView(); dash.hist_box = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None)
        dash.hist_box.bind(minimum_height=dash.hist_box.setter('height'))
        hist_scroll.add_widget(dash.hist_box); d_box.add_widget(hist_scroll)
        dash.add_widget(d_box); sm.add_widget(dash)

        # ── PRACTICE ───────────────────────────────────────
        prac = PracticeScreen(name='practice')
        p_box = BoxLayout(orientation='vertical', padding=[35,25], spacing=12)
        top_p = AppCard(padding=[16,10], spacing=12, size_hint_y=None, height=52, radius=RAD)
        prac.info_label = Label(text="", markup=True, font_size='14sp', halign='left', color=TEXT_P)
        prac.info_label.bind(size=prac.info_label.setter('text_size'))
        timer_box = BoxLayout(size_hint_x=0.15, spacing=4)
        timer_ico = VectorIcon(icon='clock', color=ACCENT, size=(18,18)); timer_ico.size_hint = (None,None)
        prac.timer_label = Label(text="0:00", font_size='18sp', bold=True, color=ACCENT)
        timer_box.add_widget(timer_ico); timer_box.add_widget(prac.timer_label)
        top_p.add_widget(prac.info_label); top_p.add_widget(timer_box); p_box.add_widget(top_p)

        stats_p = BoxLayout(spacing=20, size_hint_y=None, height=32, padding=[8,0])
        for attr, ico, col in [('wpm_label','bolt',INFO),('acc_label','target',SUCCESS),('combo_label','sparkle',WARNING)]:
            row = BoxLayout(spacing=4, size_hint_x=0.33); vi = VectorIcon(icon=ico, color=col, size=(16,16)); vi.size_hint = (None,None)
            l = Label(text="0", font_size='14sp', bold=True, color=col); setattr(prac, attr, l)
            row.add_widget(vi); row.add_widget(l); stats_p.add_widget(row)
        p_box.add_widget(stats_p)

        code_wrap = AppCard(radius=RAD, bg=BG_INPUT, border_color=BORDER); code_wrap.size_hint_y = 0.5
        code_scroll = ScrollView(); prac.code_display = CodeDisplay(font_size='14sp', padding=[18,18,18,18], halign='left', valign='top')
        prac.code_display.bind(width=lambda i,v: setattr(i,'text_size',(v,None)))
        code_scroll.add_widget(prac.code_display); code_wrap.add_widget(code_scroll); p_box.add_widget(code_wrap)

        prac.input_field = CodeInput(font_size='14sp', size_hint_y=None, height=120)
        prac.input_field.bind(text=prac.on_text_change); p_box.add_widget(prac.input_field)

        btn_row = BoxLayout(spacing=10, size_hint_y=None, height=44)
        prac.diff_spin = AppSpinner(text="All", values=["All","easy","medium","hard"], size_hint_x=0.18)
        prac.lang_spin = AppSpinner(text="All", values=["All","Python"], size_hint_x=0.18)
        btn_retry = AppButton(text="Reset", icon='refresh', bg=BG_CARD, radius=RAD, size_hint_x=0.15)
        btn_skip = AppButton(text="Random", icon='dice', bg=ACCENT, radius=RAD, size_hint_x=0.2)
        btn_back = AppButton(text="Back", icon='home', bg=BG_CARD, radius=RAD, size_hint_x=0.12)
        btn_retry.bind(on_release=lambda x: prac.reset())
        btn_skip.bind(on_release=lambda x: prac.load_random())
        btn_back.bind(on_release=lambda x: setattr(sm,'current','dashboard'))
        btn_row.add_widget(btn_back); btn_row.add_widget(prac.diff_spin); btn_row.add_widget(prac.lang_spin)
        btn_row.add_widget(btn_retry); btn_row.add_widget(btn_skip); p_box.add_widget(btn_row)
        prac.add_widget(p_box); sm.add_widget(prac)

        # ── ACHIEVEMENTS ───────────────────────────────────
        ach = AchievementsScreen(name='achievements')
        a_box = BoxLayout(orientation='vertical', padding=[35,25], spacing=16)
        hdr_a = BoxLayout(size_hint_y=None, height=50, spacing=12)
        hdr_a.add_widget(IconBadge(icon='trophy', bg=WARNING, fg=TEXT_P, badge_size=40))
        hdr_a.add_widget(Label(text="Achievements", font_size='26sp', bold=True, halign='left', color=TEXT_P))
        hdr_a.children[0].bind(size=hdr_a.children[0].setter('text_size')); a_box.add_widget(hdr_a)
        ach.count_label = Label(text="", font_size='12sp', color=TEXT_S, halign='left', size_hint_y=None, height=18)
        ach.count_label.bind(size=ach.count_label.setter('text_size')); a_box.add_widget(ach.count_label)
        scroll_ach = ScrollView(); ach.grid = GridLayout(cols=3, spacing=12, size_hint_y=None)
        ach.grid.bind(minimum_height=ach.grid.setter('height')); scroll_ach.add_widget(ach.grid)
        a_box.add_widget(scroll_ach); ach.add_widget(a_box); sm.add_widget(ach)

        # ── SNIPPETS ───────────────────────────────────────
        snip = SnippetsScreen(name='snippets')
        s_box = BoxLayout(orientation='vertical', padding=[35,25], spacing=16)
        hdr_s = BoxLayout(size_hint_y=None, height=50, spacing=12)
        hdr_s.add_widget(IconBadge(icon='code', bg=ACCENT, fg=TEXT_P, badge_size=40))
        hdr_s.add_widget(Label(text="Snippets", font_size='26sp', bold=True, halign='left', color=TEXT_P))
        hdr_s.children[0].bind(size=hdr_s.children[0].setter('text_size'))
        btn_add = AppButton(text="Add Snippet", icon='plus', bg=ACCENT, radius=RAD, size_hint_x=0.3, size_hint_y=None, height=40)
        btn_add.bind(on_release=lambda x: snip.show_add_popup()); hdr_s.add_widget(btn_add); s_box.add_widget(hdr_s)

        filter_row = BoxLayout(spacing=12, size_hint_y=None, height=45)
        snip.lang_spin = AppSpinner(text="All", values=["All","Python"], size_hint_x=0.5)
        snip.diff_spin = AppSpinner(text="All", values=["All","easy","medium","hard"], size_hint_x=0.5)
        filter_row.add_widget(snip.lang_spin); filter_row.add_widget(snip.diff_spin); s_box.add_widget(filter_row)

        snip_back = AppButton(text="Back", icon='home', bg=BG_CARD, radius=RAD, size_hint_y=None, height=40)
        snip_back.bind(on_release=lambda x: setattr(sm,'current','dashboard')); s_box.add_widget(snip_back)

        scroll_s = ScrollView(); snip.grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        snip.grid.bind(minimum_height=snip.grid.setter('height')); scroll_s.add_widget(snip.grid); s_box.add_widget(scroll_s)
        snip.add_widget(s_box); sm.add_widget(snip)

        return sm


if __name__ == '__main__':
    CodeTypistApp().run()