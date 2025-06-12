from ._anvil_designer import Form2Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go

from datetime import datetime
import anvil.tz

class Form2(Form2Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
    self.reset_db()

  def reset_db(self):
    self.repeating_panel_1.items = app_tables.table_db.search(
      tables.order_by('date', ascending=False)
    )
    self.label_2.text = self.data_grid_1.get_page() + 1

  def sync_id_name(self):
    try:
      # 1. check if it's int
      user_id = int(self.text_box_1.text.strip())

      # 2. check on server if id is valid
      user_name = anvil.server.call('get_user_byid', user_id)

      if user_name:
        # 3. success
        self.text_box_2.text = user_name
        alert('user found')
        self.button_6.enabled = True
      else:
        # if 2. failed
        alert('invalid user id')
        self.text_box_1.text = 1596956
    except Exception as e:
      # 1. int() failed
      alert(e)
      self.text_box_1.text = 1596956

  def search_user(self):
    # 1 if text_box_1 is empty
    # check text_box_2
    if self.text_box_1.text.strip() == '':
      user_name = self.text_box_2.text.strip()
      user_id = anvil.server.call('get_user_byname', user_name)

      if user_id:
        self.text_box_1.text = user_id
        alert('user found')
        self.button_6.enabled = True
      else:
        alert('invalid user name')
        self.text_box_1.text = 1596956

    # 2 if text_box_1 is not empty
    else:
      self.sync_id_name()

  def get_db(self):
    user_id = int(self.text_box_1.text.strip())

    row = app_tables.table_db.get(user_id=user_id)

    if row:
      self.repeating_panel_1.items = [row]
      self.label_2.text = self.data_grid_1.get_page() + 1
    else:
      alert('user not found in db')

    self.button_6.enabled = False

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.search_user()

  def text_box_1_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.search_user()
    
  def link_1_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form("Form1")

  def button_3_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.data_grid_1.next_page()
    self.label_2.text = self.data_grid_1.get_page() + 1

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.data_grid_1.previous_page()
    self.label_2.text = self.data_grid_1.get_page() + 1

  def button_4_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.data_grid_1.jump_to_first_page()
    self.label_2.text = self.data_grid_1.get_page() + 1

  def button_5_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.data_grid_1.jump_to_last_page()
    self.label_2.text = self.data_grid_1.get_page() + 1

  def button_6_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.get_db()

  def button_7_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.reset_db()