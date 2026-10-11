from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

from theme import *
from components import *
from icons import VectorIcon
from dashboard import DashboardScreen
from practice import PracticeScreen
from achievements import AchievementsScreen
from snippets import SnippetsScreen

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