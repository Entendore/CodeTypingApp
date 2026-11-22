from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.utils import escape_markup
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.graphics import Color, RoundedRectangle, Line

from theme import *
from icons import VectorIcon

class IconBadge(Widget):
    def __init__(self, icon='home', bg=ACCENT, fg=TEXT_P, badge_size=36, **kw):
        kw.setdefault('size_hint', (None, None)); kw.setdefault('size', (badge_size, badge_size))
        super().__init__(**kw)
        self._bg = list(bg); self._fg = list(fg); self._icon = icon
        self._vec = VectorIcon(icon=icon, color=fg, size=(badge_size*.55, badge_size*.55))
        self.add_widget(self._vec); self.bind(pos=self._layout, size=self._layout)

    def _layout(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg); RoundedRectangle(pos=self.pos, size=self.size, radius=[9])
        self._vec.center = self.center

    def set_icon(self, icon): self._icon = icon; self._vec.icon = icon
    def set_colors(self, bg=None, fg=None):
        if bg: self._bg = list(bg)
        if fg: self._fg = list(fg); self._vec.icolor = list(fg)
        self._layout()

class AppCard(BoxLayout):
    def __init__(self, radius=RAD, bg=BG_CARD, border_color=None, accent_top=None, **kw):
        self._radius = radius; self._bg = list(bg); self._border = border_color; self._accent = accent_top
        super().__init__(**kw); self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg); RoundedRectangle(pos=self.pos, size=self.size, radius=self._radius)
            if self._accent:
                Color(*self._accent); h = 3
                # FIX: Separated pos and size
                RoundedRectangle(pos=(self.x, self.y+self.height-h), size=(self.width, h), radius=[self._radius[0], self._radius[0], 0, 0])
            if self._border:
                Color(*self._border); Line(rounded_rectangle=(*self.pos, *self.size, *self._radius), width=1.0)

class AppButton(Button):
    def __init__(self, text="", icon=None, bg=ACCENT, fg=TEXT_P, radius=RAD, **kw):
        super().__init__(**kw)
        self.text = text; self._bg = list(bg); self._fg = list(fg); self._radius = radius; self._icon_name = icon
        self.background_color = (0,0,0,0); self.color = fg; self.background_normal = ''; self.background_down = ''
        self.padding = [20, 10]; self.bind(state=self._draw, pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        bg = self._bg if self.state == 'normal' else [min(c+.12,1) for c in self._bg[:3]]+[1]
        with self.canvas.before:
            Color(*bg); RoundedRectangle(pos=self.pos, size=self.size, radius=self._radius)
            # FIX: Separated pos and size
            Color(1,1,1,.04); RoundedRectangle(pos=(self.x, self.y+self.height-1), size=(self.width, 1), radius=[0])

class AppInput(TextInput):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = (0,0,0,0); self.foreground_color = TEXT_P; self.cursor_color = ACCENT_L
        self.padding = [15, 12, 15, 12]; self.bind(pos=self._draw, size=self._draw, focus=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear(); border = ACCENT if self.focus else BORDER
        with self.canvas.before:
            Color(*BG_INPUT); RoundedRectangle(pos=self.pos, size=self.size, radius=RAD)
            Color(*border); Line(rounded_rectangle=(*self.pos, *self.size, *RAD), width=1.0)
            if self.focus:
                # FIX: Separated pos and size
                Color(*GLOW); RoundedRectangle(pos=(self.x-2, self.y-2), size=(self.width+4, self.height+4), radius=[12])

class CodeInput(AppInput):
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'tab': self.insert_text('    '); return True
        return super().keyboard_on_key_down(window, keycode, text, modifiers)

class AppSpinner(Spinner):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.background_color = (0,0,0,0); self.color = TEXT_P; self.background_normal = ''
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*BG_INPUT); RoundedRectangle(pos=self.pos, size=self.size, radius=RAD)
            Color(*BORDER); Line(rounded_rectangle=(*self.pos, *self.size, *RAD), width=1.0)
            Color(*TEXT_M); ax = self.x + self.width - 22; ay = self.center_y
            Line(points=[ax-5,ay+3, ax,ay-3, ax+5,ay+3], width=1.2, cap='round', joint='round')

class CodeDisplay(Label):
    target = StringProperty(""); typed = StringProperty("")
    def __init__(self, **kw):
        super().__init__(**kw); self.markup = True; self.bind(texture_size=self._update_height)
    def _update_height(self, inst, val): self.height = val[1]
    def on_target(self, *a): self._refresh()
    def on_typed(self, *a): self._refresh()

    def _refresh(self):
        res = ""
        for i, char in enumerate(self.target):
            e = escape_markup(char)
            if char == '\n': res += '\n'; continue
            if char == '\t': res += '    '; continue
            if i < len(self.typed):
                res += f'[color={C_SUCCESS}]{e}[/color]' if self.typed[i]==char else f'[color={C_ERROR}]{e}[/color]'
            elif i == len(self.typed): res += f'[color={C_TEXT_P}][u]{e}[/u][/color]'
            else: res += f'[color={C_TEXT_M}]{e}[/color]'
        self.text = res

class XPBar(Widget):
    progress = NumericProperty(0)
    def __init__(self, **kw):
        super().__init__(**kw); self.size_hint_y = None; self.height = 10
        self.bind(pos=self._draw, size=self._draw, progress=self._draw)
    def _draw(self, *a):
        self.canvas.clear()
        with self.canvas:
            Color(*BG_DARK); RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
            if self.progress > 0:
                fw = max(self.width * self.progress, 8)
                Color(*ACCENT); RoundedRectangle(pos=self.pos, size=(fw, self.height), radius=[5])
                Color(*ACCENT_L); RoundedRectangle(pos=self.pos, size=(fw, 3), radius=[5,5,0,0])
    def set_data(self, cur, need): self.progress = min(cur / max(need, 1), 1.0)

class NavButton(BoxLayout):
    is_active = BooleanProperty(False)
    def __init__(self, icon='home', label='Home', **kw):
        super().__init__(orientation='horizontal', spacing=12, size_hint_y=None, height=46, **kw)
        self._icon_name = icon; self._label_text = label; self.padding = [8, 5]
        self.badge = IconBadge(icon=icon, bg=BG_CARD, fg=TEXT_M, badge_size=30)
        self.lbl = Label(text=label, font_size='13sp', color=TEXT_S, halign='left', valign='middle')
        self.lbl.bind(size=self.lbl.setter('text_size'))
        self.add_widget(self.badge); self.add_widget(self.lbl)
        self.bind(is_active=self._update, pos=self._update, size=self._update)

    def _update(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.is_active:
                Color(*ACCENT); RoundedRectangle(pos=(self.x, self.y+4), size=(3, self.height-8), radius=[2])
                Color(*hex_to_rgba('#6c5ce7', 0.12)); RoundedRectangle(pos=(self.x+3, self.y+2), size=(self.width-3, self.height-4), radius=[8])
        if self.is_active:
            self.badge.set_colors(bg=ACCENT, fg=TEXT_P); self.lbl.color = TEXT_P; self.lbl.bold = True
        else:
            self.badge.set_colors(bg=BG_CARD, fg=TEXT_M); self.lbl.color = TEXT_S; self.lbl.bold = False

class AchievementPopup(ModalView):
    def __init__(self, achievement, **kw):
        super().__init__(**kw)
        self.size_hint = (None, None); self.size = (420, 130); self.auto_dismiss = True; self.background = ''; self.background_color = (0,0,0,0)
        layout = AppCard(orientation='horizontal', padding=[20,15], spacing=18, radius=RAD_LG, border_color=ACCENT)
        badge = IconBadge(icon='sparkle', bg=ACCENT, fg=TEXT_P, badge_size=48)
        vbox = BoxLayout(orientation='vertical', spacing=2)
        t = Label(text="Achievement Unlocked!", font_size='10sp', color=ACCENT, size_hint_y=None, height=16, halign='left')
        n = Label(text=achievement['name'], font_size='16sp', bold=True, color=TEXT_P, halign='left', size_hint_y=None, height=24)
        d = Label(text=achievement['description'], font_size='12sp', color=TEXT_S, halign='left')
        for l in [t,n,d]: l.bind(size=l.setter('text_size'))
        vbox.add_widget(t); vbox.add_widget(n); vbox.add_widget(d)
        layout.add_widget(badge); layout.add_widget(vbox); self.add_widget(layout)
        Clock.schedule_once(self.dismiss, 3.5)