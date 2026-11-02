import os, importlib, warnings; warnings.filterwarnings(action='ignore')
from config import config_A03       as config   ; importlib.reload(config)
from utils  import functions_utils    as fu       ; importlib.reload(fu)
from utils  import functions_log      as fl       ; importlib.reload(fl)
from utils  import functions_lime     as flime    ; importlib.reload(flime)
from utils  import functions_utils_db as fud      ; importlib.reload(fud)


#==================================================================================================
# [0-1] log 기록 정의
log = fl.Logger(config.PATH_LOG, config.LOG_FILE_NM ); log.set_log_level("info")
log.info("0-1 log 기록 정의")

#==================================================================================================
# [0-2] 실행 변수 정의
log.info("0.2.실행 변수 정의")
config_info = fu.f_get_config_info(config.config_run, config.ENV_DEV)

#==================================================================================================
# [0-3] 실행 변수
log.info("0.3.실행 변수 추가"); fu.f_memory_check()
# 전역 변수 선언 부분
# config_info["TODAY"]           = "20230630"

# 1.실행 변수 정의
log.info("1.실행 변수 정의")

path_base     = "2024-04-03"

path_data_out     = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"01.외부")
path_data_in      = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"02.내부")
path_data_analyze = os.path.join(config_info["PATH_DATA_ANALYZE"])
path_data_output = os.path.join(config_info["PATH_DATA_OUTPUT"])

path_database = os.path.join(config_info["PATH_DATA_OUTPUT_DATEBASE"],path_base)
path_pretreat = os.path.join(config_info["PATH_DATA_OUTPUT_PRETREAT"],path_base)
path_middle   = os.path.join(config_info["PATH_DATA_OUTPUT_MIDDLE"]  ,path_base)
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-05-20')

import pandas as pd
import numpy as np
import geopandas as gpd

bike_data = pd.read_pickle(path_data_output+'//1.pretreatment//02.내부//01.대여반납이력//result_bike_data_0430.pkl')
bike_data0405 = pd.read_pickle(path_data_output+'//1.pretreatment//02.내부//01.대여반납이력//result_bike_data_0524.pkl')
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-06-14')
seg_ym = pd.read_pickle(path_result + '//01.excel//seg_ym.pkl')  # 대여소 대기시간 짧은 대여소 분석
folder_path = (path_result + '//01.excel//재고량평가2//대여소별_회수량분배량//')
all_data = []
for file_name in os.listdir(folder_path):
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_excel(file_path)
        all_data.append(df)
mng_stock = pd.concat(all_data, ignore_index=True)


bike_col = ['자전거번호', '대여일시_시분초', '대여_대여소ID', '대여_대여소명', '반납일시_시분초',
            '반납_대여소ID', '반납_대여소명', '이용시간(분)', '이용거리(km)', '연령대', '성별', '내외국인구분']
bike_colnew = ['자전거번호', '대여일시', '대여소ID', '대여소명', '반납일시',
            '반납대여소ID', '반납대여소명', '이용시간', '이용거리', '연령대', '성별', '내외국인']

bike_03 = bike_data[bike_col]
bike_0405 = bike_data0405[bike_col]
bike = pd.concat([bike_03,bike_0405],axis=0)
bike.columns = bike_colnew

bike['대여일자'] = bike['대여일시'].astype('str').str[:10]
bike['반납일자'] = bike['반납일시'].astype('str').str[:10]
bike_m13 = bike[bike['대여일자'] > '2023-03-31']   # 2일전 시점 누적 재고 산출을 위해 13개월로 설정


#### 대여이력 생성
stock_m13a1 = bike_m13[['자전거번호', '대여소ID', '대여소명', '대여일시']]
stock_m13a1['기준대여소'] = stock_m13a1['대여소ID']   # 대여_대여소
stock_m13a1['기준일시'] = stock_m13a1['대여일시']   # 대여일시
stock_m13a1['유형'] = '대여'
stock_m13a1['재고일자'] = stock_m13a1['기준일시'].astype('str').str[:10]

# 전일 생성 : 전일 날짜를 기준일시로 생성 후 합침
stock_m13a2 = bike_m13[['자전거번호', '대여소ID', '대여소명', '대여일시']]
stock_m13a2['기준대여소'] = stock_m13a2['대여소ID']   # 대여_대여소
stock_m13a2['기준일시'] = stock_m13a2['대여일시']
stock_m13a2['유형'] = '대여'
stock_m13a2['다음날'] = stock_m13a2['기준일시'] + pd.Timedelta(days=1)   # 대여일시
stock_m13a2['재고일자']= stock_m13a2['다음날'].astype('str').str[:10]


#### 반납이력 생성
stock_m13b1 = bike_m13[['자전거번호', '반납대여소ID', '반납대여소명', '반납일시']]
stock_m13b1['기준대여소'] = stock_m13b1['반납대여소ID']   # 반납_대여소
stock_m13b1['기준일시'] = stock_m13b1['반납일시']   # 반납일시
stock_m13b1['유형'] = '반납'
stock_m13b1['재고일자'] = stock_m13b1['기준일시'].astype('str').str[:10]

stock_m13b2 = bike_m13[['자전거번호', '반납대여소ID', '반납대여소명', '반납일시']]
stock_m13b2['기준대여소'] = stock_m13b2['반납대여소ID']   # 반납_대여소
stock_m13b2['기준일시'] = stock_m13b2['반납일시']   # 반납일시
stock_m13b2['유형'] = '반납'
stock_m13b2['다음날'] = stock_m13b2['기준일시'] + pd.Timedelta(days=1)
stock_m13b2['재고일자']= stock_m13b2['다음날'].astype('str').str[:10]

stock_m13a11 = stock_m13a1[['자전거번호', '기준일시', '기준대여소', '재고일자', '유형']]
stock_m13a12 = stock_m13a2[['자전거번호', '기준일시', '기준대여소', '재고일자', '유형']]
stock_m13b11 = stock_m13b1[['자전거번호', '기준일시', '기준대여소', '재고일자', '유형']]
stock_m13b12 = stock_m13b2[['자전거번호', '기준일시', '기준대여소', '재고일자', '유형']]

stock_m13c = pd.concat([stock_m13a11, stock_m13a12, stock_m13b11, stock_m13b12], axis = 0 )
stock_m13c = stock_m13c.sort_values(by = ['자전거번호', '재고일자', '기준일시'], ascending = True)
stock_m13c['기준일자']= stock_m13c['기준일시'].astype('str').str[:10]
stock_m13c['기준시간']= stock_m13c['기준일시'].astype('str').str[11:13]

## 전체 재고 데이터 : stock_m13c
stock_m13cc_9h = stock_m13c[(stock_m13c['기준일자'] <= stock_m13c['재고일자']) & (stock_m13c['기준시간'] < '09')]   # 재고평가를 위해 재고일자 이전의 기준일자 정보만 분석
stock_m13cc_14h = stock_m13c[(stock_m13c['기준일자'] <= stock_m13c['재고일자']) & (stock_m13c['기준시간'] < '14')]   # 재고평가를 위해 재고일자 이전의 기준일자 정보만 분석
stock_m13cc_19h = stock_m13c[(stock_m13c['기준일자'] <= stock_m13c['재고일자']) & (stock_m13c['기준시간'] < '19')]   # 재고평가를 위해 재고일자 이전의 기준일자 정보만 분석
stock_m13cc_24h = stock_m13c[stock_m13c['기준일자'] <= stock_m13c['재고일자']]  # 재고평가를 위해 재고일자 이전의 기준일자 정보만 분석


# 자전거별, 기준일시 최대값 생성 (하나씩 돌리기)
stock_m13cc9 = stock_m13cc_9h
stock_m13cc14 = stock_m13cc_14h
stock_m13cc19 = stock_m13cc_19h
stock_m13cc24 = stock_m13cc_24h

stock_m13c1_9 = stock_m13cc9.groupby(['자전거번호', '재고일자'])['기준일시'].max().reset_index()
stock_m13c1_14 = stock_m13cc14.groupby(['자전거번호', '재고일자'])['기준일시'].max().reset_index()
stock_m13c1_19 = stock_m13cc19.groupby(['자전거번호', '재고일자'])['기준일시'].max().reset_index()
stock_m13c1_24 = stock_m13cc24.groupby(['자전거번호', '재고일자'])['기준일시'].max().reset_index()

# 자전거별, 기준일시 최대값 기준 반납/대여 정보 추가
stock_m13c1a = pd.merge(stock_m13c1_9, stock_m13cc9, on= ['자전거번호', '재고일자', '기준일시'], how = 'left')
stock_m13c1b = pd.merge(stock_m13c1_14, stock_m13cc14, on= ['자전거번호', '재고일자', '기준일시'], how = 'left')
stock_m13c1c = pd.merge(stock_m13c1_19, stock_m13cc19, on= ['자전거번호', '재고일자', '기준일시'], how = 'left')
stock_m13c1d = pd.merge(stock_m13c1_24, stock_m13cc24, on= ['자전거번호', '재고일자', '기준일시'], how = 'left')

# 재고여부 생성 : '반납'이면 1, '대여' 0
stock_m13c1a['재고여부'] = np.where(stock_m13c1a['유형'] == '반납', 1, 0)
stock_m13c1a['대여중'] = np.where(stock_m13c1a['유형'] == '대여', 1, 0)
stock_m13c3a = stock_m13c1a.groupby(['기준대여소', '재고일자'])[['재고여부','대여중']].sum().reset_index()
stock_m13cnta = stock_m13c3a     # 일별재고수량 데이터 생성
stock_m13cnta.columns = ['대여소ID', '기준일자', '재고수량','대여중']

# 재고여부 생성 : '반납'이면 1, '대여' 0
stock_m13c1b['재고여부'] = np.where(stock_m13c1b['유형'] == '반납', 1, 0)
stock_m13c1b['대여중'] = np.where(stock_m13c1b['유형'] == '대여', 1, 0)
stock_m13c3b = stock_m13c1b.groupby(['기준대여소', '재고일자'])[['재고여부','대여중']].sum().reset_index()
stock_m13cntb = stock_m13c3b     # 일별재고수량 데이터 생성
stock_m13cntb.columns = ['대여소ID', '기준일자', '재고수량','대여중']

# 재고여부 생성 : '반납'이면 1, '대여' 0
stock_m13c1c['재고여부'] = np.where(stock_m13c1c['유형'] == '반납', 1, 0)
stock_m13c1c['대여중'] = np.where(stock_m13c1c['유형'] == '대여', 1, 0)
stock_m13c3c = stock_m13c1c.groupby(['기준대여소', '재고일자'])[['재고여부','대여중']].sum().reset_index()
stock_m13cntc = stock_m13c3c     # 일별재고수량 데이터 생성
stock_m13cntc.columns = ['대여소ID', '기준일자', '재고수량','대여중']

# 재고여부 생성 : '반납'이면 1, '대여' 0
stock_m13c1d['재고여부'] = np.where(stock_m13c1d['유형'] == '반납', 1, 0)
stock_m13c1d['대여중'] = np.where(stock_m13c1d['유형'] == '대여', 1, 0)
stock_m13c3d = stock_m13c1d.groupby(['기준대여소', '재고일자'])[['재고여부','대여중']].sum().reset_index()
stock_m13cntd = stock_m13c3d     # 일별재고수량 데이터 생성
stock_m13cntd.columns = ['대여소ID', '기준일자', '재고수량','대여중']


stock_m13cnt_9h = stock_m13cnta
stock_m13cnt_9h['대여시간'] = '09'
stock_m13cnt_14h = stock_m13cntb
stock_m13cnt_14h['대여시간'] = '14'
stock_m13cnt_19h = stock_m13cntc
stock_m13cnt_19h['대여시간'] = '19'
stock_m13cnt_24h = stock_m13cntd
stock_m13cnt_24h['대여시간'] = '00'

# stock_m13cnt_14h = stock_m13cnt
# stock_m13cnt_19h = stock_m13cnt
# stock_m13cnt_24h = stock_m13cnt

A9 = stock_m13cnt_9h.groupby('기준일자')[['재고수량','대여중']].sum()
A14 = stock_m13cnt_14h.groupby('기준일자')[['재고수량','대여중']].sum()
A19 = stock_m13cnt_19h.groupby('기준일자')[['재고수량','대여중']].sum()
A24 = stock_m13cnt_24h.groupby('기준일자')[['재고수량','대여중']].sum()


seg_stock_09 = pd.merge(seg_ym,stock_m13cnt_9h,left_on=['대여일자','대여시간'],right_on=['기준일자','대여시간'],how='left')
seg_stock_14 = pd.merge(seg_ym,stock_m13cnt_14h,left_on=['대여일자','대여시간'],right_on=['기준일자','대여시간'],how='left')
seg_stock_19 = pd.merge(seg_ym,stock_m13cnt_19h,left_on=['대여일자','대여시간'],right_on=['기준일자','대여시간'],how='left')
seg_stock_24 = pd.merge(seg_ym,stock_m13cnt_24h,left_on=['대여일자','대여시간'],right_on=['기준일자','대여시간'],how='left')


seg_stock_09_r = seg_stock_09.groupby(['대여일자','대여소ID','평가그룹'])[['재고수량','대여중']].sum().reset_index()
seg_stock_14_r = seg_stock_14.groupby(['대여일자','대여소ID','평가그룹'])[['재고수량','대여중']].sum().reset_index()
seg_stock_19_r = seg_stock_19.groupby(['대여일자','대여소ID','평가그룹'])[['재고수량','대여중']].sum().reset_index()
seg_stock_24_r = seg_stock_24.groupby(['대여일자','대여소ID','평가그룹'])[['재고수량','대여중']].sum().reset_index()

seg_stock_09_s = seg_stock_09_r.groupby(['대여소ID','평가그룹'])[['재고수량','대여중']].mean().reset_index()
seg_stock_14_s = seg_stock_14_r.groupby(['대여소ID','평가그룹'])[['재고수량','대여중']].mean().reset_index()
seg_stock_19_s = seg_stock_19_r.groupby(['대여소ID','평가그룹'])[['재고수량','대여중']].mean().reset_index()
seg_stock_24_s = seg_stock_24_r.groupby(['대여소ID','평가그룹'])[['재고수량','대여중']].mean().reset_index()

seg_stock_09_s = seg_stock_09_s.drop_duplicates()
seg_stock_14_s = seg_stock_14_s.drop_duplicates()
seg_stock_19_s = seg_stock_19_s.drop_duplicates()
seg_stock_24_s = seg_stock_24_s.drop_duplicates()

seg_stock_s = pd.concat([seg_stock_09_s,seg_stock_14_s,seg_stock_19_s,seg_stock_24_s],axis=0)
seg_stock_ss = seg_stock_s.groupby(['대여소ID','평가그룹'])[['재고수량','대여중']].sum().reset_index()
#test = seg_stock_s.groupby(['평가그룹'])[['재고수량','대여중']].sum().reset_index()

from itertools import product
seg_stock_station = seg_stock_ss['대여소ID'].unique()
evaluation_groups = [
    '봄가을맑음평일새벽', '봄가을맑음평일오전', '봄가을맑음평일오후', '봄가을맑음평일저녁',
    '봄가을맑음휴일새벽', '봄가을맑음휴일오전', '봄가을맑음휴일오후', '봄가을맑음휴일저녁',
    '봄가을비',
    '겨울맑음평일새벽', '겨울맑음평일오전', '겨울맑음평일오후', '겨울맑음평일저녁',
    '겨울맑음휴일새벽', '겨울맑음휴일오전', '겨울맑음휴일오후', '겨울맑음휴일저녁',
    '겨울눈',
    '여름맑음평일새벽', '여름맑음평일오전', '여름맑음평일오후', '여름맑음평일저녁',
    '여름맑음휴일새벽', '여름맑음휴일오전', '여름맑음휴일오후', '여름맑음휴일저녁',
    '여름비'
]
# 모든 조합 생성
all_combinations = list(product(seg_stock_station, evaluation_groups))

# 데이터프레임 생성
seg_stock_station = pd.DataFrame(all_combinations, columns=['대여소ID', '평가그룹'])

seg_stock_station = pd.merge(seg_stock_station,seg_stock_ss,on=['대여소ID', '평가그룹'],how='left')
seg_stock_station.replace(np.nan, 0, inplace=True)
seg_stock_station
std_deviation = seg_stock_station.groupby(['대여소ID'])['재고수량'].std().reset_index()
std_deviation.columns = ['대여소ID', '재고수량_표준편차']

seg_stock_station = seg_stock_station.merge(std_deviation, on='대여소ID', how='left')
seg_stock_station

mng_stock = mng_stock.groupby(['군집', '대여소ID','평가그룹_1','평가그룹_2'])[['회수량', '분배량']].sum().reset_index()
station_stock_r = pd.merge(seg_stock_station,mng_stock[['대여소ID','평가그룹_1','회수량','분배량']],left_on=['대여소ID','평가그룹'],right_on=['대여소ID','평가그룹_1'],how='left')
station_stock_r = station_stock_r[['대여소ID','평가그룹','재고수량','대여중','재고수량_표준편차','회수량','분배량']]
station_stock_r.replace(np.nan, 0, inplace=True)
station_stock_r
station_stock_r.to_excel(path_result + '//01.excel//재고량평가2//대여소_seg별_재고수량.xlsx',index=False)




########################################################################################################################
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-05-20')
seginfo_new = pd.read_pickle(path_result + '//03.shp//지리적군집분석//지리적_군집분석결과_1year_city.pkl')
stock_term = pd.read_pickle(path_result + '//01.excel//재고량평가//stock_term.pkl')
stock_seg_city = pd.read_pickle(path_result + '//01.excel//재고량평가//stock_seg_city.pkl')

aa1 = stock_seg_city[stock_seg_city["평가그룹"] == "봄가을맑음휴일새벽"]
aa12 = stock_seg_city[stock_seg_city["평가그룹"] == "봄가을맑음휴일오전"]

aa1.columns = ['대여소ID', '대여소명', '평가그룹_1', '대여건수평균_1', '대여건수편차_1', '반납건수평균_1', '반납건수편차_1', '재고수량_1']
aa12.columns = ['대여소ID', '대여소명', '평가그룹_2', '대여건수평균_2', '대여건수편차_2', '반납건수평균_2', '반납건수편차_2', '재고수량_2']

aa13 = pd.merge(aa1, aa12, on = ['대여소ID', '대여소명'], how = 'left')
aa13 = pd.merge(aa13, seginfo_new, on = ['대여소ID', '대여소명'], how = 'left')
aa13 = pd.merge(aa13, station_locations_gpkg[['대여소ID', 'gu']], on='대여소ID', how='left')



aa13[aa13['gu'].isna()] #gu값이 널값인 행 처리
# 조건에 따라 'gu' 컬럼 값 변경
aa13.loc[aa13['대여소ID'] == 'ST0019', 'gu'] = '서구'
aa13.loc[aa13['대여소ID'] == 'ST0873', 'gu'] = '중구'
aa13['도심'] = aa13['gu'].apply(lambda x: '구도심' if x in ['중구', '동구', '대덕구'] else '신도심' if x in ['서구', '유성구'] else '기타')


## 재고량 관리전략
aa13['재고그룹_1'] = np.where(aa13['재고수량_1'] <= -3, 'gr1',
                          np.where(aa13['재고수량_1'] <= -1, 'gr2',
                                   np.where(aa13['재고수량_1'] >= 3, 'gr5',
                                            np.where(aa13['재고수량_1'] >= 1, 'gr4',  'gr3' ))))

aa13['재고그룹_2'] = np.where(aa13['재고수량_2'] <= -3, 'gr1',
                          np.where(aa13['재고수량_2'] <= -1, 'gr2',
                                   np.where(aa13['재고수량_2'] >= 3, 'gr5',
                                            np.where(aa13['재고수량_2'] >= 1, 'gr4',  'gr3' ))))

aa13['누적재고량'] = aa13['재고수량_1'] + aa13['재고수량_2']
aa13['누적재고그룹'] = np.where(aa13['누적재고량'] <= -3, 'gr1',
                          np.where(aa13['누적재고량'] <= -1, 'gr2',
                                   np.where(aa13['누적재고량'] >= 3, 'gr5',
                                            np.where(aa13['누적재고량'] >= 1, 'gr4',  'gr3' ))))



aa13["회수량"] = np.where((aa13['재고수량_1'] > 0) & (aa13['재고수량_2'] < 0) , aa13['재고수량_1'],
                     np.where((aa13['재고수량_1'] > 0 ) & ( aa13['재고수량_2'] >= 0) , aa13['재고수량_1'] , 0 ))
aa13["회수량"] = np.where( aa13["회수량"] <= 0, 0, aa13["회수량"])
aa13["회수량"] = aa13["회수량"].round(0)
aa13['회수량'].sum()
## 대기Term 정보 추가
stock_rslt1 = aa13
stock_term['대여건수'].describe()
stock_term2 = stock_term[stock_term['대여건수'] >= 231] #50%       231.000000

stock_term2['term'].describe()
stock_term2["단기대기"] = np.where(stock_term2['term'] < 98, '단기1', np.where(stock_term2['term'] < 159, '단기2', '중장기' ))

stock_rslt1 = pd.merge(stock_rslt1, stock_term2, on = '대여소ID', how = 'left')
stock_rslt1.groupby(["단기대기"]).size()
stock_rslt1.groupby('도심')['대여건수'].size()

## 대기Term 반영한 분배량 가중치 산출
stock_rslt1["대여건수수정_2"] = np.where((stock_rslt1["단기대기"] == '단기1')&(stock_rslt1['대여건수평균_2'] <= 10), stock_rslt1['대여건수평균_2'] + stock_rslt1['대여건수편차_2'],stock_rslt1['대여건수평균_2'])


# '중구', '동구', '대덕구'에 해당하는 구도심 행들에 대해서만 0.5 가중치 적용
mask = stock_rslt1['gu'].isin(['중구', '동구', '대덕구'])
stock_rslt1.loc[mask, "대여건수수정_2"] = np.where((stock_rslt1.loc[mask, "단기대기"] == '단기1') & (stock_rslt1.loc[mask, '대여건수평균_2'] <= 10),
                                                 stock_rslt1.loc[mask, '대여건수평균_2'] + 0.5 * stock_rslt1.loc[mask, '대여건수편차_2'],
                                                 stock_rslt1.loc[mask, '대여건수평균_2'])

# 신도심 행들에 대해서는 다른 조건을 적용
stock_rslt1.loc[~mask, "대여건수수정_2"] = stock_rslt1.loc[~mask, '대여건수평균_2']

ppt = stock_rslt1[(stock_rslt1['도심'] == '구도심') & (stock_rslt1['단기대기'] == '단기1')]
ppt['대여건수평균_2'].mean()
ppt['대여건수수정_2'].mean()

stock_rslt1["재고수량수정_2"] = stock_rslt1["반납건수평균_2"] -  stock_rslt1["대여건수수정_2"]
stock_rslt1["분배량"] = np.where((stock_rslt1['재고수량수정_2'] <= -1) ,stock_rslt1['재고수량수정_2']*-1 ,0 )


divcnt = stock_rslt1["분배량"].sum()      # 분배량 총합 지정
getcnt = stock_rslt1["회수량"].sum()      # 회수량 총합 지정


stock_rslt1["분배량수정"] =((stock_rslt1["분배량"]/ divcnt) * getcnt).round(0)
stock_rslt1['분배량수정'].sum()

stock_rslt1["회수량수정"] = np.where((stock_rslt1["회수량"] > 0) & (stock_rslt1["분배량수정"] > 0),stock_rslt1["회수량"] - stock_rslt1["분배량수정"], stock_rslt1["회수량"])
stock_rslt1["회수량수정"] = np.where( stock_rslt1["회수량수정"] <= 0,0,stock_rslt1['회수량수정'])

stock_rslt1["분배량수정2"] = np.where((stock_rslt1["회수량"] > 0) & (stock_rslt1["분배량수정"] > 0),stock_rslt1['분배량수정'] - stock_rslt1['회수량'],stock_rslt1['분배량수정'])
stock_rslt1["분배량수정2"] = np.where( stock_rslt1["분배량수정2"] <= 0,0,stock_rslt1['분배량수정2'])


print(stock_rslt1['회수량수정'].sum())
print(stock_rslt1['분배량수정2'].sum())

#stock_rslt_구도심 = stock_rslt1[stock_rslt1['도심'] =='구도심']
#stock_rslt_구도심.groupby('평가그룹_2')['분배량수정2'].sum()
######################################################


## 군집모델 다시산출 : 지리적_군집분석결과_1year.pkl

stock_rslt2 = stock_rslt1[['대여소ID', '대여소명', '평가그룹_1', '대여건수평균_1', '대여건수편차_1', '반납건수평균_1',
       '반납건수편차_1', '재고수량_1', '평가그룹_2', '대여건수평균_2', '대여건수편차_2', '반납건수평균_2',
       '반납건수편차_2', '재고수량_2',  '재고그룹_1', '재고그룹_2', '누적재고량', '누적재고그룹', '회수량' ,'회수량수정',
        '분배량', '대여건수', 'term','단기대기', '대여건수수정_2', '재고수량수정_2', '분배량수정2','도심']]

stock_rslt2 = pd.merge(stock_rslt2, seginfo_new, on = ['대여소ID', '대여소명'], how = 'left')

## 분배량 0.5의 경우 너무 많음. 1이상으로 수정
stock_mng = stock_rslt2[(stock_rslt2["분배량수정2"] >= 0.5) | (stock_rslt2["회수량수정"] >= 0.5)]
stock_mng["회수량"] = stock_mng['회수량수정'].round(0)
stock_mng["분배량"] = (stock_mng['분배량수정2']).round(0)
stock_mng["회수_여부"] = np.where(stock_mng["회수량"] >= 1, 1, 0)
stock_mng["분배_여부"] = np.where(stock_mng["분배량"] >= 1, 1, 0)


mng_stock = stock_mng.groupby(['대여소ID','평가그룹_2'])[['회수량','분배량']].sum().reset_index()
path_result = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-06-14')
mng_stock.to_excel(path_result + '//01.excel//재고량평가2//대여소_seg별_재고수량.xlsx',index=False)