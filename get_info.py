import FinanceDataReader as fdr
import pandas as pd
import numpy as np

# 삼성전자(005930) 전체 (1996-11-05 ~ 현재)
# df = fdr.DataReader('005930')

def df_preprocessing(df):
    try:
        df.종목코드 = df.종목코드.map('{:06d}'.format)
    except:
        pass
    df = df[['회사명', '종목코드']]
    df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    return df

def get_stock_info(market = 'kospi'):
    if market == 'kospi':
        market_type = 'stockMkt'
    elif market == 'kosdaq':
        market_type = 'kosdaqMkt'
    
    path = f'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13&marketType={market_type}'

    df = pd.read_html(path,header=0)[0]
    return df_preprocessing(df)
    
def get_black_list():
    # 부실공시법인
    df_insincerity = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=05', header=0)[0]
    df_managing = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=01', header=0)[0]
    
    df = pd.concat([df_insincerity, df_managing])
    df.종목코드 = df.종목코드.map('{:06d}'.format)
    df = df[['회사명', '종목코드']]
    df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})
    return df




kospi = get_stock_info('kospi')
print(kospi)