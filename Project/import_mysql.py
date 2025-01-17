import pandas as pd  # 要改名的原因不可考
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://{user}:{pw}@{localhost}:{port}/{db}".format(user="db102stock", pw="db102stock_pwd", localhost="10.120.14.18", port=3307, db="stock"))
df = pd.read_csv("2891_inf_MA.csv", encoding='big5', low_memory=False)
# print(type(df))
# print(df)
df.to_sql(con=engine, name='stock_inf', if_exists='append', index=False)