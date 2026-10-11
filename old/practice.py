import time
import random
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.properties import StringProperty

from database import db
from game_logic import calc_level, xp_for_level, xp_to_next, calc_xp, check_achievements
from components import AppCard, AppButton, AppInput, CodeInput, AppSpinner, CodeDisplay, XPBar, IconBadge, AchievementPopup
from icons import VectorIcon
from theme import *

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