import pandas as pd
from pandas.core.reshape.pivot import pivot_table
from chart_func import plot_bubble

df_pt = pd.read_excel("./Reporting/20210701110520.xlsx")
df_sales = pd.read_excel("./Reporting/三合一表6月初版.xlsx")

index = "地区经理"

pivoted_pt = pd.pivot_table(data=df_pt, values="月累计相关病人数", index=index, aggfunc=sum)

mask = df_sales["产品名称"] == "信立坦"
mask_sales = (
    mask
    & (df_sales.tag.isin(["销量", "药房销量"]))
    & (df_sales["填报日期"].between(202101, 202106))
)
df_sales = df_sales.loc[mask_sales, :]
pivoted_sales = pd.pivot_table(data=df_sales, values="标准数量", index=index, aggfunc=sum)

df_combined = pd.concat([pivoted_pt, pivoted_sales], axis=1)
# xtitle = "名下客户档案数"
xtitle = "名下客户档案潜力（病人数）"
ytitle = "YTD销售（标准盒数）"
df_combined.columns = [xtitle, ytitle]
df_combined.dropna(how="any", inplace=True)
df_combined.sort_values(by=ytitle, ascending=False, inplace=True)
corr = df_combined[xtitle].corr(df_combined[ytitle])

print(df_combined, corr)

plot_bubble(
    savefile="Reporting/test.png",
    x=df_combined[xtitle],
    y=df_combined[ytitle],
    z=df_combined[ytitle],
    labels=df_combined.index,
    z_scale=0.0005,
    title="%s%s versus %s" % (index, xtitle, ytitle),
    xtitle=xtitle,
    ytitle=ytitle,
    xfmt="{:,.0f}",
    yfmt="{:,.0f}",
    with_reg=True,
    label_limit=15,
    width=6,
    height=6,
    corr=corr,
)
