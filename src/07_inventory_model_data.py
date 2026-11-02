###########################################################
# 과 제 명: AO3_대전시_공영자전거(타슈)
# 파 일 명: 06.Clustering.py
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

path_base     = "2024-05-24"

path_data_out     = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"01.외부")
path_data_in      = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"02.내부")
path_data_analyze = os.path.join(config_info["PATH_DATA_ANALYZE"])
path_data_output = os.path.join(config_info["PATH_DATA_OUTPUT"])

path_database = os.path.join(config_info["PATH_DATA_OUTPUT_DATEBASE"],path_base)
path_pretreat = os.path.join(config_info["PATH_DATA_OUTPUT_PRETREAT"],path_base)
path_middle   = os.path.join(config_info["PATH_DATA_OUTPUT_MIDDLE"]  ,path_base)
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-05-20')

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime
import holidays
import numpy as np

#차량을 이용한 배치,재배치 데이터
batch_management = pd.read_csv(path_data_in+'//대전시 공영자전거 타슈 대여이력 정보(24년 4월~5월, 관리자재배치실적)//타슈 관리자 배치,재배치,점검요청,입고(관리자실적)_2024_0523.csv',encoding='cp949')
# 대여이력정보 최종 분석 데이터
result_bike_data = pd.read_pickle(path_data_output+'//1.pretreatment//02.내부//01.대여반납이력//result_bike_data_0430.pkl')
result_bike_data0405 = pd.read_pickle(path_data_output+'//1.pretreatment//02.내부//01.대여반납이력//result_bike_data_0524.pkl')

#대여일자를 기준으로 2024년 3월 데이터만 추출
bike_data_202403 = result_bike_data[(result_bike_data['대여연도'] == 2024) & (result_bike_data['대여월'] == 3)]
bike_data_1year = result_bike_data[(result_bike_data['대여일자'] >= '2023-02-01') & (result_bike_data['대여일자'] <= '2024-03-31')]
bk_20240405 = result_bike_data0405.copy()



# 자기회귀 반납건 추출 : 52,139건
self_rentals = bike_data_202403[bike_data_202403['대여_대여소명'] == bike_data_202403['반납_대여소명']]
self_rentals = self_rentals[['자전거번호','대여일자','대여_대여소명','반납일자','반납_대여소명','이용거리(km)','이용시간(분)']]

# 이용거리 상자 그림 그리기
plt.figure(figsize=(5, 3))
plt.boxplot(self_rentals['이용거리(km)'])
plt.title('이용거리 상자 그림')
plt.ylabel('이용거리(km)')
plt.show()

# 이상치 제거 기준 설정 (IQR을 사용)
Q1 = self_rentals['이용거리(km)'].quantile(0.25)
Q3 = self_rentals['이용거리(km)'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR



filtered_data = self_rentals[(self_rentals['이용거리(km)'] >= lower_bound) & (self_rentals['이용거리(km)'] <= upper_bound)]

# 이상치 제거 후 이용거리 히스토그램 그리기
plt.figure(figsize=(5, 3))
plt.hist(filtered_data['이용거리(km)'], bins=30, edgecolor='k', alpha=0.7)
plt.axvline(filtered_data['이용거리(km)'].mean(), color='r', linestyle='dashed', linewidth=1)
plt.title('자기회귀 대여건들의 이용거리 분포 (이상치 제거 후)')
plt.xlabel('이용거리(km)')
plt.ylabel('빈도')
plt.show()

# 이용거리 평균값 계산
mean_distance = filtered_data['이용거리(km)'].mean()
print(f"이용거리 평균값: {mean_distance:.2f} km")


#(동료)에게 드린 1년치 주말공휴일 구분 및 이용건수 산출 데이터
bike_data_1year_OUT = bike_data_1year.copy()
bike_data_1year_OUT = bike_data_1year_OUT[bike_data_1year_OUT['이용거리(km)'] >= 0.1]

# 대여소별  계산
daily_rentals = bike_data_1year_OUT.groupby(['대여일자']).size().reset_index(name='일별 총대여건수')
# 대여소별 유니크한 자전거 수 계산
unique_bicycles = bike_data_1year_OUT.groupby(['대여일자'])['자전거번호'].nunique().reset_index(name='일별 유니크한 자전거수')
daily_rentals2 =  pd.merge(daily_rentals, unique_bicycles, on=['대여일자'])
daily_rentals2['대여연도'] = daily_rentals2['대여일자'].dt.year
daily_rentals2['대여월'] = daily_rentals2['대여일자'].dt.month
# 대한민국 공휴일을 확인할 holidays 객체 생성
daily_rentals4 = daily_rentals2.copy()
kr_holidays = holidays.Korea()
# 주말 및 공휴일 여부 확인
daily_rentals4['주말_공휴일여부'] = daily_rentals4['대여일자'].apply(lambda x: '주말 및 공휴일' if x.strftime('%Y-%m-%d') in kr_holidays or x.weekday() >= 5 else '평일')
daily_rentals4 = daily_rentals4[['대여연도','대여월','대여일자','일별 총대여건수','일별 유니크한 자전거수','주말_공휴일여부']]

daily_rentals4_g = daily_rentals4.groupby(['대여연도','대여월','대여일자','주말_공휴일여부'])[['일별 총대여건수','일별 유니크한 자전거수']].sum().reset_index()
daily_rentals4_g.to_pickle(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year.pkl')

# seginfo_new = pd.read_pickle(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year.pkl')






















