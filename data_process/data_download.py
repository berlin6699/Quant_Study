# # 将所有基金数据下载下来，存入txt，命名方式为“基金代码_开始日期_结束日期.txt”，
# # 方便后续读取和分析
# import pandas as pd
# import os
# import datetime
# import akshare as ak
# import time
# from py_mini_racer._value_handle import JSParseException

# def main():
#     # fund_code需要从0000001到999999
#     for i in range(1, 1000000):
#         fund_code = f"{i:06d}"  # 格式化基金代码为6位数

#         try:
#             # 获取单位净值走势
#             fund_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
#             print(f"成功获取基金 {fund_code} 数据，共 {len(fund_df)} 条记录。")
            
#             # 获取当前日期
#             current_date = datetime.datetime.now().strftime("%Y-%m-%d")

#             # 获取基金的开始日期和结束日期
#             start_date = fund_df['净值日期'].min()
#             end_date = fund_df['净值日期'].max()

#             # 将日期转换为字符串格式
#             start_date_str = start_date.strftime("%Y-%m-%d")
#             end_date_str = end_date.strftime("%Y-%m-%d")

#             # 设置文件名
#             file_name = f"{fund_code}_{start_date_str}_{end_date_str}.txt"

#             # 检查文件是否存在，如果存在则跳过
#             if os.path.exists(file_name):
#                 print(f"文件 {file_name} 已存在，跳过。")

#             # 保存到当前目录
#             try:
#                 fund_df.to_csv(file_name, index=False, encoding='utf-8-sig')
#                 print(f"基金数据已保存到 {file_name}")
#             except Exception as e:
#                 print(f"保存基金数据时出错: {e}") 


#         except JSParseException as e:
#             if "<!doctype html>" in str(e):
#                 print(f"❌ 基金 {fund_code} 请求返回了 HTML 页面，跳过此基金。")
#             else:
#                 print(f"❌ 基金 {fund_code} 发生 JS 解析错误: {e}")
#         except Exception as e:
#             print(f"⚠️ 基金 {fund_code} 发生未知错误: {e}")

#         # 适当加个延迟，防止触发反爬机制
#         # time.sleep(1)
    
# if __name__ == "__main__":
#     main()

import pandas as pd
import os
import datetime
import akshare as ak
from py_mini_racer._value_handle import JSParseException
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# 获取有效基金代码列表
def get_valid_fund_codes():
    df = ak.fund_open_fund_daily_em()
    return df["基金代码"].astype(str).str.zfill(6).tolist()

# 单个基金处理函数
def process_fund(fund_code):
    try:
        # 获取单位净值走势
        fund_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        
        # 获取基金的开始日期和结束日期
        start_date = fund_df['净值日期'].min().strftime("%Y-%m-%d")
        end_date = fund_df['净值日期'].max().strftime("%Y-%m-%d")
        
        # 构造文件名
        file_name = f"{fund_code}_{start_date}_{end_date}.txt"
        
        # 如果文件已存在，则跳过
        if os.path.exists(file_name):
            return f"文件 {file_name} 已存在，跳过。"

        # 保存到本地
        fund_df.to_csv(file_name, index=False, encoding='utf-8-sig')
        return f"✅ 基金 {fund_code} 数据已保存到 {file_name}"
    
    except JSParseException as e:
        if "<!doctype html>" in str(e):
            return f"❌ 基金 {fund_code} 请求返回了 HTML 页面，跳过此基金。"
        else:
            return f"❌ 基金 {fund_code} 发生 JS 解析错误: {e}"
    except Exception as e:
        return f"⚠️ 基金 {fund_code} 发生未知错误: {e}"

# 主函数
def main():
    fund_codes = get_valid_fund_codes()
    total = len(fund_codes)
    
    print(f"共找到 {total} 个有效基金代码，开始并发下载...")

    max_workers = 5  # 可根据网络情况调整，推荐 3~10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_fund, code): code for code in fund_codes}
        
        for future in tqdm(as_completed(futures), total=total, desc="Processing Funds"):
            result = future.result()
            # 如果需要日志输出可取消注释下一行
            # print(result)
            pass

if __name__ == "__main__":
    main()