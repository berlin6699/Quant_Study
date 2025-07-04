# 假设我有10000元的本金，预计最大的跌幅为10%，所以在每次下跌的时候我都加仓，在跌幅为10%的时候加仓到10000元
# 而我预计的涨幅为20%，所以在每次上涨的时候我都卖出，直到卖出到10000元
# 这样就可以实现一个简单的盈利计算


import akshare as ak
import matplotlib.pyplot as plt
import profit_calculate_function as pcf

def main():
    # 选择一个期望仿真的时间段和基金代码
    fund_code = "005693"
    start_date = "2021-02-03"
    end_date = "2025-06-13"

    # 获取基金的历史净值数据
    fund_df = pcf.get_fund_data(fund_code, start_date, end_date)

    # 画出单位净值走势
    plt.figure(figsize=(12, 6))
    plt.plot(fund_df.index, fund_df['单位净值'], label='单位净值', color='blue')
    plt.title('基金单位净值走势')
    plt.xlabel('索引')
    plt.ylabel('单位净值')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    buy_index = fund_df[fund_df['日增长率'] < 0].index
    sell_index = fund_df[fund_df['日增长率'] > 0].index

    # print(f"买入索引: {buy_index}")
    # print(f"卖出索引: {sell_index}")
 
    # 预计最大的跌幅为10%，计算对应预计单位净值为第一个日期的单位净值的90%
    predicated_dropvalue = fund_df['单位净值'].iloc[0] * 0.9
    # 预计最大的涨幅为20%，计算对应预计单位净值为第一个日期的单位净值的120%
    predicated_risevalue = fund_df['单位净值'].iloc[0] * 1.2

    # 基金份数
    num_shares = 0
    # 初始现金
    money = 10000 

    # 构建买入和卖出列表
    buymoney_index = []
    sellmoney_index = []


    # 假设初始本金为10000元
    for i in fund_df.index:
        # 打印该索引
        print(f"处理索引: {i}")

        if i in buy_index:
            # 在下跌时加仓
            buy_percent = abs(fund_df['单位净值'].iloc[i-725] - predicated_dropvalue)
            buy_money = money * buy_percent
            # 确保买入金额不超过10000元
            temp = money - buy_money
            if temp < 0:
                buy_money = money
                money = 0
            else:
                money = temp
                buy_money = buy_money

            num_shares = num_shares + buy_money / fund_df['单位净值'].iloc[i-725]


            # 在与i大小相同的索引点记录买入金额
            buymoney_index.append(buy_money)

            
            print(f"在索引 {i} 处买入，金额: {buy_money:.2f} 元")


        elif i in sell_index:
            # 在上涨时卖出
            sell_percent = abs(fund_df['单位净值'].iloc[i-725] - predicated_risevalue)
            sell_money = 10000 * sell_percent
            # 确保卖出金额不超过当前持有的总金额
            if sell_money > num_shares * fund_df['单位净值'].iloc[i-725]:
                # 清仓
                sell_money = num_shares * fund_df['单位净值'].iloc[i-725]
                money += sell_money
                num_shares = 0
            else:
                money += sell_money
                num_shares -= sell_money / fund_df['单位净值'].iloc[i-725]


            sellmoney_index.append(sell_money)

            print(f"在索引 {i} 处卖出，金额: {sell_money:.2f} 元")


        # 当前持有总金额
        total_money = money + num_shares * fund_df['单位净值'].iloc[i-725]
        print(f"在索引 {i} 处，当前持有总金额: {total_money:.2f} 元。其中，现金: {money:.2f} 元，基金份数: {num_shares:.2f} 份，当前单位净值: {fund_df['单位净值'].iloc[i-725]:.4f} 元，基金总值: {num_shares * fund_df['单位净值'].iloc[i-725]:.2f} 元")

# 画出买入和卖出金额趋势图
    plt.figure(figsize=(12, 6))
    plt.plot(buy_index, buymoney_index, label='买入金额', color='green')
    plt.title('买入金额趋势图')
    plt.xlabel('索引')
    plt.ylabel('金额 (元)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.plot(sell_index, sellmoney_index, label='卖出金额', color='green')
    plt.title('卖出金额趋势图')
    plt.xlabel('索引')
    plt.ylabel('金额 (元)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()






