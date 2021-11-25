import pandas as pd
from reporting import *


# list_month = (
#     pd.date_range("2020-12-31", "2021-08-31", freq="MS").strftime("%Y%m").tolist()
# )

# df_combined = pd.DataFrame()
# df_3on1 = pd.read_excel("./Reporting/%s.xlsx" % "三合一表8月初版")  # 内部销售数据3合1
# df_3on1 = df_3on1.rename(columns={"目标代码": "医院编码"})
# mask = (df_3on1["产品名称"] == "信立坦")
# df_3on1 = df_3on1.loc[mask, ["医院编码", "客户分级", "社区医院"]].drop_duplicates()

# for month in list_month:
#     df = pd.read_excel("./Reporting/%s.xlsx" % month)
#     df["年月"] = month
#     df_combined = pd.concat([df_combined, df])

# df_combined = pd.merge(left=df_combined, right=df_3on1, how="left", on="医院编码")

# print(df_combined)
# df_combined.to_csv("tracking_data.csv", index=False, encoding="utf-8-sig")


df = pd.read_csv("tracking_data.csv")
mask = (df["社区医院"] != "Y") & (df["所在科室"].isin(["心内科", "肾内科", "普内科", "老干科", "神内科", "内分泌科", "其他科室"]))
df = df.loc[mask,:]
c = Clientfile(df, name="客户档案")
print(c.get_dist(index="客户分级", columns="年月"))