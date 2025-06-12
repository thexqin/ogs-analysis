# OGS Analysis

## Uncover Your Go Game Insights

Welcome to the `ogs-analysis` repository\! This project provides a robust Python-based solution for analyzing your game data from the **Online Go Server (OGS)**. Whether you're a seasoned Go player looking to pinpoint areas for improvement or a data enthusiast interested in applying data analysis and visualization techniques to real-world data, this tool offers valuable insights into your playing habits and performance.

By leveraging the OGS API, this project fetches your game history, processes it with `pandas`, and generates insightful visualizations using `plotly`. It also integrates with **Anvil Uplink** to provide a seamless web-based interface for interacting with your data.

## Features

  * **Comprehensive Data Fetching:** Easily retrieve your ranked game history from the OGS API using efficient, multi-threaded requests.
  * **Data Transformation & Cleaning:** Raw API data is transformed into a clean, structured `pandas` DataFrame, ready for analysis. This includes calculating game durations, win/loss streaks, and converting Elo ratings to standard Go ranks (kyu/dan).
  * **Interactive Visualizations:** Generate dynamic and interactive plots using `plotly` to visualize:
      * **Daily Play Duration:** Understand your playing time distribution and its correlation with wins and losses.
      * **Board Size Preferences:** See how your game duration varies across different board sizes.
      * **Opponent Analysis:** Identify your most frequent opponents and analyze your win/loss records against them.
      * **Game Duration vs. Outcome:** Explore the relationship between game duration and win/loss.
      * **Time of Day Play Patterns:** Discover at what hours you play most frequently.
  * **Anvil Uplink Integration:** A ready-to-use Anvil Uplink server module allows you to expose the analysis functions as callable methods for a web application, providing a user-friendly way to interact with your data without direct code interaction.
  * **Docker Support:** The project includes a `Dockerfile` and `docker-compose.yml` for easy deployment and containerization, ensuring a consistent environment.

## Technologies Used

  * **Python:** The core language for data fetching, processing, and analysis.
  * **Requests:** For interacting with the OGS REST API.
  * **Pandas:** For powerful data manipulation and analysis.
  * **Plotly:** For creating interactive and publication-quality visualizations.
  * **Anvil Uplink:** For connecting the Python backend to a web frontend (not included in this repo but demonstrated in the sample code).
  * **Docker:** For containerization and simplified deployment.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

  * Python 3.8+
  * Docker (optional, for containerized deployment)
  * Anvil account (optional, for web integration)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/thexqin/ogs-analysis.git
    cd ogs-analysis
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Anvil Uplink (if using Anvil):**

      * Rename `.env.example` to `.env`.

      * Add your Anvil Uplink key to the `.env` file:

        ```
        ANVIL_UPLINK_KEY='YOUR_ANVIL_UPLINK_KEY'
        ```

      * You can obtain an Anvil Uplink key from your Anvil app's settings.

## Usage

### Running the Anvil Uplink Server

To make the analysis functions available via Anvil, run the `app.py` file:

```bash
python app.py
```

This will connect your local Python environment to your Anvil app, allowing you to call the `@anvil.server.callable` functions from your Anvil frontend.

### Example Anvil Client-Side Code (Form1.py snippet)

The provided sample `Form1.py` demonstrates how you might interact with the Anvil Uplink functions from an Anvil app:

```python
import anvil.server
import plotly.graph_objects as go
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    Plot.templates.default = 'plotly_dark'

    # Showcase the plots when opening the app
    self.load_id()
    self.plot_id()
    self.plot_nemesis()

  def sync_id_name(self):
    # ... (see sample code for implementation)

  def fetch_id(self):
    # ... (see sample code for implementation)

  def load_id(self):
    # ... (see sample code for implementation)

  def plot_id(self):
    user_id, user_name = self.sync_id_name()
    if user_id:
      self.label_9.text = 'loading...'
      fig1, fig2, fig3 = anvil.server.call('get_plot', user_id)
      # ... (update plot components)

  def plot_nemesis(self):
    user_id, user_name = self.sync_id_name()
    if user_id:
      self.label_9.text = 'loading...'
      fig4, fig5 = anvil.server.call('get_plot_nemesis', user_id)
      fig6 = anvil.server.call('get_plot_time', user_id)
      # ... (update plot components)
```

### Docker Deployment

You can containerize and run the Anvil Uplink server using Docker:

1.  **Build the Docker image:**

    ```bash
    docker build -t ogs-uplink .
    ```

2.  **Run the Docker container using docker-compose:**

    ```bash
    docker-compose up -d
    ```

    Ensure your `.env` file with `ANVIL_UPLINK_KEY` is present in the same directory as your `docker-compose.yml`.

## Project Structure

```
├── frontend/
    ├── Form1.py
    ├── Form2.py
    └── ...
├── backend/
    ├── Dockerfile
    ├── app.py
    ├── docker-compose.yml
    ├── .env.example
    └── requirements.txt
```

### Table `table_db` Schema

This project utilizes an Anvil Data Table named `table_db` to store fetched user data, enabling persistent storage and quicker data retrieval for subsequent analyses.

| Column Name   | Type       | Description                                   |
| :------------ | :--------- | :-------------------------------------------- |
| `user_id`     | `number`   | The unique numerical ID of the OGS user.      |
| `date`        | `datetime` | The timestamp of when the data was last fetched. |
| `user_name`   | `string`   | The username corresponding to `user_id`.      |
| `df_markdown` | `string`   | A Markdown formatted string of the latest game data, suitable for display. |
| `df_csv`      | `string`   | A CSV formatted string of the full game data, stored for later Pandas DataFrame reconstruction. |

## Contributing

Contributions are welcome\! If you have suggestions for improvements, new features, or bug fixes, please open an issue or submit a pull request.

## License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).
