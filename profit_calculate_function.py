import akshare as ak
import matplotlib.pyplot as plt


# 选择一个期望仿真的时间段和基金代码
def get_fund_data(fund_code, start_date, end_date):
    """
    获取基金的历史净值数据
    :param fund_code: 基金代码
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: 基金的历史净值数据
    """

    # demo: print(get_fund_data("005693", "2021-02-03", "2023-06-13"))
    
    fund_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
    
    # 找到开始和结束日期的索引
    try:
        start_index = fund_df[fund_df['净值日期'].astype(str) == start_date].index[0]
    except IndexError:
        print(f"Start date {start_date} not found in the data.")
        start_index = 0
    try:
        end_index = fund_df[fund_df['净值日期'].astype(str) == end_date].index[0]
    except IndexError:
        print(f"End date {end_date} not found in the data.")
        end_index = len(fund_df) - 1

    # 截取数据
    return fund_df[start_index:end_index + 1]

