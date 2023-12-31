#!/usr/bin/python3

import wx
import sys
import random
 

class MyPopupMenu(wx.Menu):

    def __init__(self, parent):
        super(MyPopupMenu, self).__init__()

        self.parent = parent

        ontop_menu = wx.MenuItem(self, wx.ID_ANY, 'Stay on top', kind=wx.ITEM_CHECK)
        self.Append(ontop_menu)
        self.Bind(wx.EVT_MENU, self._on_top, ontop_menu)

        sleep_menu = wx.MenuItem(self, wx.ID_ANY, 'Sleep', kind=wx.ITEM_CHECK)
        self.Append(sleep_menu)
        self.Bind(wx.EVT_MENU, self._on_sleep, sleep_menu)

        quit_menu = wx.MenuItem(self, wx.ID_ANY, 'Quit')
        self.Append(quit_menu)
        self.Bind(wx.EVT_MENU, self._on_quit, quit_menu)

        ontop_menu.Check(check=self.parent.get_stay_on_top())
        sleep_menu.Check(check=self.parent.get_sleeping())

    def _on_quit(self, e):
        self.parent.quit()

    def _on_sleep(self, e):
        self.parent.sleep()

    def _on_top(self, e):
        self.parent.toggle_stay_on_top()


class Frame(wx.Frame):

    _states = {"right": {"img_idx": [0],
                         "repeat_last_images": 1,
                         "next_state": "turn_left",
                         "direction": 1},
               "right_sleep": {"img_idx": [59, 60, 61, 62, 63],
                         "repeat_last_images": 1,
                         "next_state": "right_wakeup",
                         "direction": 0},
               "right_wakeup": {"img_idx": [63, 62, 61, 60, 59],
                         "repeat_last_images": 0,
                         "next_state": "right",
                         "direction": 0},
               "right_bob": {"img_idx": [32, 41, 38, 42, 42, 43, 43, 44, 45, 46, 45, 44, 45, 46, 45, 44, 45, 46, 45, 44, 45, 46, 45, 44, 43, 43, 42, 42, 41, 41],
                         "repeat_last_images": 0,
                         "next_state": "right",
                         "direction": 0},
               "left": {"img_idx": [15],
                        "repeat_last_images": 1,
                        "next_state": "turn_right",
                        "direction": -1},
               "left_sleep": {"img_idx": [64, 65, 66, 67, 68],
                         "repeat_last_images": 1,
                         "next_state": "left_wakeup",
                         "direction": 0},
               "left_wakeup": {"img_idx": [68, 67, 66, 65, 64],
                         "repeat_last_images": 0,
                         "next_state": "left",
                         "direction": 0},
               "left_bob": {"img_idx": [53, 47, 39, 48, 48, 49, 49, 50, 51, 52, 51, 50, 51, 52, 51, 50, 51, 52, 51, 50, 51, 52, 51, 50, 49, 49, 48, 48, 47, 47],
                         "repeat_last_images": 0,
                         "next_state": "left",
                         "direction": 0},
               "turn_left": {"img_idx": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                        "repeat_last_images": 0,
                        "next_state": "left",
                        "direction": 0},
               "turn_right": {"img_idx": [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32],
                        "repeat_last_images": 0,
                        "next_state": "right",
                        "direction": 0}}
    _images = []
    _timer = None
    _duck_pos = 0
    _duck_state = "right"
    _duck_image_idx = 0
    _screen_height = 0
    _screen_width = 0
    _screen_x_offset = 0
    _screen_y_offset = 0
    _sleeping = False
    _target_offset = 0

    def _set_target_offset(self):
        if self._states[self._duck_state]["direction"] == 1:
            self._target_offset = random.randint(self._duck_pos + 10, self._screen_width - self._duck_width)
        elif self._states[self._duck_state]["direction"] == -1:
            self._target_offset = random.randint(0, self._duck_pos - 10)

    def _should_bob(self):
        return random.randint(0, 1000) < 5

    def _load_images(self):
        for i in range(1, 70):
            self._images.append(wx.Image('images/duck{0}.png'.format(i), wx.BITMAP_TYPE_ANY))
        self._duck_height = self._images[0].GetHeight()
        self._duck_width = self._images[0].GetWidth()

    def __init__(self):
        self._load_images()
        self._screen_x_offset, self._screen_y_offset, self._screen_width, self._screen_height = wx.ClientDisplayRect()
        image = self._images[0]
        window_y = self._screen_height - image.GetHeight() + self._screen_y_offset
        wx.Frame.__init__(self,None,title = u"",pos=(self._screen_x_offset, window_y),size=(self._screen_width,image.GetHeight()),style=wx.SIMPLE_BORDER|wx.TRANSPARENT_WINDOW|wx.STAY_ON_TOP)
        self.SetTransparent(100)

        self.panel = wx.Panel(self)
        self.panel.SetTransparent(100)
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
        self._imageBitmap = wx.StaticBitmap(self.panel, wx.ID_ANY, wx.Bitmap(image))

        self.panel.Bind(wx.EVT_RIGHT_DOWN, self._on_right_down)

        self._set_target_offset()
        self._timer = wx.Timer(self, 1)
        self.Bind(wx.EVT_TIMER, self._on_timer_event)
        self._timer.Start(50)
        
    def quit(self):
        self.Destroy()

    def sleep(self):
        self._sleeping = not self._sleeping

    def get_sleeping(self):
        return self._sleeping

    def toggle_stay_on_top(self):
        self.ToggleWindowStyle(wx.STAY_ON_TOP)

    def get_stay_on_top(self):
        return self.HasFlag(wx.STAY_ON_TOP)

    def _on_right_down(self, event):
        self.PopupMenu(MyPopupMenu(self), event.GetPosition())

    def _on_timer_event(self, event):
        new_duck_state = None
        state = self._states[self._duck_state]
        self._duck_pos = self._duck_pos + state["direction"] * 2

        try:
            new_image = self._images[state["img_idx"][self._duck_image_idx]]
            image_height = new_image.GetHeight()
            self._imageBitmap.SetBitmap(wx.Bitmap(new_image))
        except:
            print("oops")
            print(sys.exc_info())
            sys.exit(1)
        self._imageBitmap.Refresh()
        self._imageBitmap.SetPosition((self._duck_pos, self._duck_height - image_height))
        self._duck_image_idx += 1
        if self._duck_image_idx == len(state["img_idx"]) and state["repeat_last_images"] > 0:
            self._duck_image_idx -= state["repeat_last_images"]
        if self._duck_image_idx == len(state["img_idx"]):
            new_duck_state = state["next_state"]
        elif self._duck_state == "right":
            if self._duck_pos > self._target_offset:
                new_duck_state = state["next_state"]
            elif self._sleeping:
                new_duck_state = "right_sleep"
            elif self._should_bob():
                new_duck_state = "right_bob"
        elif self._duck_state == "right_sleep" and not self._sleeping:
            new_duck_state = state["next_state"]
        elif self._duck_state == "left":
            if self._duck_pos < self._target_offset:
                new_duck_state = state["next_state"]
            elif self._sleeping:
                new_duck_state = "left_sleep"
            elif self._should_bob():
                new_duck_state = "left_bob"
        elif self._duck_state == "left_sleep" and not self._sleeping:
            new_duck_state = state["next_state"]

        if new_duck_state:
            self._duck_state = new_duck_state
            self._duck_image_idx = 0
            self._set_target_offset()


if __name__ == "__main__":
    app = wx.App()
    frame = Frame()
    frame.Show()
    app.MainLoop()
