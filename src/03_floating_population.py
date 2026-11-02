###########################################################
# 과 제 명: AO3_대전시_공영자전거(타슈)
# 파 일 명: 03_202403_유동인구.py
# 작 성 자: 김민서
###########################################################

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

path_base     = "2024-04-26"

path_data_out     = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"01.외부")
path_data_in      = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"02.내부")
path_data_analyze = os.path.join(config_info["PATH_DATA_ANALYZE"])
path_data_output = os.path.join(config_info["PATH_DATA_OUTPUT"])

path_database = os.path.join(config_info["PATH_DATA_OUTPUT_DATEBASE"],path_base)
path_pretreat = os.path.join(config_info["PATH_DATA_OUTPUT_PRETREAT"],path_base)
path_middle   = os.path.join(config_info["PATH_DATA_OUTPUT_MIDDLE"]  ,path_base)
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,path_base)

import pandas as pd
import geopandas as gpd

## 분석대상 유동인구 데이터 2024.03
flow_pop = pd.read_csv(path_data_in+'\\50CELL_DAEJEON_202403.csv')

#%%
flow_pop_2 = flow_pop.dropna()  # 결측치가 있는 행 제거
# 1. etl_ymd 컬럼을 날짜 형식으로 변환하고 요일 컬럼을 추가합니다.
flow_pop_2['etl_ymd'] = pd.to_datetime(flow_pop_2['etl_ymd'], format='%Y%m%d')
flow_pop_2['day_of_week'] = flow_pop_2['etl_ymd'].dt.day_name()

# 2. 평일과 주말 데이터로 나눕니다.
weekday_df = flow_pop_2[flow_pop_2['day_of_week'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])]
weekend_df = flow_pop_2[flow_pop_2['day_of_week'].isin(['Saturday', 'Sunday'])]


#평일 주말 오후 5,6시만 추출
weekday_df1718 = weekday_df[weekday_df['timezn_cd'].isin([17,18])]
weekend_df1718 = weekend_df[weekend_df['timezn_cd'].isin([17,18])]

weekday_df1718 = weekday_df1718[['id','etl_ymd','admi_cd','total','x', 'y']]
groupby_cols = ['id','admi_cd','x', 'y']
weekday_df1718_g = weekday_df1718.groupby(groupby_cols)['total'].mean().reset_index()

weekend_df1718 = weekend_df1718[['id','etl_ymd','admi_cd','total','x', 'y']]
groupby_cols = ['id','admi_cd','x', 'y']
weekend_df1718_g = weekend_df1718.groupby(groupby_cols)['total'].mean().reset_index()

weekday_df1718_g = gpd.GeoDataFrame(weekday_df1718_g,geometry = gpd.points_from_xy(weekday_df1718_g['x'],weekday_df1718_g['y']),crs=5179)
weekend_df1718_g = gpd.GeoDataFrame(weekend_df1718_g,geometry = gpd.points_from_xy(weekend_df1718_g['x'],weekend_df1718_g['y']),crs=5179)
#%%
weekday_df1718_g.to_csv(path_data_analyze + '\\02.내부\\10.유동인구\\01.csv\\평일유동인구_1718시_202403_g.csv',encoding='cp949')
weekend_df1718_g.to_csv(path_data_analyze + '\\02.내부\\10.유동인구\\01.csv\\주말유동인구_1718시_202403_g.csv',encoding='cp949')


#위의 CSV 데이터를 QGIS 에서 GPKG로 변환함 (카텍 데이터 -> 5179로 변환)

#평일 18-19시 유동인구 데이터 100m 격자 매핑
weekday_df1718_g = gpd.read_file(path_data_analyze + '\\02.내부\\10.유동인구\\02.gpkg\\평일유동인구_1718시_202403_g.gpkg',driver='GPKG')
weekend_df1718_g = gpd.read_file(path_data_analyze + '\\02.내부\\10.유동인구\\02.gpkg\\주말유동인구_1718시_202403_g.gpkg',driver='GPKG')
sigungu = gpd.read_file(path_data_analyze + '\\01.외부\\행정경계_시군구\\sigungu.gpkg',driver='GPKG') #대전시 시군구 경계면
grid_100 = gpd.read_file(path_result+"\\03.shp\\격자_거주인구\\GRID_100_HOMEPOP.gpkg", driver='GPKG') # 대전시 100m 격자 읽어오기
hjd_cd = pd.read_excel(path_data_out + '\\행정동코드.xlsx')


# 202403 평일 유동인구 구정보 매핑
weekday_df1718_sgg = pd.merge(weekday_df1718_g[['id','admi_cd','total','geometry']],hjd_cd[['행정동코드','시군구명']],left_on='admi_cd',right_on='행정동코드')
weekend_df1718_sgg = pd.merge(weekend_df1718_g[['id','admi_cd','total','geometry']],hjd_cd[['행정동코드','시군구명']],left_on='admi_cd',right_on='행정동코드')

#평일 유동인구 데이터 저장
flow_wd_usung = weekday_df1718_sgg[weekday_df1718_sgg['시군구명'] == '유성구']
flow_wd_daeduck = weekday_df1718_sgg[weekday_df1718_sgg['시군구명'] == '대덕구']
flow_wd_seo = weekday_df1718_sgg[weekday_df1718_sgg['시군구명'] == '서구']
flow_wd_jung = weekday_df1718_sgg[weekday_df1718_sgg['시군구명'] == '중구']
flow_wd_dong = weekday_df1718_sgg[weekday_df1718_sgg['시군구명'] == '동구']

weekday_df1718_sgg.to_file(path_result+"\\03.shp\\유동인구\\평일유동인구_202403_1718.gpkg", driver="GPKG")
flow_wd_usung.to_file(path_result+"\\03.shp\\유동인구\\평일유동인구_유성구_202403_1718.gpkg", driver="GPKG")
flow_wd_daeduck.to_file(path_result+"\\03.shp\\유동인구\\평일유동인구_대덕구_202403_1718.gpkg", driver="GPKG")
flow_wd_seo.to_file(path_result+"\\03.shp\\유동인구\\평일유동인구_서구_202403_1718.gpkg", driver="GPKG")
flow_wd_jung.to_file(path_result+"\\03.shp\\유동인구\\평일유동인구_중구_202403_1718.gpkg", driver="GPKG")
flow_wd_dong.to_file(path_result+"\\03.shp\\유동인구\\평일유동인구_동구_202403_1718.gpkg", driver="GPKG")

#주말 유동인구 데이터 저장
flow_wk_usung = weekend_df1718_sgg[weekend_df1718_sgg['시군구명'] == '유성구']
flow_wk_daeduck= weekend_df1718_sgg[weekend_df1718_sgg['시군구명'] == '대덕구']
flow_wk_seo = weekend_df1718_sgg[weekend_df1718_sgg['시군구명'] == '서구']
flow_wk_jung = weekend_df1718_sgg[weekend_df1718_sgg['시군구명'] == '중구']
flow_wk_dong = weekend_df1718_sgg[weekend_df1718_sgg['시군구명'] == '동구']

weekend_df1718_sgg.to_file(path_result+"\\03.shp\\유동인구\\주말유동인구_202403_1718.gpkg", driver="GPKG")
flow_wk_usung.to_file(path_result+"\\03.shp\\유동인구\\주말유동인구_유성구_202403_1718.gpkg", driver="GPKG")
flow_wk_daeduck.to_file(path_result+"\\03.shp\\유동인구\\주말유동인구_대덕구_202403_1718.gpkg", driver="GPKG")
flow_wk_seo.to_file(path_result+"\\03.shp\\유동인구\\주말유동인구_서구_202403_1718.gpkg", driver="GPKG")
flow_wk_jung.to_file(path_result+"\\03.shp\\유동인구\\주말유동인구_중구_202403_1718.gpkg", driver="GPKG")
flow_wk_dong.to_file(path_result+"\\03.shp\\유동인구\\주말유동인구_동구_202403_1718.gpkg", driver="GPKG")
