from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

import kivy.uix.boxlayout
import kivy.uix.floatlayout
from kivy.uix.button import Button
import kivy.uix.image
from kivy.uix.label import Label
import kivy.uix.scatter
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ToggleButtonBehavior, DragBehavior
import kivy.app
from kivy.core.window import Window
from kivy.graphics import Color
from kivy.uix.recycleview import RecycleView
from kivy.properties import ObjectProperty, BooleanProperty
from bglib.sheetmaker.behaviors import ResizableBehavior
import logging
import os
import sys

from kivy.graphics import Rectangle, Line


ScrollDown = 'scrolldown'
ScrollUp = 'scrollup'


class SheetmakerModel:
    def __init__(self):
        self.slots = []



def midpoint(pos1, pos2):
    return 0.5 * (pos1[0]+pos2[0]), 0.5 * (pos1[1]+pos2[1])


class LabelListView(RecycleView):
    pass
    #def __init__(self, **kwargs):
    #    super().__init__(**kwargs)
    #    self.data = [{'text': str(x)} for x in range(100)]


class KeyboardListenerMixin(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        if keycode[1] == 'escape':
            keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True


class SheetImage(kivy.uix.image.Image, KeyboardListenerMixin):
    RectColor = (.8, .9, .2, .4)
    BorderColor = (.8, .9, .2, 1.)

    slot_list = ObjectProperty(None)

    @property
    def selection(self):
        return [c for c in self.children if isinstance(c, SlotFrame) and c.is_selected]

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'delete':
            print('Removing', self.selection)
            self.clear_widgets(self.selection)

    def on_touch_down(self, event):
        if 'ctrl' in Window.modifiers and self.collide_point(*event.pos):
            with self.canvas:
                Color(*SheetImage.RectColor)
                rect = Rectangle(pos=event.pos, size=(1, 1))
                event.ud['new_rect'] = rect
                event.ud['initial_pos'] = event.pos

                Color(*SheetImage.BorderColor)
                left = Line(points=list(event.pos), width=1)
                right = Line(points=list(event.pos), width=1)
                top = Line(points=list(event.pos), width=1)
                btm = Line(points=list(event.pos), width=1)
                event.ud['borders'] = left, right, top, btm
            return False
        return super().on_touch_down(event)

    def on_touch_up(self, event):
        rect = event.ud.get('new_rect')
        if rect:
            self.canvas.remove(rect)
            for border in event.ud['borders']:
                self.canvas.remove(border)

            self.add_widget(SlotFrame(size=rect.size, pos=rect.pos))

            if self.slot_list:
                self.slot_list.data.append({'text':str(SlotFrame)})

        super().on_touch_up(event)

    def on_touch_move(self, event):
        rect = event.ud.get('new_rect')
        if rect:
            initpos = event.ud['initial_pos']
            curpos = event.pos
            w, h = rect.size = abs(curpos[0] - initpos[0]), abs(curpos[1] - initpos[1])
            newcenter = midpoint(curpos, initpos)
            rect.pos = newcenter[0] - w/2, newcenter[1] - h/2

            l, r, t, b = event.ud['borders']
            rleft = newcenter[0] - 0.5 * rect.size[0]
            rright = newcenter[0] + 0.5 * rect.size[0]
            rtop = newcenter[1] + 0.5 * rect.size[1]
            rbottom = newcenter[1] - 0.5 * rect.size[1]
            l.points = (rleft, rtop, rleft, rbottom)
            r.points = (rright, rtop, rright, rbottom)
            t.points = (rleft, rtop, rright, rtop)
            b.points = (rleft, rbottom, rright, rbottom)

        for c in self.children:
            c.on_touch_move(event)


class SlotFrame(ResizableBehavior, DragBehavior, ToggleButtonBehavior, Widget):
    is_selected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_state(self, _, value):
        self.is_selected = (value == 'down')
        print('current selection', self.parent.selection)


"""class Toolbar(kivy.uix.boxlayout.BoxLayout):
    def __init__(self):
        self.slotslabel = kivy.uix.label.Label(text='Slots:')
        super().__init__(size_hint=(.15, 1.), orientation='vertical')
        self.add_widget(kivy.uix.button.Button(text='Add slot', size_hint=(1., .2)))
        self.add_widget(self.slotslabel)"""


class RootWidget(Widget):
    pass


class SheetmakerApp(kivy.app.App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = SheetmakerModel()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        imgfile = sys.argv[1]
        if not os.path.isfile(imgfile):
            logging.error('File not found: ' + imgfile)
            sys.exit(1)
        SheetmakerApp().run()
        sys.exit(0)
    else:
        sys.exit(1)
