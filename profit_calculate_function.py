import akshare as ak
import matplotlib.pyplot as plt
import pandas as pd
import os

# 选择一个期望仿真的时间段和基金代码，从网上api获取
# demo: print(get_fund_data("005693", "2021-02-03", "2023-06-13"))
def get_fund_data_fromonline(fund_code, start_date, end_date):
    """
    获取基金的历史净值数据
    :param fund_code: 基金代码
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: 基金的历史净值数据
    """
    
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



# 从本地获取，返回一个包含所有基金数据的列表，其中每个元素都是一个DataFrame
# demo: get_fund_data_fromlocal("./data_parquet")
def get_fund_data_fromlocal(input_dir):

    # input_dir = "./data_parquet"

    # 初始化空列表来保存信息
    fund_codes = []
    start_dates = []
    end_dates = []
    data = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".parquet"):
            # 解析文件名获取所需信息
            fund_code, start_date, end_date = filename.replace(".parquet", "").split("_")
            
            # 将解析得到的信息添加到对应的列表中
            fund_codes.append(fund_code)
            start_dates.append(start_date)
            end_dates.append(end_date)


    for i in range(len(fund_codes)):
        try:
            # 构建文件路径
            file_path = os.path.join(input_dir, f"{fund_codes[i]}_{start_dates[i]}_{end_dates[i]}.parquet")
            
            # 读取数据
            df = pd.read_parquet(file_path, engine="pyarrow")
            
            # 将数据添加到列表中，同时添加基金代码、开始日期和结束日期
            df['基金代码'] = fund_codes[i]
            df['开始日期'] = start_dates[i]
            df['结束日期'] = end_dates[i]

            data.append(df)

            print(f"正在读取: {file_path}")
            # print(f"data{data}")

        except Exception as e:
            print(f"❌ 处理 {filename} 出错: {e}")
            continue
        
    return data




# 一个简单的利润计算模拟函数，根据预计的最大上升下降期望，按比例在下跌时加仓，在上涨时卖出，画出可视化图
# 数据来自于在线获取的基金数据，
def simple_profit_simulate_datafromonline(fund_code, start_date, end_date, drop_max, rise_max, Tolerance, money):
    # 获取基金的历史净值数据
    fund_df = get_fund_data_fromonline(fund_code, start_date, end_date)

    # 计算第一个日期的索引
    first_index = fund_df.index[0]

    buy_index = fund_df[fund_df['日增长率'] < 0].index
    sell_index = fund_df[fund_df['日增长率'] >= 0].index
 
    # 通过预计最大的跌幅，计算对应预计最低单位净值
    predicated_dropvalue = fund_df['单位净值'].iloc[0] * (1 - drop_max)
    # 通过预计最大的涨幅，计算对应预计单位净值
    predicated_risevalue = fund_df['单位净值'].iloc[0] * (1 + rise_max)

    # 基金份数
    num_shares = 0

    # 剩余的钱
    rest_money = money

    # 构建买入和卖出列表
    buymoney_index = []
    sellmoney_index = []

    # 构建当前份数列表
    current_shares_index = []

    # 构建盈利列表
    profit_index = []

    for i in fund_df.index:

        if i in buy_index:
            # 在下跌时加仓（绝对值是有可能跌破预期）
            if(fund_df['单位净值'].iloc[i-first_index] - predicated_dropvalue == 0):    # 分母为0
                buy_percent = 1
            else:
                buy_percent = abs(fund_df['单位净值'].iloc[i - first_index] * fund_df['日增长率'].iloc[i - first_index]/100) / abs(fund_df['单位净值'].iloc[i-first_index] - predicated_dropvalue)
            buy_money = rest_money * buy_percent

            # 确保买入金额不超过剩余金额
            temp = rest_money - buy_money
            if temp < 0:
                buy_money = rest_money
                rest_money = 0
            else:
                rest_money = temp
                buy_money = buy_money

            num_shares = num_shares + buy_money / fund_df['单位净值'].iloc[i-first_index]


            # 在与i大小相同的索引点记录买入金额
            buymoney_index.append(buy_money)
            sellmoney_index.append(0)

        elif i in sell_index:

            # 在上涨时卖出
            if(predicated_risevalue - fund_df['单位净值'].iloc[i-first_index]):    # 分母为0
                sell_percent = 1
            else:
                sell_percent = (fund_df['单位净值'].iloc[i - first_index] * fund_df['日增长率'].iloc[i - first_index]/100) / abs(predicated_risevalue - fund_df['单位净值'].iloc[i-first_index])
            sell_money = (num_shares * fund_df['单位净值'].iloc[i - first_index]) * sell_percent

            # 确保卖出金额不超过当前持有的总金额
            if sell_money > num_shares * fund_df['单位净值'].iloc[i-first_index]:
                # 清仓
                sell_money = num_shares * fund_df['单位净值'].iloc[i-first_index]
                rest_money += sell_money
                num_shares = 0
            else:
                rest_money += sell_money
                num_shares -= sell_money / fund_df['单位净值'].iloc[i-first_index]

            # 在与i大小相同的索引点记录卖出金额
            sellmoney_index.append(sell_money)
            buymoney_index.append(0)

        # 每Tolerance天更新一次预测单位净值的预期，天数的靠近程度决定了对短期波动的敏感性
        if(i - first_index) % Tolerance == 0:
            # 更新预测单位净值
            predicated_dropvalue = fund_df['单位净值'].iloc[i-first_index] * (1 - drop_max)
            predicated_risevalue = fund_df['单位净值'].iloc[i-first_index] * (1 + rise_max)

        # 记录当前份数
        current_shares_index.append(num_shares)
        # 当前持有总金额
        total_money = rest_money + num_shares * fund_df['单位净值'].iloc[i-first_index]

        # 计算利润
        profit_index.append(total_money - 10000)



    # 画出买入和卖出金额趋势图
    plt.figure(figsize=(12, 6))
    plt.plot(fund_df.index, buymoney_index, label='买入金额', color='green')
    plt.plot(fund_df.index, sellmoney_index, label='卖出金额', color='red')
    plt.plot(fund_df.index, fund_df['单位净值'] * 2000, label='单位净值', color='blue') # 乘以2000是为了更好地显示单位净值的变化
    plt.plot(fund_df.index, current_shares_index, label='当前份数', color='black')
    plt.plot(fund_df.index, profit_index, label='当前利润', color='gray')
    plt.title('基金单位净值走势与买入卖出金额趋势图')
    plt.xlabel('索引')
    plt.ylabel('金额 (元)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


    # # 返回年平均利润率
    # return (profit_index[-1] / money) / (len(fund_df) / 365)


# 从本地读取所有基金数据，计算不同基金的平均利润率
# demo: simple_profit_simulate_datafromlocal(data, 0.3, 0.5, 10, 10000)
# data 是从 get_fund_data_fromlocal 函数获取的基金数据列表
def simple_profit_simulate_datafromlocal(data, drop_max, rise_max, Tolerance, money):   

    # 构建盈利列表
    total_profit_index = []
    single_profit_index = []


    for i in range(len(data)):

        print(f"正在处理第 {i+1} 个基金数据...")

        fund_df = data[i]

        fund_code = fund_df.iloc[0]['基金代码']
        start_date = fund_df.iloc[0]['开始日期']
        end_date = fund_df.iloc[0]['结束日期']

        # 计算第一个日期的索引
        first_index = fund_df.index[0]

        buy_index = fund_df[fund_df['日增长率'] < 0].index
        sell_index = fund_df[fund_df['日增长率'] >= 0].index
    
        # 通过预计最大的跌幅，计算对应预计最低单位净值
        predicated_dropvalue = fund_df['单位净值'].iloc[0] * (1 - drop_max)
        # 通过预计最大的涨幅，计算对应预计单位净值
        predicated_risevalue = fund_df['单位净值'].iloc[0] * (1 + rise_max)

        # 基金份数
        num_shares = 0

        # 剩余的钱
        rest_money = money

        # 构建买入和卖出列表
        buymoney_index = []
        sellmoney_index = []

        # 构建当前份数列表
        current_shares_index = []

        for i in fund_df.index:

            if i in buy_index:
                # 在下跌时加仓（绝对值是有可能跌破预期）
                diff = abs(fund_df['单位净值'].iloc[i - first_index] - predicated_dropvalue)
                if(diff < 1e-6):    # 分母为0
                    buy_percent = 1
                else:
                    buy_percent = abs(fund_df['单位净值'].iloc[i - first_index] * fund_df['日增长率'].iloc[i - first_index]/100) / abs(fund_df['单位净值'].iloc[i-first_index] - predicated_dropvalue)
                buy_money = rest_money * buy_percent

                # 确保买入金额不超过剩余金额
                temp = rest_money - buy_money
                if temp < 0:
                    buy_money = rest_money
                    rest_money = 0
                else:
                    rest_money = temp
                    buy_money = buy_money

                num_shares = num_shares + buy_money / fund_df['单位净值'].iloc[i-first_index]


                # 在与i大小相同的索引点记录买入金额
                buymoney_index.append(buy_money)
                sellmoney_index.append(0)

            elif i in sell_index:

                # 在上涨时卖出
                diff = abs(fund_df['单位净值'].iloc[i - first_index] - predicated_risevalue)
                if(diff < 1e-6):    # 分母为0
                    sell_percent = 1
                else:
                    sell_percent = (fund_df['单位净值'].iloc[i - first_index] * fund_df['日增长率'].iloc[i - first_index]/100) / abs(predicated_risevalue - fund_df['单位净值'].iloc[i-first_index])
                sell_money = (num_shares * fund_df['单位净值'].iloc[i - first_index]) * sell_percent

                # 确保卖出金额不超过当前持有的总金额
                if sell_money > num_shares * fund_df['单位净值'].iloc[i-first_index]:
                    # 清仓
                    sell_money = num_shares * fund_df['单位净值'].iloc[i-first_index]
                    rest_money += sell_money
                    num_shares = 0
                else:
                    rest_money += sell_money
                    num_shares -= sell_money / fund_df['单位净值'].iloc[i-first_index]

                # 在与i大小相同的索引点记录卖出金额
                sellmoney_index.append(sell_money)
                buymoney_index.append(0)

            # 每Tolerance天更新一次预测单位净值的预期，天数的靠近程度决定了对短期波动的敏感性
            if(i - first_index) % Tolerance == 0:
                # 更新预测单位净值
                predicated_dropvalue = fund_df['单位净值'].iloc[i-first_index] * (1 - drop_max)
                predicated_risevalue = fund_df['单位净值'].iloc[i-first_index] * (1 + rise_max)

            # 记录当前份数
            current_shares_index.append(num_shares)
            # 当前持有总金额
            total_money = rest_money + num_shares * fund_df['单位净值'].iloc[i-first_index]

            # 计算利润
            single_profit_index.append(total_money - 10000)

        # # 画出买入和卖出金额趋势图
        # plt.figure(figsize=(12, 6))
        # plt.plot(fund_df.index, buymoney_index, label='买入金额', color='green')
        # plt.plot(fund_df.index, sellmoney_index, label='卖出金额', color='red')
        # plt.plot(fund_df.index, fund_df['单位净值'] * 2000, label='单位净值', color='blue')
        # plt.plot(fund_df.index, current_shares_index, label='当前份数', color='black')
        # plt.plot(fund_df.index, single_profit_index, label='当前利润', color='gray')
        # plt.title('基金单位净值走势与买入卖出金额趋势图')
        # plt.xlabel('索引')
        # plt.ylabel('金额 (元)')
        # plt.xticks(rotation=45)
        # plt.grid(True)
        # plt.legend()
        # plt.tight_layout()
        # plt.show()


        total_profit_index.append({
            "基金代码": fund_code,
            "开始日期": start_date,
            "结束日期": end_date,
            "平均利润率": (single_profit_index[-1] / money) / (len(fund_df) / 365)
        })

        # 单一基金利润表归零，等待下次循环
        single_profit_index = []

    # 返回年平均利润率
    return total_profit_index

