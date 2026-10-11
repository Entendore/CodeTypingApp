#!/usr/bin/env python3
"""Code Typist – Gamified Code Typing Practice with PySide6"""

import sys
import sqlite3
import time
import math
import random
from datetime import datetime, date

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar, QStackedWidget,
    QGridLayout, QFrame, QScrollArea, QMessageBox, QPlainTextEdit,
    QLineEdit, QDialog, QSizePolicy, QSpacerItem, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QRectF, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QFont, QColor, QPainter, QPalette, QFontMetrics,
    QLinearGradient, QBrush, QPen
)

# ═══════════════════════════════════════════════════════════
# THEME CONSTANTS
# ═══════════════════════════════════════════════════════════
BG_DARK    = '#0f1021'
BG_MAIN    = '#1a1b2e'
BG_CARD    = '#232440'
BG_INPUT   = '#1a1b2e'
ACCENT     = '#7c6aff'
ACCENT_L   = '#9d8aff'
SUCCESS    = '#4ade80'
ERROR      = '#ef4444'
WARNING    = '#fbbf24'
TEXT_P     = '#e2e8f0'
TEXT_S     = '#94a3b8'
TEXT_M     = '#64748b'
BORDER     = '#2d2f55'

DB_PATH = 'code_typist.db'

# ═══════════════════════════════════════════════════════════
# DEFAULT DATA
# ═══════════════════════════════════════════════════════════
DEFAULT_SNIPPETS = [
    ("Python", "Hello World", 'print("Hello, World!")', "easy"),
    ("Python", "Variable Swap", "a, b = b, a", "easy"),
    ("Python", "List Creation", "fruits = ['apple', 'banana', 'cherry']", "easy"),
    ("Python", "For Loop", "for i in range(5):\n    print(i)", "easy"),
    ("Python", "If-Else", "if score >= 90:\n    grade = 'A'\nelif score >= 80:\n    grade = 'B'\nelse:\n    grade = 'C'", "easy"),
    ("Python", "Function Def", "def add(a, b):\n    return a + b", "easy"),
    ("Python", "List Comprehension", "squares = [x**2 for x in range(10)]", "easy"),
    ("Python", "Dict Iteration", "for key, value in data.items():\n    print(f'{key}: {value}')", "medium"),
    ("Python", "Try-Except", "try:\n    result = 10 / x\nexcept ZeroDivisionError:\n    print('Cannot divide by zero')\nfinally:\n    print('Done')", "medium"),
    ("Python", "Class Definition", "class Dog:\n    def __init__(self, name):\n        self.name = name\n\n    def bark(self):\n        return f'{self.name} says woof!'", "medium"),
    ("Python", "File Reading", "with open('data.txt', 'r') as f:\n    content = f.read()\n    lines = content.splitlines()", "medium"),
    ("Python", "Lambda & Map", "doubled = list(map(lambda x: x * 2, numbers))", "medium"),
    ("Python", "Fibonacci", "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)", "medium"),
    ("Python", "Decorator", "def timer(func):\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        end = time.time()\n        print(f'{func.__name__}: {end-start:.2f}s')\n        return result\n    return wrapper", "hard"),
    ("Python", "Generator", "def fibonacci_gen():\n    a, b = 0, 1\n    while True:\n        yield a\n        a, b = b, a + b", "hard"),
    ("Python", "Context Manager", "class ManagedFile:\n    def __init__(self, path):\n        self.path = path\n\n    def __enter__(self):\n        self.file = open(self.path, 'r')\n        return self.file\n\n    def __exit__(self, *exc):\n        self.file.close()", "hard"),
    ("JavaScript", "Console Log", 'console.log("Hello, World!");', "easy"),
    ("JavaScript", "Arrow Function", "const add = (a, b) => a + b;", "easy"),
    ("JavaScript", "Array Map", "const doubled = nums.map(n => n * 2);", "easy"),
    ("JavaScript", "Object Destructure", "const { name, age } = person;", "easy"),
    ("JavaScript", "Async Function", "async function fetchData(url) {\n    const res = await fetch(url);\n    const data = await res.json();\n    return data;\n}", "medium"),
    ("JavaScript", "Class", "class Person {\n    constructor(name, age) {\n        this.name = name;\n        this.age = age;\n    }\n    greet() {\n        return `Hi, I'm ${this.name}`;\n    }\n}", "medium"),
    ("JavaScript", "Promise Chain", "fetch(url)\n    .then(res => res.json())\n    .then(data => processData(data))\n    .catch(err => console.error(err));", "medium"),
    ("C", "Hello World", '#include <stdio.h>\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}', "easy"),
    ("C", "Pointer Swap", "void swap(int *a, int *b) {\n    int temp = *a;\n    *a = *b;\n    *b = temp;\n}", "medium"),
    ("C", "Struct", "typedef struct {\n    char name[50];\n    int age;\n} Person;", "medium"),
    ("Java", "Hello World", 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}', "easy"),
    ("Java", "ArrayList", "ArrayList<String> list = new ArrayList<>();\nlist.add(\"Hello\");\nlist.add(\"World\");\nfor (String s : list) {\n    System.out.println(s);\n}", "medium"),
    ("Rust", "Function", 'fn greet(name: &str) -> String {\n    format!("Hello, {}!", name)\n}', "medium"),
    ("Rust", "Match Expression", "let result = match value {\n    0 => \"zero\",\n    1..=10 => \"small\",\n    _ => \"large\",\n};", "medium"),
    ("Go", "Hello World", 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}', "easy"),
    ("Go", "Goroutine", "go func(msg string) {\n    fmt.Println(msg)\n}(\"Hello from goroutine\")", "medium"),
    ("SQL", "Basic Select", "SELECT * FROM users\nWHERE age > 18\nORDER BY name ASC;", "easy"),
    ("SQL", "Join Query", "SELECT u.name, o.total\nFROM users u\nJOIN orders o ON u.id = o.user_id\nWHERE o.total > 100;", "medium"),
    ("HTML", "Basic Page", "<!DOCTYPE html>\n<html>\n<head>\n    <title>Page</title>\n</head>\n<body>\n    <h1>Hello</h1>\n</body>\n</html>", "easy"),
    ("TypeScript", "Interface", "interface User {\n    id: number;\n    name: string;\n    email?: string;\n}", "easy"),
    ("TypeScript", "Generic Function", "function first<T>(arr: T[]): T | undefined {\n    return arr[0];\n}", "medium"),
]

DEFAULT_ACHIEVEMENTS = [
    ("First Steps",      "Complete your first snippet",         "🎯"),
    ("Speed Demon",      "Reach 40 WPM",                        "⚡"),
    ("Lightning Fingers", "Reach 80 WPM",                       "🔥"),
    ("Perfectionist",    "Get 100% accuracy on a snippet",      "💎"),
    ("Streak Starter",   "Achieve a 3-day streak",              "📅"),
    ("Week Warrior",     "Achieve a 7-day streak",              "💪"),
    ("Ten Down",         "Complete 10 snippets",                "🔟"),
    ("Century",          "Complete 100 snippets",               "💯"),
    ("Level 5",          "Reach level 5",                       "⭐"),
    ("Level 10",         "Reach level 10",                      "🌟"),
    ("Hard Mode",        "Complete a hard snippet",             "🏔️"),
    ("Combo King",       "Reach a 50-character combo",          "👑"),
    ("XP Hunter",        "Earn 1,000 total XP",                 "💰"),
    ("Polyglot",         "Complete snippets in 3+ languages",   "🌍"),
    ("Marathon",         "Complete 5 snippets in one session",  "🏃"),
]

# ═══════════════════════════════════════════════════════════
# DATABASE FUNCTIONS
# ═══════════════════════════════════════════════════════════
def init_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT NOT NULL, title TEXT NOT NULL,
        code TEXT NOT NULL, difficulty TEXT NOT NULL DEFAULT 'medium')''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1,
        current_streak INTEGER DEFAULT 0, best_streak INTEGER DEFAULT 0,
        best_wpm REAL DEFAULT 0, total_snippets INTEGER DEFAULT 0,
        total_xp INTEGER DEFAULT 0, last_active DATE,
        session_count INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, description TEXT NOT NULL,
        icon TEXT DEFAULT '🏆', unlocked INTEGER DEFAULT 0,
        unlocked_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snippet_id INTEGER, language TEXT,
        wpm REAL, accuracy REAL, xp_earned INTEGER,
        combo_max INTEGER, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('INSERT OR IGNORE INTO user_stats (id) VALUES (1)')
    c.execute('SELECT COUNT(*) FROM snippets')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO snippets (language,title,code,difficulty) VALUES (?,?,?,?)', DEFAULT_SNIPPETS)
    c.execute('SELECT COUNT(*) FROM achievements')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO achievements (name,description,icon) VALUES (?,?,?)', DEFAULT_ACHIEVEMENTS)
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    s = dict(conn.execute('SELECT * FROM user_stats WHERE id=1').fetchone())
    conn.close()
    return s

def update_stats(**kw):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for k, v in kw.items():
        c.execute(f'UPDATE user_stats SET {k}=? WHERE id=1', (v,))
    conn.commit()
    conn.close()

def xp_for_level(level):
    return sum(i * 100 for i in range(1, level))

def calc_level(total_xp):
    lv = 1
    while xp_for_level(lv + 1) <= total_xp:
        lv += 1
    return lv

def xp_to_next(level):
    return level * 100

def get_snippets(language=None, difficulty=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    q = 'SELECT * FROM snippets WHERE 1=1'
    p = []
    if language:
        q += ' AND language=?'; p.append(language)
    if difficulty:
        q += ' AND difficulty=?'; p.append(difficulty)
    rows = [dict(r) for r in conn.execute(q, p).fetchall()]
    conn.close()
    return rows

def add_snippet(language, title, code, difficulty):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO snippets (language,title,code,difficulty) VALUES (?,?,?,?)',
                 (language, title, code, difficulty))
    conn.commit()
    conn.close()

def delete_snippet(sid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM snippets WHERE id=?', (sid,))
    conn.commit()
    conn.close()

def get_achievements():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM achievements').fetchall()]
    conn.close()
    return rows

def unlock_achievement(aid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('UPDATE achievements SET unlocked=1, unlocked_at=? WHERE id=?', (datetime.now().isoformat(), aid))
    conn.commit()
    conn.close()

def add_history(snippet_id, language, wpm, accuracy, xp_earned, combo_max):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('INSERT INTO history (snippet_id,language,wpm,accuracy,xp_earned,combo_max) VALUES (?,?,?,?,?,?)',
                 (snippet_id, language, wpm, accuracy, xp_earned, combo_max))
    conn.commit()
    conn.close()

def get_history(limit=20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute('SELECT * FROM history ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()]
    conn.close()
    return rows

def get_completed_languages():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('SELECT DISTINCT language FROM history').fetchall()
    conn.close()
    return [r[0] for r in rows]

def update_streak():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    row = c.execute('SELECT last_active, current_streak, best_streak FROM user_stats WHERE id=1').fetchone()
    today = date.today()
    last_str, cur, best = row
    if last_str:
        last = date.fromisoformat(last_str)
        if last == today:
            conn.close(); return
        elif (today - last).days == 1:
            cur += 1
        else:
            cur = 1
    else:
        cur = 1
    best = max(cur, best)
    c.execute('UPDATE user_stats SET last_active=?, current_streak=?, best_streak=? WHERE id=1',
              (str(today), cur, best))
    conn.commit()
    conn.close()

def calc_xp(difficulty, wpm, accuracy, max_combo):
    base = {'easy': 20, 'medium': 40, 'hard': 60}.get(difficulty, 30)
    speed = max(0, int(wpm - 20))
    acc = 15 if accuracy == 100 else (10 if accuracy >= 95 else (5 if accuracy >= 90 else 0))
    combo = max_combo // 10
    return base + speed + acc + combo

def check_achievements(stats, wpm, accuracy, difficulty, combo, session_count):
    new = []
    langs = get_completed_languages()
    for a in get_achievements():
        if a['unlocked']:
            continue
        ok = False
        n = a['name']
        if n == "First Steps"       and stats['total_snippets'] >= 1:      ok = True
        elif n == "Speed Demon"     and wpm >= 40:                         ok = True
        elif n == "Lightning Fingers" and wpm >= 80:                       ok = True
        elif n == "Perfectionist"   and accuracy == 100:                   ok = True
        elif n == "Streak Starter"  and stats['current_streak'] >= 3:      ok = True
        elif n == "Week Warrior"    and stats['current_streak'] >= 7:      ok = True
        elif n == "Ten Down"        and stats['total_snippets'] >= 10:     ok = True
        elif n == "Century"         and stats['total_snippets'] >= 100:    ok = True
        elif n == "Level 5"         and stats['level'] >= 5:               ok = True
        elif n == "Level 10"        and stats['level'] >= 10:              ok = True
        elif n == "Hard Mode"       and difficulty == 'hard':              ok = True
        elif n == "Combo King"      and combo >= 50:                       ok = True
        elif n == "XP Hunter"       and stats['total_xp'] >= 1000:        ok = True
        elif n == "Polyglot"        and len(langs) >= 3:                   ok = True
        elif n == "Marathon"        and session_count >= 5:                ok = True
        if ok:
            unlock_achievement(a['id'])
            new.append(a)
    return new

# ═══════════════════════════════════════════════════════════
# STYLESHEET
# ═══════════════════════════════════════════════════════════
STYLESHEET = f"""
QMainWindow {{ background: {BG_MAIN}; }}
QWidget {{ color: {TEXT_P}; font-family: 'Segoe UI', sans-serif; font-size: 13px; }}
QFrame#card {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}
QFrame#sidebar {{ background: {BG_DARK}; border-right: 1px solid {BORDER}; }}
QPushButton#nav {{ background: transparent; border: none; border-radius: 8px;
    padding: 10px 16px; text-align: left; font-size: 14px; color: {TEXT_S}; }}
QPushButton#nav:hover {{ background: {BG_CARD}; color: {TEXT_P}; }}
QPushButton#nav:checked {{ background: {ACCENT}; color: white; font-weight: bold; }}
QPushButton#accent {{ background: {ACCENT}; color: white; border: none; border-radius: 8px;
    padding: 10px 20px; font-weight: bold; font-size: 13px; }}
QPushButton#accent:hover {{ background: {ACCENT_L}; }}
QPushButton#small {{ background: {BG_CARD}; color: {TEXT_S}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 6px 14px; font-size: 12px; }}
QPushButton#small:hover {{ background: {BORDER}; color: {TEXT_P}; }}
QPushButton#danger {{ background: #7f1d1d; color: #fca5a5; border: none; border-radius: 6px; padding: 6px 12px; }}
QPushButton#danger:hover {{ background: #991b1b; }}
QComboBox {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 6px;
    padding: 6px 12px; color: {TEXT_P}; min-width: 100px; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{ background: {BG_CARD}; border: 1px solid {BORDER};
    color: {TEXT_P}; selection-background-color: {ACCENT}; }}
QLineEdit, QPlainTextEdit {{ background: {BG_INPUT}; border: 1px solid {BORDER};
    border-radius: 8px; padding: 8px 12px; color: {TEXT_P}; selection-background-color: {ACCENT}; }}
QLineEdit:focus, QPlainTextEdit:focus {{ border-color: {ACCENT}; }}
QProgressBar {{ background: {BG_DARK}; border: none; border-radius: 6px; height: 8px; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 6px; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: {BG_DARK}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QLabel#heading {{ font-size: 22px; font-weight: bold; color: {TEXT_P}; }}
QLabel#subheading {{ font-size: 15px; font-weight: 600; color: {TEXT_P}; }}
QLabel#muted {{ color: {TEXT_M}; font-size: 12px; }}
QLabel#stat_value {{ font-size: 28px; font-weight: bold; color: {ACCENT}; }}
QLabel#badge_easy {{ background: #064e3b; color: #6ee7b7; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
QLabel#badge_medium {{ background: #78350f; color: #fcd34d; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
QLabel#badge_hard {{ background: #7f1d1d; color: #fca5a5; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
QLabel#badge_lang {{ background: {BORDER}; color: {ACCENT_L}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
"""

# ═══════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════
class CodeDisplayWidget(QWidget):
    """Renders code with per-character color coding via QPainter."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target = ""
        self.typed = ""
        self.code_font = QFont("Consolas", 14)
        self.code_font.setStyleHint(QFont.Monospace)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(BG_INPUT))
        self.setPalette(pal)

    def set_text(self, target, typed=""):
        self.target = target
        self.typed = typed
        self.updateGeometry()
        self.update()

    def sizeHint(self):
        fm = QFontMetrics(self.code_font)
        lines = self.target.count('\n') + 1 if self.target else 1
        h = int(lines * fm.height() * 1.8) + 50
        return QSize(0, max(h, 120))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.setFont(self.code_font)
        fm = QFontMetrics(self.code_font)
        lh = fm.height() * 1.8
        margin_l, margin_t = 50, 16

        # Draw background
        p.fillRect(self.rect(), QColor(BG_INPUT))

        # Line numbers
        lines = self.target.split('\n')
        y = margin_t + fm.ascent()
        for i, _ in enumerate(lines):
            p.setPen(QColor(TEXT_M))
            p.drawText(4, int(y), str(i + 1))
            y += lh

        # Characters
        x = margin_l
        y = margin_t + fm.ascent()
        for i, ch in enumerate(self.target):
            if ch == '\n':
                x = margin_l
                y += lh
                continue
            if ch == '\t':
                x += fm.horizontalAdvance(' ') * 4
                continue

            if i < len(self.typed):
                if self.typed[i] == ch:
                    p.setPen(QColor(SUCCESS))
                else:
                    bg = QRectF(x - 1, y - fm.ascent() - 2,
                                fm.horizontalAdvance(ch) + 2, fm.height() + 4)
                    p.fillRect(bg, QColor('#7f1d1d'))
                    p.setPen(QColor(ERROR))
            else:
                if i == len(self.typed):
                    bg = QRectF(x - 1, y - fm.ascent() - 2,
                                fm.horizontalAdvance(ch) + 2, fm.height() + 4)
                    p.fillRect(bg, QColor('#2a2c52'))
                    p.setPen(QColor(TEXT_P))
                else:
                    p.setPen(QColor(TEXT_M))

            p.drawText(int(x), int(y), ch)
            x += fm.horizontalAdvance(ch)

        p.end()


class InputEdit(QPlainTextEdit):
    """Custom input: Tab inserts 4 spaces."""
    tab_pressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Consolas", 14))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.insertPlainText('    ')
            return
        super().keyPressEvent(event)


class XPBarWidget(QWidget):
    """Custom-painted XP progress bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.level = 1
        self.xp_cur = 0
        self.xp_need = 100
        self.setFixedHeight(30)

    def set_data(self, level, xp_cur, xp_need):
        self.level = level
        self.xp_cur = xp_cur
        self.xp_need = max(xp_need, 1)
        self.progress = min(xp_cur / self.xp_need, 1.0)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # BG
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(BG_DARK))
        p.drawRoundedRect(self.rect(), 8, 8)
        # Fill
        if self.progress > 0:
            fw = max(int((self.width() - 4) * self.progress), 8)
            grad = QLinearGradient(0, 0, fw, 0)
            grad.setColorAt(0, QColor(ACCENT))
            grad.setColorAt(1, QColor(ACCENT_L))
            p.setBrush(grad)
            p.drawRoundedRect(2, 2, fw, self.height() - 4, 6, 6)
        # Text
        p.setPen(QColor(TEXT_P))
        p.setFont(QFont('Segoe UI', 9, QFont.Bold))
        txt = f"Lv.{self.level}   {self.xp_cur}/{self.xp_need} XP"
        p.drawText(self.rect(), Qt.AlignCenter, txt)
        p.end()


class NotificationPopup(QFrame):
    """Achievement unlock notification."""
    def __init__(self, achievement, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            QFrame {{ background: {BG_CARD}; border: 2px solid {ACCENT};
            border-radius: 12px; }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 8, 16, 8)
        icon = QLabel(achievement['icon'])
        icon.setFont(QFont('Segoe UI', 28))
        lay.addWidget(icon)
        vl = QVBoxLayout()
        t = QLabel("Achievement Unlocked!")
        t.setFont(QFont('Segoe UI', 9))
        t.setStyleSheet(f"color: {ACCENT};")
        vl.addWidget(t)
        n = QLabel(achievement['name'])
        n.setFont(QFont('Segoe UI', 13, QFont.Bold))
        vl.addWidget(n)
        d = QLabel(achievement['description'])
        d.setStyleSheet(f"color: {TEXT_S}; font-size: 11px;")
        vl.addWidget(d)
        lay.addLayout(vl, 1)

# ═══════════════════════════════════════════════════════════
# DIALOGS
# ═══════════════════════════════════════════════════════════
class ResultsDialog(QDialog):
    def __init__(self, wpm, accuracy, xp_earned, combo_max, level, xp_cur, xp_need, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Results")
        self.setFixedSize(400, 380)
        self.setStyleSheet(f"background: {BG_CARD}; border-radius: 16px;")
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(30, 24, 30, 24)

        t = QLabel("Snippet Complete! 🎉")
        t.setFont(QFont('Segoe UI', 20, QFont.Bold))
        t.setAlignment(Qt.AlignCenter)
        lay.addWidget(t)

        grid = QGridLayout()
        grid.setSpacing(8)
        stats = [
            ("⚡ WPM", f"{wpm:.0f}"),
            ("🎯 Accuracy", f"{accuracy:.1f}%"),
            ("🔥 Max Combo", f"x{combo_max}"),
            ("✨ XP Earned", f"+{xp_earned}"),
        ]
        for i, (label, val) in enumerate(stats):
            l = QLabel(label)
            l.setStyleSheet(f"color: {TEXT_S}; font-size: 13px;")
            v = QLabel(val)
            v.setFont(QFont('Segoe UI', 22, QFont.Bold))
            v.setStyleSheet(f"color: {ACCENT_L};")
            v.setAlignment(Qt.AlignCenter)
            grid.addWidget(l, 0, i)
            grid.addWidget(v, 1, i)
        lay.addLayout(grid)

        lay.addSpacing(8)
        xp_label = QLabel(f"Level {level}  •  {xp_cur}/{xp_need} XP")
        xp_label.setAlignment(Qt.AlignCenter)
        xp_label.setStyleSheet(f"color: {TEXT_S}; font-size: 12px;")
        lay.addWidget(xp_label)
        self.xp_bar = XPBarWidget()
        self.xp_bar.set_data(level, xp_cur, xp_need)
        lay.addWidget(self.xp_bar)

        lay.addSpacing(8)
        btn_lay = QHBoxLayout()
        self.retry_btn = QPushButton("🔄  Retry")
        self.retry_btn.setObjectName("small")
        self.next_btn = QPushButton("➡️  Next Snippet")
        self.next_btn.setObjectName("accent")
        btn_lay.addWidget(self.retry_btn)
        btn_lay.addWidget(self.next_btn)
        lay.addLayout(btn_lay)


class AddSnippetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Snippet")
        self.setFixedSize(500, 440)
        self.setStyleSheet(f"background: {BG_CARD};")
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(24, 20, 24, 20)

        t = QLabel("📝 Add New Snippet")
        t.setFont(QFont('Segoe UI', 18, QFont.Bold))
        lay.addWidget(t)

        lay.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.setEditable(True)
        self.lang_combo.addItems(["Python", "JavaScript", "TypeScript", "Java", "C", "C++",
                                   "Rust", "Go", "SQL", "HTML", "CSS", "Bash", "Ruby", "Swift", "Kotlin"])
        lay.addWidget(self.lang_combo)

        lay.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g. Binary Search")
        lay.addWidget(self.title_edit)

        lay.addWidget(QLabel("Code:"))
        self.code_edit = QPlainTextEdit()
        self.code_edit.setFont(QFont("Consolas", 12))
        self.code_edit.setPlaceholderText("Paste or type the code snippet here...")
        self.code_edit.setMinimumHeight(140)
        lay.addWidget(self.code_edit)

        lay.addWidget(QLabel("Difficulty:"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["easy", "medium", "hard"])
        lay.addWidget(self.diff_combo)

        self.add_btn = QPushButton("✅  Add Snippet")
        self.add_btn.setObjectName("accent")
        self.add_btn.clicked.connect(self.accept)
        lay.addWidget(self.add_btn)

    def get_data(self):
        return (self.lang_combo.currentText().strip(),
                self.title_edit.text().strip(),
                self.code_edit.toPlainText(),
                self.diff_combo.currentText())

# ═══════════════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════════════
class DashboardPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        lay = QVBoxLayout(self)
        lay.setSpacing(16)
        lay.setContentsMargins(32, 28, 32, 28)

        header = QLabel("🏠 Dashboard")
        header.setObjectName("heading")
        lay.addWidget(header)

        # Top cards row
        top = QHBoxLayout()
        top.setSpacing(12)
        self.level_card = self._stat_card("⭐ Level", "1")
        self.streak_card = self._stat_card("🔥 Streak", "0 days")
        self.wpm_card = self._stat_card("⚡ Best WPM", "0")
        self.total_card = self._stat_card("📊 Completed", "0")
        for c in (self.level_card, self.streak_card, self.wpm_card, self.total_card):
            top.addWidget(c)
        lay.addLayout(top)

        # XP Bar
        self.xp_bar = XPBarWidget()
        lay.addWidget(self.xp_bar)

        # Quick Start
        qs = QFrame()
        qs.setObjectName("card")
        qs_lay = QVBoxLayout(qs)
        qs_lay.setContentsMargins(20, 16, 20, 16)
        qs_lay.addWidget(QLabel("Quick Start"))
        hl = QHBoxLayout()
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["All", "easy", "medium", "hard"])
        hl.addWidget(QLabel("Difficulty:"))
        hl.addWidget(self.diff_combo)
        self.lang_combo_dash = QComboBox()
        self.lang_combo_dash.addItem("All")
        self._refresh_langs()
        hl.addWidget(QLabel("Language:"))
        hl.addWidget(self.lang_combo_dash)
        start_btn = QPushButton("⌨️  Start Practice")
        start_btn.setObjectName("accent")
        start_btn.clicked.connect(self._start)
        hl.addWidget(start_btn)
        qs_lay.addLayout(hl)
        lay.addWidget(qs)

        # Recent History
        hist_label = QLabel("Recent Activity")
        hist_label.setObjectName("subheading")
        lay.addWidget(hist_label)
        self.hist_area = QScrollArea()
        self.hist_area.setWidgetResizable(True)
        self.hist_area.setMinimumHeight(160)
        self.hist_widget = QWidget()
        self.hist_layout = QVBoxLayout(self.hist_widget)
        self.hist_layout.setSpacing(6)
        self.hist_layout.addStretch()
        self.hist_area.setWidget(self.hist_widget)
        lay.addWidget(self.hist_area)

        lay.addStretch()
        self.refresh()

    def _stat_card(self, label, value):
        f = QFrame()
        f.setObjectName("card")
        fl = QVBoxLayout(f)
        fl.setContentsMargins(16, 12, 16, 12)
        l = QLabel(label)
        l.setStyleSheet(f"color: {TEXT_S}; font-size: 12px;")
        v = QLabel(value)
        v.setObjectName("stat_value")
        v.setAlignment(Qt.AlignCenter)
        fl.addWidget(l)
        fl.addWidget(v)
        f.value_label = v
        return f

    def _refresh_langs(self):
        self.lang_combo_dash.clear()
        self.lang_combo_dash.addItem("All")
        langs = sorted(set(s['language'] for s in get_snippets()))
        self.lang_combo_dash.addItems(langs)

    def _start(self):
        diff = self.diff_combo.currentText()
        lang = self.lang_combo_dash.currentText()
        self.mw.practice_page.set_filter(
            diff if diff != "All" else None,
            lang if lang != "All" else None
        )
        self.mw.switch_page(1)

    def refresh(self):
        s = get_stats()
        lv = calc_level(s['total_xp'])
        self.level_card.value_label.setText(str(lv))
        self.streak_card.value_label.setText(f"{s['current_streak']} days")
        self.wpm_card.value_label.setText(f"{s['best_wpm']:.0f}")
        self.total_card.value_label.setText(str(s['total_snippets']))
        xp_in_lv = s['total_xp'] - xp_for_level(lv)
        need = xp_to_next(lv)
        self.xp_bar.set_data(lv, xp_in_lv, need)
        self._refresh_langs()

        # History
        for i in reversed(range(self.hist_layout.count() - 1)):
            w = self.hist_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        for h in get_history(10):
            row = QFrame()
            row.setStyleSheet(f"background: {BG_CARD}; border-radius: 8px; padding: 6px 12px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 6, 12, 6)
            lang_l = QLabel(h['language'])
            lang_l.setObjectName("badge_lang")
            rl.addWidget(lang_l)
            info = QLabel(f"WPM: {h['wpm']:.0f}  •  Acc: {h['accuracy']:.1f}%  •  +{h['xp_earned']} XP")
            info.setStyleSheet(f"color: {TEXT_S}; font-size: 12px;")
            rl.addWidget(info, 1)
            ts = QLabel(h['timestamp'][:16] if h['timestamp'] else "")
            ts.setObjectName("muted")
            rl.addWidget(ts)
            self.hist_layout.insertWidget(self.hist_layout.count() - 1, row)


class PracticePage(QWidget):
    snippet_completed = Signal(dict)

    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        self.current_snippet = None
        self.start_time = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.elapsed = 0.0
        self.max_combo = 0
        self.filter_diff = None
        self.filter_lang = None
        self.completed = False

        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(32, 28, 32, 28)

        # Top bar
        top = QHBoxLayout()
        self.info_label = QLabel("No snippet loaded")
        self.info_label.setObjectName("subheading")
        top.addWidget(self.info_label)
        self.timer_label = QLabel("0:00")
        self.timer_label.setFont(QFont('Consolas', 16, QFont.Bold))
        self.timer_label.setStyleSheet(f"color: {ACCENT_L};")
        top.addWidget(self.timer_label)
        lay.addLayout(top)

        # Live stats
        stats_row = QHBoxLayout()
        self.wpm_label = QLabel("WPM: 0")
        self.wpm_label.setFont(QFont('Segoe UI', 13, QFont.Bold))
        self.wpm_label.setStyleSheet(f"color: {ACCENT_L};")
        stats_row.addWidget(self.wpm_label)
        self.acc_label = QLabel("Accuracy: 100%")
        self.acc_label.setFont(QFont('Segoe UI', 13, QFont.Bold))
        self.acc_label.setStyleSheet(f"color: {SUCCESS};")
        stats_row.addWidget(self.acc_label)
        self.combo_label = QLabel("Combo: x0")
        self.combo_label.setFont(QFont('Segoe UI', 13, QFont.Bold))
        self.combo_label.setStyleSheet(f"color: {TEXT_S};")
        stats_row.addWidget(self.combo_label)
        stats_row.addStretch()
        lay.addLayout(stats_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(6)
        lay.addWidget(self.progress_bar)

        # Code display
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        self.code_display = CodeDisplayWidget()
        scroll.setWidget(self.code_display)
        lay.addWidget(scroll, 1)

        # Input
        input_label = QLabel("Type the code below:")
        input_label.setStyleSheet(f"color: {TEXT_S}; font-size: 12px;")
        lay.addWidget(input_label)
        self.input_edit = InputEdit()
        self.input_edit.setMinimumHeight(120)
        self.input_edit.setMaximumHeight(200)
        self.input_edit.textChanged.connect(self._on_text_changed)
        lay.addWidget(self.input_edit)

        # Buttons
        btn_row = QHBoxLayout()
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setObjectName("small")
        self.reset_btn.clicked.connect(self._reset)
        btn_row.addWidget(self.reset_btn)
        self.skip_btn = QPushButton("⏭ Skip")
        self.skip_btn.setObjectName("small")
        self.skip_btn.clicked.connect(self._load_random)
        btn_row.addWidget(self.skip_btn)
        btn_row.addStretch()

        # Filter controls
        btn_row.addWidget(QLabel("Difficulty:"))
        self.diff_filter = QComboBox()
        self.diff_filter.addItems(["All", "easy", "medium", "hard"])
        btn_row.addWidget(self.diff_filter)
        btn_row.addWidget(QLabel("Language:"))
        self.lang_filter = QComboBox()
        self.lang_filter.addItem("All")
        btn_row.addWidget(self.lang_filter)
        random_btn = QPushButton("🎲 Random")
        random_btn.setObjectName("accent")
        random_btn.clicked.connect(self._load_random)
        btn_row.addWidget(random_btn)
        lay.addLayout(btn_row)

        self._refresh_lang_filter()

    def set_filter(self, diff, lang):
        self.filter_diff = diff
        self.filter_lang = lang
        if diff:
            idx = self.diff_filter.findText(diff)
            if idx >= 0:
                self.diff_filter.setCurrentIndex(idx)
        if lang:
            idx = self.lang_filter.findText(lang)
            if idx >= 0:
                self.lang_filter.setCurrentIndex(idx)
        self._load_random()

    def _refresh_lang_filter(self):
        self.lang_filter.clear()
        self.lang_filter.addItem("All")
        langs = sorted(set(s['language'] for s in get_snippets()))
        self.lang_filter.addItems(langs)

    def _load_random(self):
        diff = self.diff_filter.currentText()
        lang = self.lang_filter.currentText()
        snippets = get_snippets(
            language=lang if lang != "All" else None,
            difficulty=diff if diff != "All" else None
        )
        if not snippets:
            QMessageBox.information(self, "No Snippets",
                                    "No snippets found for this filter. Try different filters or add new snippets.")
            return
        self.current_snippet = random.choice(snippets)
        self._reset()

    def _reset(self):
        if not self.current_snippet:
            self._load_random()
            return
        self.completed = False
        self.start_time = None
        self.elapsed = 0.0
        self.max_combo = 0
        self.timer.stop()
        self.timer_label.setText("0:00")
        self.wpm_label.setText("WPM: 0")
        self.acc_label.setText("Accuracy: 100%")
        self.acc_label.setStyleSheet(f"color: {SUCCESS};")
        self.combo_label.setText("Combo: x0")
        self.combo_label.setStyleSheet(f"color: {TEXT_S};")
        self.progress_bar.setValue(0)
        s = self.current_snippet
        diff_color = {'easy': SUCCESS, 'medium': WARNING, 'hard': ERROR}.get(s['difficulty'], TEXT_S)
        self.info_label.setText(
            f"<span style='color:{ACCENT_L}'>{s['language']}</span>  •  "
            f"<span style='color:{diff_color}'>{s['difficulty'].upper()}</span>  •  "
            f"{s['title']}"
        )
        self.code_display.set_text(s['code'])
        self.input_edit.blockSignals(True)
        self.input_edit.clear()
        self.input_edit.blockSignals(False)
        self.input_edit.setFocus()

    def _on_text_changed(self):
        if self.completed or not self.current_snippet:
            return
        typed = self.input_edit.toPlainText()
        target = self.current_snippet['code']

        # Start timer on first keystroke
        if self.start_time is None and len(typed) > 0:
            self.start_time = time.time()
            self.timer.start(100)

        # Calculate stats
        compare_len = min(len(typed), len(target))
        correct = 0
        combo = 0
        cur_combo = 0
        for i in range(compare_len):
            if typed[i] == target[i]:
                correct += 1
                cur_combo += 1
                combo = max(combo, cur_combo)
            else:
                cur_combo = 0
        self.max_combo = max(self.max_combo, combo)

        # Update display
        self.code_display.set_text(target, typed)

        # Progress
        progress = min(int(len(typed) / max(len(target), 1) * 100), 100)
        self.progress_bar.setValue(progress)

        # WPM
        if self.start_time and self.elapsed > 0:
            wpm = (len(typed) / 5) / (self.elapsed / 60)
            self.wpm_label.setText(f"WPM: {wpm:.0f}")

        # Accuracy
        if len(typed) > 0:
            acc = correct / len(typed) * 100
            self.acc_label.setText(f"Accuracy: {acc:.1f}%")
            if acc >= 95:
                self.acc_label.setStyleSheet(f"color: {SUCCESS};")
            elif acc >= 80:
                self.acc_label.setStyleSheet(f"color: {WARNING};")
            else:
                self.acc_label.setStyleSheet(f"color: {ERROR};")

        # Combo display
        combo_text = f"Combo: x{cur_combo}"
        if cur_combo >= 50:
            combo_text += " 🔥🔥"
            self.combo_label.setStyleSheet(f"color: {ERROR}; font-size: 16px;")
        elif cur_combo >= 25:
            combo_text += " 🔥"
            self.combo_label.setStyleSheet(f"color: {WARNING}; font-size: 15px;")
        elif cur_combo >= 10:
            combo_text += " ✨"
            self.combo_label.setStyleSheet(f"color: {SUCCESS};")
        else:
            self.combo_label.setStyleSheet(f"color: {TEXT_S};")
        self.combo_label.setText(combo_text)

        # Check completion
        if len(typed) >= len(target):
            self._complete()

    def _tick(self):
        if self.start_time:
            self.elapsed = time.time() - self.start_time
            m = int(self.elapsed) // 60
            s = int(self.elapsed) % 60
            self.timer_label.setText(f"{m}:{s:02d}")

    def _complete(self):
        self.completed = True
        self.timer.stop()
        if self.start_time:
            self.elapsed = time.time() - self.start_time

        target = self.current_snippet['code']
        typed = self.input_edit.toPlainText()[:len(target)]
        correct = sum(1 for i in range(len(target)) if i < len(typed) and typed[i] == target[i])
        accuracy = correct / len(target) * 100 if target else 0
        wpm = (len(target) / 5) / (self.elapsed / 60) if self.elapsed > 0 else 0

        # XP
        xp = calc_xp(self.current_snippet['difficulty'], wpm, accuracy, self.max_combo)

        # Update DB
        update_streak()
        stats = get_stats()
        new_total_xp = stats['total_xp'] + xp
        new_level = calc_level(new_total_xp)
        new_best_wpm = max(stats['best_wpm'], wpm)
        new_total_snippets = stats['total_snippets'] + 1
        self.mw.session_count += 1

        update_stats(
            total_xp=new_total_xp,
            level=new_level,
            best_wpm=new_best_wpm,
            total_snippets=new_total_snippets,
            xp=xp,
            session_count=self.mw.session_count
        )
        add_history(
            self.current_snippet['id'],
            self.current_snippet['language'],
            wpm, accuracy, xp, self.max_combo
        )

        # Achievements
        updated_stats = get_stats()
        new_achs = check_achievements(updated_stats, wpm, accuracy,
                                       self.current_snippet['difficulty'],
                                       self.max_combo, self.mw.session_count)

        # Show results
        lv = calc_level(new_total_xp)
        xp_in_lv = new_total_xp - xp_for_level(lv)
        need = xp_to_next(lv)
        dlg = ResultsDialog(wpm, accuracy, xp, self.max_combo, lv, xp_in_lv, need, self)
        dlg.retry_btn.clicked.connect(lambda: (dlg.accept(), self._reset()))
        dlg.next_btn.clicked.connect(lambda: (dlg.accept(), self._load_random()))
        dlg.exec()

        # Show achievement notifications
        for a in new_achs:
            self._show_notification(a)

        self.mw.dashboard_page.refresh()

    def _show_notification(self, achievement):
        notif = NotificationPopup(achievement, self.mw)
        notif.setGeometry(
            self.mw.width() // 2 - 200,
            self.mw.height() - 110,
            400, 80
        )
        notif.raise_()
        notif.show()
        QTimer.singleShot(3500, notif.deleteLater)


class AchievementsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        lay = QVBoxLayout(self)
        lay.setSpacing(16)
        lay.setContentsMargins(32, 28, 32, 28)

        header = QLabel("🏆 Achievements")
        header.setObjectName("heading")
        lay.addWidget(header)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet(f"color: {TEXT_S}; font-size: 13px;")
        lay.addWidget(self.count_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.grid_widget)
        lay.addWidget(scroll)

        self.refresh()

    def refresh(self):
        achs = get_achievements()
        unlocked = sum(1 for a in achs if a['unlocked'])
        self.count_label.setText(f"{unlocked}/{len(achs)} unlocked")

        # Clear
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        cols = 3
        for i, a in enumerate(achs):
            card = QFrame()
            card.setObjectName("card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 12, 16, 12)
            cl.setSpacing(4)

            icon = QLabel(a['icon'])
            icon.setFont(QFont('Segoe UI', 28))
            icon.setAlignment(Qt.AlignCenter)
            cl.addWidget(icon)

            name = QLabel(a['name'])
            name.setFont(QFont('Segoe UI', 12, QFont.Bold))
            name.setAlignment(Qt.AlignCenter)
            cl.addWidget(name)

            desc = QLabel(a['description'])
            desc.setObjectName("muted")
            desc.setAlignment(Qt.AlignCenter)
            desc.setWordWrap(True)
            cl.addWidget(desc)

            if a['unlocked']:
                card.setStyleSheet(f"""
                    QFrame#card {{ background: {BG_CARD}; border: 2px solid {ACCENT};
                    border-radius: 12px; }}
                """)
                date_str = a['unlocked_at'][:10] if a['unlocked_at'] else ""
                ul = QLabel(f"✅ Unlocked {date_str}")
                ul.setStyleSheet(f"color: {SUCCESS}; font-size: 10px;")
                ul.setAlignment(Qt.AlignCenter)
                cl.addWidget(ul)
            else:
                card.setStyleSheet(f"""
                    QFrame#card {{ background: {BG_DARK}; border: 1px solid {BORDER};
                    border-radius: 12px; }}
                    QFrame#card QLabel {{ color: {TEXT_M}; }}
                """)

            self.grid_layout.addWidget(card, i // cols, i % cols)


class SnippetsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(32, 28, 32, 28)

        header_row = QHBoxLayout()
        header = QLabel("📝 Snippets")
        header.setObjectName("heading")
        header_row.addWidget(header)
        header_row.addStretch()
        add_btn = QPushButton("➕ Add Snippet")
        add_btn.setObjectName("accent")
        add_btn.clicked.connect(self._add_snippet)
        header_row.addWidget(add_btn)
        lay.addLayout(header_row)

        # Filters
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("All")
        filter_row.addWidget(self.lang_combo)
        filter_row.addWidget(QLabel("Difficulty:"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["All", "easy", "medium", "hard"])
        filter_row.addWidget(self.diff_combo)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("small")
        refresh_btn.clicked.connect(self.refresh)
        filter_row.addWidget(refresh_btn)
        filter_row.addStretch()
        lay.addLayout(filter_row)

        # Scroll area for snippet cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.snippets_widget = QWidget()
        self.snippets_layout = QVBoxLayout(self.snippets_widget)
        self.snippets_layout.setSpacing(8)
        self.snippets_layout.addStretch()
        scroll.setWidget(self.snippets_widget)
        lay.addWidget(scroll)

        self.refresh()

    def refresh(self):
        # Refresh language combo
        current_lang = self.lang_combo.currentText()
        self.lang_combo.clear()
        self.lang_combo.addItem("All")
        langs = sorted(set(s['language'] for s in get_snippets()))
        self.lang_combo.addItems(langs)
        idx = self.lang_combo.findText(current_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

        # Clear cards
        while self.snippets_layout.count():
            item = self.snippets_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        lang = self.lang_combo.currentText()
        diff = self.diff_combo.currentText()
        snippets = get_snippets(
            language=lang if lang != "All" else None,
            difficulty=diff if diff != "All" else None
        )

        if not snippets:
            empty = QLabel("No snippets found. Add one or change filters!")
            empty.setStyleSheet(f"color: {TEXT_M}; font-size: 14px; padding: 40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.snippets_layout.addWidget(empty)
            return

        for s in snippets:
            card = self._snippet_card(s)
            self.snippets_layout.addWidget(card)

        self.snippets_layout.addStretch()

    def _snippet_card(self, s):
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 10, 16, 10)
        cl.setSpacing(4)

        row1 = QHBoxLayout()
        lang_l = QLabel(s['language'])
        lang_l.setObjectName("badge_lang")
        row1.addWidget(lang_l)

        diff_obj = "badge_easy" if s['difficulty'] == 'easy' else (
            "badge_medium" if s['difficulty'] == 'medium' else "badge_hard")
        diff_l = QLabel(s['difficulty'].upper())
        diff_l.setObjectName(diff_obj)
        row1.addWidget(diff_l)

        title_l = QLabel(s['title'])
        title_l.setFont(QFont('Segoe UI', 12, QFont.Bold))
        row1.addWidget(title_l, 1)

        del_btn = QPushButton("🗑")
        del_btn.setObjectName("danger")
        del_btn.setFixedSize(32, 28)
        del_btn.setToolTip("Delete snippet")
        del_btn.clicked.connect(lambda _, sid=s['id']: self._delete(sid))
        row1.addWidget(del_btn)
        cl.addLayout(row1)

        code_preview = s['code'][:120].replace('\n', ' ↵ ')
        if len(s['code']) > 120:
            code_preview += "..."
        code_l = QLabel(code_preview)
        code_l.setFont(QFont("Consolas", 11))
        code_l.setStyleSheet(f"color: {TEXT_M};")
        code_l.setWordWrap(True)
        cl.addWidget(code_l)

        chars_l = QLabel(f"{len(s['code'])} characters")
        chars_l.setObjectName("muted")
        cl.addWidget(chars_l)

        return card

    def _add_snippet(self):
        dlg = AddSnippetDialog(self)
        if dlg.exec() == QDialog.Accepted:
            lang, title, code, diff = dlg.get_data()
            if not title or not code:
                QMessageBox.warning(self, "Validation", "Title and code are required.")
                return
            add_snippet(lang, title, code, diff)
            self.refresh()
            self.mw.practice_page._refresh_lang_filter()

    def _delete(self, sid):
        r = QMessageBox.question(self, "Delete", "Delete this snippet?",
                                 QMessageBox.Yes | QMessageBox.No)
        if r == QMessageBox.Yes:
            delete_snippet(sid)
            self.refresh()


# ═══════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⌨️ Code Typist – Gamified Typing Practice")
        self.setMinimumSize(960, 720)
        self.resize(1100, 780)
        self.session_count = 0

        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setSpacing(0)
        main_lay.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        side_lay = QVBoxLayout(sidebar)
        side_lay.setContentsMargins(12, 16, 12, 16)
        side_lay.setSpacing(4)

        logo = QLabel("⌨️ Code Typist")
        logo.setFont(QFont('Segoe UI', 16, QFont.Bold))
        logo.setStyleSheet(f"color: {ACCENT_L}; padding: 8px;")
        side_lay.addWidget(logo)
        side_lay.addSpacing(8)

        self.nav_buttons = []
        pages = [
            ("🏠  Dashboard", 0),
            ("⌨️  Practice", 1),
            ("🏆  Achievements", 2),
            ("📝  Snippets", 3),
        ]
        for text, idx in pages:
            btn = QPushButton(text)
            btn.setObjectName("nav")
            btn.setCheckable(True)
            btn.setMinimumHeight(42)
            btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            side_lay.addWidget(btn)
            self.nav_buttons.append(btn)

        side_lay.addStretch()

        # XP bar in sidebar
        self.sidebar_xp = XPBarWidget()
        side_lay.addWidget(self.sidebar_xp)

        side_lay.addSpacing(4)
        ver = QLabel("v1.0  •  SQLite + PySide6")
        ver.setObjectName("muted")
        ver.setAlignment(Qt.AlignCenter)
        side_lay.addWidget(ver)

        main_lay.addWidget(sidebar)

        # Stacked pages
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage(self)
        self.practice_page = PracticePage(self)
        self.achievements_page = AchievementsPage(self)
        self.snippets_page = SnippetsPage(self)
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.practice_page)
        self.stack.addWidget(self.achievements_page)
        self.stack.addWidget(self.snippets_page)
        main_lay.addWidget(self.stack, 1)

        self.switch_page(0)

    def switch_page(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)
        # Refresh data when switching pages
        if idx == 0:
            self.dashboard_page.refresh()
        elif idx == 1:
            self.practice_page._refresh_lang_filter()
        elif idx == 2:
            self.achievements_page.refresh()
        elif idx == 3:
            self.snippets_page.refresh()
        # Update sidebar XP
        s = get_stats()
        lv = calc_level(s['total_xp'])
        xp_in = s['total_xp'] - xp_for_level(lv)
        self.sidebar_xp.set_data(lv, xp_in, xp_to_next(lv))


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    init_database()
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # Dark palette fallback
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(BG_MAIN))
    palette.setColor(QPalette.WindowText, QColor(TEXT_P))
    palette.setColor(QPalette.Base, QColor(BG_CARD))
    palette.setColor(QPalette.AlternateBase, QColor(BG_DARK))
    palette.setColor(QPalette.ToolTipBase, QColor(BG_CARD))
    palette.setColor(QPalette.ToolTipText, QColor(TEXT_P))
    palette.setColor(QPalette.Text, QColor(TEXT_P))
    palette.setColor(QPalette.Button, QColor(BG_CARD))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_P))
    palette.setColor(QPalette.BrightText, QColor(ERROR))
    palette.setColor(QPalette.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor(TEXT_P))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()