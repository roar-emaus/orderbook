import bokeh.plotting as bp
import bokeh.layouts as bl
import numpy as np
import pandas as pd
import datetime as dt

o = pd.read_csv('NEL_02_01.pd')
o = o.set_index(pd.DatetimeIndex(o['time']))


columns = ['time', 'open','close', 'high', 'low', 'volume']
freq = pd.Timedelta(minutes=30)
g = o.groupby(pd.Grouper(freq=freq))
candles = {col: [] for col in columns}
for name, group in g:
    if group.values.size != 0:
        open_v, close_v = group.price[-1], group.price[0]
        high_v, low_v = group.price.agg([np.max, np.min])
        vol_v = group.volume.sum()
        candles['time'].append(name + freq//2)
        candles['open'].append(open_v)
        candles['close'].append(close_v)
        candles['high'].append(high_v)
        candles['low'].append(low_v)
        candles['volume'].append(vol_v)


cf = pd.DataFrame(data=candles, columns=columns)

inc = cf.close > cf.open
dec = cf.open > cf.close

TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

candles = bp.figure(x_axis_type="datetime", tools=TOOLS, plot_height=750, plot_width=2000, title = "NEL 30 minutes")
volume = bp.figure(x_range=candles.x_range, x_axis_type="datetime", tools=TOOLS, plot_height=250, plot_width=2000, title = "NEL volume")
candles.grid.grid_line_alpha=0.3
candles.segment(cf.time, cf.high, cf.time, cf.low, color="black")
candles.vbar(cf.time[inc], freq//2, cf.open[inc], cf.close[inc], fill_color="#D5E1DD", line_color="black")
candles.vbar(cf.time[dec], freq//2, cf.open[dec], cf.close[dec], fill_color="#F2583E", line_color="black")
volume.vbar(cf.time, freq//2, cf.volume*0, cf.volume, fill_color='blue')
layout = bl.layout(candles, volume)

bp.output_file("NEL.html", title="NEL 30 minutes")

bp.show(layout)  # open a browser
