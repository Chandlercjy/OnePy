import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.style as style
from matplotlib.widgets import MultiCursor,Cursor
from matplotlib.ticker import FuncFormatter
# style.use('ggplot')

df = pd.read_pickle('/Users/chandler/Desktop/test.pkl')
s = pd.read_csv('/Users/chandler/Desktop/stock/data_csv/000006.csv',parse_dates=True,index_col=0)
equity = df['equity']
log = df['log']
positions = df['positions']
holdings = df['holdings']


plt.rc('axes', grid=True)
plt.rc('grid', color='0.75', linestyle=':', linewidth=0.5)
#
textsize = 9
left, width = 0.1, 0.8
rect1 = [left, 0.7, width, 0.2]
rect2 = [left, 0.3, width, 0.4]
rect3 = [left, 0.1, width, 0.2]

fig = plt.figure(facecolor='white')
axescolor = 'white'  # the axes background color

ax1 = fig.add_axes(rect1, facecolor=axescolor)  # left, bottom, width, height
ax2 = fig.add_axes(rect2, facecolor=axescolor, sharex=ax1)
ax3 = fig.add_axes(rect3, facecolor=axescolor, sharex=ax1)

# fig = plt.figure()
# ax1 = plt.subplot2grid((6,1),(0, 0),colspan=1,rowspan=2)
# ax2 = plt.subplot2grid((6,1),(2, 0),colspan=1,rowspan=4)
# ax3 = plt.subplot2grid((6,1),(5, 0),colspan=1,rowspan=2)

ax1.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off') # labels along the bottom edge are off

ax2.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off') # labels along the bottom edge are off


# Volume
ax2v = ax2.twinx()  # means share the same space
ax2v.fill_between(s.index, 0,
                  s['volume'], facecolor='#0079a3', alpha=0.4)
ax2v.grid(False)
ax2v.set_ylim(0, 3*s['volume'].max())
ax2v.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelright='on',
    labelleft='off') # labels along the bottom edge are off
yticks = ax2v.get_yticks()

ax2v.set_yticks([0,500000,1000000,1500000])
def millions(x, pos):
    'The two args are the value and tick position'
    return '%0.1fM' % (x*1e-6)

formatter = FuncFormatter(millions)
ax2v.yaxis.set_major_formatter(formatter)


equity['total'].plot(ax=ax1,figsize=[10,8],legend=True)
equity['cash'].plot(ax=ax1,legend=True)
s['close'].plot(ax=ax2,legend=True)
positions.plot(ax=ax3,legend=True,secondary_y=True)



#
multi = MultiCursor(fig.canvas, (ax1,ax2,ax3),
                    color='gray', lw=1,ls=':',horizOn=True)
# a = Cursor(ax2,useblit=True,color='gray', lw=1,ls=':',)
plt.subplots_adjust(left=0.07, bottom=0.10,
                    right=0.96, top=0.88,
                    wspace= 0.2, hspace=0)
import plotly.offline as py
import plotly.tools as tls
plotly_fig = tls.mpl_to_plotly(fig)

plotly_url = py.plot(plotly_fig, filename='mpl-time-series.html')
