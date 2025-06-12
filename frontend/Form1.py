from ._anvil_designer import Form1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go

from datetime import datetime
import anvil.tz

class Form1(Form1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # material_light, material_dark rally_light, rally_dark, mykonos_light, mykonos_dark, manarola_light， manarola_dark
    # plotly, plotly_white, plotly_dark, presentation, ggplot2, seaborn, simple_white, gridon, xgridoff, ygridoff
    # Any code you write here will run before the form opens.
    Plot.templates.default = 'plotly_dark'

    # showcase the plots when opening the app
    self.load_id()
    self.plot_id()
    self.plot_nemesis()

  def sync_id_name(self):
    try:
      # 1. check if it's int
      user_id = int(self.text_box_1.text.strip())

      # 2. check on server if id is valid
      user_name = anvil.server.call('get_user_byid', user_id)

      if user_name:
        # 3. success
        self.label_8.text = user_name
        return user_id, user_name
      else:
        # if 2. failed
        alert('invalid user id')
        self.text_box_1.text = 1596956
        return False, False
    except Exception as e:
      # 1. int() failed
      alert(e)
      self.text_box_1.text = 1596956
      return False, False
    
  def fetch_id(self):
    user_id, user_name = self.sync_id_name()

    # id and name ok
    if user_id:
      self.label_6.text = 'fetching...'
  
      # actual fetch
      length, url, new = anvil.server.call('overall', user_id, user_name)
  
      self.label_2.text = f'fetched: {length} games'
      self.label_4.text = url

      if new:
        self.label_6.text = 'new record inserted'
      else:
        self.label_6.text = 'user found, record updated'
        
      # done
      alert('fetch completed')

  def load_id(self):
    user_id, user_name = self.sync_id_name()

    # id and name ok
    if user_id:
      self.label_7.text = 'loading...'

      df_markdown = anvil.server.call('get_df_markdown', user_id)

      self.rich_text_1.content = df_markdown
      self.label_7.text = 'loaded'

  def plot_id(self):
    user_id, user_name = self.sync_id_name()

    # id and name ok
    if user_id:
      self.label_9.text = 'loading...'
      fig1, fig2, fig3 = anvil.server.call('get_plot', user_id)

      if fig1 is None:
        self.label_9.text = 'user not found in db'
      else:
        self.plot_1.figure = fig1
        self.plot_1.visible = True
        self.plot_2.figure = fig2
        self.plot_2.visible = True
        self.plot_3.figure = fig3
        self.plot_3.visible = True
        
        self.label_9.text = 'plotted'
  
  def plot_nemesis(self):
    user_id, user_name = self.sync_id_name()

    # id and name ok
    if user_id:
      self.label_9.text = 'loading...'
      fig4, fig5 = anvil.server.call('get_plot_nemesis', user_id)
      fig6 = anvil.server.call('get_plot_time', user_id)
      
      if fig4 is None:
        self.label_9.text = 'user not found in db'
      else:
        self.plot_4.figure = fig4
        self.plot_4.visible = True
        self.plot_5.figure = fig5
        self.plot_5.visible = True
        self.plot_6.figure = fig6
        self.plot_6.visible = True
        
        self.label_9.text = 'plotted'

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.fetch_id()
    
  def text_box_1_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    self.fetch_id()

  def button_2_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.load_id()

  def button_3_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.plot_id()

  def link_1_click(self, **event_args):
    """This method is called when the link is clicked"""
    open_form('Form2')

  def button_4_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.plot_nemesis()