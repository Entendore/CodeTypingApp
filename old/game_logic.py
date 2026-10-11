from database import db

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