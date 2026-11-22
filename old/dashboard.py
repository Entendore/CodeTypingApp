from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from database import db
from game_logic import calc_level, xp_for_level, xp_to_next
from components import AppCard, AppSpinner, AppButton, IconBadge, XPBar
from theme import *

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