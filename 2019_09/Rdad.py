
import pandas as pd

# 读出文件数据到dataframe
covid_df = pd.read_csv("world_covid_history-04-11.csv")

# 过滤非国家数据，保留日期、国家、确诊人数
covid_df = covid_df[['date', 'country', 'confirmed']][covid_df.isnull().province == True]
covid_df = covid_df.pivot(index='country', columns='date', values='confirmed')
covid_df = covid_df.sort_values(by='2020-04-10', axis=0, ascending=False)

# 保存规整后的数据
covid_df.to_csv('covid_range_data.csv', index=False, encoding='utf_8_sig')
