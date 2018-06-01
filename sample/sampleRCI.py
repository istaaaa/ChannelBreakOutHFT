# -*- coding: utf-8 -*-
"""
Created on Sun May 13 20:37:58 2018

@author: user
"""
def getohlc():
	timestamp = round(datetime.datetime.now().timestamp()*1000)
	timest    = timestamp - ( 60 * 1000 * 50 )

	candles = bitmex.fetch_ohlcv("BTC/USD", timeframe = "1m", since = timest)

	# candles には、時刻(unixtime), open, high, low, close, amount の順で格納される
	# 時刻の若い順に格納される。（最後が一番新しい）
	# 時刻は桁が多いので 1000 で割るのを忘れないように。
	df_tmpdata = pd.DataFrame(candles)
	df_tmpdata.columns = ['datetime','open','high','low','close','volume']
	df_data = df_tmpdata

	# unixtime を float 型に変換
	df_data["datetime"] = df_data["datetime"].apply(lambda x: datetime.datetime.fromtimestamp(x/1000))

	#index を連番ではなく時刻に変更
	df_data.set_index('datetime', inplace=True)
	
	return df_data

def ord(seq, idx, itv):
   
   p = seq[idx]
   o = 1
   for i in range(0,itv):
       if p < seq[i]:
           o = o + 1
   return o

def d(itv,src):
   from scipy.stats import rankdata
   sum = 0.0
   for i in range(itv, 0, -1):
       date_rank = itv - i + 1
       price_rank = (itv - rankdata(src)[i-1] + 1)
       sum = sum + pow( (date_rank - price_rank) ,2)
       #pprint("hiduke = {},  price={},  juni={},  goukei={}".format(date_rank, src[i-1], price_rank, sum) )

   return sum

def calc_rci(src, term):

    listnull = [None]
    itv = term
    rcinull = listnull * itv
    rci_tmp = [   (1.0 - 6.0 * d(itv,src[i-itv:i]) / (itv * itv * itv - itv)) * 100.0   for i in range(itv,len(src))]
    rci = rcinull + rci_tmp

    return rci

def main():
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import mpl_finance as mpl

    df = getohlc()
    fig = plt.figure(figsize=(8, 8))
    fig.autofmt_xdate()

    # 1つ目のグラフ(ローソク足)
    ax = plt.subplot(2, 1, 1)
    # ローソク足描画
    mpl.candlestick2_ohlc(ax, df["open"], df["high"], df["low"], df["close"], width=0.7, colorup="b", colordown="r")
    # 描画幅の設定
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom - (top - bottom) / 5, top)
    # 出来高の描画
    ax_v = ax.twinx()
    mpl.volume_overlay(ax_v, df["open"], df["close"], df["volume"], width=0.7, colorup="g", colordown="g")
    ax_v.set_xlim([0, df.shape[0]])
    ax_v.set_ylim([0, df["volume"].max() * 4])
    ax_v.set_ylabel("Volume")
    # X軸調整
    xdate = [i.strftime('%y-%m-%d %H:%M') for i in df.index]

    def dateformat(x, pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''
    locate_size = len(ax.get_xticks())
    ax.xaxis.set_major_locator(ticker.MaxNLocator(locate_size))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(dateformat))

    ax.autoscale_view()
    ax.grid()
    ax.set_ylabel("Price(USD)")

    # 2つ目のグラフ(ADX and DI)
    close = df["close"]
    rci9  = calc_rci(close,  9)
    rci36 = calc_rci(close, 36)
    rci52 = calc_rci(close, 52)

    ax3 = plt.subplot(2, 1, 2)

    xdate3 = []
    x=0
    for i in df.index:
        xdate3.append(x)
        x = x + 1
    
    ax3.hold(True)
    ax3.plot(xdate3, rci9, color='red')
    ax3.plot(xdate3, rci36, color='blue')
    ax3.plot(xdate3, rci52, color='green')

    # 0,80,-80に横線
    ax3.hlines(y=0,   xmin=ax.get_xticks()[0], xmax=ax.get_xticks()[-1],
               colors='k', linestyles='dashed')
    ax3.hlines(y=80,  xmin=ax.get_xticks()[0], xmax=ax.get_xticks()[-1],
               colors='k', linestyles='dashed')
    ax3.hlines(y=-80, xmin=ax.get_xticks()[0], xmax=ax.get_xticks()[-1],
               colors='k', linestyles='dashed')

    # X軸の範囲を合わせる(candlestick2_ohlc内でxlimが指定されている為)
    ax3.set_xlim(ax.get_xlim())
    ax3.xaxis.set_major_locator(ticker.MaxNLocator(locate_size))
    ax3.xaxis.set_major_formatter(ticker.FuncFormatter(dateformat))
    ax3.autoscale_view()
    ax3.grid()
    ax3.set_ylim(0, 80)
    ax3.set_ylabel("ADX and DI")

    plt.show()
    plt.close(fig)
