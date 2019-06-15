import logging
import time
from logging import getLogger, StreamHandler, Formatter, FileHandler
from pathlib import Path

import numpy as np
import pandas as pd
import pandas.tseries.offsets as offsets
import schedule
from bokeh.layouts import Column
from bokeh.models import RangeTool
from bokeh.plotting import figure, output_file, save, show

import conf

logger = getLogger(Path(__file__).name)
logger.setLevel(logging.DEBUG)

stream_handler = StreamHandler()
stream_handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

file_handler = FileHandler('log/analyze.log')
file_handler.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if not Path('log').exists():
    Path('log').mkdir()


def exec_per_minute(job, *args, **kwargs):
    schedule.every().minutes.do(job, *args, **kwargs)


def draw_graph(product_code):
    logger.debug(f"start draw chart: {product_code}")
    figure_width = 1200

    df = pd.read_csv(f'data/{product_code}.tsv', names=('timestamp', 'price', 'latency'), sep='\t')
    df['timestamp'] = pd.to_datetime(df.timestamp, unit='s')
    df['timestamp'] = df['timestamp'] + offsets.timedelta(hours=9)  # offset "+09:00"
    df = df.set_index('timestamp')

    latency = df['latency'].resample('T').max()
    ohlc = df['price'].resample('T').ohlc()

    short = ohlc['close'].rolling(5).mean()
    mid = ohlc['close'].rolling(25).mean()
    long = ohlc['close'].rolling(50).mean()
    std = ohlc['close'].rolling(25).std()

    upper = mid + (std * 2)
    lower = mid - (std * 2)

    df = pd.concat([latency, ohlc , short, mid, long, std, upper, lower], axis=1)
    df.columns = ('latency', 'open', 'high', 'low', 'close', 'short', 'mid', 'long', 'std', 'upper', 'lower')



    if len(df) > 2000:
        df = df[-2000:]  # 後ろから2000行までを使用する

    df.to_csv(f'data/{product_code}.resample.tsv', sep='\t')

    upper_band = df['upper'].fillna(100000000) < df['high']
    lower_band = df['lower'].fillna(0)         > df['low']

    inc = df['close'] > df['open']
    dec = df['open'] > df['close']
    w = 60 * 1000  # 1 minutes

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    start_range = -300 if len(df) > 300 else -len(df)
    p = figure(x_axis_type="datetime",
               tools=TOOLS,
               plot_width=figure_width,
               x_range=(df.index[start_range], df.index[-1]),
               toolbar_location="above",
               title=product_code)

    p.xaxis.major_label_orientation = np.pi / 4
    p.grid.grid_line_alpha = 0.3

    # ローソク足
    p.segment(df.index, df['high'], df.index, df['low'], color="black")
    p.vbar(df.index[inc], w, df['open'][inc], df['close'][inc], fill_color="#D5E1DD", line_color="black", legend="増加")
    p.vbar(df.index[dec], w, df['open'][dec], df['close'][dec], fill_color="#F2583E", line_color="black", legend="減少")

    # 移動平均線
    p.line(df.index, df.short, color='orange', legend='5分平均線')
    p.line(df.index, df.mid, color='red', legend='25分平均線')
    p.line(df.index, df.long, color='blue', legend='50分平均線')

    # ボリンジャーバンド
    p.line(df.index, df.upper, color='black', legend='ボリンジャーバンド')
    p.line(df.index, df.lower, color='black')

    # バンドブレイク
    p.cross(df.index[upper_band], df[upper_band]['high'], size=20, color="red", line_width=1, legend="アッパーブレイク")
    p.cross(df.index[lower_band], df[lower_band]['low'], size=20, color="blue", line_width=1, legend="アンダーブレイク")

    # ボリンジャーバンド幅グラフ
    p_bb = figure(x_axis_type="datetime",
                  tools=TOOLS,
                  plot_height=150,
                  plot_width=figure_width,
                  x_range=p.x_range,
                  toolbar_location=None,
                  title="BB Width")
    p_bb.line(df.index, (df['upper'] - df['lower']).fillna(0), color='black')

    # レイテンシーグラフ
    p_ltc = figure(x_axis_type='datetime',
                   plot_height=150,
                   plot_width=figure_width,
                   x_range=p.x_range,
                   toolbar_location=None,
                   title="API Latency")
    p_ltc.vbar(df.index, w, 0, df['latency'], fill_color='green', line_color="black")

    # レンジツールチャート
    p_range = figure(x_axis_type='datetime',
                     plot_height=300,
                     plot_width=figure_width,
                     y_range=p.y_range,
                     toolbar_location=None)
    p_range.line(df.index, df['close'], line_color="black")

    range_tool = RangeTool(x_range=p.x_range)
    p_range.add_tools(range_tool)

    # htmlファイル出力
    output_file(f'static/chart/{product_code}.html', title=product_code)

    save(Column(p, p_bb, p_ltc, p_range))
    # show(Column(p, p_bb, p_ltc, p_range))  # open a browser


def main():
    for product in conf.product_code_list:
        exec_per_minute(draw_graph, product)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
