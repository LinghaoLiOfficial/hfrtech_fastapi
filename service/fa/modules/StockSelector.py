import os
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import akshare as ak
from datetime import datetime, timedelta
import mplfinance as mpf
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
from datetime import datetime

from service.fa.modules.DecisionTools import DecisionTools
from service.fa.modules.ComputeTools import ComputeTools
from mapper.FAMapper import FAMapper
from utils.common.GeneralTool import GeneralTool
from utils.common.StrGenerator import StrGenerator

plt.rcParams['font.sans-serif'] = ['SimHei']  # 常用中文字体列表
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常


class StockSelector:

    @classmethod
    def recreate_global_stock(cls):
        star_stock_df = ak.stock_zh_kcb_spot()
        star_stock_code_list = [x.lstrip("sh") for x in star_stock_df.loc[:, "代码"].tolist()]

        all_stock_df = ak.stock_zh_a_spot_em()

        FAMapper.sync_delete_all_global_stock({})

        for i in tqdm(range(len(all_stock_df)), desc="insert stock"):
            stock_code = all_stock_df.loc[i, "代码"]
            # 去除名称中所有空格
            stock_name = all_stock_df.loc[i, "名称"].replace(" ", "").replace("*", "")

            stock_info_df = ak.stock_individual_info_em(symbol=stock_code)
            industry_name = stock_info_df.loc[stock_info_df['item'] == '行业', 'value'].values[0]

            FAMapper.sync_insert_global_stock({
                "stock_id": StrGenerator.generate_uuid(),
                "stock_code": stock_code,
                "stock_name": stock_name,
                "industry_name": industry_name,
                "on_star_market": 1 if stock_code in star_stock_code_list else 0
            })

    @classmethod
    def update_stocks_info_with_image(cls, max_stock_price=30, day_window_len=180, x_ticks_interval=7, trend_curve_type="SMA", period_window_list=[5, 10, 20, 40], image_path="", user_id=None):
        """
        :param max_stock_price: 最大股价阈值
        :param day_window_len: 近期时间窗口长度
        :param x_ticks_interval: K线图时间间隔
        :param period_window_list: 移动平均窗口列表
        :return:
        """

        """
        选股分析
        """

        industry_df = ak.stock_board_industry_name_em()
        for i in range(len(industry_df)):
            industry_name = industry_df.loc[i, "板块名称"]
            industry_code = industry_df.loc[i, "板块代码"]

            industry_stocks_df = ak.stock_board_industry_cons_em(symbol=industry_code)
            for j in tqdm(range(len(industry_stocks_df)), desc=f"{i+1}/{len(industry_df)} updating stock image..."):
                try:
                    """
                    选股条件1：当前股价小于等于当前最大股价限制
                    """
                    if max_stock_price is not None and float(industry_stocks_df.loc[j, "最新价"]) > max_stock_price:
                        continue

                    stock_code = industry_stocks_df.loc[j, "代码"]
                    stock_name = industry_stocks_df.loc[j, "名称"].replace(" ", "").replace("*", "")
                    start_date = datetime.now()
                    early_date = start_date - timedelta(days=day_window_len + max(period_window_list))
                    start_date = start_date.strftime("%Y-%m-%d")
                    early_date = early_date.strftime("%Y-%m-%d")

                    """
                    选股条件2：当前股价处于近期低价
                    """
                    history_stock_df = ak.stock_zh_a_hist(
                        symbol=stock_code,
                        period="daily",  # 日k
                        start_date=early_date.replace("-", ""),
                        end_date=start_date.replace("-", ""),
                        adjust="qfq"  # 前复权后的数据
                    )

                    # 若数据无效
                    if len(history_stock_df) == 0:
                        print(f"{stock_code} {stock_name} no history data!")
                        continue

                    # 若股票不存在于全局股票库
                    mysql_result0 = FAMapper.sync_select_global_stock_where_stock_name({
                        "stock_name": stock_name
                    })
                    if not mysql_result0.verify_data_on_results():
                        print(f"{stock_code} {stock_name} non exist!")
                        continue

                    candle_history_stock_df = history_stock_df.loc[:, ["日期", "开盘", "最高", "最低", "收盘", "成交量"]]
                    candle_history_stock_df.rename(columns={
                        "日期": "Date",
                        "开盘": "Open",
                        "最高": "High",
                        "最低": "Low",
                        "收盘": "Close",
                        "成交量": "Volume"
                    }, inplace=True)
                    candle_history_stock_df["Date"] = pd.to_datetime(candle_history_stock_df["Date"])
                    candle_history_stock_df.set_index("Date", inplace=True)

                    trend_colors = ['black', 'orange', 'red', 'purple']
                    extra_plots = []
                    legend_elements = []
                    # 趋势曲线
                    trend_data = {}
                    for period in period_window_list:
                        # 根据收盘价
                        if trend_curve_type == "SMA":
                            trend_data[f'{trend_curve_type}_{period}'] = ComputeTools.compute_sma(
                                candle_history_stock_df['Close'], period)
                        elif trend_curve_type == "EMA":
                            trend_data[f'{trend_curve_type}_{period}'] = ComputeTools.compute_ema(
                                candle_history_stock_df['Close'], period)

                    # 添加趋势线
                    for idx, period in enumerate(period_window_list):
                        if idx < len(trend_colors):  # 确保颜色索引不越界
                            extra_plots.append(
                                mpf.make_addplot(trend_data[f'{trend_curve_type}_{period}'][max(period_window_list):],
                                                 color=trend_colors[idx], width=1.0))
                    # 创建图例标签
                    for idx, period in enumerate(period_window_list):
                        if idx < len(trend_colors):
                            legend_elements.append(
                                plt.Line2D([0], [0], color=trend_colors[idx], lw=2, label=f'{trend_curve_type}{period}'))

                    # 获取股票当前价格
                    stock_current_price_df = ak.stock_individual_info_em(symbol=stock_code)
                    stock_current_price = stock_current_price_df.loc[stock_current_price_df['item'] == '最新', 'value'].values[0]

                    # 创建多条水平参考线
                    horizontal_colors = ['purple', 'orange']
                    buy_refer_price = DecisionTools.mean_decision_buy_price(trend_data[f'{trend_curve_type}_{min(period_window_list)}'][max(period_window_list):])
                    sell_refer_price = DecisionTools.mean_decision_sell_price(trend_data[f'{trend_curve_type}_{min(period_window_list)}'][max(period_window_list):])
                    refer_line_dict = {
                        "买入参考线": buy_refer_price,
                        "卖出参考线": sell_refer_price
                    }
                    for refer_id, (refer_name, refer_value) in enumerate(refer_line_dict.items()):
                        horizontal_line = pd.Series(
                            [refer_value] * len(candle_history_stock_df[max(period_window_list):]),
                            index=candle_history_stock_df[max(period_window_list):].index
                        )
                        extra_plots.append(
                            mpf.make_addplot(horizontal_line, color=horizontal_colors[refer_id], linestyle='-', width=1.0))
                        legend_elements.append(plt.Line2D([0], [0], color=horizontal_colors[refer_id], linestyle='-', lw=2,
                                                          label=f'{refer_name.replace("_", " ")}'))

                    display_candle_history_stock_df = candle_history_stock_df.iloc[max(period_window_list):, :]
                    # 设置图表蜡烛颜色
                    mpf_colors = mpf.make_marketcolors(
                        up='red',
                        down='green',
                        # edge='black',
                        # wick={'up': 'black', 'down': 'black'},
                        # volume='black',
                        # ohlc='black'
                    )
                    # 设置为支持中文的图表
                    mpf_style = mpf.make_mpf_style(marketcolors=mpf_colors, rc={'font.family': 'SimHei', 'axes.unicode_minus': 'False'})
                    # 绘制蜡烛图表
                    fig, axlist = mpf.plot(
                        display_candle_history_stock_df,
                        type='candle',
                        title=f"{stock_code}-{stock_name}",
                        style=mpf_style,
                        addplot=extra_plots,
                        returnfig=True,  # 返回Figure和Axes对象
                        figratio=(16, 6),
                        volume=False  # 是否显示成交量
                    )

                    # 添加图例
                    ax_main = axlist[0]  # 主K线图的Axes对象
                    ax_main.legend(handles=legend_elements, loc='upper left')

                    # 设置x轴刻度
                    ax_main.set_xticks([x for x in range(len(display_candle_history_stock_df))][::x_ticks_interval])
                    ax_main.set_xticklabels(
                        [x.strftime("%m-%d") for x in display_candle_history_stock_df.index][::x_ticks_interval])
                    ax_main.set_ylabel("价格", fontsize=8)
                    # 显示网格
                    ax_main.grid(True)

                    # 保存图像
                    plt.savefig(f"{GeneralTool.root_path}/{image_path}/{stock_code}.png")
                    plt.close(fig)

                    # 保存数据

                    # 判断当前股票数据是否存在
                    mysql_result = FAMapper.sync_select_stock_price_where_belong_user_id_and_stock_code({
                        "belong_user_id": user_id,
                        "stock_code": stock_code
                    })
                    if mysql_result.verify_data_on_results():
                        # 当前股票数据存在，则更新旧数据
                        FAMapper.sync_update_stock_price({
                            "stock_current_price": stock_current_price,
                            "stock_buy_refer_price": buy_refer_price,
                            "stock_sell_refer_price": sell_refer_price,
                            "belong_user_id": user_id,
                            "stock_code": stock_code
                        })
                    else:
                        # 当前股票数据不存在，则插入新的数据
                        FAMapper.sync_insert_stock_price({
                            "stock_id": StrGenerator.generate_uuid(),
                            "belong_user_id": user_id,
                            "industry_code": industry_code,
                            "industry_name": industry_name,
                            "stock_code": stock_code,
                            "stock_name": stock_name,
                            "stock_price_trend_path": f"{os.getenv('URL')}/file/{image_path}/{stock_code}.png",
                            "stock_current_price": stock_current_price,
                            "stock_buy_refer_price": buy_refer_price,
                            "stock_sell_refer_price": sell_refer_price
                        })

                    time.sleep(0.2)

                except Exception as e:
                    print(e)
                    continue
