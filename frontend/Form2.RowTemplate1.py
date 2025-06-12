from ._anvil_designer import RowTemplate1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import plotly.graph_objects as go

from datetime import datetime
import anvil.tz

class RowTemplate1(RowTemplate1Template):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    t = TextBox(placeholder='passcode to delete')
    alert(content=t)
    if t.text == '':
      self.item.delete()
      self.parent.items = app_tables.table_db.search(
        tables.order_by('date', ascending=False)
      )
    else:
      alert('invalid passcode')
