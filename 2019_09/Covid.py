import akshare as ak
import pandas as pd
covid_19_history_df = ak.covid_19_history()

# 保存原始数据到csv文件
covid_19_history_df.to_csv('world_covid_history-222', index=False, encoding='utf_8_sig')

# 读出文件数据到dataframe
covid_df = pd.read_csv("world_covid_history-222.csv", header=None)

# 过滤非国家数据，保留日期、国家、确诊人数
covid_df = covid_df[['date', 'country', 'confirmed']][covid_df.isnull().province == True]
covid_df = covid_df.pivot(index='country', columns='date', values='confirmed')
covid_df = covid_df.sort_values(by='2020-04-10', axis=0, ascending=False)

# 保存规整后的数据
covid_df.to_csv('covid_range_data-2222.csv', index=False, encoding='utf_8_sig')
print(covid_19_history_df)