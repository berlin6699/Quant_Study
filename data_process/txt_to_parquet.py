import os
import pandas as pd

# 设置输入输出目录
input_dir = "./"
output_dir = "../data_parquet"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 遍历所有 .txt 文件并转换
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        txt_path = os.path.join(input_dir, filename)
        parquet_path = os.path.join(output_dir, filename.replace(".txt", ".parquet"))

        print(f"正在处理: {filename}")

        try:
            # 读取数据
            df = pd.read_csv(txt_path, sep=",", encoding="utf-8-sig")

            # 日期列转换为 datetime 类型
            if "净值日期" in df.columns:
                df["净值日期"] = pd.to_datetime(df["净值日期"])

            # 保存为 Parquet
            df.to_parquet(parquet_path, engine="pyarrow")
            print(f"已保存: {parquet_path}")
        except Exception as e:
            print(f"❌ 处理 {filename} 出错: {e}")