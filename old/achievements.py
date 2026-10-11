from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from database import db
from components import AppCard, IconBadge
from theme import *

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