###########################################################
# 과 제 명: AO3_대전시_공영자전거(타슈)
# 파 일 명: 03_현황분석.ipynb
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
# [분석 처리 시작]
fl.f_log_line("03_현황분석.ipynb")
###########################################################
# 모 듈 명: 모 듈 명 - 09.구도심현황분석(추가).py
# 파 일 명: 09.구도심현황분석(추가).py
# 작 성 자: 김민서
# 설    명: 대전시 타슈 분석 현황분석
# 파일 버전: v1.0 [2024.04.01]
# 작성 일자: 2024.06.10
# 수정 일자: 2024.006.10
###########################################################
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
# 1.1.SQLite 저장시 사용됨
##name_database = f"DB_{config_info['과제ID']}_202309.db" #
#==================================================================================================
#########################################################################################################
# 필요라이브러리
import math
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
import seaborn as sns
from shapely.geometry import Point, LineString
import pickle

# 글꼴 설정
# 그래프 시각화를 위한 폰트 설정
font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
font_list[:10]  # 일부만 출력
font_path='C:\\Windows\\Fonts'
mpl.rcParams['font.family'] = 'Malgun Gothic'
# 한글 폰트의 경우 글꼴을 찾을 수 없다는 경고가 나오는 경우에는 다음과 같이 경고를 무시
import warnings
warnings.filterwarnings('ignore')
#########################################################################################################
# 대여이력정보 최종 분석 데이터
result_bike_data = pd.read_pickle(path_data_output+'//1.pretreatment//02.내부//01.대여반납이력//result_bike_data_0430.pkl')
station_locations = pd.read_csv(path_data_output+'//1.pretreatment//02.내부//02.대여소정보//station_locations.csv',encoding='cp949') # 타슈 대여소 내역 데이터
station_locations_gpkg = gpd.read_file(path_data_output+'//3.result//2024-04-25//03.shp//대여소_위치정보.gpkg', driver='GPKG') # 타슈 대여소 내역 데이터 위치좌표

#외부데이터 읽어오기(전처리 후)
# 자체다운로드 데이터 읽어오기
kosis_pop = pd.read_csv(path_data_analyze + '//01.외부//kosis_주민등록인구//kosis_5gu_age.csv', encoding='cp949')# kosis_주민등록인구 파일 읽어오기
dj_bjd = pd.read_csv(path_data_analyze + '//01.외부//법정동코드//법정동코드.csv', encoding='cp949') # 법정동 코드파일 읽어오기
SIGUNGU = gpd.read_file(path_data_analyze + '//01.외부//행정경계_시군구//sigungu.gpkg' , driver='GPKG') # 대전시 행정경계 읽어오기
grid_100 = gpd.read_file(path_data_analyze + '//01.외부//100m격자//grid_100.gpkg', driver='GPKG') # 대전시 100m 격자 읽어오기
BUBJUNGDONG = gpd.read_file(path_data_analyze + '//01.외부//법정동경계//bupjungdong.gpkg', driver='GPKG')


bike = result_bike_data.copy()

# 도심구분 컬럼 추가
bike['도심구분'] = bike['대여_구'].apply(lambda x: '구도심' if x in ['동구', '대덕구', '중구'] else '신도심')

#필요컬럼 추출
bike = bike[['대여일시_시분초','대여일자', '대여연도', '대여월','대여일시_시','도심구분','대여_구','대여_동', '대여_대여소ID', '대여_대여소명',
             '반납일시_시분초','반납일자','반납연도','반납월','반납일시_시','반납_구','반납_동','반납_대여소ID','반납_대여소명',
             '이용시간(분)', '이용거리(km)', '연령대', '성별', '내외국인구분',]]


hourly_counts_rental = bike.groupby(['대여일시_시','도심구분','대여_구','성별','연령대']).size().reset_index(name='대여건수')
# 시작 날짜와 종료 날짜 지정
start_date = bike['대여일시_시'].min()
end_date = bike['반납일시_시'].max()

# 1시간 간격의 시간 값 생성
hourly_time = pd.date_range(start=start_date, end=end_date, freq='H')

# 기준시간 데이터프레임 생성
time_df = pd.DataFrame({'기준일자시간': hourly_time}).reset_index(drop=True)
time_df['기준일자'] = pd.to_datetime(time_df['기준일자시간']).dt.strftime('%Y-%m-%d')
time_df['기준연도'] = time_df['기준일자시간'].dt.year
time_df['기준월'] = time_df['기준일자시간'].dt.month
time_df['시간대'] = pd.to_datetime(time_df['기준일자시간']).dt.hour
time_df['요일'] = time_df['기준일자시간'].dt.day_name()
# 기준시간 데이터프레임에 시간대 카운트 추가
# 대여건수 데이터프레임에서 대여일자와 대여시간대에 해당하는 데이터만 추출하여 병합
merged_df = time_df.merge(hourly_counts_rental, left_on=['기준일자시간'], right_on=['대여일시_시'], how='left')
merged_df = merged_df.dropna()
merged_df
time_1hour = merged_df.copy()

# 기준월에 따른 계절 매핑
season_mapping = {
    12: '겨울', 1: '겨울', 2: '겨울',
    3: '봄', 4: '봄', 5: '봄',
    6: '여름', 7: '여름', 8: '여름',
    9: '가을', 10: '가을', 11: '가을'
}

# 계절 컬럼 추가
time_1hour['계절'] = time_1hour['기준월'].map(season_mapping)
#time_1hour.to_excel(path_result+'//01.excel//도심현황//도심별_이용현황(1).xlsx',encoding='cp949',index=False)

#같은 일별로는 sum ()
time_1day = time_1hour.groupby(['기준연도','기준월','기준일자','요일','도심구분','대여_구','성별','연령대'])['대여건수'].sum().reset_index()

result_1 = time_1day.groupby(['기준연도','기준월','기준일자','도심구분','대여_구'])['대여건수'].sum().reset_index()
result_1_1 = result_1.groupby(['기준연도','기준월','도심구분','대여_구'])['대여건수'].mean().reset_index()
result_1_2 = result_1.groupby(['기준연도','기준월','도심구분','대여_구'])['대여건수'].sum().reset_index()
result_1_2


result_2 = time_1day.groupby(['기준연도','기준월','기준일자','도심구분','대여_구','성별'])['대여건수'].sum().reset_index()
result_2_2 = result_2.groupby(['기준연도','기준월','도심구분','대여_구','성별'])['대여건수'].mean().reset_index()
result_2_3 = result_2.groupby(['기준연도','기준월','도심구분','대여_구','성별'])['대여건수'].sum().reset_index()


result_3 = time_1day.groupby(['기준연도','기준월','기준일자','도심구분','대여_구','연령대'])['대여건수'].sum().reset_index()
result_3_3 = result_3.groupby(['기준연도','기준월','도심구분','대여_구','연령대'])['대여건수'].mean().reset_index()
result_3_4 = result_3.groupby(['기준연도','기준월','도심구분','대여_구','연령대'])['대여건수'].sum().reset_index()

#구별 일평균
result_1_1.to_excel(path_result+'//01.excel//도심현황//도심별(구)_일평균대여건수.xlsx',index=False)
#구별 성별 일평균
result_2_2.to_excel(path_result+'//01.excel//도심현황//도심별(구)성별_일평균대여건수.xlsx',index=False)
#구별 성별 합계
result_2_3.to_excel(path_result+'//01.excel//도심현황//도심별(구)성별_대여건수.xlsx',index=False)
#구별 연령대별 일평균
result_3_3.to_excel(path_result+'//01.excel//도심현황//도심별(구)연령대_일평균대여건수.xlsx',index=False)
#구별 연령대별 합계
result_3_4.to_excel(path_result+'//01.excel//도심현황//도심별(구)연령대_대여건수.xlsx',index=False)

























