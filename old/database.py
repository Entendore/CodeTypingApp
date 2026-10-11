import sqlite3
import time
from datetime import datetime, date

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