import akshare as ak
import matplotlib.pyplot as plt

# 后来发现休市的日期会导致索引不连续，所以这种直接通过算时间差再线性转换到索引的方式不适用

# 计算两个日期之间的天数
def calculate_days(date):
    start_date = "2018-02-13"  #根据选取的基金不同而不同
    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(date, "%Y-%m-%d")
    return (end - start).days


# 计算天数到索引的转换
def days_to_index(date):
    start_index = 0  # 假设数据从索引0开始
    days = calculate_days(date)
    return start_index + days

# 获取基金的历史净值数据
fund_df = ak.fund_open_fund_info_em(symbol="005693", indicator="单位净值走势") 

# 查看前几行数据
print(fund_df)

# 只保留从2020年1月1日到2023年10月1日的数据
start_date = "2020-02-13"
end_date = "2022-02-13"
start_index = days_to_index(start_date)
end_index = days_to_index(end_date)
print(f"Start index: {start_index}, End index: {end_index}")
fund_df = fund_df[start_index:end_index]

print(fund_df)



# # 绘制累计净值走势
# plt.figure(figsize=(12, 6))
# plt.plot(fund_df['净值日期'], fund_df['单位净值'], label='单位净值', color='blue')
# plt.title('基金累计净值走势')
# plt.xlabel('日期')
# plt.ylabel('累计净值')
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()