from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

import kivy.uix.boxlayout
import kivy.uix.floatlayout
import kivy.uix.button
import kivy.uix.image
import kivy.uix.label
import kivy.uix.scatter
import kivy.uix.widget
import kivy.app
from kivy.core.window import Window
from kivy.graphics import Color
import logging
import os
import sys

from kivy.graphics import Rectangle, Line


ScrollDown = 'scrolldown'
ScrollUp = 'scrollup'


def midpoint(pos1, pos2):
    return 0.5 * (pos1[0]+pos2[0]), 0.5 * (pos1[1]+pos2[1])


class SheetImage(kivy.uix.image.Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True


#class SheetWidget(kivy.uix.scatter.Scatter):
class SheetWidget(kivy.uix.floatlayout.FloatLayout):
    RectColor = (.1, .9, .9, .4)
    BorderColor = (.11, .99, .99, 1.)

    def __init__(self, imgpath, slotslabel):
        # allow only scaling(and translation?), no rotation
        super().__init__()  # do_rotation=False, do_translation=True)
        self._img = SheetImage(source=imgpath)
        self.add_widget(self._img)

        self._slotrects = []
        self._slotslabel = slotslabel

    def on_touch_down(self, event):
        if 'ctrl' in Window.modifiers and self.collide_point(*event.pos):
            with self.canvas:
                Color(*SheetWidget.RectColor)
                rect = Rectangle(pos=event.pos, size=(1, 1))
                event.ud['new_rect'] = rect
                event.ud['initial_pos'] = event.pos

                Color(*SheetWidget.BorderColor)
                left = Line(points=list(event.pos), width=1)
                right = Line(points=list(event.pos), width=1)
                top = Line(points=list(event.pos), width=1)
                btm = Line(points=list(event.pos), width=1)
                event.ud['borders'] = left, right, top, btm

        super().on_touch_down(event)

    def on_touch_up(self, event):
        rect = event.ud.get('new_rect')
        if rect:
            self._slotrects.append(rect)
            self._slotslabel.text += '\n(x{:.0f}, y{:.0f}): ({:.0f}x{:.0f}px)'.format(
                rect.pos[0], rect.pos[1], rect.size[0], rect.size[1])
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


class SheetmakerLayout(kivy.uix.boxlayout.BoxLayout):
    pass


class Toolbar(kivy.uix.boxlayout.BoxLayout):
    def __init__(self):
        self.slotslabel = kivy.uix.label.Label(text='Slots:')
        super().__init__(size_hint=(.15, 1.), orientation='vertical')
        self.add_widget(kivy.uix.button.Button(text='Add slot', size_hint=(1., .2)))
        self.add_widget(self.slotslabel)


class SheetmakerApp(kivy.app.App):
    def __init__(self, imgpath):
        super().__init__()
        self._toolbar = Toolbar()
        self._layout = SheetmakerLayout()
        self._layout.add_widget(self._toolbar)
        self._layout.add_widget(SheetWidget(imgpath, slotslabel=self._toolbar.slotslabel))
        #self._sheet_wdg = SheetWidget(imgpath)

    def build(self):
        return self._layout


if __name__ == '__main__':
    if len(sys.argv) > 1:
        imgfile = sys.argv[1]
        if not os.path.isfile(imgfile):
            logging.error('File not found: ' + imgfile)
            sys.exit(1)
        SheetmakerApp(sys.argv[1]).run()
        sys.exit(0)
    else:
        sys.exit(1)
