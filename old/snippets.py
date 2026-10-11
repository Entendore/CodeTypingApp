from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

from database import db
from components import AppCard, AppButton, AppInput, CodeInput, AppSpinner, IconBadge
from theme import *

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