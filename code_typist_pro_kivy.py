#!/usr/bin/env python3
"""
Code Typist Pro  -  Enhanced Kivy Edition (single-file)
Features: Sidebar nav, Settings, Stats/Analytics, Timed Mode, Streak Calendar,
          Import/Export, Search, Edit Snippets, Keyboard Shortcuts, Sound Feedback,
          Daily Challenge, Progress Bar, Clipboard Copy, extra languages, extra achievements.
Run:  pip install kivy  &&  python code_typist_pro_kivy.py
"""
import math, time, random, json, sqlite3, hashlib, os, struct, wave, tempfile
from datetime import datetime, date, timedelta

from kivy.app import App
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import escape_markup
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse

# === THEME ===
def hex_to_rgba(h, alpha=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (alpha,)

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
SIDEBAR_BG = hex_to_rgba('#0e1024')

C_ACCENT='#6c5ce7'; C_ACCENT_L='#a29bfe'; C_SUCCESS='#00e676'
C_ERROR='#ff5252'; C_WARNING='#ffab40'; C_TEXT_P='#eceff1'
C_TEXT_M='#546e7a'; C_TEXT_S='#90a4ae'; C_INFO='#40c4ff'

RAD=[10]; RAD_LG=[16]; RAD_SM=[6]
PAD=[15,20]; PAD_LG=[25,30]

# === SETTINGS (persistent JSON) ===
class Settings:
    PATH = 'ctp_settings.json'
    DEFAULTS = dict(font_size=14, sound_enabled=True, timer_mode='Off', countdown_seconds=60)
    def __init__(self):
        self.data = dict(self.DEFAULTS); self._load()
    def _load(self):
        try:
            with open(self.PATH) as f: self.data.update(json.load(f))
        except Exception: pass
    def save(self):
        try:
            with open(self.PATH, 'w') as f: json.dump(self.data, f, indent=2)
        except: pass
    def __getitem__(self, k): return self.data.get(k, self.DEFAULTS.get(k))
    def __setitem__(self, k, v): self.data[k] = v; self.save()

settings = Settings()

# === VECTOR ICONS ===
class VectorIcon(Widget):
    icon = StringProperty('home')
    icolor = ListProperty(ACCENT)
    def __init__(self, icon='home', color=None, **kw):
        kw.setdefault('size_hint', (None, None)); kw.setdefault('size', (24, 24))
        super().__init__(**kw); self.icon = icon; self.icolor = list(color or ACCENT)
        self.bind(pos=self._redraw, size=self._redraw, icon=self._redraw, icolor=self._redraw)
    def _redraw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(*self.icolor); cx, cy = self.center_x, self.center_y
            s = min(self.width, self.height) * 0.82; lw = max(1.4, s / 11)
            fn = getattr(self, '_draw_' + self.icon, None)
            if fn: fn(cx, cy, s, lw)
    def _draw_home(self, cx, cy, s, lw):
        Line(points=[cx-s*.42,cy+s*.08,cx,cy+s*.45,cx+s*.42,cy+s*.08], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.32,cy+s*.08,cx-s*.32,cy-s*.38,cx+s*.32,cy-s*.38,cx+s*.32,cy+s*.08], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.09,cy-s*.38,cx-s*.09,cy-s*.12,cx+s*.09,cy-s*.12,cx+s*.09,cy-s*.38], width=lw*.7, cap='round', joint='round')
    def _draw_keyboard(self, cx, cy, s, lw):
        Line(rounded_rectangle=(cx-s*.48,cy-s*.35,s*.96,s*.7,3), width=lw)
        kw2,kh,gap=s*.12,s*.1,s*.04
        for r in range(2):
            for c in range(4):
                kx=cx-s*.32+c*(kw2+gap); ky=cy+s*.12-r*(kh+gap)
                Line(rounded_rectangle=(kx,ky,kw2,kh,1), width=lw*.6)
        Line(rounded_rectangle=(cx-s*.18,cy-s*.24,s*.36,kh,2), width=lw*.6)
    def _draw_trophy(self, cx, cy, s, lw):
        Line(points=[cx-s*.32,cy+s*.45,cx-s*.22,cy-s*.02,cx+s*.22,cy-s*.02,cx+s*.32,cy+s*.45], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.32,cy+s*.45,cx+s*.32,cy+s*.45], width=lw)
        Line(points=[cx-s*.32,cy+s*.35,cx-s*.46,cy+s*.28,cx-s*.42,cy+s*.12,cx-s*.32,cy+s*.12], width=lw*.7, cap='round')
        Line(points=[cx+s*.32,cy+s*.35,cx+s*.46,cy+s*.28,cx+s*.42,cy+s*.12,cx+s*.32,cy+s*.12], width=lw*.7, cap='round')
        Line(points=[cx,cy-s*.02,cx,cy-s*.22], width=lw)
        Line(points=[cx-s*.18,cy-s*.22,cx+s*.18,cy-s*.22], width=lw, cap='round')
    def _draw_code(self, cx, cy, s, lw):
        Line(points=[cx-s*.18,cy+s*.35,cx-s*.42,cy,cx-s*.18,cy-s*.35], width=lw, cap='round', joint='round')
        Line(points=[cx+s*.18,cy-s*.35,cx+s*.42,cy,cx+s*.18,cy+s*.35], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.06,cy+s*.22,cx+s*.06,cy-s*.22], width=lw*.7, cap='round')
    def _draw_star(self, cx, cy, s, lw):
        pts=[]
        for i in range(10):
            a2=math.pi/2+i*math.pi/5; r=s*.45 if i%2==0 else s*.2
            pts+=[cx+r*math.cos(a2), cy+r*math.sin(a2)]
        pts+=pts[:2]; Line(points=pts, width=lw, cap='round', joint='round')
    def _draw_bolt(self, cx, cy, s, lw):
        Line(points=[cx+s*.08,cy+s*.45,cx-s*.15,cy+s*.04,cx+s*.08,cy+s*.04,cx-s*.12,cy-s*.45], width=lw, cap='round', joint='round')
    def _draw_flame(self, cx, cy, s, lw):
        po=[]
        for i in range(20):
            t=i/19; a2=math.pi*t; r=s*.4*(1-.3*math.sin(a2*3))
            po+=[cx+r*math.sin(a2)*.7, cy-s*.35+s*.7*t]
        Line(points=po, width=lw, cap='round')
        pi2=[]
        for i in range(12):
            t=i/11; a2=math.pi*t; r=s*.15*(1-.2*math.sin(a2*2))
            pi2+=[cx+r*math.sin(a2)*.6, cy-s*.15+s*.35*t]
        Line(points=pi2, width=lw*.6, cap='round')
    def _draw_chart(self, cx, cy, s, lw):
        Line(points=[cx-s*.4,cy-s*.4,cx-s*.4,cy+s*.4,cx+s*.4,cy+s*.4], width=lw, cap='round')
        bw=s*.14
        for i,h in enumerate([.35,.6,.45,.8]):
            bx=cx-s*.3+i*(bw+s*.06); by=cy-s*.4; bh=s*.7*h
            Line(rounded_rectangle=(bx,by,bw,bh,2), width=lw*.7)
    def _draw_plus(self, cx, cy, s, lw):
        Line(points=[cx,cy-s*.35,cx,cy+s*.35], width=lw, cap='round')
        Line(points=[cx-s*.35,cy,cx+s*.35,cy], width=lw, cap='round')
    def _draw_refresh(self, cx, cy, s, lw):
        Line(circle=(cx,cy,s*.32,45,315), width=lw, cap='round')
        ax=cx+s*.32*math.cos(math.radians(315)); ay=cy+s*.32*math.sin(math.radians(315))
        Line(points=[ax,ay,ax+s*.12,ay+s*.08,ax+s*.04,ay-s*.1], width=lw*.8, cap='round', joint='round')
        ax2=cx+s*.32*math.cos(math.radians(45)); ay2=cy+s*.32*math.sin(math.radians(45))
        Line(points=[ax2,ay2,ax2-s*.12,ay2-s*.08,ax2-s*.04,ay2+s*.1], width=lw*.8, cap='round', joint='round')
    def _draw_arrow_right(self, cx, cy, s, lw):
        Line(points=[cx-s*.3,cy,cx+s*.2,cy], width=lw, cap='round')
        Line(points=[cx+s*.05,cy+s*.2,cx+s*.3,cy,cx+s*.05,cy-s*.2], width=lw, cap='round', joint='round')
    def _draw_trash(self, cx, cy, s, lw):
        Line(points=[cx-s*.28,cy+s*.38,cx-s*.22,cy-s*.12,cx+s*.22,cy-s*.12,cx+s*.28,cy+s*.38], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.38,cy+s*.38,cx+s*.38,cy+s*.38], width=lw, cap='round')
        Line(points=[cx-s*.12,cy-s*.12,cx-s*.08,cy-s*.35,cx+s*.08,cy-s*.35,cx+s*.12,cy-s*.12], width=lw*.8, cap='round', joint='round')
        for dx in [-.08,.08]: Line(points=[cx+s*dx,cy-s*.02,cx+s*dx,cy+s*.28], width=lw*.5, cap='round')
    def _draw_check(self, cx, cy, s, lw):
        Line(points=[cx-s*.3,cy+s*.02,cx-s*.08,cy-s*.22,cx+s*.32,cy+s*.32], width=lw*1.2, cap='round', joint='round')
    def _draw_target(self, cx, cy, s, lw):
        Line(circle=(cx,cy,s*.38), width=lw); Line(circle=(cx,cy,s*.2), width=lw*.7)
        Ellipse(pos=(cx-s*.06,cy-s*.06), size=(s*.12,s*.12))
    def _draw_sparkle(self, cx, cy, s, lw):
        for a2 in [0,math.pi/2,math.pi,3*math.pi/2]:
            x1=cx+s*.06*math.cos(a2+math.pi/2); y1=cy+s*.06*math.sin(a2+math.pi/2)
            x2=cx+s*.38*math.cos(a2); y2=cy+s*.38*math.sin(a2)
            x3=cx-s*.06*math.cos(a2+math.pi/2); y3=cy-s*.06*math.sin(a2+math.pi/2)
            Line(points=[x1,y1,x2,y2,x3,y3], width=lw, cap='round', joint='round')
    def _draw_dice(self, cx, cy, s, lw):
        Line(rounded_rectangle=(cx-s*.35,cy-s*.35,s*.7,s*.7,5), width=lw)
        ds=s*.055
        for dx,dy in [(-.15,.15),(.15,.15),(0,0),(-.15,-.15),(.15,-.15)]:
            Ellipse(pos=(cx+s*dx-ds,cy+s*dy-ds), size=(ds*2,ds*2))
    def _draw_clock(self, cx, cy, s, lw):
        Line(circle=(cx,cy,s*.38), width=lw)
        Line(points=[cx,cy,cx,cy+s*.22], width=lw, cap='round')
        Line(points=[cx,cy,cx+s*.16,cy+s*.06], width=lw*.8, cap='round')
    def _draw_hash(self, cx, cy, s, lw):
        Line(points=[cx-s*.12,cy+s*.35,cx+s*.12,cy-s*.35], width=lw, cap='round')
        Line(points=[cx+s*.12,cy+s*.35,cx-s*.12,cy-s*.35], width=lw, cap='round')
        Line(points=[cx-s*.32,cy+s*.1,cx+s*.32,cy+s*.1], width=lw, cap='round')
        Line(points=[cx-s*.32,cy-s*.1,cx+s*.32,cy-s*.1], width=lw, cap='round')
    def _draw_play(self, cx, cy, s, lw):
        Line(points=[cx-s*.18,cy+s*.3,cx-s*.18,cy-s*.3,cx+s*.28,cy,cx-s*.18,cy+s*.3], width=lw, cap='round', joint='round')
    def _draw_close(self, cx, cy, s, lw):
        Line(points=[cx-s*.25,cy+s*.25,cx+s*.25,cy-s*.25], width=lw, cap='round')
        Line(points=[cx+s*.25,cy+s*.25,cx-s*.25,cy-s*.25], width=lw, cap='round')
    def _draw_footprints(self, cx, cy, s, lw):
        Line(ellipse=(cx-s*.1,cy+s*.05,s*.18,s*.25), width=lw)
        Line(ellipse=(cx+s*.1,cy-s*.15,s*.15,s*.2), width=lw)
    def _draw_settings(self, cx, cy, s, lw):
        Line(circle=(cx, cy, s*.3), width=lw)
        for a2 in range(0, 360, 45):
            r2 = math.radians(a2)
            x1=cx+s*.3*math.cos(r2); y1=cy+s*.3*math.sin(r2)
            x2=cx+s*.42*math.cos(r2); y2=cy+s*.42*math.sin(r2)
            Line(points=[x1,y1,x2,y2], width=lw, cap='round')
    def _draw_search(self, cx, cy, s, lw):
        Line(circle=(cx-s*.06, cy+s*.06, s*.25), width=lw)
        Line(points=[cx+s*.1,cy-s*.1,cx+s*.32,cy-s*.32], width=lw, cap='round')
    def _draw_copy(self, cx, cy, s, lw):
        Line(rounded_rectangle=(cx-s*.28,cy-s*.1,s*.36,s*.38,3), width=lw)
        Line(rounded_rectangle=(cx-s*.08,cy-s*.35,s*.36,s*.38,3), width=lw)
    def _draw_edit(self, cx, cy, s, lw):
        Line(points=[cx-s*.3,cy+s*.3,cx+s*.1,cy-s*.1,cx+s*.3,cy-s*.3], width=lw, cap='round', joint='round')
        Line(points=[cx+s*.1,cy-s*.1,cx+s*.25,cy+s*.05,cx+s*.3,cy-s*.1,cx+s*.15,cy-s*.25], width=lw*.6, cap='round', joint='round')
    def _draw_download(self, cx, cy, s, lw):
        Line(points=[cx,cy+s*.4,cx,cy-s*.1], width=lw, cap='round')
        Line(points=[cx-s*.2,cy-s*.2,cx,cy,cx+s*.2,cy-s*.2], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.3,cy+s*.35,cx+s*.3,cy+s*.35], width=lw, cap='round')
    def _draw_upload(self, cx, cy, s, lw):
        Line(points=[cx,cy-s*.4,cx,cy+s*.1], width=lw, cap='round')
        Line(points=[cx-s*.2,cy+s*.2,cx,cy,cx+s*.2,cy+s*.2], width=lw, cap='round', joint='round')
        Line(points=[cx-s*.3,cy-s*.35,cx+s*.3,cy-s*.35], width=lw, cap='round')
    def _draw_calendar(self, cx, cy, s, lw):
        Line(rounded_rectangle=(cx-s*.35,cy-s*.35,s*.7,s*.7,4), width=lw)
        Line(points=[cx-s*.35,cy-s*.1,cx+s*.35,cy-s*.1], width=lw)
        Line(points=[cx-s*.15,cy-s*.45,cx-s*.15,cy-s*.25], width=lw*.8, cap='round')
        Line(points=[cx+s*.15,cy-s*.45,cx+s*.15,cy-s*.25], width=lw*.8, cap='round')
        for dx,dy in [(-.15,.12),(.1,.05),(.05,.22)]:
            Ellipse(pos=(cx+s*dx-s*.04,cy+s*dy-s*.04), size=(s*.08,s*.08))

# === DATABASE ===
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
    ("Python","List Sort","nums = [3, 1, 4, 1, 5]\nnums.sort(key=lambda x: -x)","easy"),
    ("Python","With Statement","with open('file.txt') as f:\n    content = f.read()","medium"),
    ("JavaScript","Console Log",'console.log("Hello, World!");',"easy"),
    ("JavaScript","Arrow Function","const add = (a, b) => a + b;","easy"),
    ("JavaScript","Array Map","const doubled = nums.map(n => n * 2);","easy"),
    ("JavaScript","Destructuring","const {name, age} = user;\nconst [first, ...rest] = items;","medium"),
    ("JavaScript","Async","async function fetchData(url) {\n    const res = await fetch(url);\n    return res.json();\n}","hard"),
    ("JavaScript","Promise","new Promise((resolve, reject) => {\n    setTimeout(() => resolve('done'), 1000);\n});","medium"),
    ("TypeScript","Interface","interface User {\n    name: string;\n    age: number;\n    email?: string;\n}","medium"),
    ("TypeScript","Generic Function","function identity<T>(arg: T): T {\n    return arg;\n}","medium"),
    ("TypeScript","Type Guard","function isString(val: unknown): val is string {\n    return typeof val === 'string';\n}","hard"),
    ("C","Hello World",'#include <stdio.h>\nint main() {\n    printf("Hello!");\n    return 0;\n}',"easy"),
    ("C","Pointer Swap","void swap(int *a, int *b) {\n    int temp = *a;\n    *a = *b;\n    *b = temp;\n}","medium"),
    ("C","Struct","typedef struct {\n    char name[50];\n    int age;\n} Person;","medium"),
    ("C++","Vector","std::vector<int> nums = {1, 2, 3};\nnums.push_back(4);\nfor (auto n : nums) {}","medium"),
    ("C++","Class","class Animal {\npublic:\n    virtual void speak() = 0;\n};","hard"),
    ("Java","Hello World",'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello!");\n    }\n}',"easy"),
    ("Java","ArrayList",'ArrayList<String> list = new ArrayList<>();\nlist.add("Hello");',"medium"),
    ("Java","Lambda","list.stream()\n    .filter(s -> s.length() > 3)\n    .map(String::toUpperCase)\n    .collect(Collectors.toList());","hard"),
    ("Rust","Function",'fn greet(name: &str) -> String {\n    format!("Hello, {}!", name)\n}',"medium"),
    ("Rust","Match",'match value {\n    1..=10 => println!("small"),\n    _ => println!("big"),\n}',"medium"),
    ("Go","Hello World",'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello!")\n}',"easy"),
    ("Go","Goroutine",'go func() {\n    fmt.Println("running")\n}()',"medium"),
    ("Ruby","Hello World",'puts "Hello, World!"',"easy"),
    ("Ruby","Block","[1, 2, 3].map { |n| n * 2 }\n[1, 2, 3].select { |n| n > 1 }","easy"),
    ("Ruby","Class","class Dog\n  attr_accessor :name\n  def initialize(name)\n    @name = name\n  end\nend","medium"),
    ("Swift","Hello World",'print("Hello, World!")',"easy"),
    ("Swift","Optional Guard",'func greet(name: String?) {\n    guard let n = name else { return }\n    print("Hello \\(n)")\n}',"medium"),
    ("Kotlin","Hello World",'fun main() {\n    println("Hello, World!")\n}',"easy"),
    ("Kotlin","When Expression",'when (x) {\n    in 1..10 -> println("small")\n    else -> println("big")\n}',"medium"),
    ("Bash","Echo",'echo "Hello, World!"',"easy"),
    ("Bash","For Loop",'for i in {1..5}; do\n    echo "Number: $i"\ndone',"easy"),
    ("Bash","If Statement",'if [ "$age" -gt 18 ]; then\n    echo "Adult"\nelse\n    echo "Minor"\nfi',"easy"),
    ("HTML","Basic Page","<!DOCTYPE html>\n<html>\n<head><title>Page</title></head>\n<body>\n    <h1>Hello</h1>\n</body>\n</html>","easy"),
    ("CSS","Flexbox",".container {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    gap: 16px;\n}","medium"),
    ("SQL","Select","SELECT * FROM users\nWHERE age > 18\nORDER BY name ASC;","easy"),
    ("SQL","Join","SELECT u.name, o.total\nFROM users u\nJOIN orders o ON u.id = o.user_id;","medium"),
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
    ("Polyglot","Practice 3+ languages","code"),
    ("Marathon","Complete 50 snippets","star"),
    ("Scholar","Practice 6+ languages","code"),
    ("Timed Ace","Complete a timed challenge","clock"),
    ("Collector","Have 50+ snippets","plus"),
    ("Dedicated","5-day streak","flame"),
]

class Database:
    def __init__(self, path='code_typist_pro.db'):
        self.conn = sqlite3.connect(path); self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor(); self._migrate()
    def _migrate(self):
        self.c.executescript('''CREATE TABLE IF NOT EXISTS snippets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,lang TEXT,name TEXT,code TEXT,difficulty TEXT);
            CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,snippet_id INTEGER,lang TEXT,name TEXT,
            wpm REAL,accuracy REAL,xp INTEGER,elapsed REAL,ts TEXT,combo_max INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS achievements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,desc TEXT,icon TEXT,unlocked INTEGER DEFAULT 0,ts TEXT);
            CREATE TABLE IF NOT EXISTS activity(
            id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT UNIQUE,snippets INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,time_sec REAL DEFAULT 0);''')
        try: self.c.execute('SELECT combo_max FROM history LIMIT 0')
        except: self.c.execute('ALTER TABLE history ADD COLUMN combo_max INTEGER DEFAULT 0')
        self.conn.commit()
        for lang, name, code, diff in DEFAULT_SNIPPETS:
            self.c.execute('INSERT OR IGNORE INTO snippets(lang,name,code,difficulty) VALUES(?,?,?,?)', (lang, name, code, diff))
        for name, desc, icon in DEFAULT_ACHIEVEMENTS:
            self.c.execute('INSERT OR IGNORE INTO achievements(name,desc,icon) VALUES(?,?,?)', (name, desc, icon))
        self.conn.commit()
    def get_snippets(self, search=None):
        if search:
            self.c.execute('SELECT * FROM snippets WHERE lang LIKE ? OR name LIKE ? OR code LIKE ?',
                (f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            self.c.execute('SELECT * FROM snippets ORDER BY lang, name')
        return [dict(r) for r in self.c.fetchall()]
    def add_snippet(self, lang, name, code, diff='medium'):
        self.c.execute('INSERT INTO snippets(lang,name,code,difficulty) VALUES(?,?,?,?)', (lang, name, code, diff))
        self.conn.commit(); return self.c.lastrowid
    def update_snippet(self, sid, lang, name, code, diff):
        self.c.execute('UPDATE snippets SET lang=?,name=?,code=?,difficulty=? WHERE id=?', (lang, name, code, diff, sid))
        self.conn.commit()
    def delete_snippet(self, sid):
        self.c.execute('DELETE FROM snippets WHERE id=?', (sid,)); self.conn.commit()
    def get_history(self, limit=20):
        self.c.execute('SELECT * FROM history ORDER BY id DESC LIMIT ?', (limit,))
        return [dict(r) for r in self.c.fetchall()]
    def get_full_history(self):
        self.c.execute('SELECT * FROM history ORDER BY id DESC')
        return [dict(r) for r in self.c.fetchall()]
    def add_history(self, sid, lang, name, wpm, acc, xp, elapsed, combo=0):
        ts = datetime.now().isoformat()
        self.c.execute('INSERT INTO history(snippet_id,lang,name,wpm,accuracy,xp,elapsed,ts,combo_max) VALUES(?,?,?,?,?,?,?,?,?)',
            (sid, lang, name, wpm, acc, xp, elapsed, ts, combo)); self.conn.commit()
    def get_achievements(self):
        self.c.execute('SELECT * FROM achievements ORDER BY id'); return [dict(r) for r in self.c.fetchall()]
    def unlock_achievement(self, name):
        self.c.execute('UPDATE achievements SET unlocked=1,ts=? WHERE name=?', (datetime.now().isoformat(), name))
        self.conn.commit()
    def get_total_xp(self):
        r = self.c.execute('SELECT COALESCE(SUM(xp),0) as s FROM history').fetchone(); return r['s']
    def get_streak(self):
        days = set()
        for r in self.c.execute('SELECT DISTINCT date(ts) as d FROM history ORDER BY d DESC'):
            days.add(r['d'])
        if not days: return 0
        streak = 0; today = date.today()
        for i in range(365):
            d = (today - timedelta(days=i)).isoformat()
            if d in days: streak += 1
            elif i > 0: break
            else: pass
        return streak
    def get_lang_stats(self):
        self.c.execute('''SELECT lang, COUNT(*) as cnt, ROUND(AVG(wpm),1) as avg_wpm,
            ROUND(AVG(accuracy),1) as avg_acc, MAX(wpm) as best_wpm, SUM(xp) as total_xp
            FROM history GROUP BY lang ORDER BY cnt DESC''')
        return [dict(r) for r in self.c.fetchall()]
    def get_activity_days(self, n=28):
        result = {}
        today = date.today()
        for i in range(n):
            d = (today - timedelta(days=i)).isoformat()
            r = self.c.execute('SELECT snippets, xp FROM activity WHERE date=?', (d,)).fetchone()
            if r: result[d] = dict(r)
            else: result[d] = None
        return result
    def record_activity(self, d=None, snippets=1, xp=0, time_sec=0):
        if d is None: d = date.today().isoformat()
        self.c.execute('INSERT INTO activity(date,snippets,xp,time_sec) VALUES(?,?,?,?) ON CONFLICT(date) DO UPDATE SET snippets=snippets+?,xp=xp+?,time_sec=time_sec+?',
            (d, snippets, xp, time_sec, snippets, xp, time_sec)); self.conn.commit()
    def export_snippets(self):
        return json.dumps(self.get_snippets(), indent=2)
    def import_snippets_json(self, data):
        try:
            items = json.loads(data) if isinstance(data, str) else data
            count = 0
            for item in items:
                self.c.execute('INSERT OR IGNORE INTO snippets(lang,name,code,difficulty) VALUES(?,?,?,?)',
                    (item.get('lang',''), item.get('name',''), item.get('code',''), item.get('difficulty','medium')))
                count += self.c.rowcount
            self.conn.commit(); return count
        except: return 0
    def reset_progress(self):
        self.c.execute('DELETE FROM history'); self.c.execute('UPDATE achievements SET unlocked=0,ts=NULL')
        self.c.execute('DELETE FROM activity'); self.conn.commit()

db = Database()

# === GAME LOGIC ===
def xp_for_level(lvl): return int(50 * (lvl ** 1.5))
def calc_level(xp):
    lvl = 0; needed = 0
    while needed + xp_for_level(lvl + 1) <= xp:
        lvl += 1; needed += xp_for_level(lvl)
    return lvl
def xp_to_next(xp):
    lvl = calc_level(xp); used = sum(xp_for_level(i) for i in range(1, lvl + 1))
    return xp_for_level(lvl + 1) - (xp - used), xp_for_level(lvl + 1)
def calc_xp(wpm, acc, elapsed, diff_mult=1.0):
    base = int(wpm * (acc / 100) * (elapsed / 60) * 2)
    return max(5, int(base * diff_mult))

def check_achievements(stats):
    unlocked = set(r['name'] for r in db.get_achievements() if r['unlocked'])
    new = []
    def chk(name, cond):
        if name not in unlocked and cond: new.append(name)
    chk('First Steps', stats.get('total', 0) >= 1)
    chk('Speed Demon', stats.get('best_wpm', 0) >= 40)
    chk('Lightning Fingers', stats.get('best_wpm', 0) >= 80)
    chk('Perfectionist', stats.get('best_acc', 0) >= 100)
    chk('Streak Starter', stats.get('streak', 0) >= 3)
    chk('Week Warrior', stats.get('streak', 0) >= 7)
    chk('Dedicated', stats.get('streak', 0) >= 5)
    chk('Ten Down', stats.get('total', 0) >= 10)
    chk('Hard Mode', stats.get('hard_done', False))
    chk('Combo King', stats.get('max_combo', 0) >= 50)
    chk('Polyglot', stats.get('lang_count', 0) >= 3)
    chk('Marathon', stats.get('total', 0) >= 50)
    chk('Scholar', stats.get('lang_count', 0) >= 6)
    chk('Timed Ace', stats.get('timed_done', False))
    chk('Collector', stats.get('snippet_count', 0) >= 50)
    for n in new: db.unlock_achievement(n)
    return new

def daily_snippet():
    today = date.today().isoformat()
    seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
    all_snips = db.get_snippets()
    if not all_snips: return None
    return all_snips[seed % len(all_snips)]

def play_error_sound():
    if not settings['sound_enabled']: return
    try:
        sr = 22050; dur = 0.08; freq = 300
        n = int(sr * dur)
        buf = b''
        for i in range(n):
            t = i / sr; env = max(0, 1 - t / dur)
            val = int(env * 8000 * math.sin(2 * math.pi * freq * t))
            val = max(-32768, min(32767, val))
            buf += struct.pack('<h', val)
        fd, path = tempfile.mkstemp(suffix='.wav')
        with wave.open(path, 'w') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
            wf.writeframes(buf)
        import subprocess; subprocess.Popen(['aplay', '-q', path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        Clock.schedule_once(lambda dt: os.unlink(path), 2)
    except: pass

# === UI COMPONENTS ===
class IconBadge(BoxLayout):
    def __init__(self, icon, text='', color=ACCENT, size=24, **kw):
        super().__init__(**kw)
        self.size_hint = (None, None); self.size = (size, size)
        self.icon_w = VectorIcon(icon=icon, color=color, size=(size, size))
        self.add_widget(self.icon_w)
        if text:
            lbl = Label(text=text, font_size=9, color=TEXT_P,
                pos_hint={'center_x': .8, 'center_y': .8}, size_hint=(None, None), size=(16, 16))
            self.add_widget(lbl)

class AppCard(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', padding=PAD, spacing=8, **kw)
        self.size_hint = (1, None)
        with self.canvas.before:
            Color(*BG_CARD); self._bg = RoundedRectangle(radius=RAD, pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *a):
        self._bg.pos = self.pos; self._bg.size = self.size

class AppButton(Button):
    def __init__(self, text='', icon=None, color=ACCENT, bold=False, **kw):
        super().__init__(**kw)
        self.background_normal = ''; self.background_color = (0, 0, 0, 0)
        self.color = color if not bold else TEXT_P
        self.font_size = 13 if not bold else 14
        self.markup = True
        self._text = text; self._icon_name = icon; self._ic = color
        self._icon_w = None
        with self.canvas.before:
            Color(*BG_HOVER); self._bg = RoundedRectangle(radius=RAD_SM, pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd, state=self._on_state)
        self._build_label()
    def _build_label(self):
        if self._icon_w: self.remove_widget(self._icon_w)
        if self._icon_name:
            inner = BoxLayout(orientation='horizontal', spacing=6, size_hint_x=None, padding=(4, 0))
            inner.bind(minimum_width=inner.setter('width'))
            self._icon_w = VectorIcon(icon=self._icon_name, color=self._ic, size=(16, 16))
            inner.add_widget(self._icon_w)
            if self._text:
                lbl = Label(text=self._text, color=self.color, font_size=self.font_size, size_hint_x=None)
                lbl.bind(texture_size=lbl.setter('size'))
                inner.add_widget(lbl)
            self.clear_widgets()
            self.add_widget(inner)
        else:
            self.clear_widgets()
    def _upd(self, *a):
        self._bg.pos = self.pos; self._bg.size = self.size
    def _on_state(self, *a):
        if self.state == 'down': self._bg.rgba = ACCENT
        else: self._bg.rgba = BG_HOVER

class AppInput(TextInput):
    def __init__(self, hint='', multiline=False, **kw):
        super().__init__(**kw)
        self.multiline = multiline
        self.hint_text = hint
        self.background_color = BG_INPUT; self.foreground_color = TEXT_P
        self.border = [0, 0, 0, 0]; self.padding = [12, 10]
        self.font_size = 14; self.cursor_color = ACCENT
        self.selection_color = hex_to_rgba('#6c5ce7', 0.3)
        with self.canvas.before:
            Color(*BORDER); self._brd = Line(rounded_rectangle=(0, 0, 0, 0, 6), width=1)
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *a):
        self._brd.rounded_rectangle = (*self.pos, *self.size, 6)

class CodeInput(TextInput):
    def __init__(self, target='', on_complete=None, **kw):
        super().__init__(**kw)
        self.target = target; self._on_complete = on_complete
        self.multiline = True; self.readonly = False
        self.background_color = BG_INPUT; self.foreground_color = TEXT_P
        self.border = [0, 0, 0, 0]; self.padding = [12, 10]
        self.font_name = 'monospace'; self.font_size = settings['font_size']
        self.cursor_color = ACCENT; self.write_tab = False
        self._combo = 0; self._max_combo = 0; self._errors = 0; self._started = False; self._start_time = 0
        with self.canvas.before:
            Color(*BORDER); self._brd = Line(rounded_rectangle=(0, 0, 0, 0, 6), width=1)
        self.bind(pos=self._upd, size=self._upd, text=self._on_text)
    def _upd(self, *a):
        self._brd.rounded_rectangle = (*self.pos, *self.size, 6)
    def _on_text(self, inst, val):
        if not self.target: return
        typed = val; tl = len(typed)
        if tl > 0 and not self._started:
            self._started = True; self._start_time = time.time()
        if tl > 0 and tl <= len(self.target):
            if typed[-1] == self.target[tl - 1]:
                self._combo += 1; self._max_combo = max(self._max_combo, self._combo)
            else:
                self._errors += 1; self._combo = 0; play_error_sound()
        if tl >= len(self.target):
            if self._on_complete: self._on_complete()
    def keyboard_on_key_down(self, window, key, keycode, text, modifiers):
        if 'ctrl' in modifiers:
            if keycode == 114:
                self.reset(); return True
            if keycode == 110:
                app = App.get_running_app()
                if hasattr(app, 'practice_screen'): app.practice_screen.next_snippet()
                return True
        return super().keyboard_on_key_down(window, key, keycode, text, modifiers)
    def reset(self):
        self.text = ''; self._combo = 0; self._errors = 0
        self._started = False; self._start_time = 0
    def get_stats(self):
        elapsed = time.time() - self._start_time if self._started else 0
        chars = len(self.text)
        words = chars / 5 if elapsed > 0 else 0
        wpm = (words / (elapsed / 60)) if elapsed > 0 else 0
        acc = ((chars - self._errors) / chars * 100) if chars > 0 else 100
        return dict(wpm=round(wpm, 1), accuracy=round(min(acc, 100), 1),
                   elapsed=elapsed, combo=self._combo, max_combo=self._max_combo,
                   errors=self._errors, chars=chars, completed=chars >= len(self.target))

class AppSpinner(Spinner):
    def __init__(self, values=(), **kw):
        super().__init__(**kw)
        self.values = list(values); self.size_hint = (None, None); self.size = (140, 36)
        self.background_normal = ''; self.background_color = BG_INPUT
        self.color = TEXT_P; self.font_size = 13; self.border = [0, 0, 0, 0]
        self.option_cls = 'DropDown'
        with self.canvas.before:
            Color(*BORDER); self._brd = Line(rounded_rectangle=(0, 0, 0, 0, 6), width=1)
        self.bind(pos=self._upd, size=self._upd)
    def _upd(self, *a):
        self._brd.rounded_rectangle = (*self.pos, *self.size, 6)

class CodeDisplay(Label):
    def __init__(self, target='', typed='', **kw):
        super().__init__(**kw)
        self.target = target; self.typed = typed
        self.font_name = 'monospace'; self.font_size = settings['font_size']
        self.markup = True; self.halign = 'left'; self.valign = 'top'
        self.text_size = (None, None); self.size_hint = (1, None)
        self.size = (0, 200); self.padding = [12, 10]
        self.background_color = BG_INPUT
        with self.canvas.before:
            Color(*BG_INPUT); self._bg = RoundedRectangle(radius=RAD, pos=self.pos, size=self.size)
            Color(*BORDER); self._brd = Line(rounded_rectangle=(0, 0, 0, 0, 6), width=1)
        self.bind(pos=self._upd, size=self._upd)
        self._refresh()
    def _upd(self, *a):
        self._bg.pos = self.pos; self._bg.size = self.size
        self._brd.rounded_rectangle = (*self.pos, *self.size, 6)
    def update_typed(self, typed):
        self.typed = typed; self._refresh()
    def _refresh(self):
        t = self.target; tp = self.typed; parts = []
        for i, ch in enumerate(t):
            esc = escape_markup(ch)
            if i < len(tp):
                if ch == tp[i]:
                    parts.append('[color=#00e676]' + esc + '[/color]')
                else:
                    parts.append('[color=#ff5252]' + esc + '[/color]')
            else:
                parts.append('[color=#546e7a]' + esc + '[/color]')
        if len(tp) > len(t):
            extra = escape_markup(tp[len(t):])
            parts.append('[color=#ff5252]' + extra + '[/color]')
        self.text = ''.join(parts)
        self.texture_update()
        self.height = max(200, self.texture_size[1] + 20)
    def reset(self):
        self.typed = ''; self._refresh()

class XPBar(Widget):
    value = NumericProperty(0); max_val = NumericProperty(100)
    def __init__(self, **kw):
        super().__init__(**kw); self.size_hint = (1, None); self.height = 8
        with self.canvas.before:
            Color(*BG_INPUT); self._bg = RoundedRectangle(radius=[4], pos=self.pos, size=self.size)
        with self.canvas:
            Color(*ACCENT); self._fill = RoundedRectangle(radius=[4], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd, value=self._upd, max_val=self._upd)
    def _upd(self, *a):
        self._bg.pos = self.pos; self._bg.size = self.size
        ratio = min(self.value / max(self.max_val, 1), 1.0)
        fw = self.width * ratio
        self._fill.pos = self.pos; self._fill.size = (fw, self.height)

class ProgressBar(Widget):
    value = NumericProperty(0); max_val = NumericProperty(100)
    def __init__(self, **kw):
        super().__init__(**kw); self.size_hint = (1, None); self.height = 6
        with self.canvas.before:
            Color(*BG_INPUT); self._bg = RoundedRectangle(radius=[3], pos=self.pos, size=self.size)
        with self.canvas:
            Color(*SUCCESS); self._fill = RoundedRectangle(radius=[3], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd, value=self._upd, max_val=self._upd)
    def _upd(self, *a):
        self._bg.pos = self.pos; self._bg.size = self.size
        ratio = min(self.value / max(self.max_val, 1), 1.0)
        self._fill.pos = self.pos; self._fill.size = (self.width * ratio, self.height)

class NavButton(BoxLayout):
    def __init__(self, icon, label, screen_name, active=False, **kw):
        super().__init__(orientation='vertical', padding=(5, 8), spacing=3, **kw)
        self.size_hint = (1, None); self.height = 58; self.screen_name = screen_name
        self._active = False
        self._icon_w = VectorIcon(icon=icon, color=TEXT_S, size=(22, 22))
        self._lbl = Label(text=label, font_size=9, color=TEXT_S, halign='center')
        self._lbl.bind(texture_size=self._lbl.setter('size'))
        self.add_widget(self._icon_w); self.add_widget(self._lbl)
        with self.canvas.before:
            Color(0, 0, 0, 0); self._bg = RoundedRectangle(radius=[6], pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)
        if active: self.set_active(True)
    def _upd(self, *a):
        self._bg.pos = self.pos; self._bg.size = self.size
    def set_active(self, val):
        self._active = val
        if val:
            self._bg.rgba = hex_to_rgba('#6c5ce7', 0.2)
            self._icon_w.icolor = list(ACCENT_L); self._lbl.color = TEXT_P
        else:
            self._bg.rgba = (0, 0, 0, 0)
            self._icon_w.icolor = list(TEXT_S); self._lbl.color = TEXT_S
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            if hasattr(app, 'switch_screen'):
                app.switch_screen(self.screen_name)
            return True
        return False

class AchievementPopup(ModalView):
    def __init__(self, name, desc, icon, **kw):
        super().__init__(size_hint=(0.7, 0.35), auto_dismiss=True, **kw)
        self.background_color = (0, 0, 0, 0)
        box = BoxLayout(orientation='vertical', padding=PAD_LG, spacing=12, size_hint=(0.8, 0.8),
                        pos_hint={'center_x': .5, 'center_y': .5})
        with box.canvas.before:
            Color(*BG_CARD); self._card = RoundedRectangle(radius=RAD_LG, pos=box.pos, size=box.size)
        box.bind(pos=lambda *a: setattr(self._card, 'pos', box.pos),
                 size=lambda *a: setattr(self._card, 'size', box.size))
        title = Label(text='[color=#ffab40]Achievement Unlocked![/color]', markup=True, font_size=18,
                      size_hint_y=None, halign='center')
        title.bind(texture_size=title.setter('size'))
        row = BoxLayout(size_hint_y=None, spacing=12, padding=(0, 8))
        row.bind(minimum_height=row.setter('height'))
        ic = VectorIcon(icon=icon, color=WARNING, size=(36, 36))
        row.add_widget(ic)
        info = BoxLayout(orientation='vertical', spacing=4)
        n_lbl = Label(text=name, font_size=16, color=TEXT_P, bold=True, size_hint_y=None)
        n_lbl.bind(texture_size=n_lbl.setter('size'))
        d_lbl = Label(text=desc, font_size=12, color=TEXT_S, size_hint_y=None)
        d_lbl.bind(texture_size=d_lbl.setter('size'))
        info.add_widget(n_lbl); info.add_widget(d_lbl)
        row.add_widget(info)
        box.add_widget(title); box.add_widget(row)
        btn = AppButton(text='Awesome!', bold=True, size_hint=(None, None), size=(120, 36),
                        pos_hint={'center_x': .5})
        btn.bind(on_release=self.dismiss)
        box.add_widget(btn)
        self.add_widget(box)

# === SCREENS ===
class AchievementsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical', padding=PAD, spacing=12)
        header = BoxLayout(size_hint_y=None, height=36)
        header.add_widget(VectorIcon(icon='trophy', color=WARNING, size=(24, 24)))
        lbl = Label(text='Achievements', font_size=20, color=TEXT_P, bold=True)
        header.add_widget(lbl)
        header.add_widget(Widget())
        self._count_lbl = Label(text='', font_size=12, color=TEXT_S, size_hint=(None, None))
        header.add_widget(self._count_lbl)
        root.add_widget(header)
        scroll = ScrollView(size_hint=(1, 1)); scroll.bar_width = 4; scroll.scroll_type = ['bars', 'content']
        self._grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=(0, 0, 0, 10))
        self._grid.bind(minimum_height=self._grid.setter('height'))
        scroll.add_widget(self._grid)
        root.add_widget(scroll)
        self.add_widget(root)
    def on_enter(self):
        self._grid.clear_widgets()
        achs = db.get_achievements()
        unlocked = sum(1 for a in achs if a['unlocked'])
        self._count_lbl.text = str(unlocked) + '/' + str(len(achs))
        for a in achs:
            card = BoxLayout(orientation='vertical', padding=12, spacing=6, size_hint=(1, None))
            with card.canvas.before:
                Color(*BG_CARD); bg = RoundedRectangle(radius=RAD, pos=card.pos, size=card.size)
            card.bind(pos=lambda *a, b=bg, c=card: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)),
                     size=lambda *a, b=bg, c=card: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)))
            row = BoxLayout(size_hint_y=None, spacing=8)
            ic_color = ACCENT_L if a['unlocked'] else TEXT_M
            row.add_widget(VectorIcon(icon=a['icon'], color=ic_color, size=(24, 24)))
            name_lbl = Label(text=a['name'], font_size=13, color=TEXT_P if a['unlocked'] else TEXT_M, bold=True)
            name_lbl.bind(texture_size=name_lbl.setter('size')); name_lbl.size_hint_x = None
            row.add_widget(name_lbl)
            if a['unlocked']:
                row.add_widget(VectorIcon(icon='check', color=SUCCESS, size=(18, 18)))
            card.add_widget(row)
            desc_lbl = Label(text=a['desc'], font_size=11, color=TEXT_S, size_hint_y=None)
            desc_lbl.bind(texture_size=desc_lbl.setter('size'))
            card.add_widget(desc_lbl)
            if a['unlocked'] and a['ts']:
                dt = Label(text=a['ts'][:10], font_size=10, color=TEXT_M, size_hint_y=None)
                dt.bind(texture_size=dt.setter('size')); card.add_widget(dt)
            self._grid.add_widget(card)

class DashboardScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._timer_ev = None
        root = BoxLayout(orientation='vertical', padding=PAD, spacing=14)
        hdr = BoxLayout(size_hint_y=None, height=36)
        hdr.add_widget(VectorIcon(icon='home', color=ACCENT_L, size=(24, 24)))
        hdr.add_widget(Label(text='Dashboard', font_size=20, color=TEXT_P, bold=True))
        hdr.add_widget(Widget())
        root.add_widget(hdr)
        self._streak_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=6, padding=PAD)
        with self._streak_box.canvas.before:
            Color(*BG_CARD); self._sb_bg = RoundedRectangle(radius=RAD_LG, pos=self._streak_box.pos, size=self._streak_box.size)
        self._streak_box.bind(pos=self._sb_upd, size=self._sb_upd)
        root.add_widget(self._streak_box)
        self._cal_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=PAD)
        with self._cal_box.canvas.before:
            Color(*BG_CARD); self._cal_bg = RoundedRectangle(radius=RAD_LG, pos=self._cal_box.pos, size=self._cal_box.size)
        self._cal_box.bind(pos=self._cal_upd, size=self._cal_upd)
        root.add_widget(self._cal_box)
        self._daily_btn = AppButton(text='Daily Challenge', icon='target', color=WARNING,
            size_hint=(1, None), size=(0, 44))
        self._daily_btn.bind(on_release=self._start_daily)
        root.add_widget(self._daily_btn)
        self._recent_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=6, padding=PAD)
        with self._recent_box.canvas.before:
            Color(*BG_CARD); self._rb_bg = RoundedRectangle(radius=RAD_LG, pos=self._recent_box.pos, size=self._recent_box.size)
        self._recent_box.bind(pos=self._rb_upd, size=self._rb_upd)
        root.add_widget(self._recent_box)
        scroll = ScrollView(size_hint=(1, 1)); scroll.bar_width = 4
        self._scroll_inner = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self._scroll_inner.bind(minimum_height=self._scroll_inner.setter('height'))
        scroll.add_widget(self._scroll_inner)
        self._scroll_inner.add_widget(self._streak_box)
        self._scroll_inner.add_widget(self._cal_box)
        self._scroll_inner.add_widget(self._daily_btn)
        self._scroll_inner.add_widget(self._recent_box)
        root.clear_widgets()
        root.add_widget(hdr)
        root.add_widget(scroll)
        self.add_widget(root)
    def _sb_upd(self, *a):
        self._sb_bg.pos = self._streak_box.pos; self._sb_bg.size = self._streak_box.size
    def _cal_upd(self, *a):
        self._cal_bg.pos = self._cal_box.pos; self._cal_bg.size = self._cal_box.size
    def _rb_upd(self, *a):
        self._rb_bg.pos = self._recent_box.pos; self._rb_bg.size = self._recent_box.size
    def _start_daily(self, *a):
        app = App.get_running_app()
        if hasattr(app, 'switch_screen'): app.switch_screen('practice')
        if hasattr(app, 'practice_screen'):
            ps = app.practice_screen
            snip = daily_snippet()
            if snip: ps.load_snippet(snip)
    def on_enter(self):
        self._streak_box.clear_widgets(); self._cal_box.clear_widgets(); self._recent_box.clear_widgets()
        streak = db.get_streak(); total_xp = db.get_total_xp(); lvl = calc_level(total_xp)
        rem, need = xp_to_next(total_xp)
        sh = BoxLayout(size_hint_y=None, height=24, spacing=8)
        sh.add_widget(VectorIcon(icon='flame', color=WARNING, size=(20, 20)))
        sh.add_widget(Label(text=str(streak) + ' day streak', font_size=14, color=TEXT_P, bold=True))
        sh.add_widget(Widget())
        self._streak_box.add_widget(sh)
        lv_row = BoxLayout(size_hint_y=None, spacing=8)
        lv_row.add_widget(Label(text='Level ' + str(lvl), font_size=13, color=ACCENT_L, bold=True))
        lv_row.add_widget(Label(text=str(total_xp) + ' XP', font_size=12, color=TEXT_S))
        lv_row.add_widget(Widget())
        self._streak_box.add_widget(lv_row)
        self._streak_box.add_widget(XPBar(value=need - rem, max_val=need))
        self._streak_box.height = 100
        cl = Label(text='Last 28 Days', font_size=12, color=TEXT_P, bold=True, size_hint_y=None, height=20)
        self._cal_box.add_widget(cl)
        cal_grid = GridLayout(cols=7, spacing=3, size_hint_y=None)
        cal_grid.bind(minimum_height=cal_grid.setter('height'))
        days_data = db.get_activity_days(28)
        day_keys = list(days_data.keys())
        for i in range(28):
            d = day_keys[i]
            box = BoxLayout(size_hint=(1, None), height=22)
            with box.canvas.before:
                if days_data[d]:
                    intensity = min(days_data[d].get('snippets', 0) / 5.0, 1.0)
                    c = hex_to_rgba('#6c5ce7', 0.2 + intensity * 0.8)
                else:
                    c = BG_INPUT
                Color(*c); bg = RoundedRectangle(radius=[3], pos=box.pos, size=box.size)
            box.bind(pos=lambda *a, b=bg, c2=box: (setattr(b, 'pos', c2.pos), setattr(b, 'size', c2.size)),
                     size=lambda *a, b=bg, c2=box: (setattr(b, 'pos', c2.pos), setattr(b, 'size', c2.size)))
            cal_grid.add_widget(box)
        self._cal_box.add_widget(cal_grid)
        self._cal_box.height = cal_grid.minimum_height + 30
        rl = Label(text='Recent Sessions', font_size=12, color=TEXT_P, bold=True, size_hint_y=None, height=20)
        self._recent_box.add_widget(rl)
        hist = db.get_history(5)
        if not hist:
            self._recent_box.add_widget(Label(text='No sessions yet. Start practicing!', font_size=12, color=TEXT_S))
        for h in hist:
            row = BoxLayout(size_hint_y=None, height=28, spacing=8)
            row.add_widget(Label(text=h['name'] or '?', font_size=12, color=TEXT_P, size_hint_x=2))
            row.add_widget(Label(text=str(round(h['wpm'])) + ' wpm', font_size=11, color=SUCCESS, size_hint_x=1))
            row.add_widget(Label(text=str(round(h['accuracy'])) + '%', font_size=11, color=TEXT_S, size_hint_x=1))
            self._recent_box.add_widget(row)
        self._recent_box.height = 50 + len(hist) * 28

class PracticeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._timer_ev = None; self._time_left = 0; self._snippet = None; self._is_timed = False
        root = BoxLayout(orientation='vertical', padding=PAD, spacing=10)
        self._hdr = BoxLayout(size_hint_y=None, height=36, spacing=8)
        self._hdr.add_widget(VectorIcon(icon='keyboard', color=ACCENT_L, size=(24, 24)))
        self._hdr.add_widget(Label(text='Practice', font_size=20, color=TEXT_P, bold=True))
        self._hdr.add_widget(Widget())
        self._lang_lbl = Label(text='', font_size=13, color=ACCENT_L, bold=True)
        self._hdr.add_widget(self._lang_lbl)
        root.add_widget(self._hdr)
        info = BoxLayout(size_hint_y=None, height=26, spacing=12)
        self._diff_lbl = Label(text='', font_size=11, color=TEXT_S)
        self._wpm_lbl = Label(text='0 WPM', font_size=13, color=SUCCESS, bold=True)
        self._acc_lbl = Label(text='100%', font_size=13, color=ACCENT_L, bold=True)
        self._timer_lbl = Label(text='', font_size=13, color=WARNING, bold=True)
        self._combo_lbl = Label(text='', font_size=12, color=C_INFO)
        for w in [self._diff_lbl, self._wpm_lbl, self._acc_lbl, self._timer_lbl, self._combo_lbl]:
            info.add_widget(w)
        root.add_widget(info)
        self._progress = ProgressBar(value=0, max_val=100)
        root.add_widget(self._progress)
        scroll = ScrollView(size_hint=(1, 1)); scroll.bar_width = 4
        self._code_inner = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self._code_inner.bind(minimum_height=self._code_inner.setter('height'))
        self._display = CodeDisplay(target='', typed='')
        self._display.bind(height=lambda *a: setattr(self._code_inner, 'height', self._display.height + 8))
        self._code_inner.add_widget(self._display)
        self._input = CodeInput(target='', on_complete=self._on_complete)
        self._input.bind(text=self._on_typed, height=lambda *a: setattr(self._code_inner,
            'height', self._display.height + self._input.height + 16))
        self._code_inner.add_widget(self._input)
        scroll.add_widget(self._code_inner)
        root.add_widget(scroll)
        self._result_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8, padding=PAD, height=0)
        with self._result_box.canvas.before:
            Color(*BG_CARD); self._res_bg = RoundedRectangle(radius=RAD, pos=self._result_box.pos, size=self._result_box.size)
        self._result_box.bind(pos=lambda *a: (setattr(self._res_bg, 'pos', self._result_box.pos),
            setattr(self._res_bg, 'size', self._result_box.size)),
            size=lambda *a: (setattr(self._res_bg, 'pos', self._result_box.pos),
            setattr(self._res_bg, 'size', self._result_box.size)))
        root.add_widget(self._result_box)
        ctrl = BoxLayout(size_hint_y=None, height=44, spacing=8)
        self._lang_sp = AppSpinner(values=['All'] + sorted(set(s['lang'] for s in db.get_snippets())))
        self._lang_sp.text = 'All'
        self._lang_sp.bind(text=self._on_lang_change)
        ctrl.add_widget(self._lang_sp)
        self._diff_sp = AppSpinner(values=['All', 'easy', 'medium', 'hard'])
        self._diff_sp.text = 'All'
        self._diff_sp.bind(text=self._on_filter)
        ctrl.add_widget(self._diff_sp)
        self._timer_sp = AppSpinner(values=['Off', '30s', '60s', '120s'])
        self._timer_sp.text = settings['timer_mode']
        ctrl.add_widget(self._timer_sp)
        reset_btn = AppButton(text='Reset', icon='refresh', size_hint=(None, None), size=(80, 36))
        reset_btn.bind(on_release=self._reset)
        ctrl.add_widget(reset_btn)
        next_btn = AppButton(text='Next', icon='arrow_right', size_hint=(None, None), size=(80, 36))
        next_btn.bind(on_release=lambda *a: self.next_snippet())
        ctrl.add_widget(next_btn)
        copy_btn = AppButton(text='Copy', icon='copy', size_hint=(None, None), size=(70, 36))
        copy_btn.bind(on_release=self._copy_code)
        ctrl.add_widget(copy_btn)
        root.add_widget(ctrl)
        self.add_widget(root)
        self._on_lang_change(None, 'All')
    def _copy_code(self, *a):
        if self._snippet: Clipboard.copy(self._snippet['code'])
    def _on_typed(self, inst, val):
        self._display.update_typed(val)
        total = len(self._input.target)
        if total > 0:
            self._progress.value = (len(val) / total) * 100
        if self._input._started:
            elapsed = time.time() - self._input._start_time
            chars = len(val); words = chars / 5
            wpm = (words / (elapsed / 60)) if elapsed > 0 else 0
            acc = ((chars - self._input._errors) / chars * 100) if chars > 0 else 100
            self._wpm_lbl.text = str(round(wpm)) + ' WPM'
            self._acc_lbl.text = str(round(min(acc, 100))) + '%'
        combo = self._input._combo
        if combo >= 5:
            self._combo_lbl.text = str(combo) + 'x combo'
        else:
            self._combo_lbl.text = ''
    def _on_complete(self):
        self._cancel_timer()
        stats = self._input.get_stats()
        self._finish_session(stats, fully_completed=True)
    def _on_timer_expire(self, dt):
        self._time_left = 0; self._timer_lbl.text = '0s'
        stats = self._input.get_stats()
        self._finish_session(stats, fully_completed=False)
    def _finish_session(self, stats, fully_completed):
        self._input.readonly = True
        self._result_box.clear_widgets(); self._result_box.height = 160
        if not fully_completed:
            res_title = Label(text='[color=#ffab40]Time Up![/color]', markup=True, font_size=16,
                bold=True, size_hint_y=None, halign='center')
        else:
            res_title = Label(text='[color=#00e676]Complete![/color]', markup=True, font_size=16,
                bold=True, size_hint_y=None, halign='center')
        res_title.bind(texture_size=res_title.setter('size'))
        self._result_box.add_widget(res_title)
        wpm = stats['wpm']; acc = stats['accuracy']; elapsed = stats['elapsed']
        self._wpm_lbl.text = str(wpm) + ' WPM'
        self._acc_lbl.text = str(acc) + '%'
        detail = Label(text='WPM: ' + str(wpm) + '  |  Accuracy: ' + str(acc) + '%  |  Time: ' + str(round(elapsed, 1)) + 's  |  Combo: ' + str(stats['max_combo']),
            font_size=12, color=TEXT_S, size_hint_y=None)
        detail.bind(texture_size=detail.setter('size'))
        self._result_box.add_widget(detail)
        if self._snippet:
            diff = self._snippet.get('difficulty', 'medium')
            mult = {'easy': 0.8, 'medium': 1.0, 'hard': 1.5}.get(diff, 1.0)
        else:
            mult = 1.0
        if not fully_completed: mult *= 0.5
        xp = calc_xp(wpm, acc, elapsed, mult)
        xp_lbl = Label(text='[color=#a29bfe]+' + str(xp) + ' XP[/color]', markup=True, font_size=14,
            bold=True, size_hint_y=None)
        xp_lbl.bind(texture_size=xp_lbl.setter('size'))
        self._result_box.add_widget(xp_lbl)
        if self._snippet:
            db.add_history(self._snippet['id'], self._snippet['lang'], self._snippet['name'],
                wpm, acc, xp, elapsed, stats['max_combo'])
            db.record_activity(snippets=1, xp=xp, time_sec=elapsed)
            ach_stats = dict(total=len(db.get_full_history()), best_wpm=wpm, best_acc=acc,
                streak=db.get_streak(), max_combo=stats['max_combo'], hard_done=False,
                lang_count=len(set(r['lang'] for r in db.get_full_history())),
                timed_done=self._is_timed, snippet_count=len(db.get_snippets()))
            if diff == 'hard' and fully_completed: ach_stats['hard_done'] = True
            new_achs = check_achievements(ach_stats)
            for an in new_achs:
                a_info = [a for a in db.get_achievements() if a['name'] == an]
                if a_info:
                    ai = a_info[0]
                    pop = AchievementPopup(ai['name'], ai['desc'], ai['icon'])
                    pop.open()
        try_again = AppButton(text='Try Again', icon='refresh', size_hint=(None, None), size=(110, 36))
        try_again.bind(on_release=self._reset)
        nxt = AppButton(text='Next', icon='arrow_right', size_hint=(None, None), size=(90, 36))
        nxt.bind(on_release=lambda *a: self.next_snippet())
        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=8, padding=(0, 4))
        btn_row.add_widget(Widget()); btn_row.add_widget(try_again); btn_row.add_widget(nxt)
        btn_row.add_widget(Widget())
        self._result_box.add_widget(btn_row)
    def _reset(self, *a):
        self._cancel_timer()
        self._input.readonly = False; self._input.reset(); self._display.reset()
        self._result_box.clear_widgets(); self._result_box.height = 0
        self._wpm_lbl.text = '0 WPM'; self._acc_lbl.text = '100%'
        self._timer_lbl.text = ''; self._combo_lbl.text = ''
        self._progress.value = 0
        if self._is_timed: self._start_timer()
    def _start_timer(self):
        self._cancel_timer()
        txt = self._timer_sp.text
        if txt == 'Off':
            self._is_timed = False; self._timer_lbl.text = ''; return
        self._is_timed = True
        secs = int(txt.replace('s', ''))
        self._time_left = secs
        self._timer_lbl.text = str(secs) + 's'
        self._timer_ev = Clock.schedule_interval(self._tick_timer, 1)
    def _tick_timer(self, dt):
        self._time_left -= 1
        if self._time_left <= 0:
            self._cancel_timer(); self._on_timer_expire(None)
        else:
            self._timer_lbl.text = str(self._time_left) + 's'
    def _cancel_timer(self):
        if self._timer_ev:
            self._timer_ev.cancel(); self._timer_ev = None
    def load_snippet(self, snip):
        self._cancel_timer(); self._snippet = snip
        self._display.target = snip['code']; self._display.reset()
        self._input.target = snip['code']; self._input.readonly = False; self._input.reset()
        self._lang_lbl.text = snip['lang']
        self._diff_lbl.text = snip.get('difficulty', '')
        self._result_box.clear_widgets(); self._result_box.height = 0
        self._wpm_lbl.text = '0 WPM'; self._acc_lbl.text = '100%'
        self._combo_lbl.text = ''; self._progress.value = 0
        self._input.font_size = settings['font_size']
        self._display.font_size = settings['font_size']
        self._start_timer()
    def next_snippet(self, *a):
        self._cancel_timer()
        lang = self._lang_sp.text; diff = self._diff_sp.text
        snips = db.get_snippets()
        if lang != 'All': snips = [s for s in snips if s['lang'] == lang]
        if diff != 'All': snips = [s for s in snips if s['difficulty'] == diff]
        if snips:
            snip = random.choice(snips); self.load_snippet(snip)
    def _on_lang_change(self, *a):
        self.next_snippet()
    def _on_filter(self, *a):
        self.next_snippet()

class SnippetsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._editing_id = None
        root = BoxLayout(orientation='vertical', padding=PAD, spacing=10)
        hdr = BoxLayout(size_hint_y=None, height=36, spacing=8)
        hdr.add_widget(VectorIcon(icon='code', color=ACCENT_L, size=(24, 24)))
        hdr.add_widget(Label(text='Snippets', font_size=20, color=TEXT_P, bold=True))
        hdr.add_widget(Widget())
        root.add_widget(hdr)
        search_row = BoxLayout(size_hint_y=None, height=36, spacing=8)
        self._search = AppInput(hint='Search snippets...')
        self._search.size_hint_x = 3
        self._search.bind(text=self._on_search)
        search_row.add_widget(self._search)
        add_btn = AppButton(text='Add', icon='plus', size_hint=(None, None), size=(70, 36))
        add_btn.bind(on_release=self._add_snippet)
        search_row.add_widget(add_btn)
        imp_btn = AppButton(text='Import', icon='upload', size_hint=(None, None), size=(80, 36))
        imp_btn.bind(on_release=self._import)
        search_row.add_widget(imp_btn)
        exp_btn = AppButton(text='Export', icon='download', size_hint=(None, None), size=(80, 36))
        exp_btn.bind(on_release=self._export)
        search_row.add_widget(exp_btn)
        root.add_widget(search_row)
        scroll = ScrollView(size_hint=(1, 1)); scroll.bar_width = 4
        self._list = BoxLayout(orientation='vertical', spacing=6, size_hint_y=None, padding=(0, 0, 0, 10))
        self._list.bind(minimum_height=self._list.setter('height'))
        scroll.add_widget(self._list)
        root.add_widget(scroll)
        self.add_widget(root)
    def on_enter(self):
        self._refresh()
    def _on_search(self, *a):
        self._refresh(self._search.text)
    def _refresh(self, search=None):
        self._list.clear_widgets()
        snips = db.get_snippets(search=search)
        for s in snips:
            row = BoxLayout(size_hint_y=None, height=60, spacing=8, padding=(8, 4))
            with row.canvas.before:
                Color(*BG_CARD); bg = RoundedRectangle(radius=RAD_SM, pos=row.pos, size=row.size)
            row.bind(pos=lambda *a, b=bg, c=row: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)),
                     size=lambda *a, b=bg, c=row: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)))
            info = BoxLayout(orientation='vertical', spacing=2, size_hint_x=3)
            n_lbl = Label(text=s['name'], font_size=13, color=TEXT_P, bold=True, size_hint_y=None)
            n_lbl.bind(texture_size=n_lbl.setter('size'))
            info.add_widget(n_lbl)
            m_lbl = Label(text=s['lang'] + '  |  ' + s.get('difficulty', ''), font_size=11, color=TEXT_S, size_hint_y=None)
            m_lbl.bind(texture_size=m_lbl.setter('size'))
            info.add_widget(m_lbl)
            row.add_widget(info)
            edit_btn = AppButton(icon='edit', size_hint=(None, None), size=(36, 36))
            edit_btn.bind(on_release=lambda *a, sid=s['id']: self._edit_snippet(sid))
            row.add_widget(edit_btn)
            del_btn = AppButton(icon='trash', size_hint=(None, None), size=(36, 36))
            del_btn.bind(on_release=lambda *a, sid=s['id']: self._del_snippet(sid))
            row.add_widget(del_btn)
            self._list.add_widget(row)
    def _add_snippet(self, *a):
        self._open_editor(None)
    def _edit_snippet(self, sid):
        self._open_editor(sid)
    def _del_snippet(self, sid):
        db.delete_snippet(sid); self._refresh(self._search.text)
    def _open_editor(self, sid):
        snip = None
        if sid:
            snips = db.get_snippets()
            snip = [s for s in snips if s['id'] == sid]
            snip = snip[0] if snip else None
        popup = ModalView(size_hint=(0.85, 0.75), background_color=(0, 0, 0, 0))
        box = BoxLayout(orientation='vertical', padding=PAD_LG, spacing=10, size_hint=(0.95, 0.95),
                        pos_hint={'center_x': .5, 'center_y': .5})
        with box.canvas.before:
            Color(*BG_CARD); bg = RoundedRectangle(radius=RAD_LG, pos=box.pos, size=box.size)
        box.bind(pos=lambda *a: (setattr(bg, 'pos', box.pos), setattr(bg, 'size', box.size)),
                 size=lambda *a: (setattr(bg, 'pos', box.pos), setattr(bg, 'size', box.size)))
        title = Label(text='Edit Snippet' if snip else 'Add Snippet', font_size=16, color=TEXT_P,
            bold=True, size_hint_y=None)
        title.bind(texture_size=title.setter('size'))
        box.add_widget(title)
        lang_inp = AppInput(hint='Language')
        lang_inp.text = snip['lang'] if snip else 'Python'
        box.add_widget(lang_inp)
        name_inp = AppInput(hint='Name')
        name_inp.text = snip['name'] if snip else ''
        box.add_widget(name_inp)
        code_inp = AppInput(hint='Code...', multiline=True)
        code_inp.text = snip['code'] if snip else ''
        code_inp.size_hint_y = 3
        box.add_widget(code_inp)
        diff_sp = AppSpinner(values=['easy', 'medium', 'hard'])
        diff_sp.text = snip.get('difficulty', 'medium') if snip else 'medium'
        box.add_widget(diff_sp)
        def save(*a):
            if lang_inp.text and name_inp.text and code_inp.text:
                if sid: db.update_snippet(sid, lang_inp.text, name_inp.text, code_inp.text, diff_sp.text)
                else: db.add_snippet(lang_inp.text, name_inp.text, code_inp.text, diff_sp.text)
                popup.dismiss(); self._refresh(self._search.text)
        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=8)
        save_btn = AppButton(text='Save', bold=True, size_hint=(None, None), size=(100, 36))
        save_btn.bind(on_release=save)
        cancel_btn = AppButton(text='Cancel', size_hint=(None, None), size=(100, 36))
        cancel_btn.bind(on_release=popup.dismiss)
        btn_row.add_widget(Widget()); btn_row.add_widget(save_btn); btn_row.add_widget(cancel_btn)
        btn_row.add_widget(Widget())
        box.add_widget(btn_row)
        popup.add_widget(box); popup.open()
    def _export(self, *a):
        data = db.export_snippets()
        Clipboard.copy(data)
    def _import(self, *a):
        popup = ModalView(size_hint=(0.8, 0.5), background_color=(0, 0, 0, 0))
        box = BoxLayout(orientation='vertical', padding=PAD_LG, spacing=10, size_hint=(0.9, 0.9),
                        pos_hint={'center_x': .5, 'center_y': .5})
        with box.canvas.before:
            Color(*BG_CARD); bg = RoundedRectangle(radius=RAD_LG, pos=box.pos, size=box.size)
        box.bind(pos=lambda *a: (setattr(bg, 'pos', box.pos), setattr(bg, 'size', box.size)),
                 size=lambda *a: (setattr(bg, 'pos', box.pos), setattr(bg, 'size', box.size)))
        box.add_widget(Label(text='Paste JSON below:', font_size=13, color=TEXT_P))
        ti = AppInput(hint='Paste JSON here...', multiline=True); ti.size_hint_y = 3
        box.add_widget(ti)
        def do_import(*a2):
            count = db.import_snippets_json(ti.text)
            popup.dismiss(); self._refresh(self._search.text)
        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=8)
        imp_b = AppButton(text='Import', bold=True, size_hint=(None, None), size=(100, 36))
        imp_b.bind(on_release=do_import)
        can_b = AppButton(text='Cancel', size_hint=(None, None), size=(100, 36))
        can_b.bind(on_release=popup.dismiss)
        btn_row.add_widget(Widget()); btn_row.add_widget(imp_b); btn_row.add_widget(can_b)
        btn_row.add_widget(Widget())
        box.add_widget(btn_row)
        popup.add_widget(box); popup.open()

class StatsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical', padding=PAD, spacing=10)
        hdr = BoxLayout(size_hint_y=None, height=36, spacing=8)
        hdr.add_widget(VectorIcon(icon='chart', color=ACCENT_L, size=(24, 24)))
        hdr.add_widget(Label(text='Statistics', font_size=20, color=TEXT_P, bold=True))
        hdr.add_widget(Widget())
        root.add_widget(hdr)
        scroll = ScrollView(size_hint=(1, 1)); scroll.bar_width = 4
        self._inner = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=(0, 0, 0, 20))
        self._inner.bind(minimum_height=self._inner.setter('height'))
        scroll.add_widget(self._inner)
        root.add_widget(scroll)
        self.add_widget(root)
    def on_enter(self):
        self._inner.clear_widgets()
        history = db.get_full_history()
        lang_stats = db.get_lang_stats()
        if not history:
            self._inner.add_widget(Label(text='No practice data yet.', font_size=14, color=TEXT_S))
            return
        overall_wpm = sum(h['wpm'] for h in history) / len(history)
        overall_acc = sum(h['accuracy'] for h in history) / len(history)
        best_wpm = max(h['wpm'] for h in history)
        total_time = sum(h['elapsed'] for h in history)
        total_xp = sum(h['xp'] for h in history)
        bests_card = self._make_card()
        bests_card.add_widget(self._section_title('Personal Bests'))
        for label, val in [('Best WPM', str(round(best_wpm))), ('Avg WPM', str(round(overall_wpm, 1))),
            ('Avg Accuracy', str(round(overall_acc, 1)) + '%'),
            ('Total Sessions', str(len(history))),
            ('Total Time', str(round(total_time / 60, 1)) + ' min'),
            ('Total XP', str(total_xp))]:
            row = BoxLayout(size_hint_y=None, height=24, spacing=8)
            row.add_widget(Label(text=label, font_size=12, color=TEXT_S, size_hint_x=3))
            row.add_widget(Label(text=val, font_size=12, color=TEXT_P, bold=True, halign='right', size_hint_x=2))
            bests_card.add_widget(row)
        bests_card.height = 30 + 6 * 24
        self._inner.add_widget(bests_card)
        if lang_stats:
            lang_card = self._make_card()
            lang_card.add_widget(self._section_title('Language Breakdown'))
            header = BoxLayout(size_hint_y=None, height=22, spacing=4)
            for t, w in [('Lang', 2), ('Count', 1), ('Avg WPM', 1), ('Avg Acc', 1), ('Best', 1), ('XP', 1)]:
                lbl = Label(text=t, font_size=10, color=TEXT_M, size_hint_x=w, bold=True)
                header.add_widget(lbl)
            lang_card.add_widget(header)
            for ls in lang_stats:
                row = BoxLayout(size_hint_y=None, height=22, spacing=4)
                for t, w in [(ls['lang'], 2), (str(ls['cnt']), 1),
                    (str(ls['avg_wpm']), 1), (str(ls['avg_acc']) + '%', 1),
                    (str(round(ls['best_wpm'])), 1), (str(ls['total_xp']), 1)]:
                    lbl = Label(text=t, font_size=11, color=TEXT_P, size_hint_x=w)
                    row.add_widget(lbl)
                lang_card.add_widget(row)
            lang_card.height = 30 + (len(lang_stats) + 1) * 22
            self._inner.add_widget(lang_card)
        chart_card = self._make_card()
        chart_card.add_widget(self._section_title('Recent WPM (last 10)'))
        recent = history[:10]
        chart = Widget(size_hint=(1, None), height=120)
        with chart.canvas:
            Color(*BG_INPUT); bg = RoundedRectangle(radius=RAD_SM, pos=chart.pos, size=chart.size)
        chart.bind(pos=lambda *a: self._draw_bars(chart, recent),
                   size=lambda *a: self._draw_bars(chart, recent))
        chart_card.add_widget(chart)
        chart_card.height = 50 + 120
        self._inner.add_widget(chart_card)
    def _make_card(self):
        card = BoxLayout(orientation='vertical', padding=PAD, spacing=4, size_hint=(1, None))
        with card.canvas.before:
            Color(*BG_CARD); bg = RoundedRectangle(radius=RAD, pos=card.pos, size=card.size)
        card.bind(pos=lambda *a, b=bg, c=card: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)),
                 size=lambda *a, b=bg, c=card: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)))
        return card
    def _section_title(self, text):
        lbl = Label(text=text, font_size=13, color=TEXT_P, bold=True, size_hint_y=None, height=22)
        return lbl
    def _draw_bars(self, widget, data):
        widget.canvas.after.clear()
        if not data: return
        max_wpm = max((d['wpm'] for d in data), default=1)
        if max_wpm == 0: max_wpm = 1
        x, y, w, h = widget.x + 10, widget.y + 8, widget.width - 20, widget.height - 16
        n = len(data); bw = max(8, (w - (n - 1) * 4) / n)
        with widget.canvas.after:
            for i, d in enumerate(reversed(data)):
                bh = (d['wpm'] / max_wpm) * h
                bx = x + i * (bw + 4)
                by = y
                Color(*ACCENT)
                Line(rounded_rectangle=(bx, by, bw, bh, 3), width=1.2)
                Color(*TEXT_S)

class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical', padding=PAD, spacing=10)
        hdr = BoxLayout(size_hint_y=None, height=36, spacing=8)
        hdr.add_widget(VectorIcon(icon='settings', color=ACCENT_L, size=(24, 24)))
        hdr.add_widget(Label(text='Settings', font_size=20, color=TEXT_P, bold=True))
        hdr.add_widget(Widget())
        root.add_widget(hdr)
        scroll = ScrollView(size_hint=(1, 1)); scroll.bar_width = 4
        self._inner = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=(0, 0, 0, 20))
        self._inner.bind(minimum_height=self._inner.setter('height'))
        scroll.add_widget(self._inner)
        root.add_widget(scroll)
        self.add_widget(root)
        self._build_settings()
    def _build_settings(self):
        self._inner.clear_widgets()
        card = self._make_card()
        card.add_widget(self._section_title('Appearance'))
        fs_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        fs_row.add_widget(Label(text='Font Size', font_size=13, color=TEXT_P, size_hint_x=3))
        self._fs_val = Label(text=str(settings['font_size']), font_size=13, color=ACCENT_L, size_hint=(None, None))
        self._fs_val.size = (30, 40)
        fs_row.add_widget(self._fs_val)
        card.add_widget(fs_row)
        self._fs_slider = Slider(min=12, max=24, step=1, value=settings['font_size'])
        self._fs_slider.bind(value=self._on_fs_change)
        card.add_widget(self._fs_slider)
        card.height = 110
        self._inner.add_widget(card)
        snd_card = self._make_card()
        snd_card.add_widget(self._section_title('Audio'))
        snd_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        snd_row.add_widget(Label(text='Error Sound', font_size=13, color=TEXT_P, size_hint_x=3))
        self._snd_sw = Switch(active=settings['sound_enabled'])
        self._snd_sw.bind(active=self._on_sound_toggle)
        snd_row.add_widget(self._snd_sw)
        snd_card.add_widget(snd_row)
        snd_card.height = 70
        self._inner.add_widget(snd_card)
        tmr_card = self._make_card()
        tmr_card.add_widget(self._section_title('Timer Mode'))
        tmr_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        tmr_row.add_widget(Label(text='Default Timer', font_size=13, color=TEXT_P, size_hint_x=3))
        self._tmr_sp = AppSpinner(values=['Off', '30s', '60s', '120s'])
        self._tmr_sp.text = settings['timer_mode']
        self._tmr_sp.bind(text=self._on_timer_change)
        tmr_row.add_widget(self._tmr_sp)
        tmr_card.add_widget(tmr_row)
        tmr_card.height = 70
        self._inner.add_widget(tmr_card)
        rst_card = self._make_card()
        rst_card.add_widget(self._section_title('Data'))
        rst_row = BoxLayout(size_hint_y=None, height=40, spacing=10)
        rst_row.add_widget(Label(text='Reset All Progress', font_size=13, color=ERROR, size_hint_x=3))
        rst_btn = AppButton(text='Reset', icon='trash', color=ERROR, size_hint=(None, None), size=(90, 36))
        rst_btn.bind(on_release=self._confirm_reset)
        rst_row.add_widget(rst_btn)
        rst_card.add_widget(rst_row)
        rst_card.height = 70
        self._inner.add_widget(rst_card)
    def _make_card(self):
        card = BoxLayout(orientation='vertical', padding=PAD, spacing=4, size_hint=(1, None))
        with card.canvas.before:
            Color(*BG_CARD); bg = RoundedRectangle(radius=RAD, pos=card.pos, size=card.size)
        card.bind(pos=lambda *a, b=bg, c=card: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)),
                 size=lambda *a, b=bg, c=card: (setattr(b, 'pos', c.pos), setattr(b, 'size', c.size)))
        return card
    def _section_title(self, text):
        lbl = Label(text=text, font_size=13, color=TEXT_P, bold=True, size_hint_y=None, height=22)
        return lbl
    def _on_fs_change(self, inst, val):
        v = int(val); settings['font_size'] = v; self._fs_val.text = str(v)
    def _on_sound_toggle(self, inst, val):
        settings['sound_enabled'] = val
    def _on_timer_change(self, inst, val):
        settings['timer_mode'] = val
    def _confirm_reset(self, *a):
        popup = ModalView(size_hint=(0.7, 0.3), background_color=(0, 0, 0, 0))
        box = BoxLayout(orientation='vertical', padding=PAD_LG, spacing=12, size_hint=(0.9, 0.9),
                        pos_hint={'center_x': .5, 'center_y': .5})
        with box.canvas.before:
            Color(*BG_CARD); bg = RoundedRectangle(radius=RAD_LG, pos=box.pos, size=box.size)
        box.bind(pos=lambda *a: (setattr(bg, 'pos', box.pos), setattr(bg, 'size', box.size)),
                 size=lambda *a: (setattr(bg, 'pos', box.pos), setattr(bg, 'size', box.size)))
        box.add_widget(Label(text='Reset all progress?', font_size=16, color=ERROR, bold=True))
        box.add_widget(Label(text='This cannot be undone.', font_size=12, color=TEXT_S))
        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=8)
        yes = AppButton(text='Yes, Reset', color=ERROR, bold=True, size_hint=(None, None), size=(120, 36))
        yes.bind(on_release=lambda *a2: (db.reset_progress(), popup.dismiss(), self._build_settings()))
        no = AppButton(text='Cancel', size_hint=(None, None), size=(100, 36))
        no.bind(on_release=popup.dismiss)
        btn_row.add_widget(Widget()); btn_row.add_widget(yes); btn_row.add_widget(no)
        btn_row.add_widget(Widget())
        box.add_widget(btn_row)
        popup.add_widget(box); popup.open()

class CodeTypistApp(App):
    def build(self):
        Window.clearcolor = BG_DARK
        root = BoxLayout(orientation='horizontal', spacing=0)
        sidebar = BoxLayout(orientation='vertical', size_hint=(None, 1), width=70, padding=(4, 12, 4, 12), spacing=2)
        with sidebar.canvas.before:
            Color(*SIDEBAR_BG); sb_bg = RoundedRectangle(pos=sidebar.pos, size=sidebar.size, radius=[0])
        sidebar.bind(pos=lambda *a: (setattr(sb_bg, 'pos', sidebar.pos), setattr(sb_bg, 'size', sidebar.size)),
                     size=lambda *a: (setattr(sb_bg, 'pos', sidebar.pos), setattr(sb_bg, 'size', sidebar.size)))
        self._nav_btns = []
        nav_items = [
            ('home', 'Home', 'dashboard'),
            ('keyboard', 'Practice', 'practice'),
            ('trophy', 'Awards', 'achievements'),
            ('code', 'Snippets', 'snippets'),
            ('chart', 'Stats', 'stats'),
            ('settings', 'Config', 'settings'),
        ]
        for icon, label, sname in nav_items:
            btn = NavButton(icon=icon, label=label, screen_name=sname, active=(sname == 'dashboard'))
            self._nav_btns.append(btn)
            sidebar.add_widget(btn)
        sidebar.add_widget(Widget())
        self.sm = ScreenManager(transition=NoTransition())
        self.sidebar_sm = ScreenManager(transition=SlideTransition(direction='left'))
        self.sidebar_sm.add_widget(self.sm)
        self.dashboard_screen = DashboardScreen(name='dashboard')
        self.practice_screen = PracticeScreen(name='practice')
        self.sm.add_widget(self.dashboard_screen)
        self.sm.add_widget(self.practice_screen)
        self.sm.add_widget(AchievementsScreen(name='achievements'))
        self.sm.add_widget(SnippetsScreen(name='snippets'))
        self.sm.add_widget(StatsScreen(name='stats'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        root.add_widget(sidebar)
        root.add_widget(self.sidebar_sm)
        Clock.schedule_once(lambda dt: self.switch_screen('dashboard'), 0.1)
        return root
    def switch_screen(self, name):
        if self.sm.current == name: return
        self.sm.transition = SlideTransition(direction='left')
        self.sm.current = name
        for btn in self._nav_btns:
            btn.set_active(btn.screen_name == name)
        screen = self.sm.current_screen
        if hasattr(screen, 'on_enter'):
            screen.on_enter()

if __name__ == '__main__':
    CodeTypistApp().run()
