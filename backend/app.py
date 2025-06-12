# -*- coding: utf-8 -*-

# check_list = (r'^(matplotlib|numpy|pandas|seaborn|yfinance|requests|'
# r'beautifulsoup4|plotly|kaleido|google-genai|anvil-uplink|pillow|pytz|'
# r'tabulate|selenium|lxml|html5lib|statsmodels) '
# )
# 
# !pip list | grep -E '{check_list}'

# @title anvil uplink

import os
import anvil.server

ANVIL_UPLINK_KEY = os.environ['ANVIL_UPLINK_KEY']
anvil.server.connect(ANVIL_UPLINK_KEY)

# @title import library & globals

import threading
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import math

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

import datetime
from zoneinfo import ZoneInfo

pio.templates.default = 'plotly_dark'

# global

PAGE_SIZE = 100
LIMIT = 12
DF_ROW = 20
NE_CNT = 10

MAX_WORKER = 10

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0')

URL = ('https://online-go.com/api/v1/players/user_id/games/?'
    'ended__isnull=false&annulled=false&ranked=true&'
    f'ordering=-ended&page_size={PAGE_SIZE}')

"""## 1- fetch"""

# @title overall

# 1 get game, 1200 [], results
# 2 get df, feed the 1200 [], out df
# 3 csv df, for future use
# 4 write everything back to app_tables.table_db

from io import StringIO

import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.media

@anvil.server.callable
def overall(user_id, user_name):
    # id, name, datetime
    ny_now = datetime.datetime.now(ZoneInfo('America/New_York'))

    # raw results
    results, url = get_game(user_id)
    length = len(results)

    # df
    df = get_df(user_id, results)
    df_csv = df.to_csv(index=False)

    # df_markdown
    df2 = df.drop(['game_id', 'ranked', 'annulled', 'opponent_rating', 'started'],
                  axis=1
                  ).copy()
    df2['ended'] = df2['ended'].dt.tz_convert('America/New_York')
    df2['ended'] = df2['ended'].dt.strftime('%Y-%m-%d %H:%M %Z')
    df_markdown= df2.head(DF_ROW).to_markdown(index=False, floatfmt='.1f')

    # write to db
    existing_row = app_tables.table_db.get(user_id=user_id)

    if existing_row:
        new = False
        existing_row.update(user_id=user_id,
                            user_name=user_name,
                            date=ny_now,
                            df_csv=df_csv,
                            df_markdown=df_markdown
                            )
    else:
        new = True
        app_tables.table_db.add_row(user_id=user_id,
                                    user_name=user_name,
                                    date=ny_now,
                                    df_csv=df_csv,
                                    df_markdown=df_markdown
                                    )

    return length, url, new

# internal
def get_csv(user_id):
    row = app_tables.table_db.get(user_id=user_id)

    if row:
        try:
            csv_str = StringIO(row['df_csv'])
            df = pd.read_csv(csv_str, parse_dates=['started', 'ended'])

            df['ended'] = df['ended'].dt.tz_convert('America/New_York')
            df['started'] = df['started'].dt.tz_convert('America/New_York')
            df['day'] = df['ended'].dt.date
            df['day'] = pd.to_datetime(df['day'])

            return df
        except:
            return None
    else:
        return None

# @title game and user

thread_local = threading.local()

# internal
def get_session_for_thread():
    if not hasattr(thread_local, 'session'):
        thread_local.session = requests.Session()
        thread_local.session.headers.update({'User-Agent':UA})
    return thread_local.session

# internal
def get_pool(user_id):

    url = URL.replace('user_id', str(user_id))
    s = get_session_for_thread()

    try:
        with s.get(url) as r:
            r.raise_for_status()
            j = r.json()
            count = j.get('count', 0)
    except requests.exceptions.RequestException as e:
        print(f'RequestException: {e}')
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f'JSONDecodeError: {e}')
        return []

    page = math.ceil(count / PAGE_SIZE)

    if page == 0:
        return []
    elif page < LIMIT:
        return [f'{url}&page={i}' for i in range(1, page+1)]
    else:
        return [f'{url}&page={i}' for i in range(1, LIMIT+1)]

# internal
def get_ogs_per_thread(url):
    s = get_session_for_thread()

    try:
        with s.get(url) as r:
            r.raise_for_status()
            j = r.json()
            return j.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f'RequestException: {e}')
        return []
    except requests.exceptions.JSONDecodeError as e:
        print(f'JSONDecodeError: {e}')
        return []

@anvil.server.callable
def get_game(user_id):

    pool = get_pool(user_id)

    if not pool:
        return [], ''

    all_results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKER) as executor:
        re_iterator = executor.map(get_ogs_per_thread, pool)
        for g in re_iterator:
            all_results.extend(g)

    url_1 = pool[0]
    n = 25
    url_neat = '\n'.join([url_1[i:i+n] for i in range(0, len(url_1), n)])

    return all_results, url_neat

@anvil.server.callable
def get_user_byname(user_name):
    url = f'https://online-go.com/api/v1/players/?username={user_name}'
    s = get_session_for_thread()

    try:
        with s.get(url) as r:
            r.raise_for_status()
            j = r.json()
            if j['count'] == 0:
                return False
            else:
                user_id = j['results'][0]['id']
                return user_id
    except requests.exceptions.RequestException as e:
        print(f'RequestException: {e}')
        return False
    except requests.exceptions.JSONDecodeError as e:
        print(f'JSONDecodeError: {e}')
        return False

@anvil.server.callable
def get_user_byid(user_id):
    url = f'https://online-go.com/api/v1/players/?id={user_id}'
    s = get_session_for_thread()

    try:
        with s.get(url) as r:
            r.raise_for_status()
            j = r.json()
            if j['count'] == 0:
                return False
            else:
                user_name = j['results'][0]['username']
                return user_name
    except requests.exceptions.RequestException as e:
        print(f'RequestException: {e}')
        return False
    except requests.exceptions.JSONDecodeError as e:
        print(f'JSONDecodeError: {e}')
        return False

# @title df and markdown

# internal
def elo_to_rank(rating, min_rating=0, max_rating=2500):
    if not (min_rating <= rating <= max_rating):
        return None

    rating_range = max_rating - min_rating
    num_kyu_ranks = 25
    num_dan_ranks = 7

    rating_per_kyu = rating_range / (num_kyu_ranks + num_dan_ranks - 1)

    # for i, j in enumerate(range(min_rating, max_rating, int(rating_per_kyu))):
    #     print(j)

    lv = round((rating - min_rating) / rating_per_kyu)

    if lv < num_kyu_ranks:
        return str(num_kyu_ranks - lv) + 'k'
    else:
        return str(lv - num_kyu_ranks + 1) + 'd'

# internal
def get_df(user_id, results):
    # array
    game_id = []
    started = []
    ended = []
    annulled = []
    ranked = []

    color = []
    opponent = []
    opponent_rating = []
    opponent_rank = []
    opponent_id = []
    outcome = []

    board = []
    handicap = []

    for item in results:
        # id
        game_id.append(item['id'])

        # date
        started.append(pd.to_datetime(item['started']))
        ended.append(pd.to_datetime(item['ended']))

        # ranked
        ranked.append(item['ranked'])
        annulled.append(item['annulled'])

        # player color
        # opponent color
        if item['black'] == user_id:
            color.append('b')

            opponent.append(item['players']['white']['username'])
            opponent_id.append(item['white'])
            opponent_rating.append(item['players']['white']['ratings']['overall']['rating'])
            opponent_rank.append(elo_to_rank(item['players']['white']['ratings']['overall']['rating']))
        else:
            color.append('w')

            opponent.append(item['players']['black']['username'])
            opponent_id.append(item['black'])
            opponent_rating.append(item['players']['black']['ratings']['overall']['rating'])
            opponent_rank.append(elo_to_rank(item['players']['black']['ratings']['overall']['rating']))

        # outcome
        if item['black_lost'] == False:
            outcome.append('b')
        else:
            outcome.append('w')

        # others
        board.append(item['width'])
        handicap.append(item['handicap'])

    # df
    df = pd.DataFrame({'game_id': game_id,
                    'started': started,
                    'ended': ended,
                    'ranked': ranked,
                    'annulled': annulled,
                    'color': color,
                    'opponent': opponent,
                    'opponent_id': opponent_id,
                    'opponent_rating': opponent_rating,
                    'opponent_rank': opponent_rank,
                    'outcome': outcome,
                    'board': board,
                    'handicap': handicap
                    })

    # clean
    df['win'] = (df['outcome'] == df['color'])

    df['opponent_rating'] = round(df['opponent_rating'], 1)
    df['duration'] = df['ended'] - df['started']
    df['duration_s'] = round(df['duration'].dt.total_seconds(), 1)
    df['duration_m'] = round(df['duration_s'] / 60, 1)

    # have to re-order the df as executor.map is used
    df = df.drop('duration', axis=1)
    df = df.sort_values(by='ended', ascending=False)
    df = df.reset_index(drop=True)

    # streak
    win_streak = 0
    lose_streak = 0

    for index, row in df[::-1].iterrows():
        if row['win'] == True:
            win_streak += 1
            df.loc[index, 'win_streak'] = win_streak
        else:
            win_streak = 0
            df.loc[index, 'win_streak'] = win_streak

        if row['win'] == False:
            lose_streak += 1
            df.loc[index, 'lose_streak'] = lose_streak
        else:
            lose_streak = 0
            df.loc[index, 'lose_streak'] = lose_streak

    df['win_streak'] = df['win_streak'].astype(int)
    df['lose_streak'] = df['lose_streak'].astype(int)

    return df

@anvil.server.callable
def get_df_markdown(user_id):
    row = app_tables.table_db.get(user_id=user_id)

    if row:
        df_markdown = row['df_markdown']
        return df_markdown
    else:
        return 'user not found in db'

# @title plot

@anvil.server.callable
def get_plot(user_id):
    df = get_csv(user_id)

    if df is None:
        return None, None, None
    else:
        df['board'] = df['board'].astype(str)

        df1 = df.groupby(['day','win'])['duration_m'].sum().reset_index()
        df2 = df.groupby(['day', 'board'])['duration_m'].sum().reset_index()
        df3 = df.groupby('day')['duration_m'].sum().reset_index()

        # impossible to have > 1440 duration_m in one day

        df1 = df1[df1['duration_m'] < 1440]
        df2 = df2[df2['duration_m'] < 1440]
        df3 = df3[df3['duration_m'] < 1440]

        fig1 = px.scatter(
            df1,
            x='day',
            y='duration_m',
            color='win',
            size='duration_m',
            size_max=15,
            title = f'{user_id}: duration / date / win or lose',
            width=1500,
            height=400,
            trendline='ols'
        )
        fig2 = px.scatter(
            df2,
            x='day',
            y='duration_m',
            color='board',
            size='duration_m',
            size_max=15,
            title = f'{user_id}: duration / date / board size',
            width=1500,
            height=400,
            trendline='ols'
        )
        fig3 = px.scatter(
            df3,
            x='day',
            y='duration_m',
            size='duration_m',
            size_max=15,
            title = f'{user_id}: duration / date',
            width=1500,
            height=400,
            trendline='ols'
        )

        for trace in fig3.data:
            if 'mode' in trace and trace['mode'] == 'lines':
                trace.line.color = 'lightseagreen'

        fig1.update_layout(
            margin=dict(
                l=15,
                r=10,
                t=35,
                b=10
            )
        )
        fig2.update_layout(
            margin=dict(
                l=15,
                r=10,
                t=35,
                b=10
            )
        )
        fig3.update_layout(
            margin=dict(
                l=15,
                r=10,
                t=35,
                b=10
            )
        )

        return fig1, fig2, fig3

# @title plot nemesis

@anvil.server.callable
def get_plot_nemesis(user_id):
    df = get_csv(user_id)

    if df is None:
        return None, None
    else:
        # not likely to have > 360 duration_m per game
        df = df[df['duration_m'] < 360]

        # nemesis
        dfgroup = df.groupby(['opponent', 'opponent_id', 'opponent_rank', 'board', 'win']).size().reset_index(name='count')
        temp = df.value_counts(subset='opponent').head(NE_CNT).index.to_list()
        nemesis = dfgroup[dfgroup['opponent'].isin(temp)].set_index('opponent').loc[temp].reset_index()
        nemesis['op'] = nemesis['opponent'] + '-' + nemesis['opponent_rank']

        fig1 = px.bar(
            nemesis,
            x='op',
            y='count',
            color='win',
            barmode='group',
            title = f'{user_id}: most played opponent',
            width=1500,
            height=400,
            hover_data=['opponent_id']
        )
        fig2 = px.box(
            df,
            x='duration_m',
            y='win',
            title = f'{user_id}: win or lose / duration',
            width=1500,
            height=400,
            orientation='h',
            color='win'
        )

        fig1.update_layout(
            margin=dict(
                l=15,
                r=10,
                t=35,
                b=10
            )
        )
        fig2.update_layout(
            margin=dict(
                l=15,
                r=10,
                t=35,
                b=10
            )
        )

        return fig1, fig2

# @title time of day histogram

@anvil.server.callable
def get_plot_time(user_id):
    df = get_csv(user_id)

    if df is None:
        return None
    else:
        df['hour'] = df['ended'].dt.hour

        fig = px.histogram(
            df,
            x='hour',
            nbins=24,
            width=1500,
            height=400
        )
        fig.update_layout(
            bargap=0.2,
            margin=dict(
                l=15,
                r=10,
                t=35,
                b=10
            )
        )
        fig.update_xaxes(
            tickvals=list(range(24))
        )

        return fig

# @title anvil wait_forever

anvil.server.wait_forever()