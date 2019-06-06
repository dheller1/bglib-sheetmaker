from kivy.core.window import Window
from kivy.properties import NumericProperty


class ResizableBehavior:
    edge_tolerance = NumericProperty(5)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._resizemode = None
        self._original_rect = None
        Window.bind(mouse_pos=self.on_mouse_pos)

    @property
    def is_resizing(self):
        return self._resizemode is not None and self._original_rect is not None

    def _collided_edges_from_point(self, x, y):
        tol = self.edge_tolerance
        mode = ''
        if abs(y - self.top) <= tol:
            mode += 'n'
        elif abs(y - self.y) <= tol:
            mode += 's'
        if abs(x - self.x) <= tol:
            mode += 'w'
        elif abs(x - self.right) <= tol:
            mode += 'e'
        return mode if mode else None

    def _collide_with_tol(self, x, y):
        tol = self.edge_tolerance
        l, r, t, b = self.x - tol, self.right + tol, self.top + tol, self.y - tol
        return l <= x <= r and b <= y <= t

    def on_mouse_pos(self, *args):
        if self.is_resizing:
            return  # careful not to abort the operation we're currently in

        if not self.get_root_window():
            return  # do proceed if I'm not displayed <=> If have no parent
        pos = args[1]

        # Next line to_widget allow to compensate for relative layout TODO: Also in other callbacks?
        localpos = self.to_widget(*pos)
        if self._collide_with_tol(*localpos):
            self._resizemode = self._collided_edges_from_point(*localpos)
        else:
            self._resizemode = None

        self._adjustcursor()

    def on_touch_move(self, touch):
        if not self.is_resizing:
            return super().on_touch_move(touch)

        l_, b_, r_, t_ = self._original_rect  # original left, btm, right, top
        mode = self._resizemode
        if 'w' in mode:
            self.x = touch.pos[0]
            self.width = r_ - self.x  # initial 'right' minus current 'x'
        elif 'e' in mode:
            # keep old 'x', but adjust width
            self.width = touch.pos[0] - self.x

        if 's' in mode:
            self.y = touch.pos[1]
            self.height = t_ - self.y  # initial top minus current y
        elif 'n' in mode:
            # keep old 'y', but adjust height
            self.height = touch.pos[1] - self.y

    def on_touch_down(self, touch):
        if self._collide_with_tol(*touch.pos) and self._resizemode:
            self._original_rect = (self.x, self.y, self.right, self.top)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._original_rect:
            self._original_rect = None
            return True
        return super().on_touch_up(touch)

    def _adjustcursor(self):
        if self._resizemode in ('nw', 'se'):
            cursor = 'size_nwse'
        elif self._resizemode in ('ne', 'sw'):
            cursor = 'size_nesw'
        elif self._resizemode in ('n', 's'):
            cursor = 'size_ns'
        elif self._resizemode in ('w', 'e'):
            cursor = 'size_we'
        else:
            cursor = 'arrow'
        Window.set_system_cursor(cursor)
