import bokeh.layouts as bl
import bokeh.models as bm
import bokeh.plotting as bp
import datetime as dt
import numpy as np
import pandas as pd
from pathlib import Path

data_path = Path.cwd() / '../data'

columns = ['time', 'open', 'close', 'high', 'low', 'volume']
candles = {col: [] for col in columns}

for filename in sorted(list(data_path.glob('SSO_15*'))):
    o = pd.read_csv(filename)
    o = o.set_index(pd.DatetimeIndex(o['time']))
    freq = pd.Timedelta(hours=1)
    g = o.groupby(pd.Grouper(freq=freq))
    for name, group in g:
        if group.values.size != 0:
            open_v, close_v = group.price[-1], group.price[0]
            high_v, low_v = group.price.agg([np.max, np.min])
            vol_v = group.volume.sum()
            candles["time"].append((name).strftime('%H:%M %d/%m-%y'))
            candles["open"].append(open_v)
            candles["close"].append(close_v)
            candles["high"].append(high_v)
            candles["low"].append(low_v)
            candles["volume"].append(vol_v)
        else:
            candles["time"].append(None)
            candles["open"].append(None)
            candles["close"].append(None)
            candles["high"].append(None)
            candles["low"].append(None)
            candles["volume"].append(None)


num_points = len(candles['time'])
cf = pd.DataFrame(data=candles, columns=columns, index=list(range(num_points)))
freq = 0.5
inc = cf.close > cf.open
dec = cf.open > cf.close

#use ColumnDataSource to pass in data for tooltips
source_inc=bm.ColumnDataSource(bm.ColumnDataSource.from_df(cf.loc[inc]))
source_dec=bm.ColumnDataSource(bm.ColumnDataSource.from_df(cf.loc[dec]))

hover = bm.HoverTool(
    tooltips=[
        ('date', '@time'),
        ('open', '@open'),
        ('close', '@close'),
        ('high', '@high'),
        ('low', '@low'),
        ('volume', '@volume')
    ]
)

TOOLS = ["pan,wheel_zoom,box_zoom,reset,save", bm.CrosshairTool(), hover]

candles = bp.figure(
    tools=TOOLS,
    plot_height=750,
    plot_width=2000,
    title="NEL 30 minutes",
)
volume = bp.figure(
    x_range=candles.x_range,
    tools=TOOLS,
    plot_height=250,
    plot_width=2000,
    title="NEL volume",
)
candles.segment(cf.index, cf.high, cf.index, cf.low, color="black")
candles.vbar(
    x='index', # cf.time[inc],
    width=freq,
    top='open', # cf.open[inc],
    bottom='close', # cf.close[inc],
    fill_color="#D5E1DD",
    line_color="black",
    source=source_inc
)
candles.vbar(
    x='index', # cf.time[dec],
    width=freq,
    top='open',  # cf.open[dec],
    bottom='close',  # cf.close[dec],
    fill_color="#F2583E",
    line_color="black",
    source=source_dec
)
volume.vbar(x=cf.index, width=freq, bottom=cf.volume*0, top=cf.volume, fill_color="blue")
date_labels = [date.strftime('%d/%m-%y') for date in pd.to_datetime(cf.time)]
candles.xaxis.major_label_overrides = {i: d for i, d in enumerate(date_labels)}
volume.xaxis.major_label_overrides = {i: d for i, d in enumerate(date_labels)}
layout = bl.layout(candles, volume)

bp.output_file("NEL.html", title="NEL 1h")

bp.show(layout)  # open a browser
