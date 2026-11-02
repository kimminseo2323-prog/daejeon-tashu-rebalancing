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
# 모 듈 명: 모 듈 명 - 03_현황분석.ipynb
# 파 일 명: 03_현황분석.ipynb
# 작 성 자: 김민서
# 설    명: 대전시 타슈 분석 현황분석
# 파일 버전: v1.0 [2024.04.01]
# 작성 일자: 2024.04.03
# 수정 일자: 2024.04.25 00:00
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
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-04-30')
# 1.1.SQLite 저장시 사용됨
##name_database = f"DB_{config_info['과제ID']}_202309.db" #
#==================================================================================================
###############################################################################
# 작성자 : 김민서
# 최초작성일자 : 2024-04-23
# 최종수정일자 : 2024-04-25
# 제목 : 대전교통공사 타슈 재배치 분석 데이터 현황분석
###############################################################################
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
###############################################################################

#########################################################################################################
# 대전 데이터 읽어오기
#########################################################################################################
# 대여이력정보 최종 분석 데이터
result_bike_data = pd.read_pickle(path_data_output+'//1.pretreatment//02.내부//01.대여반납이력//result_bike_data_0430.pkl')
weather_data = pd.read_pickle(path_data_analyze+'//02.내부//02.기상정보//weather_data.pkl') # 기상정보 데이터 (2022.07 ~ 2024.03)
dj_air = pd.read_csv(path_data_analyze +'//02.내부//02.기상정보//air_data.csv',encoding='cp949')
station_locations = pd.read_csv(path_data_output+'//1.pretreatment//02.내부//02.대여소정보//station_locations.csv',encoding='cp949') # 타슈 대여소 내역 데이터
station_locations_gpkg = gpd.read_file(path_data_output+'//3.result//2024-04-25//03.shp//대여소_위치정보.gpkg', driver='GPKG') # 타슈 대여소 내역 데이터 위치좌표
################################### 현황분석 ###################################
bike = result_bike_data.copy()
batch_management_data =  pd.read_csv(path_data_in+"//타슈 데이터 분석 사업 자료(대여이력, 대여소 등)//타슈 관리자 배치,재배치,점검요청,입고.csv",encoding='cp949') # 타슈 관리자 배치,재배치,점검요청,입고 데이터
daily_membership_data = pd.read_csv(path_data_in+"//타슈 데이터 분석 사업 자료(대여이력, 대여소 등)//일별 회원 가입 및 탈퇴정보.csv",encoding='cp949') #일별 회원 가입 및 탈퇴정보

#외부데이터 읽어오기(전처리 후)
# 자체다운로드 데이터 읽어오기
kosis_pop = pd.read_csv(path_data_analyze + '//01.외부//kosis_주민등록인구//kosis_5gu_age.csv', encoding='cp949')# kosis_주민등록인구 파일 읽어오기
dj_bjd = pd.read_csv(path_data_analyze + '//01.외부//법정동코드//법정동코드.csv', encoding='cp949') # 법정동 코드파일 읽어오기
SIGUNGU = gpd.read_file(path_data_analyze + '//01.외부//행정경계_시군구//sigungu.gpkg' , driver='GPKG') # 대전시 행정경계 읽어오기
grid_100 = gpd.read_file(path_data_analyze + '//01.외부//100m격자//grid_100.gpkg', driver='GPKG') # 대전시 100m 격자 읽어오기
BUBJUNGDONG = gpd.read_file(path_data_analyze + '//01.외부//법정동경계//bupjungdong.gpkg', driver='GPKG')
bike03 = bike[(bike['대여연도'] == '2024')&(bike['대여월'] == '3')]
## ppt 내용 (간단현황)
# 대여소별 대여수를 계산합니다.
count_by_station = bike.groupby(['대여_대여소ID', '대여_대여소명']).size().reset_index(name='대여수').sort_values(by='대여수', ascending=False)
# 결과를 출력합니다.
print("가장 대여수가 많은 대여소:")
print(count_by_station.reset_index()) # 한밭수목원(동원)
#count_by_station['대여수'].sum()

return_station = bike[bike['대여_대여소명'] == '한밭수목원(동원)']
count_by_return_station = return_station.groupby(['반납_대여소ID', '반납_대여소명']).size().reset_index(name='반납수').sort_values(by='반납수', ascending=False)
print(count_by_return_station.reset_index())

# 연도,월,시간,요일별 대여/반납현황
# 건수 COUNTS
hourly_counts_rental = bike.groupby(['대여일시_시']).size().reset_index(name='대여건수')
hourly_counts_return = bike.groupby(['반납일시_시']).size().reset_index(name='반납건수')
# 시작 날짜와 종료 날짜 지정
start_date = '2022-08-01 00:00:00'
end_date = '2024-04-05 23:00:00'

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

time_1hour = merged_df[['기준일자시간','기준일자','기준연도','기준월','요일','시간대','대여건수']]
time_1hour = time_1hour.fillna(0)
# 기준월에 따른 계절 매핑
season_mapping = {
    12: '겨울', 1: '겨울', 2: '겨울',
    3: '봄', 4: '봄', 5: '봄',
    6: '여름', 7: '여름', 8: '여름',
    9: '가을', 10: '가을', 11: '가을'
}

# 계절 컬럼 추가
time_1hour['계절'] = time_1hour['기준월'].map(season_mapping)
#time_1hour.to_excel(path_result+'//01.excel//대여반납현황(일자,시간,요일).xlsx',index=False)

# 행정구역별 대여/반납 현황
bike_dong = bike.copy()
bike_dong['대여_구동'] = bike_dong['대여_구'] + ' ' + bike_dong['대여_동']
bike_dong['반납_구동'] = bike_dong['반납_구'] + ' ' + bike_dong['반납_동']

대여_구동 = bike_dong.groupby('대여_구동').size()
반납_구동 = bike_dong.groupby('반납_구동').size()

# 데이터프레임 생성
대여반납_동별 = pd.DataFrame({'대여건수': 대여_구동, '반납건수': 반납_구동})
대여반납_동별 = 대여반납_동별.reset_index()
대여반납_동별 = 대여반납_동별.rename(columns={'index': '대전_구동'})
대여반납_동별 = 대여반납_동별.fillna(0)
# dj_bjd 대전시 전체 법정동 정보
dj_bjd_대여반납 = pd.merge(dj_bjd,대여반납_동별,left_on= '구동' ,right_on='대전_구동',how='outer')
dj_bjd_대여반납[['대여건수', '반납건수']] = dj_bjd_대여반납[['대여건수', '반납건수']].fillna(0)
dj_bjd_대여반납 = dj_bjd_대여반납[['법정동코드','구동','시','구','동','대여건수','반납건수']]
dj_bjd_대여반납 = dj_bjd_대여반납[(dj_bjd_대여반납['구'] != '0') & (dj_bjd_대여반납['동'] != '0')]
# 법정동코드 컬럼을 문자열로 변환 후 '00' 제거
dj_bjd_대여반납['법정동코드'] = dj_bjd_대여반납['법정동코드'].astype(str).str[:-2]

dj_bjd_대여반납.to_excel(path_result+'//01.excel//대여반납현황(행정구역(법정동).xlsx',index=False) #excel 저장

dj_bjd_대여반납_gpkg = pd.merge(dj_bjd_대여반납,BUBJUNGDONG[['EMD_CD','geometry']],left_on='법정동코드',right_on='EMD_CD',how='left')
dj_bjd_대여반납_gpkg.drop('EMD_CD', axis=1, inplace=True)
dj_bjd_대여반납_gpkg = gpd.GeoDataFrame(dj_bjd_대여반납_gpkg, geometry='geometry')
dj_bjd_대여반납_gpkg.to_file(path_result+'//03.shp//법정동_현황//대여반납현황(행정구역(법정동).gpkg',driver='GPKG') #shp 저장

# 대여,반납이력이 0건인 법정동 중 대여소가 존재하는 행정동
dj_bjd_대여반납_0 = dj_bjd_대여반납[(dj_bjd_대여반납['대여건수'] == 0) & (dj_bjd_대여반납['반납건수'] == 0)]

# 대여소별 대여 반납 현환
bike_station = bike.copy()

대여_대여소 = bike_station.groupby(['대여연도','대여월','대여_대여소ID','대여_대여소명','대여_구','대여_동']).size()
반납_대여소 = bike_station.groupby(['반납연도','반납월','반납_대여소ID','반납_대여소명','반납_구','반납_동']).size()
# 데이터프레임 생성
대여반납_대여소 = pd.DataFrame({'대여건수': 대여_대여소, '반납건수': 반납_대여소})
대여반납_대여소 = 대여반납_대여소.reset_index()
대여반납_대여소 = 대여반납_대여소.rename(columns={'index': '대여소'})
대여반납_대여소[['대여건수', '반납건수']] = 대여반납_대여소[['대여건수', '반납건수']].fillna(0)
# level_0 컬럼을 대여소ID로, level_1 컬럼을 대여소명으로 변경
대여반납_대여소.rename(columns={'level_0': '기준연도','level_1': '기준월','level_2': '이력_대여소ID', 'level_3': '이력_대여소명','level_4':'대전_구','level_5':'대전_동'}, inplace=True)
대여반납_station = pd.merge(대여반납_대여소,station_locations,left_on=['이력_대여소ID','이력_대여소명'],right_on=['id','name'],how='outer')
대여반납_station = 대여반납_station[['기준연도','기준월','이력_대여소ID','이력_대여소명','id', 'station_cd', 'name', '대전_구', '대전_동', 'gu','dong','대여건수','반납건수']]
대여반납_station['대전_구동'] = 대여반납_station['대전_구'] + ' ' + 대여반납_station['대전_동']
대여반납_station.rename(columns={'id': '정식_대여소ID', 'station_cd': '정식_station_cd','name':'정식_대여소명','gu':'대여소_구','dong':'대여소_동'}, inplace=True)
대여반납_station = 대여반납_station.fillna('-')
대여반납_station.to_excel(path_result+'//01.excel//대여반납현황(대여소).xlsx',index=False)

#정식 대여소 기준
top_tail_station = pd.merge(대여반납_대여소,station_locations,left_on=['이력_대여소ID','이력_대여소명'],right_on=['id','name'])
top_tail_station = top_tail_station[['gu','dong','이력_대여소ID','station_cd','이력_대여소명','대여건수','반납건수','x_pos','y_pos']]
top_tail_station.rename(columns={'gu':'대여소_구','dong':'대여소_동','이력_대여소ID': '정식_대여소ID', 'station_cd': '정식_station_cd','이력_대여소명':'정식_대여소명'}, inplace=True)
top_tail_station['대여소_구동'] = top_tail_station['대여소_구'] + ' ' + top_tail_station['대여소_동']
# 대여와 반납이 모두 0인 행 필터링
zero_counts = top_tail_station[(top_tail_station['대여건수'] == 0) & (top_tail_station['반납건수'] == 0)]
#print(zero_counts)
# 위도와 경도를 사용하여 Point 객체 생성
geometry = [Point(xy) for xy in zip(top_tail_station['y_pos'], top_tail_station['x_pos'])]
# GeoDataFrame 생성
from pyproj import CRS

# 좌표계를 EPSG 5186로 정의
crs = CRS.from_epsg(5186)
# GeoDataFrame 생성
top_tail_station = gpd.GeoDataFrame(top_tail_station, geometry=geometry, crs=crs)

# SHP 파일로 저장
top_tail_station.to_file(path_result+'//03.shp//대여소_현황//대여소_위치정보.gpkg', driver='GPKG')
top_tail_station.to_excel(path_result+'//01.excel//대여소_위치정보.xlsx',index=False)

# 대여소 위치 _구별 저장
station_usung = top_tail_station[top_tail_station['대여소_구'] == '유성구']
station_seo = top_tail_station[top_tail_station['대여소_구'] == '서구']
station_jung = top_tail_station[top_tail_station['대여소_구'] == '중구']
station_daeduck = top_tail_station[top_tail_station['대여소_구'] == '대덕구']
station_dong = top_tail_station[top_tail_station['대여소_구'] == '동구']
station_usung.to_file(path_result+'//03.shp//대여소_현황//대여소_위치정보(유성구).gpkg', driver='GPKG')
station_seo.to_file(path_result+'//03.shp//대여소_현황//대여소_위치정보(서구).gpkg', driver='GPKG')
station_jung.to_file(path_result+'//03.shp//대여소_현황//대여소_위치정보(중구).gpkg', driver='GPKG')
station_daeduck.to_file(path_result+'//03.shp//대여소_현황//대여소_위치정보(대덕구).gpkg', driver='GPKG')
station_dong.to_file(path_result+'//03.shp//대여소_현황//대여소_위치정보(동구).gpkg', driver='GPKG')
# 대여건수 상위 대여소 TOP5, 하위 대여소 TOP5 위치저장
# 조건을 리스트로 정의합니다.
conditions = ['한밭수목원(동원)', '무역전시관입구(택시승강장)(1)', '타슈관제센터', '유성구청(31)', '타임월드']
# '정식_대여소명'이 조건 중 하나에 해당하는 행들을 가져옵니다.
top5_points = top_tail_station[top_tail_station['정식_대여소명'].isin(conditions)]

# 조건을 리스트로 정의합니다.
conditions_tail = ['벤쳐타운 장열실관 앞 버스정류장', '신동 중이온가속기연구소 입구', '용산동 호반써밋(401동)', '한밭대학교 그린에너지관','용산동 호반써밋(205동)']
# '정식_대여소명'이 조건 중 하나에 해당하는 행들을 가져옵니다.
tail5_points = top_tail_station[top_tail_station['정식_대여소명'].isin(conditions_tail)]
top5_points.to_file(path_result+'//03.shp//대여소_현황//대여건수_상위TOP5대여소_위치정보.gpkg', driver='GPKG')
tail5_points.to_file(path_result+'//03.shp//대여소_현황//대여건수_하위TOP5대여소_위치정보.gpkg', driver='GPKG')

conditions_top_tail = ['한밭수목원(동원)', '무역전시관입구(택시승강장)(1)', '타슈관제센터', '유성구청(31)', '타임월드','벤쳐타운 장열실관 앞 버스정류장', '신동 중이온가속기연구소 입구', '용산동 호반써밋(401동)', '한밭대학교 그린에너지관','용산동 호반써밋(205동)']
top5_time = bike[bike['대여_대여소명'].isin(conditions_top_tail)]

# 시작 날짜와 종료 날짜 지정
start_date = '2022-08-01 00:00:00'
end_date = '2024-04-05 23:00:00'

# 1시간 간격의 시간 값 생성
hourly_time = pd.date_range(start=start_date, end=end_date, freq='H')

# 기준시간 데이터프레임 생성
time_df = pd.DataFrame({'기준일자시간': hourly_time}).reset_index(drop=True)
time_df['기준일자'] = pd.to_datetime(time_df['기준일자시간']).dt.strftime('%Y-%m-%d')
time_df['기준연도'] = time_df['기준일자시간'].dt.year
time_df['기준월'] = time_df['기준일자시간'].dt.month
time_df['시간대'] = pd.to_datetime(time_df['기준일자시간']).dt.hour
time_df['요일'] = time_df['기준일자시간'].dt.day_name()

# 대여소명별로 시간대별 대여 및 반납건수를 계산하기 위해 기준시간 데이터프레임과 병합
top5_time = pd.merge(time_df, top5_time, left_on=['기준일자시간'], right_on=['대여일시_시'], how='left')
top5_time = top5_time.fillna(0)

def plot_rental_return_by_station(bike_data, station_name):
    top5_time_1 = bike_data[bike_data['대여_대여소명'] == station_name]
    top5_time_ = top5_time_1.groupby('시간대').size()

    # 그래프 그리기
    plt.figure(figsize=(10, 6))

    # 평일 대여/반납 그래프
    plt.plot(top5_time_.index, top5_time_.values, label='평일 대여', marker='o')

    plt.xlabel('시간')
    plt.ylabel('횟수')
    plt.xticks(range(24))  # x축 시간 설정
    plt.legend()
    plt.grid(True)
    plt.show()
# 사용 예시
plot_rental_return_by_station(top5_time, '한밭수목원(동원)')
plot_rental_return_by_station(top5_time, '무역전시관입구(택시승강장)(1)')
plot_rental_return_by_station(top5_time, '타슈관제센터')
plot_rental_return_by_station(top5_time, '유성구청(31)')
plot_rental_return_by_station(top5_time, '타임월드')


def plot_rental_return_by_multiple_stations(bike_data, station_names):
    plt.figure(figsize=(10, 6))

    for station_name in station_names:
        top5_time_1 = bike_data[bike_data['대여_대여소명'] == station_name]
        top5_time_ = top5_time_1.groupby('시간대').size()
        plt.plot(top5_time_.index, top5_time_.values, label=station_name, marker='o')

    plt.xlabel('시간')
    plt.ylabel('횟수')
    plt.xticks(range(24))  # x축 시간 설정
    plt.legend()
    plt.grid(True)
    plt.show()
# 사용 예시
상위_top10_stations = ['한밭수목원(동원)', '무역전시관입구(택시승강장)(1)', '타슈관제센터', '유성구청(31)', '타임월드']
plot_rental_return_by_multiple_stations(top5_time, 상위_top10_stations)
하위_top10_stations = ['벤쳐타운 장열실관 앞 버스정류장', '신동 중이온가속기연구소 입구', '용산동 호반써밋(401동)', '한밭대학교 그린에너지관','용산동 호반써밋(205동)']
plot_rental_return_by_multiple_stations(top5_time, 하위_top10_stations)

merged_bike1 = pd.merge(bike,station_locations_gpkg[['대여소명','geometry']],left_on='대여_대여소명',right_on='대여소명',how='inner')
merged_bike1.rename(columns={'geometry': '대여_geometry'}, inplace=True)  # 컬럼 이름 변경
# 대여소 2를 기준으로 geometry 컬럼을 붙이기
bike_route = pd.merge(merged_bike1, station_locations_gpkg[['대여소명', 'geometry']], left_on='반납_대여소명', right_on='대여소명', how='inner')
bike_route.rename(columns={'geometry': '반납_geometry'}, inplace=True)  # 컬럼 이름 변경

#2023년 기준 대여반납 경로분석
bike_route_2023 = bike_route[bike_route['대여연도'] == 2023]
#bike_route_2023 = bike_route_2023[bike_route_2023['이용거리(km)'] <= 0.7]
bike_route_2023.reset_index(drop=True,inplace=True)
# 대여 장소와 반납 장소를 연결하여 LineString 객체로 변환
bike_route_2023['경로'] = bike_route_2023.apply(lambda row: LineString([row['대여_geometry'], row['반납_geometry']]), axis=1)
# Geometry 컬럼들 제거
bike_route_2023.drop(columns=['대여_geometry', '반납_geometry'], inplace=True)
# GeoDataFrame으로 변환
bike_route_2023_gdf = gpd.GeoDataFrame(bike_route_2023, geometry='경로')
# GeoPackage로 저장
#bike_route_2023_gdf.to_file(path_result+'//03.shp//경로분석//경로분석_2023.gpkg', driver='GPKG')

#2024년 기준 대여반납 경록분석
bike_route_2024 = bike_route[bike_route['대여연도'] == 2024]
bike_route_2024.reset_index(drop=True,inplace=True)
bike_route_2024['경로'] = bike_route_2024.apply(lambda row: LineString([row['대여_geometry'], row['반납_geometry']]), axis=1)
bike_route_2024.drop(columns=['대여_geometry', '반납_geometry'], inplace=True)
bike_route_2024 = gpd.GeoDataFrame(bike_route_2024, geometry='경로')
# GeoPackage로 저장
#bike_route_2024.to_file(path_result+'//03.shp//경로분석//경로분석_2024.gpkg', driver='GPKG')

#2024년 3월기준 대여반납 경로분석
bike_route_202403 = bike_route_2024[bike_route_2024['대여월'] == 3]
bike_route_202403 = bike_route_202403[['자전거번호','대여일시_시분초','이용시간(분)','이용거리(km)','연령대','대여_대여소명','대여_X좌표','대여_Y좌표','반납_대여소명','반납_X좌표','반납_Y좌표', '경로']]
bike_route_202403[(bike_route_202403['대여_대여소명'] == '타슈관제센터') & (bike_route_202403['이용거리(km)'] == 0)]
bike_route_202403.to_csv(path_result+'//01.excel//경로분석_202403.csv',encoding='cp949',index=False)
bike_route_202403.to_file(path_result+'//03.shp//경로분석//경로분석_202403.gpkg', driver='GPKG')

#추가현황
bike_route_202403 = gpd.read_file(path_result+'//03.shp//경로분석//경로분석_202403.gpkg', driver='GPKG')
return_station_top2 = bike_route_202403[bike_route_202403['대여_대여소명'] == '무역전시관입구(택시승강장)(1)']
무역전시관입구_반납list = return_station_top2.groupby(['반납_대여소명']).size().reset_index(name='반납수').sort_values(by='반납수', ascending=False)
무역전시관입구_반납list.reset_index(drop='True')
무역전시관입구_반납list['대여_대여소'] = '무역전시관입구(택시승강장)(1)'
무역전시관입구_반납list_30 = 무역전시관입구_반납list.head(30)
return_station_top2_line = pd.merge(return_station_top2,무역전시관입구_반납list_30,on='반납_대여소명',how='inner')
return_station_top2_line = return_station_top2_line[['대여_대여소명','반납_대여소명','반납수','geometry']]
return_station_top2_line = return_station_top2_line.drop_duplicates()
return_station_top2_line.to_file(path_result+'//03.shp//경로분석//경로분석_무역전시관입구_반납30_line.gpkg', driver='GPKG')

무역전시관입구_반납list_p = pd.merge(무역전시관입구_반납list_30,station_locations_gpkg,left_on='반납_대여소명',right_on='대여소명')
무역전시관입구_반납list_p = gpd.GeoDataFrame(무역전시관입구_반납list_p, geometry='geometry')
#무역전시관입구_반납list_p.to_file(path_result+'//03.shp//경로분석//경로분석_무역전시관입구_반납30.gpkg', driver='GPKG')

return_station_top3 = bike_route_202403[bike_route_202403['대여_대여소명'] == '카이스트 창의학습관(22)']
카이스트list = return_station_top3.groupby(['반납_대여소명']).size().reset_index(name='반납수').sort_values(by='반납수', ascending=False)
카이스트list.reset_index(drop='True')
카이스트list['대여_대여소'] = '카이스트 창의학습관(22)'
카이스트list_30 = 카이스트list.head(30)

return_station_top3_line = pd.merge(return_station_top3,카이스트list_30,on='반납_대여소명',how='inner')
return_station_top3_line = return_station_top3_line[['대여_대여소명','반납_대여소명','반납수','geometry']]
return_station_top3_line = return_station_top3_line.drop_duplicates()
return_station_top3_line.to_file(path_result+'//03.shp//경로분석//경로분석_카이스트_반납30_line.gpkg', driver='GPKG')

카이스트list_p = pd.merge(카이스트list_30,station_locations_gpkg,left_on='반납_대여소명',right_on='대여소명')
카이스트list_p = gpd.GeoDataFrame(카이스트list_p, geometry='geometry')
#카이스트list_p.to_file(path_result+'//03.shp//경로분석//경로분석_카이스트_반납30.gpkg', driver='GPKG')

#추가현황

# daily_membership_data 가입탈퇴자수
# 회원가입자 수 현황
daily_membership_data['reg_date'] = pd.to_datetime(daily_membership_data['reg_date'])
daily_membership_data['가입연도'] = daily_membership_data['reg_date'].dt.year
daily_membership_data['가입월'] = daily_membership_data['reg_date'].dt.month

# 연월별 가입 및 탈퇴 수
monthly_stats = daily_membership_data.groupby(['가입연도','가입월', '가입'])['count(*)'].sum().unstack(fill_value=0)
monthly_stats = monthly_stats.reset_index()
#cumulative_stats = monthly_stats.cumsum()
monthly_stats.to_csv(path_result+'//01.excel//타슈가입탈퇴자_현황.csv',encoding='cp949',index=False)
# result_bike_data 대여이력
# 연도,월,시간,요일별 대여/반납현황
# 건수 COUNTS
hourly_counts_rental = bike.groupby(['대여일시_시','성별','연령대']).size().reset_index(name='대여건수')
#hourly_counts_return = bike.groupby(['반납일시_시','성별','연령대']).size().reset_index(name='반납건수')
# 시작 날짜와 종료 날짜 지정
start_date = bike['대여일시_시'].min()
end_date = bike['대여일시_시'].max()

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
bike_sx_age = merged_df.groupby(['기준연도','기준월','성별','연령대'])['대여건수'].sum().reset_index()

bike_sx_age_month = bike_sx_age.groupby(['기준연도','기준월'])['대여건수'].sum().reset_index()
bike_sx_age_year = bike_sx_age_month.groupby(['기준연도'])['대여건수'].mean().reset_index()
bike_sx_age_year.to_csv(path_result+'//01.excel//대여반납현황(월평균이용자수).csv',encoding='cp949',index=False)

bike_sx_age_month = bike_sx_age.groupby(['기준연도','기준월'])['대여건수'].sum().reset_index()
bike_sx_age_year = bike_sx_age_month.groupby(['기준연도'])['대여건수'].sum().reset_index()
bike_sx_age_year.to_csv(path_result+'//01.excel//대여반납현황(누적합이용자수).csv',encoding='cp949',index=False)

bike_sx_month = bike_sx_age.groupby(['기준연도','기준월','성별'])['대여건수'].sum().reset_index()
bike_sx_year = bike_sx_month.groupby(['기준연도','성별'])['대여건수'].mean().reset_index()
bike_sx_year.to_csv(path_result+'//01.excel//대여반납현황(성별_월평균).csv',encoding='cp949',index=False)
bike_sx_month = bike_sx_age.groupby(['기준연도','기준월','성별'])['대여건수'].sum().reset_index()
bike_sx_year = bike_sx_month.groupby(['기준연도','성별'])['대여건수'].sum().reset_index()
bike_sx_year.to_csv(path_result+'//01.excel//대여반납현황(성별_누적합).csv',encoding='cp949',index=False)

bike_age_month = bike_sx_age.groupby(['기준연도','기준월','연령대'])['대여건수'].sum().reset_index()
bike_age_year = bike_age_month.groupby(['기준연도','연령대'])['대여건수'].mean().reset_index()
bike_age_year.to_csv(path_result+'//01.excel//대여반납현황(연령대별_월평균).csv',encoding='cp949',index=False)
bike_age_month = bike_sx_age.groupby(['기준연도','기준월','연령대'])['대여건수'].sum().reset_index()
bike_age_year = bike_age_month.groupby(['기준연도','연령대'])['대여건수'].sum().reset_index()
bike_age_year.to_csv(path_result+'//01.excel//대여반납현황(연령대별_누적합).csv',encoding='cp949',index=False)


#추가현황
data1 = time_1hour.groupby(['기준연도','기준일자','요일'])['대여건수'].sum().reset_index()
data1 = data1.groupby(['요일'])['대여건수'].mean().reset_index()
data1.to_excel(path_result+'//01.excel//대여반납현황(요일별_평균).xlsx',index=False)

#추가현황
data2 = time_1hour.groupby(['기준연도','기준일자','요일','시간대'])['대여건수'].sum().reset_index()
data2['주말여부'] = data2['요일'].apply(lambda x: '주말' if x in ['Saturday','Sunday'] else '주중')
data2 = data2.groupby(['주말여부', '시간대'])['대여건수'].mean().reset_index()
data2.to_excel(path_result+'//01.excel//대여반납현황(주중주말시간대별평균).xlsx',index=False)

#추가현황
bike03 = bike[(bike['대여연도'] == 2024)&(bike['대여월'] == 3)]
count_by_station = bike03.groupby(['대여_대여소ID', '대여_대여소명']).size().reset_index(name='대여수').sort_values(by='대여수', ascending=False)
# 결과를 출력합니다.
print("가장 대여수가 많은 대여소:")
count_by_station = count_by_station.reset_index(drop=True)
count_by_station_10 = count_by_station.head(10)
count_by_station_10.to_excel(path_result+'//01.excel//2024년3월기준_대여건수top10대여소.xlsx',index=False)
count_by_station_10
# 조건을 리스트로 정의합니다.
top5 = ['타슈관제센터', '한밭수목원(동원)', '무역전시관입구(택시승강장)(1)', '카이스트 창의학습관(22)','충남대학교 학생회관']
# '정식_대여소명'이 조건 중 하나에 해당하는 행들을 가져옵니다.
top5_points = top_tail_station[top_tail_station['정식_대여소명'].isin(top5)]
top5_points.to_file(path_result+'//03.shp//대여소_현황//대여건수_상위TOP5대여소_위치정보)202403.gpkg', driver='GPKG')

