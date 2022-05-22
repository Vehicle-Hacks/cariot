"""
Created on Sun Mai 22 21:15:00 2022

aws_gui.py
Copyright (C) 2022 Ralph Grewe
  
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class aws_gui(GridLayout):
    def __init__(self, **kwargs):
        super(aws_iot, self).__init__(**kwargs)
        self.cols = 2
        self.gui_status = Label(text='AWS Offline')
        self.gui_status.color = (1,0,0)
        self.add_widget(self.gui_status)
        self.gui_messages = Label(text='message')
        self.add_widget(self.gui_messages)

    def status(self):
        self.gui_status.text = 'AWS Connected'
        self.gui_status.color = (0,1,0)

    def update(self):
            self.gui_messages.text = str(counter)