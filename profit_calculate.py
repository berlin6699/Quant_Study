# 假设我有10000元的本金，预计最大的跌幅为10%，所以在每次下跌的时候我都加仓，在跌幅为10%的时候加仓到10000元
# 而我预计的涨幅为20%，所以在每次上涨的时候我都卖出，直到卖出到10000元9
# 这样就可以实现一个简单的盈利计算


import akshare as ak
import matplotlib.pyplot as plt
import profit_calculate_function as pcf

# 选择一个期望仿真的时间段和基金代码
fund_code = "005693"
start_date = "2024-06-06"
end_date = "2025-06-13"

# 预计最大的涨幅和跌幅
drop_max = 0.1
rise_max = 0.3

# 波动容忍度,数值越大代表越抗波动
Tolerance = 1

# 初始现金
money = 10000 

def main():
    # 获取基金的历史净值数据
    fund_df = pcf.get_fund_data(fund_code, start_date, end_date)

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
    plt.plot(fund_df.index, fund_df['单位净值'] * 6000, label='单位净值', color='blue')
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


if __name__ == "__main__":
    main()






