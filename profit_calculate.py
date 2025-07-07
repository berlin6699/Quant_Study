# 假设我有10000元的本金，预计最大的跌幅为10%，所以在每次下跌的时候我都加仓，在跌幅为10%的时候加仓到10000元
# 而我预计的涨幅为20%，所以在每次上涨的时候我都卖出，直到卖出到10000元
# 这样就可以实现一个简单的盈利计算


import akshare as ak
import matplotlib.pyplot as plt
import profit_calculate_function as pcf
import pandas as pd
import os
import plotly.express as px
import concurrent.futures


# 从以下几个维度进行分析
# 1. 不同的基金
# 2. 不同的时间段长度
# 3. 同一时间段长度的不同位置
# 4. 最大上升下降期望
# 5. 波动的容忍度


def main():

    # demo1:从网上获取基金数据，计算该基金的利润曲线
    pcf.simple_profit_simulate_datafromonline(
        fund_code="000001",  # 示例基金代码
        start_date="2024-06-06",
        end_date="2025-05-09",
        drop_max=0.3,
        rise_max=0.5,
        Tolerance=10,
        money=10000
    )


    # demo2:从本地读取所有基金数据，计算不同基金的平均利润率
    input_path = "./data_parquet"
    data = pcf.get_fund_data_fromlocal(input_path)
    

    # 设置参数
    drop_max = 0.3  # 最大跌幅
    rise_max = 0.5  # 最大涨幅
    Tolerance = 10  # 容忍度

    # 计算利润率
    profit_index = pcf.simple_profit_simulate_datafromlocal(data, drop_max, rise_max, Tolerance, 10000)

    # 保存为 HTML 文件
    df = pd.DataFrame(profit_index)

    # 构造文件名和图表标题
    title = f"各基金全生命周期年平均利润率对比_简单策略_最大跌幅{drop_max}_最大涨幅{rise_max}_容忍度{Tolerance}"
    filename = f"{title}.html"

    fig = px.line(df, x="基金代码", y="平均利润率", title="不同基金的平均利润率比较")
    fig.update_xaxes(tickangle=45)
    fig.write_html(filename)  # 保存为 HTML 文件

    print(f"已保存: {filename}")
    fig.show()

    

if __name__ == "__main__":
    main()