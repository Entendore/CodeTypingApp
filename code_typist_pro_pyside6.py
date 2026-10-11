#!/usr/bin/env python3
"""
Code Typist Pro - PySide6 Edition (single-file)
Features: Sidebar nav, Settings, Stats/Analytics, Timed Mode, Streak Calendar,
          Import/Export, Search, Edit Snippets, Keyboard Shortcuts, Sound Feedback,
          Daily Challenge, Progress Bar, Clipboard Copy, 14 languages, 15 achievements.
Run:  pip install PySide6  &&  python code_typist_pro_pyside6.py
"""
import math, time, random, json, sqlite3, hashlib, os, struct, wave, tempfile, subprocess, sys
from datetime import datetime, date, timedelta

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QFrame, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLabel, QPushButton, QLineEdit, QTextEdit,
    QComboBox, QSlider, QCheckBox, QScrollArea, QSizePolicy, QDialog,
    QMessageBox, QShortcut, QSpinBox, QScrollBar, QMenu
)
from PySide6.QtCore import Qt, QTimer, QRectF, QRegExp, Signal, QSize, QPoint
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QSyntaxHighlighter,
    QTextCharFormat, QTextDocument, QKeySequence, QTextCursor, QClipboard,
    QGuiApplication
)

# === THEME ===
BG_DARK = "#0b0d1a"
BG_MAIN = "#12142a"
BG_CARD = "#1a1d3a"
BG_INPUT = "#161833"
BG_HOVER = "#22254a"
ACCENT = "#6c5ce7"
ACCENT_L = "#a29bfe"
ACCENT_D = "#4834d4"
SUCCESS = "#00e676"
ERROR = "#ff5252"
WARNING = "#ffab40"
INFO = "#40c4ff"
TEXT_P = "#eceff1"
TEXT_S = "#90a4ae"
TEXT_M = "#546e7a"
BORDER = "#26294a"
SIDEBAR_BG = "#0e1024"

GLOBAL_QSS = f"""
QMainWindow {{ background: {BG_MAIN}; }}
QFrame#card {{ background: {BG_CARD}; border-radius: 10px; border: 1px solid {BORDER}; }}
QPushButton#accent {{ background: {ACCENT}; color: {TEXT_P}; border: none; border-radius: 10px;
    padding: 10px 20px; font-weight: bold; font-size: 13px; }}
QPushButton#accent:hover {{ background: #7d6ff0; }}
QPushButton#accent:pressed {{ background: {ACCENT_D}; }}
QPushButton {{ background: transparent; color: {TEXT_P}; border: none; border-radius: 6px;
    padding: 6px 12px; font-size: 13px; }}
QPushButton:hover {{ background: {BG_HOVER}; }}
QLineEdit {{ background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 10px; font-size: 13px; selection-background-color: {ACCENT}; }}
QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
QTextEdit {{ background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 10px; font-size: 13px; selection-background-color: {ACCENT}; }}
QTextEdit:focus {{ border: 1px solid {ACCENT}; }}
QComboBox {{ background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
    border-radius: 10px; padding: 8px 12px; font-size: 13px; min-width: 100px; }}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox::down-arrow {{ image: none; border: none; }}
QComboBox QAbstractItemView {{ background: {BG_CARD}; color: {TEXT_P}; border: 1px solid {BORDER};
    border-radius: 6px; selection-background-color: {ACCENT}; outline: none; }}
QLabel {{ color: {TEXT_P}; background: transparent; }}
QSlider::groove:horizontal {{ background: {BG_INPUT}; height: 6px; border-radius: 3px; }}
QSlider::handle:horizontal {{ background: {ACCENT}; width: 18px; margin: -6px 0; border-radius: 9px; }}
QSlider::handle:horizontal:hover {{ background: #7d6ff0; }}
QScrollBar:vertical {{ background: {BG_MAIN}; width: 8px; border: none; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
QCheckBox {{ color: {TEXT_P}; spacing: 8px; font-size: 13px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 4px; border: 1px solid {BORDER};
    background: {BG_INPUT}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QToolTip {{ background: {BG_CARD}; color: {TEXT_P}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 4px 8px; font-size: 12px; }}
"""

# === SETTINGS (persistent JSON) ===
class Settings:
    PATH = 'ctp_settings.json'
    DEFAULTS = dict(font_size=14, sound_enabled=True, timer_mode='Off', countdown_seconds=60)
    def __init__(self):
        self.data = dict(self.DEFAULTS)
        self._load()
    def _load(self):
        try:
            with open(self.PATH) as f:
                self.data.update(json.load(f))
        except Exception:
            pass
    def save(self):
        try:
            with open(self.PATH, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass
    def __getitem__(self, k):
        return self.data.get(k, self.DEFAULTS.get(k))
    def __setitem__(self, k, v):
        self.data[k] = v
        self.save()

settings = Settings()

# === DEFAULT SNIPPETS ===
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
    ("First Steps","Complete your first snippet","\U0001f463"),
    ("Speed Demon","Reach 40 WPM","\u26a1"),
    ("Lightning Fingers","Reach 80 WPM","\u26a1"),
    ("Perfectionist","Get 100% accuracy","\U0001f3af"),
    ("Streak Starter","3-day streak","\U0001f525"),
    ("Week Warrior","7-day streak","\U0001f525"),
    ("Ten Down","Complete 10 snippets","\U0001f4ca"),
    ("Hard Mode","Complete a hard snippet","\U0001f3c6"),
    ("Combo King","50-character combo","\u2728"),
    ("Polyglot","Practice 3+ languages","\U0001f4bb"),
    ("Marathon","Complete 50 snippets","\u2b50"),
    ("Scholar","Practice 6+ languages","\U0001f4bb"),
    ("Timed Ace","Complete a timed challenge","\u23f0"),
    ("Collector","Have 50+ snippets","+"),
    ("Dedicated","5-day streak","\U0001f525"),
]

# === DATABASE ===
class Database:
    def __init__(self, path='code_typist_pro.db'):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self._migrate()

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
        try:
            self.c.execute('SELECT combo_max FROM history LIMIT 0')
        except Exception:
            self.c.execute('ALTER TABLE history ADD COLUMN combo_max INTEGER DEFAULT 0')
        self.conn.commit()
        for lang, name, code, diff in DEFAULT_SNIPPETS:
            self.c.execute('INSERT OR IGNORE INTO snippets(lang,name,code,difficulty) VALUES(?,?,?,?)',
                           (lang, name, code, diff))
        for name, desc, icon in DEFAULT_ACHIEVEMENTS:
            self.c.execute('INSERT OR IGNORE INTO achievements(name,desc,icon) VALUES(?,?,?)',
                           (name, desc, icon))
        self.conn.commit()

    def get_snippets(self, search=None):
        if search:
            self.c.execute('SELECT * FROM snippets WHERE lang LIKE ? OR name LIKE ? OR code LIKE ?',
                           (f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            self.c.execute('SELECT * FROM snippets ORDER BY lang, name')
        return [dict(r) for r in self.c.fetchall()]

    def add_snippet(self, lang, name, code, diff='medium'):
        self.c.execute('INSERT INTO snippets(lang,name,code,difficulty) VALUES(?,?,?,?)',
                       (lang, name, code, diff))
        self.conn.commit()
        return self.c.lastrowid

    def update_snippet(self, sid, lang, name, code, diff):
        self.c.execute('UPDATE snippets SET lang=?,name=?,code=?,difficulty=? WHERE id=?',
                       (lang, name, code, diff, sid))
        self.conn.commit()

    def delete_snippet(self, sid):
        self.c.execute('DELETE FROM snippets WHERE id=?', (sid,))
        self.conn.commit()

    def get_history(self, limit=20):
        self.c.execute('SELECT * FROM history ORDER BY id DESC LIMIT ?', (limit,))
        return [dict(r) for r in self.c.fetchall()]

    def get_full_history(self):
        self.c.execute('SELECT * FROM history ORDER BY id DESC')
        return [dict(r) for r in self.c.fetchall()]

    def add_history(self, sid, lang, name, wpm, acc, xp, elapsed, combo=0):
        ts = datetime.now().isoformat()
        self.c.execute(
            'INSERT INTO history(snippet_id,lang,name,wpm,accuracy,xp,elapsed,ts,combo_max) VALUES(?,?,?,?,?,?,?,?,?)',
            (sid, lang, name, wpm, acc, xp, elapsed, ts, combo))
        self.conn.commit()

    def get_achievements(self):
        self.c.execute('SELECT * FROM achievements ORDER BY id')
        return [dict(r) for r in self.c.fetchall()]

    def unlock_achievement(self, name):
        self.c.execute('UPDATE achievements SET unlocked=1,ts=? WHERE name=?',
                       (datetime.now().isoformat(), name))
        self.conn.commit()

    def get_total_xp(self):
        r = self.c.execute('SELECT COALESCE(SUM(xp),0) as s FROM history').fetchone()
        return r['s']

    def get_streak(self):
        days = set()
        for r in self.c.execute('SELECT DISTINCT date(ts) as d FROM history ORDER BY d DESC'):
            days.add(r['d'])
        if not days:
            return 0
        streak = 0
        today = date.today()
        for i in range(365):
            d = (today - timedelta(days=i)).isoformat()
            if d in days:
                streak += 1
            elif i > 0:
                break
            else:
                pass
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
            if r:
                result[d] = dict(r)
            else:
                result[d] = None
        return result

    def record_activity(self, d=None, snippets=1, xp=0, time_sec=0):
        if d is None:
            d = date.today().isoformat()
        self.c.execute(
            'INSERT INTO activity(date,snippets,xp,time_sec) VALUES(?,?,?,?) '
            'ON CONFLICT(date) DO UPDATE SET snippets=snippets+?,xp=xp+?,time_sec=time_sec+?',
            (d, snippets, xp, time_sec, snippets, xp, time_sec))
        self.conn.commit()

    def export_snippets(self):
        return json.dumps(self.get_snippets(), indent=2)

    def import_snippets_json(self, data):
        try:
            items = json.loads(data) if isinstance(data, str) else data
            count = 0
            for item in items:
                self.c.execute(
                    'INSERT OR IGNORE INTO snippets(lang,name,code,difficulty) VALUES(?,?,?,?)',
                    (item.get('lang', ''), item.get('name', ''), item.get('code', ''),
                     item.get('difficulty', 'medium')))
                count += self.c.rowcount
            self.conn.commit()
            return count
        except Exception:
            return 0

    def reset_progress(self):
        self.c.execute('DELETE FROM history')
        self.c.execute('UPDATE achievements SET unlocked=0,ts=NULL')
        self.c.execute('DELETE FROM activity')
        self.conn.commit()

db = Database()

# === GAME LOGIC ===
def xp_for_level(lvl):
    return int(50 * (lvl ** 1.5))

def calc_level(xp):
    lvl = 0
    needed = 0
    while needed + xp_for_level(lvl + 1) <= xp:
        lvl += 1
        needed += xp_for_level(lvl)
    return lvl

def xp_to_next(xp):
    lvl = calc_level(xp)
    used = sum(xp_for_level(i) for i in range(1, lvl + 1))
    return xp_for_level(lvl + 1) - (xp - used), xp_for_level(lvl + 1)

def calc_xp(wpm, acc, elapsed, diff_mult=1.0):
    base = int(wpm * (acc / 100) * (elapsed / 60) * 2)
    return max(5, int(base * diff_mult))

def check_achievements(stats):
    unlocked = set(r['name'] for r in db.get_achievements() if r['unlocked'])
    new = []
    def chk(name, cond):
        if name not in unlocked and cond:
            new.append(name)
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
    for n in new:
        db.unlock_achievement(n)
    return new

def daily_snippet():
    today = date.today().isoformat()
    seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
    all_snips = db.get_snippets()
    if not all_snips:
        return None
    return all_snips[seed % len(all_snips)]

# FIX #5: Cross-platform sound with multiple fallbacks (no longer Linux-only aplay)
def play_error_sound():
    if not settings['sound_enabled']:
        return
    try:
        sr, dur, freq = 22050, 0.06, 280
        n = int(sr * dur)
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        with wave.open(path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            for i in range(n):
                t = i / sr
                env = max(0, 1 - t / dur)
                val = int(env * 6000 * math.sin(2 * math.pi * freq * t))
                wf.writeframes(struct.pack('<h', max(-32768, min(32767, val))))
        # Try multiple audio players for cross-platform support
        for cmd in [['aplay', '-q'], ['paplay'],
                    ['ffplay', '-nodisp', '-autoexit'],
                    ['powershell', '-c', f'(New-Object Media.SoundPlayer "{path}").PlaySync()']]:
            try:
                subprocess.Popen(cmd + [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            except FileNotFoundError:
                continue
        QTimer.singleShot(2000, lambda: os.unlink(path) if os.path.exists(path) else None)
    except Exception:
        pass

# === STYLED WIDGETS ===

class StyledCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(f"""
            QFrame#card {{
                background: {BG_CARD}; border-radius: 10px; border: 1px solid {BORDER};
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(15, 15, 15, 15)
        self._layout.setSpacing(8)

    def addWidget(self, w):
        self._layout.addWidget(w)

    def clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

class StyledButton(QPushButton):
    def __init__(self, text="", accent=False, icon_text=None, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(36)
        self.setCursor(Qt.PointingHandCursor)
        self._accent = accent
        self._icon_text = icon_text
        if accent:
            self.setObjectName("accent")
            self.setStyleSheet(f"""
                QPushButton#accent {{
                    background: {ACCENT}; color: {TEXT_P}; border: none; border-radius: 10px;
                    padding: 10px 20px; font-weight: bold; font-size: 13px;
                }}
                QPushButton#accent:hover {{ background: #7d6ff0; }}
                QPushButton#accent:pressed {{ background: {ACCENT_D}; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {BG_HOVER}; color: {TEXT_P}; border: none; border-radius: 6px;
                    padding: 6px 12px; font-size: 13px;
                }}
                QPushButton:hover {{ background: #2e315a; }}
            """)
        if icon_text:
            self.setText(f"{icon_text}  {text}" if text else icon_text)

class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 10px; padding: 10px; font-size: 13px;
            }}
            QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
        """)

class StyledTextEdit(QTextEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(f"""
            QTextEdit {{
                background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 10px; padding: 10px; font-size: 13px;
            }}
            QTextEdit:focus {{ border: 1px solid {ACCENT}; }}
        """)

class StyledComboBox(QComboBox):
    def __init__(self, items=(), parent=None):
        super().__init__(parent)
        self.addItems(items)
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            QComboBox {{
                background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 10px; padding: 8px 12px; font-size: 13px; min-width: 100px;
            }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox::down-arrow {{ image: none; border: none; }}
            QComboBox QAbstractItemView {{
                background: {BG_CARD}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 6px; selection-background-color: {ACCENT}; outline: none;
            }}
        """)

class CodeHighlighter(QSyntaxHighlighter):
    """Colors each character of the target text based on typed text."""
    def __init__(self, document, parent=None):
        super().__init__(document, parent)
        self._target = ""
        self._typed = ""

    def set_data(self, target, typed):
        self._target = target
        self._typed = typed
        self.rehighlight()

    def reset(self):
        self._typed = ""
        self.rehighlight()

    def highlightBlock(self, text):
        if not self._target:
            return
        target = self._target
        typed = self._typed
        for i, ch in enumerate(text):
            fmt = QTextCharFormat()
            idx = self.currentBlock().position() + i
            if idx < len(typed):
                if idx < len(target) and ch == target[idx]:
                    fmt.setForeground(QColor(SUCCESS))
                else:
                    fmt.setForeground(QColor(ERROR))
            elif idx < len(target):
                fmt.setForeground(QColor(TEXT_M))
                if idx == len(typed):
                    fmt.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
                    fmt.setUnderlineColor(QColor(ACCENT_L))
            else:
                fmt.setForeground(QColor(ERROR))
            self.setFormat(i, 1, fmt)


class CodeDisplayWidget(QTextEdit):
    """Read-only display showing the target code with character highlighting."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("monospace", settings['font_size']))
        self._target = ""
        self._highlighter = CodeHighlighter(self.document(), self)
        self.setStyleSheet(f"""
            QTextEdit {{
                background: {BG_INPUT}; color: {TEXT_M}; border: 1px solid {BORDER};
                border-radius: 10px; padding: 12px; font-family: monospace;
            }}
        """)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def set_target(self, target):
        self._target = target
        self.setPlainText(target)
        self._highlighter.set_data(target, "")

    def update_typed(self, typed):
        self._highlighter.set_data(self._target, typed)

    def reset(self):
        self._highlighter.reset()

    def set_font_size(self, size):
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)


class XPBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._max_val = 100
        self.setFixedHeight(8)

    def set_value(self, value, max_val):
        self._value = value
        self._max_val = max(max_val, 1)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(BG_INPUT))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 4, 4)
        ratio = min(self._value / self._max_val, 1.0)
        w = self.width() * ratio
        if w > 0:
            p.setBrush(QColor(ACCENT))
            p.drawRoundedRect(QRectF(0, 0, w, self.height()), 4, 4)
        p.end()


class ProgressBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._max_val = 100
        self.setFixedHeight(6)

    def set_value(self, value, max_val=100):
        self._value = value
        self._max_val = max(max_val, 1)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(BG_INPUT))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 3, 3)
        ratio = min(self._value / self._max_val, 1.0)
        w = self.width() * ratio
        if w > 0:
            p.setBrush(QColor(SUCCESS))
            p.drawRoundedRect(QRectF(0, 0, w, self.height()), 3, 3)
        p.end()


class WpmChartWidget(QWidget):
    """Bar chart of WPM for the last N sessions."""
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self._data = data or []
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)

    def set_data(self, data):
        self._data = data
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(BG_INPUT))
        if not self._data:
            p.end()
            return
        max_wpm = max((d['wpm'] for d in self._data), default=1)
        if max_wpm == 0:
            max_wpm = 1
        x, y, w, h = 10, 8, self.width() - 20, self.height() - 24
        n = len(self._data)
        bw = max(8, (w - (n - 1) * 4) / n)
        for i, d in enumerate(reversed(self._data)):
            bh = (d['wpm'] / max_wpm) * h
            bx = x + i * (bw + 4)
            by = y + h - bh
            p.setBrush(QColor(ACCENT))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRectF(bx, by, bw, bh), 3, 3)
            p.setPen(QColor(TEXT_S))
            p.setFont(QFont("sans-serif", 8))
            p.drawText(QRectF(bx, by - 14, bw, 14), Qt.AlignCenter, str(int(d['wpm'])))
        p.end()


class ScrollableWidget(QWidget):
    """A widget that contains a QScrollArea with a vertical layout inside."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(0)
        self._inner_layout.addStretch()
        self._scroll.setWidget(self._inner)
        self._layout.addWidget(self._scroll)

    def inner_layout(self):
        return self._inner_layout

    def scroll_area(self):
        return self._scroll

    def clear_inner(self):
        while self._inner_layout.count():
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
            elif item.spacerItem():
                self._inner_layout.removeItem(item)
        self._inner_layout.addStretch()

# === SCREENS ===

ICON_MAP = {
    'home': '\U0001f3e0', 'keyboard': '\u2328\ufe0f', 'trophy': '\U0001f3c6',
    'code': '\U0001f4bb', 'chart': '\U0001f4ca', 'settings': '\u2699\ufe0f',
    'flame': '\U0001f525', 'target': '\U0001f3af', 'check': '\u2705',
    'refresh': '\U0001f504', 'arrow_right': '\u27a1\ufe0f', 'copy': '\U0001f4cb',
    'plus': '\u2795', 'upload': '\U0001f4e5', 'download': '\U0001f4e4',
    'trash': '\U0001f5d1\ufe0f', 'edit': '\u270f\ufe0f', 'clock': '\u23f0',
    'star': '\u2b50', 'sparkle': '\u2728', 'bolt': '\u26a1',
    'footprints': '\U0001f463',
}

def make_label(text, size=13, color=TEXT_P, bold=False, align=None):
    lbl = QLabel(text)
    font = lbl.font()
    font.setPointSize(size)
    font.setBold(bold)
    lbl.setFont(font)
    lbl.setStyleSheet(f"color: {color}; background: transparent; border: none;")
    if align:
        lbl.setAlignment(align)
    return lbl

def make_icon_label(icon_name, size=20):
    ch = ICON_MAP.get(icon_name, '\u2022')
    lbl = QLabel(ch)
    lbl.setStyleSheet(f"background: transparent; border: none;")
    lbl.setFixedSize(size, size)
    font = lbl.font()
    font.setPointSize(max(size - 6, 10))
    lbl.setFont(font)
    return lbl

def make_hbox(items, spacing=8):
    box = QHBoxLayout()
    box.setSpacing(spacing)
    for item in items:
        if item is None:
            box.addStretch()
        else:
            box.addWidget(item)
    return box

def make_vbox(items, spacing=8):
    box = QVBoxLayout()
    box.setSpacing(spacing)
    for item in items:
        if item is None:
            box.addStretch()
        else:
            box.addWidget(item)
    return box


class DashboardScreen(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self._main_win = main_win
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(14)

        # Header
        hdr = make_hbox([make_icon_label('home', 24), make_label('Dashboard', 20, bold=True), None])
        layout.addLayout(hdr)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        inner = QWidget()
        self._inner_layout = QVBoxLayout(inner)
        self._inner_layout.setSpacing(10)
        self._inner_layout.setContentsMargins(0, 0, 0, 20)
        self._inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll)

    def on_enter(self):
        # Clear old content (remove everything except the stretch at end)
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        streak = db.get_streak()
        total_xp = db.get_total_xp()
        lvl = calc_level(total_xp)
        rem, need = xp_to_next(total_xp)
        history = db.get_full_history()
        best_wpm = max((h['wpm'] for h in history), default=0)

        # Stats card
        stats_card = StyledCard()
        stats_card._layout.setSpacing(6)
        row1 = make_hbox([make_icon_label('flame', 20), make_label(f'{streak} day streak', 14, bold=True), None])
        stats_card._layout.addLayout(row1)
        row2 = make_hbox([
            make_label(f'Level {lvl}', 13, ACCENT_L, bold=True),
            make_label(f'{total_xp} XP', 12, TEXT_S),
            None,
            make_label(f'Best WPM: {int(best_wpm)}', 12, SUCCESS, bold=True),
            make_label(f'Completed: {len(history)}', 12, TEXT_S),
        ])
        stats_card._layout.addLayout(row2)
        xp_bar = XPBarWidget()
        xp_bar.set_value(need - rem, need)
        stats_card._layout.addWidget(xp_bar)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, stats_card)

        # Calendar card
        cal_card = StyledCard()
        cal_card._layout.setSpacing(8)
        cal_card._layout.addWidget(make_label('Last 28 Days', 12, bold=True))
        cal_grid = QGridLayout()
        cal_grid.setSpacing(3)
        days_data = db.get_activity_days(28)
        day_keys = list(days_data.keys())
        for i in range(28):
            d = day_keys[i]
            cell = QFrame()
            cell.setFixedSize(32, 22)
            if days_data[d]:
                intensity = min(days_data[d].get('snippets', 0) / 5.0, 1.0)
                alpha = 0.2 + intensity * 0.8
                r, g, b = 0x6c, 0x5c, 0xe7
                bg = f'rgba({r},{g},{b},{alpha:.2f})'
                cell.setStyleSheet(f"background: {ACCENT}; border-radius: 3px; opacity: {alpha:.2f};")
            else:
                cell.setStyleSheet(f"background: {BG_INPUT}; border-radius: 3px;")
            col = i % 7
            row = i // 7
            cal_grid.addWidget(cell, row, col)
        cal_card._layout.addLayout(cal_grid)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, cal_card)

        # Daily challenge button
        daily_btn = StyledButton("Daily Challenge", accent=True, icon_text=ICON_MAP.get('target', ''))
        daily_btn.setFixedHeight(44)
        daily_btn.clicked.connect(self._start_daily)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, daily_btn)

        # Recent sessions card
        recent_card = StyledCard()
        recent_card._layout.setSpacing(6)
        recent_card._layout.addWidget(make_label('Recent Sessions', 12, bold=True))
        recent_hist = db.get_history(5)
        if not recent_hist:
            recent_card._layout.addWidget(make_label('No sessions yet. Start practicing!', 12, TEXT_S))
        for h in recent_hist:
            row = make_hbox([
                make_label(h['name'] or '?', 12),
                make_label(f'{int(h["wpm"])} wpm', 11, SUCCESS),
                make_label(f'{int(h["accuracy"])}%', 11, TEXT_S),
                None,
            ])
            recent_card._layout.addLayout(row)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, recent_card)

    def _start_daily(self):
        self._main_win.switch_screen('practice')
        snip = daily_snippet()
        if snip:
            self._main_win.practice_screen.load_snippet(snip)


class PracticeScreen(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self._main_win = main_win
        self._timer_ev = None
        self._time_left = 0
        self._snippet = None
        self._is_timed = False
        self._combo = 0
        self._max_combo = 0
        self._errors = 0
        self._started = False
        self._start_time = 0
        self._last_typed_len = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header
        self._lang_lbl = make_label('', 13, ACCENT_L, bold=True)
        hdr = make_hbox([
            make_icon_label('keyboard', 24), make_label('Practice', 20, bold=True),
            None, self._lang_lbl,
        ])
        layout.addLayout(hdr)

        # Info bar
        self._diff_lbl = make_label('', 11, TEXT_S)
        self._wpm_lbl = make_label('0 WPM', 13, SUCCESS, bold=True)
        self._acc_lbl = make_label('100%', 13, ACCENT_L, bold=True)
        self._timer_lbl = make_label('', 13, WARNING, bold=True)
        self._combo_lbl = make_label('', 12, INFO)
        info = make_hbox([self._diff_lbl, self._wpm_lbl, self._acc_lbl, self._timer_lbl, self._combo_lbl])
        layout.addLayout(info)

        # Progress bar
        self._progress = ProgressBarWidget()
        layout.addWidget(self._progress)

        # Code display (read-only with highlighting)
        self._display = CodeDisplayWidget()
        layout.addWidget(self._display, stretch=3)

        # FIX #1: Use QTextEdit (not QLineEdit) for multiline typing support
        self._input = QTextEdit()
        self._input.setAcceptRichText(False)
        self._input.setFont(QFont("monospace", settings['font_size']))
        self._input.setPlaceholderText("Start typing here...")
        self._input.setStyleSheet(f"""
            QTextEdit {{
                background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 10px; padding: 10px; font-size: 13px;
                font-family: monospace; selection-background-color: {ACCENT};
            }}
            QTextEdit:focus {{ border: 1px solid {ACCENT}; }}
        """)
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        # Result box
        self._result_frame = QFrame()
        self._result_frame.setFixedHeight(0)
        self._result_frame.setStyleSheet(f"background: {BG_CARD}; border-radius: 10px; border: 1px solid {BORDER};")
        self._result_layout = QVBoxLayout(self._result_frame)
        self._result_layout.setContentsMargins(15, 12, 15, 12)
        self._result_layout.setSpacing(8)
        layout.addWidget(self._result_frame)

        # Controls row (FIX #2: removed dead `if False else None` code block)
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(8)

        all_langs = sorted(set(s['lang'] for s in db.get_snippets()))
        self._lang_combo = StyledComboBox(['All'] + all_langs)
        self._lang_combo.currentTextChanged.connect(lambda _: self.next_snippet())
        ctrl_layout.addWidget(self._lang_combo)

        self._diff_combo = StyledComboBox(['All', 'easy', 'medium', 'hard'])
        self._diff_combo.currentTextChanged.connect(lambda _: self.next_snippet())
        ctrl_layout.addWidget(self._diff_combo)

        self._timer_combo = StyledComboBox(['Off', '30s', '60s', '120s'])
        self._timer_combo.setCurrentText(settings['timer_mode'])
        ctrl_layout.addWidget(self._timer_combo)

        ctrl_layout.addStretch()

        reset_btn = StyledButton("Reset", icon_text=ICON_MAP.get('refresh', ''))
        reset_btn.clicked.connect(self._reset)
        ctrl_layout.addWidget(reset_btn)

        next_btn = StyledButton("Next", icon_text=ICON_MAP.get('arrow_right', ''))
        next_btn.clicked.connect(lambda: self.next_snippet())
        ctrl_layout.addWidget(next_btn)

        copy_btn = StyledButton("Copy", icon_text=ICON_MAP.get('copy', ''))
        copy_btn.clicked.connect(self._copy_code)
        ctrl_layout.addWidget(copy_btn)

        layout.addLayout(ctrl_layout)

        # Keyboard shortcuts
        self._shortcut_reset = QShortcut(QKeySequence("Ctrl+R"), self)
        self._shortcut_reset.activated.connect(self._reset)
        self._shortcut_next = QShortcut(QKeySequence("Ctrl+N"), self)
        self._shortcut_next.activated.connect(lambda: self.next_snippet())

        # Load initial snippet
        QTimer.singleShot(100, self.next_snippet)

    def keyPressEvent(self, event):
        # Intercept Tab key to insert 4 spaces instead of changing focus
        if event.key() == Qt.Key_Tab and self._snippet:
            tc = self._input.textCursor()
            tc.insertText('    ')
            return
        super().keyPressEvent(event)

    def _copy_code(self):
        if self._snippet:
            QApplication.clipboard().setText(self._snippet['code'])

    def _on_text_changed(self):
        if not self._snippet:
            return
        # FIX #1: Use toPlainText() for QTextEdit (was .text() for QLineEdit)
        text = self._input.toPlainText()
        target = self._snippet['code']
        tl = len(text)
        prev_len = self._last_typed_len
        self._last_typed_len = tl

        if tl > 0 and not self._started:
            self._started = True
            self._start_time = time.time()

        # Detect new character typed (only check last char if text grew)
        if tl > prev_len and tl <= len(target):
            if text[-1] == target[tl - 1]:
                self._combo += 1
                self._max_combo = max(self._max_combo, self._combo)
            else:
                self._errors += 1
                self._combo = 0
                play_error_sound()

        # If text shrank (backspace), recompute errors from scratch for accuracy
        if tl < prev_len:
            self._errors = sum(1 for i in range(tl) if i < len(target) and text[i] != target[i])

        self._display.update_typed(text)
        if len(target) > 0:
            self._progress.set_value(min(tl, len(target)), len(target))

        if self._started and tl > 0:
            elapsed = time.time() - self._start_time
            words = tl / 5
            wpm = (words / (elapsed / 60)) if elapsed > 0 else 0
            acc = ((tl - self._errors) / tl * 100) if tl > 0 else 100
            self._wpm_lbl.setText(f'{int(wpm)} WPM')
            self._acc_lbl.setText(f'{int(min(acc, 100))}%')

        if self._combo >= 5:
            self._combo_lbl.setText(f'{self._combo}x combo')
        else:
            self._combo_lbl.setText('')

        if tl >= len(target):
            self._on_complete()

    def _on_complete(self):
        self._cancel_timer()
        stats = self._get_stats()
        self._finish_session(stats, fully_completed=True)

    def _on_timer_expire(self):
        self._time_left = 0
        self._timer_lbl.setText('0s')
        stats = self._get_stats()
        self._finish_session(stats, fully_completed=False)

    def _get_stats(self):
        elapsed = time.time() - self._start_time if self._started else 0
        # FIX #1: Use toPlainText() instead of .text()
        chars = len(self._input.toPlainText())
        words = chars / 5 if elapsed > 0 else 0
        wpm = (words / (elapsed / 60)) if elapsed > 0 else 0
        acc = ((chars - self._errors) / chars * 100) if chars > 0 else 100
        return dict(wpm=round(wpm, 1), accuracy=round(min(acc, 100), 1),
                    elapsed=elapsed, combo=self._combo, max_combo=self._max_combo,
                    errors=self._errors, chars=chars)

    def _finish_session(self, stats, fully_completed):
        self._input.setEnabled(False)
        self._result_frame.setFixedHeight(180)
        # Clear old results
        while self._result_layout.count():
            item = self._result_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        if not fully_completed:
            self._result_layout.addWidget(make_label('Time Up!', 16, WARNING, bold=True, align=Qt.AlignCenter))
        else:
            self._result_layout.addWidget(make_label('Complete!', 16, SUCCESS, bold=True, align=Qt.AlignCenter))

        wpm = stats['wpm']
        acc = stats['accuracy']
        elapsed = stats['elapsed']
        self._wpm_lbl.setText(f'{wpm} WPM')
        self._acc_lbl.setText(f'{acc}%')

        detail = f'WPM: {wpm}  |  Accuracy: {acc}%  |  Time: {round(elapsed, 1)}s  |  Combo: {stats["max_combo"]}'
        self._result_layout.addWidget(make_label(detail, 12, TEXT_S, align=Qt.AlignCenter))

        if self._snippet:
            diff = self._snippet.get('difficulty', 'medium')
            mult = {'easy': 0.8, 'medium': 1.0, 'hard': 1.5}.get(diff, 1.0)
        else:
            mult = 1.0
        if not fully_completed:
            mult *= 0.5
        xp = calc_xp(wpm, acc, elapsed, mult)
        self._result_layout.addWidget(make_label(f'+{xp} XP', 14, ACCENT_L, bold=True, align=Qt.AlignCenter))

        if self._snippet:
            db.add_history(self._snippet['id'], self._snippet['lang'], self._snippet['name'],
                           wpm, acc, xp, elapsed, stats['max_combo'])
            db.record_activity(snippets=1, xp=xp, time_sec=elapsed)
            ach_stats = dict(total=len(db.get_full_history()), best_wpm=wpm, best_acc=acc,
                             streak=db.get_streak(), max_combo=stats['max_combo'], hard_done=False,
                             lang_count=len(set(r['lang'] for r in db.get_full_history())),
                             timed_done=self._is_timed, snippet_count=len(db.get_snippets()))
            if diff == 'hard' and fully_completed:
                ach_stats['hard_done'] = True
            new_achs = check_achievements(ach_stats)
            for an in new_achs:
                a_info = [a for a in db.get_achievements() if a['name'] == an]
                if a_info:
                    ai = a_info[0]
                    QMessageBox.information(self, 'Achievement Unlocked!',
                                            f'{ai["icon"]}\n{ai["name"]}\n{ai["desc"]}')

        btn_row = make_hbox([None,
            StyledButton("Try Again", accent=True, icon_text=ICON_MAP.get('refresh', '')),
            StyledButton("Next", accent=True, icon_text=ICON_MAP.get('arrow_right', '')),
            None])
        self._result_layout.addLayout(btn_row)
        # Connect buttons
        for i in range(btn_row.count()):
            w = btn_row.itemAt(i).widget()
            if isinstance(w, StyledButton):
                if 'Try Again' in w.text():
                    w.clicked.connect(self._reset)
                elif 'Next' in w.text():
                    w.clicked.connect(lambda: self.next_snippet())

    def _reset(self):
        self._cancel_timer()
        self._input.setEnabled(True)
        self._input.clear()
        self._combo = 0
        self._max_combo = 0
        self._errors = 0
        self._started = False
        self._start_time = 0
        self._last_typed_len = 0
        self._display.reset()
        # Clear results
        self._result_frame.setFixedHeight(0)
        while self._result_layout.count():
            item = self._result_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._wpm_lbl.setText('0 WPM')
        self._acc_lbl.setText('100%')
        self._timer_lbl.setText('')
        self._combo_lbl.setText('')
        self._progress.set_value(0)
        if self._is_timed:
            self._start_timer()

    def _start_timer(self):
        self._cancel_timer()
        txt = self._timer_combo.currentText()
        if txt == 'Off':
            self._is_timed = False
            self._timer_lbl.setText('')
            return
        self._is_timed = True
        secs = int(txt.replace('s', ''))
        self._time_left = secs
        self._timer_lbl.setText(f'{secs}s')
        self._timer_ev = QTimer()
        self._timer_ev.timeout.connect(self._tick_timer)
        self._timer_ev.start(1000)

    def _tick_timer(self):
        self._time_left -= 1
        if self._time_left <= 0:
            self._cancel_timer()
            self._on_timer_expire()
        else:
            self._timer_lbl.setText(f'{self._time_left}s')

    def _cancel_timer(self):
        if self._timer_ev:
            self._timer_ev.stop()
            self._timer_ev.deleteLater()
            self._timer_ev = None

    def load_snippet(self, snip):
        self._cancel_timer()
        self._snippet = snip
        self._input.setEnabled(True)
        self._input.clear()
        self._combo = 0
        self._max_combo = 0
        self._errors = 0
        self._started = False
        self._start_time = 0
        self._last_typed_len = 0
        self._display.set_target(snip['code'])
        self._lang_lbl.setText(snip['lang'])
        self._diff_lbl.setText(snip.get('difficulty', ''))
        # Clear results
        self._result_frame.setFixedHeight(0)
        while self._result_layout.count():
            item = self._result_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self._wpm_lbl.setText('0 WPM')
        self._acc_lbl.setText('100%')
        self._combo_lbl.setText('')
        self._progress.set_value(0)
        fs = settings['font_size']
        self._input.setFont(QFont("monospace", fs))
        self._display.set_font_size(fs)
        self._start_timer()

    def next_snippet(self):
        self._cancel_timer()
        lang = self._lang_combo.currentText()
        diff = self._diff_combo.currentText()
        snips = db.get_snippets()
        if lang != 'All':
            snips = [s for s in snips if s['lang'] == lang]
        if diff != 'All':
            snips = [s for s in snips if s['difficulty'] == diff]
        if snips:
            self.load_snippet(random.choice(snips))

    def apply_font_size(self, size):
        """Called when settings change font size, to update live."""
        self._input.setFont(QFont("monospace", size))
        self._display.set_font_size(size)

    def on_enter(self):
        self._input.setFocus()

class AchievementsScreen(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self._main_win = main_win
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        self._count_lbl = make_label('', 12, TEXT_S)
        hdr = make_hbox([
            make_icon_label('trophy', 24), make_label('Achievements', 20, bold=True),
            None, self._count_lbl,
        ])
        layout.addLayout(hdr)

        # Scrollable grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._grid = QGridLayout(self._inner)
        self._grid.setSpacing(10)
        self._grid.setContentsMargins(0, 0, 0, 10)
        scroll.setWidget(self._inner)
        layout.addWidget(scroll)

    def on_enter(self):
        # Clear grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        achs = db.get_achievements()
        unlocked = sum(1 for a in achs if a['unlocked'])
        self._count_lbl.setText(f'{unlocked}/{len(achs)}')

        col, row = 0, 0
        for a in achs:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: {BG_CARD}; border-radius: 10px; border: 1px solid {BORDER};
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(6)

            name_color = TEXT_P if a['unlocked'] else TEXT_M
            icon_ch = a.get('icon', '\u2022')

            top_row = QHBoxLayout()
            icon_lbl = make_label(icon_ch, 18, ACCENT_L if a['unlocked'] else TEXT_M)
            icon_lbl.setFixedSize(28, 28)
            top_row.addWidget(icon_lbl)
            top_row.addWidget(make_label(a['name'], 13, name_color, bold=True))
            if a['unlocked']:
                top_row.addWidget(make_label('\u2705', 14, SUCCESS))
            top_row.addStretch()
            card_layout.addLayout(top_row)

            card_layout.addWidget(make_label(a['desc'], 11, TEXT_S))
            if a['unlocked'] and a.get('ts'):
                card_layout.addWidget(make_label(a['ts'][:10], 10, TEXT_M))

            self._grid.addWidget(card, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
        self._grid.setRowStretch(row, 1)


class SnippetsScreen(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self._main_win = main_win
        self._editing_id = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        hdr = make_hbox([make_icon_label('code', 24), make_label('Snippets', 20, bold=True), None])
        layout.addLayout(hdr)

        # Search + buttons row
        self._search = StyledLineEdit("Search snippets...")
        add_btn = StyledButton("Add", accent=True, icon_text=ICON_MAP.get('plus', ''))
        add_btn.clicked.connect(lambda: self._open_editor(None))
        imp_btn = StyledButton("Import", icon_text=ICON_MAP.get('upload', ''))
        imp_btn.clicked.connect(self._import)
        exp_btn = StyledButton("Export", icon_text=ICON_MAP.get('download', ''))
        exp_btn.clicked.connect(self._export)
        top_row = make_hbox([self._search, None, add_btn, imp_btn, exp_btn])
        layout.addLayout(top_row)

        self._search.textChanged.connect(lambda _: self._refresh())

        # Scrollable list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 10)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch()
        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll)

    def on_enter(self):
        self._refresh()

    def _refresh(self, search_text=None):
        # Clear all but the stretch
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        search = search_text or self._search.text()
        snips = db.get_snippets(search=search) if search else db.get_snippets()
        for s in snips:
            row = QFrame()
            row.setFixedHeight(60)
            row.setStyleSheet(f"""
                QFrame {{
                    background: {BG_CARD}; border-radius: 6px; border: 1px solid {BORDER};
                }}
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 6, 8, 6)
            row_layout.setSpacing(8)
            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)
            info_layout.addWidget(make_label(s['name'], 13, bold=True))
            meta = f"{s['lang']}  |  {s.get('difficulty', '')}"
            info_layout.addWidget(make_label(meta, 11, TEXT_S))
            row_layout.addLayout(info_layout, stretch=1)
            edit_btn = StyledButton("", icon_text=ICON_MAP.get('edit', ''))
            edit_btn.setFixedSize(36, 36)
            sid = s['id']
            edit_btn.clicked.connect(lambda checked, sid=sid: self._open_editor(sid))
            row_layout.addWidget(edit_btn)
            del_btn = StyledButton("", icon_text=ICON_MAP.get('trash', ''))
            del_btn.setFixedSize(36, 36)
            del_btn.clicked.connect(lambda checked, sid=sid: self._del_snippet(sid))
            row_layout.addWidget(del_btn)
            self._list_layout.insertWidget(self._list_layout.count() - 1, row)

    def _del_snippet(self, sid):
        db.delete_snippet(sid)
        self._refresh()

    def _open_editor(self, sid):
        snip = None
        if sid:
            snips = db.get_snippets()
            snip = [s for s in snips if s['id'] == sid]
            snip = snip[0] if snip else None

        dlg = QDialog(self)
        dlg.setWindowTitle('Edit Snippet' if snip else 'Add Snippet')
        dlg.setFixedSize(550, 420)
        dlg.setStyleSheet(f"""
            QDialog {{ background: {BG_MAIN}; color: {TEXT_P}; }}
            QLabel {{ color: {TEXT_P}; background: transparent; }}
            QLineEdit, QTextEdit {{
                background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 8px; padding: 8px; font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {ACCENT}; }}
            QComboBox {{
                background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 8px; padding: 6px 10px; font-size: 13px;
            }}
        """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(make_label('Edit Snippet' if snip else 'Add Snippet', 16, bold=True))

        lang_inp = StyledLineEdit("Language")
        lang_inp.setText(snip['lang'] if snip else 'Python')
        layout.addWidget(lang_inp)

        name_inp = StyledLineEdit("Name")
        name_inp.setText(snip['name'] if snip else '')
        layout.addWidget(name_inp)

        code_inp = QTextEdit()
        code_inp.setPlaceholderText("Code...")
        code_inp.setFont(QFont("monospace", 13))
        code_inp.setText(snip['code'] if snip else '')
        layout.addWidget(code_inp, stretch=1)

        diff_combo = StyledComboBox(['easy', 'medium', 'hard'])
        diff_combo.setCurrentText(snip.get('difficulty', 'medium') if snip else 'medium')
        layout.addWidget(diff_combo)

        btn_row = make_hbox([None,
            StyledButton("Save", accent=True),
            StyledButton("Cancel")])
        layout.addLayout(btn_row)

        # Connect buttons
        for i in range(btn_row.count()):
            w = btn_row.itemAt(i).widget()
            if isinstance(w, StyledButton):
                if w.text() == "Save":
                    def save_snippet():
                        if lang_inp.text() and name_inp.text() and code_inp.toPlainText():
                            if sid:
                                db.update_snippet(sid, lang_inp.text(), name_inp.text(),
                                                  code_inp.toPlainText(), diff_combo.currentText())
                            else:
                                db.add_snippet(lang_inp.text(), name_inp.text(),
                                               code_inp.toPlainText(), diff_combo.currentText())
                            dlg.accept()
                            self._refresh()
                    w.clicked.connect(save_snippet)
                elif w.text() == "Cancel":
                    w.clicked.connect(dlg.reject)

        dlg.exec()

    def _export(self):
        data = db.export_snippets()
        QApplication.clipboard().setText(data)

    def _import(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('Import Snippets')
        dlg.setFixedSize(500, 350)
        dlg.setStyleSheet(f"""
            QDialog {{ background: {BG_MAIN}; color: {TEXT_P}; }}
            QLabel {{ color: {TEXT_P}; background: transparent; }}
            QTextEdit {{
                background: {BG_INPUT}; color: {TEXT_P}; border: 1px solid {BORDER};
                border-radius: 8px; padding: 8px; font-size: 12px;
            }}
        """)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(make_label('Paste JSON below:', 13))
        ti = QTextEdit()
        ti.setPlaceholderText("Paste JSON here...")
        ti.setFont(QFont("monospace", 12))
        layout.addWidget(ti, stretch=1)

        btn_row = make_hbox([None, StyledButton("Import", accent=True), StyledButton("Cancel")])
        layout.addLayout(btn_row)

        for i in range(btn_row.count()):
            w = btn_row.itemAt(i).widget()
            if isinstance(w, StyledButton):
                if w.text() == "Import":
                    def do_import():
                        count = db.import_snippets_json(ti.toPlainText())
                        dlg.accept()
                        self._refresh()
                    w.clicked.connect(do_import)
                elif w.text() == "Cancel":
                    w.clicked.connect(dlg.reject)

        dlg.exec()

class StatsScreen(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self._main_win = main_win
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        hdr = make_hbox([make_icon_label('chart', 24), make_label('Statistics', 20, bold=True), None])
        layout.addLayout(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 20)
        self._inner_layout.setSpacing(10)
        self._inner_layout.addStretch()
        scroll.setWidget(self._inner)
        layout.addWidget(scroll)

    def on_enter(self):
        # Clear old content
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        history = db.get_full_history()
        lang_stats = db.get_lang_stats()
        if not history:
            self._inner_layout.insertWidget(0, make_label('No practice data yet.', 14, TEXT_S))
            return

        overall_wpm = sum(h['wpm'] for h in history) / len(history)
        overall_acc = sum(h['accuracy'] for h in history) / len(history)
        best_wpm = max(h['wpm'] for h in history)
        total_time = sum(h['elapsed'] for h in history)
        total_xp = sum(h['xp'] for h in history)

        # Personal bests card
        bests_card = StyledCard()
        bests_card._layout.setSpacing(4)
        bests_card._layout.addWidget(make_label('Personal Bests', 13, bold=True))
        for label, val in [
            ('Best WPM', str(int(best_wpm))),
            ('Avg WPM', str(round(overall_wpm, 1))),
            ('Avg Accuracy', str(round(overall_acc, 1)) + '%'),
            ('Total Sessions', str(len(history))),
            ('Total Time', str(round(total_time / 60, 1)) + ' min'),
            ('Total XP', str(total_xp)),
        ]:
            row = make_hbox([make_label(label, 12, TEXT_S), None, make_label(val, 12, bold=True)])
            bests_card._layout.addLayout(row)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, bests_card)

        # Language breakdown
        if lang_stats:
            lang_card = StyledCard()
            lang_card._layout.setSpacing(4)
            lang_card._layout.addWidget(make_label('Language Breakdown', 13, bold=True))
            # Header
            hdr = make_hbox([
                make_label('Lang', 10, TEXT_M, bold=True),
                make_label('Count', 10, TEXT_M, bold=True),
                make_label('Avg WPM', 10, TEXT_M, bold=True),
                make_label('Avg Acc', 10, TEXT_M, bold=True),
                make_label('Best', 10, TEXT_M, bold=True),
                make_label('XP', 10, TEXT_M, bold=True),
            ])
            lang_card._layout.addLayout(hdr)
            for ls in lang_stats:
                r = make_hbox([
                    make_label(ls['lang'], 11),
                    make_label(str(ls['cnt']), 11),
                    make_label(str(ls['avg_wpm']), 11),
                    make_label(f"{ls['avg_acc']}%", 11),
                    make_label(str(int(ls['best_wpm'])), 11),
                    make_label(str(ls['total_xp']), 11),
                ])
                lang_card._layout.addLayout(r)
            self._inner_layout.insertWidget(self._inner_layout.count() - 1, lang_card)

        # WPM chart
        chart_card = StyledCard()
        chart_card._layout.setSpacing(4)
        chart_card._layout.addWidget(make_label('Recent WPM (last 10)', 13, bold=True))
        recent = history[:10]
        chart = WpmChartWidget(recent)
        chart_card._layout.addWidget(chart)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, chart_card)


class SettingsScreen(QWidget):
    def __init__(self, main_win, parent=None):
        super().__init__(parent)
        self._main_win = main_win
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        hdr = make_hbox([make_icon_label('settings', 24), make_label('Settings', 20, bold=True), None])
        layout.addLayout(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._inner = QWidget()
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 20)
        self._inner_layout.setSpacing(10)
        self._inner_layout.addStretch()
        scroll.setWidget(self._inner)
        layout.addWidget(scroll)

        self._build_settings()

    def _build_settings(self):
        # Clear old content
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        # Font size card — FIX #6: update practice screen font live
        fs_card = StyledCard()
        fs_card._layout.setSpacing(8)
        fs_card._layout.addWidget(make_label('Appearance', 13, bold=True))
        self._fs_val_lbl = make_label(str(settings['font_size']), 13, ACCENT_L, bold=True)
        fs_row = make_hbox([
            make_label('Font Size', 13),
            None,
            self._fs_val_lbl,
        ])
        fs_card._layout.addLayout(fs_row)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(10, 24)
        slider.setValue(settings['font_size'])
        slider.valueChanged.connect(self._on_fs_change)
        fs_card._layout.addWidget(slider)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, fs_card)

        # Sound card
        snd_card = StyledCard()
        snd_card._layout.setSpacing(8)
        snd_card._layout.addWidget(make_label('Audio', 13, bold=True))
        snd_row = make_hbox([
            make_label('Error Sound', 13),
            None,
            self._make_sound_toggle(settings['sound_enabled']),
        ])
        snd_card._layout.addLayout(snd_row)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, snd_card)

        # Timer mode card
        tmr_card = StyledCard()
        tmr_card._layout.setSpacing(8)
        tmr_card._layout.addWidget(make_label('Timer Mode', 13, bold=True))
        tmr_row = make_hbox([
            make_label('Default Timer', 13),
            None,
            self._make_timer_combo(settings['timer_mode']),
        ])
        tmr_card._layout.addLayout(tmr_row)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, tmr_card)

        # Reset card
        rst_card = StyledCard()
        rst_card._layout.setSpacing(8)
        rst_card._layout.addWidget(make_label('Data', 13, bold=True))
        rst_row = make_hbox([
            make_label('Reset All Progress', 13, ERROR),
            None,
            self._make_reset_button(),
        ])
        rst_card._layout.addLayout(rst_row)
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, rst_card)

    def _on_fs_change(self, val):
        settings['font_size'] = val
        self._fs_val_lbl.setText(str(val))
        # FIX #6: Apply font size change live to the practice screen
        practice = self._main_win._screens.get('practice')
        if practice and hasattr(practice, 'apply_font_size'):
            practice.apply_font_size(val)

    def _make_sound_toggle(self, enabled):
        cb = QCheckBox()
        cb.setChecked(enabled)
        cb.stateChanged.connect(lambda state: settings.__setitem__('sound_enabled', state == Qt.Checked.Value))
        return cb

    def _make_timer_combo(self, current):
        combo = StyledComboBox(['Off', '30s', '60s', '120s'])
        combo.setCurrentText(current)
        combo.currentTextChanged.connect(lambda t: settings.__setitem__('timer_mode', t))
        return combo

    def _make_reset_button(self):
        btn = StyledButton("Reset", icon_text=ICON_MAP.get('trash', ''))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(255,82,82,0.2); color: {ERROR}; border: 1px solid {ERROR};
                border-radius: 6px; padding: 6px 12px; font-size: 13px;
            }}
            QPushButton:hover {{ background: rgba(255,82,82,0.3); }}
        """)
        btn.clicked.connect(self._confirm_reset)
        return btn

    def _confirm_reset(self):
        reply = QMessageBox.question(self, 'Reset Progress',
                                     'Reset all progress?\nThis cannot be undone.',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db.reset_progress()
            self._build_settings()

# === SIDEBAR ===

SIDEBAR_ICONS = [
    ('home', 'Home', 'dashboard'),
    ('keyboard', 'Practice', 'practice'),
    ('trophy', 'Awards', 'achievements'),
    ('code', 'Snippets', 'snippets'),
    ('chart', 'Stats', 'stats'),
    ('settings', 'Config', 'settings'),
]

class SidebarButton(QPushButton):
    def __init__(self, icon_name, label, screen_name, parent=None):
        super().__init__(parent)
        self.screen_name = screen_name
        self._icon_name = icon_name
        self._active = False
        self._label_text = label
        self.setFixedSize(64, 56)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    # FIX #4: Single setStyleSheet call instead of 3 redundant calls
    def _update_style(self):
        if self._active:
            bg = 'rgba(108, 92, 231, 0.25)'
            color = TEXT_P
        else:
            bg = 'transparent'
            color = TEXT_S
        icon_ch = ICON_MAP.get(self._icon_name, '\u2022')
        self.setText(f'{icon_ch}\n{self._label_text}')
        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; border: none; border-radius: 8px;
                padding: 4px; color: {color}; font-size: 10px;
            }}
            QPushButton:hover {{ background: rgba(108, 92, 231, 0.15); }}
        """)

    def set_active(self, val):
        self._active = val
        self._update_style()


# === MAIN WINDOW ===

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Code Typist Pro')
        self.setMinimumSize(1000, 700)
        self.resize(1100, 750)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(76)
        sidebar.setStyleSheet(f"background: {SIDEBAR_BG};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(6, 16, 6, 16)
        sidebar_layout.setSpacing(4)

        # Logo / title
        logo = make_label('\u2328\ufe0f', 20, ACCENT_L)
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedHeight(32)
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(8)

        self._nav_btns = []
        for icon, label, sname in SIDEBAR_ICONS:
            btn = SidebarButton(icon, label, sname)
            btn.clicked.connect(lambda checked, sn=sname: self.switch_screen(sn))
            self._nav_btns.append(btn)
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        # Stacked widget for screens
        self._stack = QStackedWidget()
        self._screens = {}

        # Create screens
        self._screens['dashboard'] = DashboardScreen(self)
        self._screens['practice'] = PracticeScreen(self)
        self._screens['achievements'] = AchievementsScreen(self)
        self._screens['snippets'] = SnippetsScreen(self)
        self._screens['stats'] = StatsScreen(self)
        self._screens['settings'] = SettingsScreen(self)

        for name, screen in self._screens.items():
            self._stack.addWidget(screen)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self._stack, stretch=1)

        # Expose practice_screen for dashboard access
        self.practice_screen = self._screens['practice']

        # Start on dashboard
        self.switch_screen('dashboard')

    def switch_screen(self, name):
        idx_map = {name: i for i, name in enumerate(self._screens.keys())}
        if name not in idx_map:
            return
        self._stack.setCurrentIndex(idx_map[name])
        for btn in self._nav_btns:
            btn.set_active(btn.screen_name == name)
        screen = self._screens[name]
        if hasattr(screen, 'on_enter'):
            screen.on_enter()


# === MAIN ENTRY POINT ===

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(GLOBAL_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
