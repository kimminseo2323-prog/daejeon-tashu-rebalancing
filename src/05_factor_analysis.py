###########################################################
# 과 제 명: AO3_대전시_공영자전거(타슈)
# 파 일 명: 04_영향요인분석.ipynb
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
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
import seaborn as sns
from datetime import datetime
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import holidays

# 대여소별 경로분석
from shapely.geometry import Point, LineString
from matplotlib.ticker import ScalarFormatter

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
# 영향요인 데이터
weather_data = pd.read_pickle(path_data_analyze+'//02.내부//02.기상정보//weather_data.pkl') # 기상정보 데이터 (2022.07 ~ 2024.03)
dj_air = pd.read_csv(path_data_analyze +'//02.내부//02.기상정보//air_data.csv',encoding='cp949') #미세먼지 데이터
dj_busstop_geo = gpd.read_file(path_data_analyze +"//02.내부//05.버스정류장(지오코딩)//대전광역시_버스정류장.gpkg", driver="GPKG")
dj_subway_geo = gpd.read_file(path_data_analyze +"//02.내부//06.지하철(지오코딩)//대전광역시_지하철역.gpkg", driver="GPKG")
time_1hour = pd.read_excel(path_result+'//01.excel//대여반납현황(일자,시간,요일).xlsx') #시간대별 대여/반납 현황
#외부데이터 읽어오기(전처리 후)
# 자체다운로드 데이터 읽어오기
kosis_pop = pd.read_csv(path_data_analyze + '//01.외부//kosis_주민등록인구//kosis_5gu_age.csv', encoding='cp949')# kosis_주민등록인구 파일 읽어오기
dj_bjd = pd.read_csv(path_data_analyze + '//01.외부//법정동코드//법정동코드.csv', encoding='cp949') # 법정동 코드파일 읽어오기
SIGUNGU = gpd.read_file(path_data_analyze + '//01.외부//행정경계_시군구//sigungu.gpkg' , driver='GPKG') # 대전시 행정경계 읽어오기
grid_100 = gpd.read_file(path_data_analyze + '//01.외부//100m격자//grid_100.gpkg', driver='GPKG') # 대전시 100m 격자 읽어오기
BUBJUNGDONG = gpd.read_file(path_data_analyze + '//01.외부//법정동경계//bupjungdong.gpkg', driver='GPKG')

# 주소에서 두 번째 단어(구정보) 추출하여 시군구명 컬럼 생성
dj_subway_geo['시군구명'] = dj_subway_geo['STATION_ADDR'].apply(lambda x: x.split()[1])
#dj_subway_geo.to_file(path_data_analyze +"//02.내부//06.지하철(지오코딩)//대전광역시_지하철역.gpkg", driver="GPKG")
dj_busstop_geo['시군구명'] = dj_busstop_geo['행정읍면동'].apply(lambda x: x.split()[1])
#dj_busstop_geo.to_file(path_data_analyze +"//02.내부//05.버스정류장(지오코딩)//대전광역시_버스정류장.gpkg", driver="GPKG")
# SIGUNGU 및 grid_100 (기존 5181) 데이터를 EPSG:5179 좌표계로 변환
SIGUNGU = SIGUNGU.to_crs(epsg=5179)
grid_100 = grid_100.to_crs(epsg=5179)

## 변환된 좌표계 확인
#print(SIGUNGU.crs)
#print(grid_100.crs)

# 격자 데이터의 중심점 생성
grid_100['geometry_center'] = grid_100.centroid
grid_100_center = gpd.GeoDataFrame(geometry=grid_100['geometry_center'], crs=grid_100.crs)


# 각 격자의 중심점을 포함하는 시군구 찾기
# 이 단계에서는 격자의 중심점이 여러 시군구에 걸쳐 있는 경우를 고려하지 않음
mapping = gpd.sjoin(grid_100_center, SIGUNGU, how="inner", op='intersects')

# 격자의 전체 면적이 여러 시군구에 걸쳐 있는 경우를 처리
# 격자와 시군구의 교차점을 계산하고, 그 면적을 기준으로 가장 큰 시군구를 선택
def map_largest_area(grid, sigungu):
    grid['mapped_sigungu'] = None
    for index, row in grid.iterrows():
        intersecting_sigungus = sigungu[sigungu.intersects(row['geometry'])]
        largest_area = 0
        largest_sigungu = None
        for _, sg_row in intersecting_sigungus.iterrows():
            intersection_area = row['geometry'].intersection(sg_row['geometry']).area
            if intersection_area > largest_area:
                largest_area = intersection_area
                largest_sigungu = sg_row
        grid.at[index, 'mapped_sigungu'] = largest_sigungu['SIGUNGU_NM'] if largest_sigungu is not None else None
    return grid

# 함수 실행
grid_mapped = map_largest_area(grid_100, SIGUNGU)
grid_mapped = grid_mapped[['gid','val','mapped_sigungu','geometry']]
grid_mapped = gpd.GeoDataFrame(grid_mapped, geometry='geometry')
grid_mapped.to_file(path_result+"\\03.shp\\격자_거주인구\\GRID_100_HOMEPOP.gpkg", driver="GPKG")


grid_mapped_usung = grid_mapped[grid_mapped['mapped_sigungu'] == '유성구']
grid_mapped_daeduck = grid_mapped[grid_mapped['mapped_sigungu'] == '대덕구']
grid_mapped_seo = grid_mapped[grid_mapped['mapped_sigungu'] == '서구']
grid_mapped_jung = grid_mapped[grid_mapped['mapped_sigungu'] == '중구']
grid_mapped_dong = grid_mapped[grid_mapped['mapped_sigungu'] == '동구']

grid_mapped_usung.to_file(path_result+"\\03.shp\\격자_거주인구\\GRID_100_HOMEPOP_유성구.gpkg", driver="GPKG")
grid_mapped_daeduck.to_file(path_result+"\\03.shp\\격자_거주인구\\GRID_100_HOMEPOP_대덕구.gpkg", driver="GPKG")
grid_mapped_seo.to_file(path_result+"\\03.shp\\격자_거주인구\\GRID_100_HOMEPOP_서구.gpkg", driver="GPKG")
grid_mapped_jung.to_file(path_result+"\\03.shp\\격자_거주인구\\GRID_100_HOMEPOP_중구.gpkg", driver="GPKG")
grid_mapped_dong.to_file(path_result+"\\03.shp\\격자_거주인구\\GRID_100_HOMEPOP_동구.gpkg", driver="GPKG")


#날씨 연관성 분석
weather_usecol = weather_data[['일시', '기온(°C)','강수량(mm)','적설(cm)','3시간신적설(cm)']]
weather_usecol.fillna(0,inplace=True)
weather_usecol.columns = ['일시','기온(c)','강수량(mm)','적설량(cm)','3시간신적설량(cm)']


weather_time = pd.merge(time_1hour,weather_usecol,left_on='기준일자시간',right_on='일시',how='inner')
weather_result = weather_time.groupby(['기준연도','기준월','기준일자','계절']).agg({'대여건수': 'sum', '반납건수': 'sum', '기온(c)': 'max', '강수량(mm)': 'sum', '적설량(cm)': 'sum', '3시간신적설량(cm)': 'sum'}).reset_index()
#weather_result.to_csv(path_result+'//01.excel//날씨현황.csv',encoding='cp949',index=False)

path_result2   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-05-20')
filtered_df = weather_result[(weather_result['기준연도'] > 2023) | ((weather_result['기준연도'] == 2023) & (weather_result['기준월'] >= 3))]
weather_23042404 = filtered_df[(filtered_df['기준연도'] < 2024) | ((filtered_df['기준연도'] == 2024) & (filtered_df['기준월'] <= 3))]
 #최근 1년
weather_1year = weather_23042404[['기준연도','기준월','기준일자','계절','대여건수','반납건수','강수량(mm)','적설량(cm)']]
# 대한민국 공휴일을 확인할 holidays 객체 생성
kr_holidays = holidays.Korea()
# 기준일자를 datetime 형식으로 변환하여 대한민국 공휴일 여부를 확인하고, 이를 새로운 컬럼에 추가
weather_1year['공휴일여부'] = weather_1year['기준일자'].apply(lambda x: 1 if datetime.strptime(x, '%Y-%m-%d') in kr_holidays else 0)
weather_1year.to_pickle(path_result2+'//01.excel//최근1년_(날씨,대여,공휴일)//최근1년_날씨현황.pkl')

weather_2023 = weather_result[weather_result['기준연도'] == 2023] #2023년
weather_temp = weather_2023.copy()

# 강수량에 대한 더미 변수 생성
weather_temp['비_여부'] = np.where(weather_temp['강수량(mm)'] > 0, 1, 0)

# 독립 변수 X와 종속 변수 y 설정 (계절 더미 변수를 제거)
X = weather_temp[['기온(c)', '비_여부']]
y = weather_temp['대여건수']

# 상수항(절편)을 추가
X = sm.add_constant(X)

# 선형 회귀 모델을 만들고 피팅
model = sm.OLS(y, X).fit()
print(model.summary())

# 강수량이 0일 때의 산점도와 회귀선 그리기
plt.scatter(weather_temp.loc[weather_temp['비_여부'] == 0, '기온(c)'], y[weather_temp['비_여부'] == 0], color='blue', label='비 없음', alpha=0.5)
plt.plot(weather_temp.loc[weather_temp['비_여부'] == 0, '기온(c)'], model.predict(X)[weather_temp['비_여부'] == 0], color='blue')


# 강수량이 0이 아닐 때의 산점도와 회귀선 그리기
plt.scatter(weather_temp.loc[weather_temp['비_여부'] == 1, '기온(c)'], y[weather_temp['비_여부'] == 1], color='red', label='비 있음', alpha=0.5)
plt.plot(weather_temp.loc[weather_temp['비_여부'] == 1, '기온(c)'], model.predict(X)[weather_temp['비_여부'] == 1], color='red')
plt.xlabel('기온(c)')
plt.ylabel('대여건수')
plt.title('강수량에 따른 대여건수 회귀 그래프')
plt.legend()
plt.show()

# 비가 오지 않을 때만 필터링
weather_no_rain = weather_2023[weather_2023['강수량(mm)'] == 0]

# 독립 변수 X와 종속 변수 y 설정 (비 여부 더미 변수를 제거)
X = weather_no_rain[['기온(c)']]
y = weather_no_rain['대여건수']

# 상수항(절편)을 추가
X = sm.add_constant(X)

# 선형 회귀 모델을 만들고 피팅
model = sm.OLS(y, X).fit()
print(model.summary())

# 회귀 분석 결과를 시각화
plt.scatter(weather_no_rain['기온(c)'], y, label='비 없음', alpha=0.5)  # 산점도
plt.plot(weather_no_rain['기온(c)'], model.predict(X), color='red')  # 회귀선
plt.xlabel('기온(c)')
plt.ylabel('대여건수')
plt.title('비가 오지 않을 때의 기온과 대여건수 회귀 그래프')
plt.legend()
plt.show()

weather_2023 = weather_result[weather_result['기준연도'] == 2023] #2023년
weather_rain = weather_2023[weather_2023['계절'].isin(['봄', '여름', '가을'])]
# 회귀 분석에 사용할 독립변수와 종속변수를 선택합니다.

X = weather_rain['강수량(mm)']
y = weather_rain['대여건수']


# 상수항(절편)을 추가
X = sm.add_constant(X)
# 선형 회귀 모델을 만들고 피팅
model = sm.OLS(y, X).fit()
print(model.summary())

# 회귀 결과를 시각화합니다.
plt.scatter(X['강수량(mm)'], y, alpha=0.5)  # 산점도
plt.plot(X['강수량(mm)'], model.predict(X), color='red')  # 회귀선
plt.xlabel('강수량(mm)')
plt.ylabel('대여건수')
plt.title('봄,여름,가을 강수량에 따른 대여건수 회귀 그래프(0mm포함)')
plt.show()

# 강수량 값이 0인 행 제거
weather_rain_2 = weather_rain[weather_rain['강수량(mm)'] > 0]
X = weather_rain_2['강수량(mm)']
y = weather_rain_2['대여건수']

X = sm.add_constant(X)

model = sm.OLS(y, X).fit()
print(model.summary())

plt.scatter(X['강수량(mm)'], y, alpha=0.5)  # 산점도
plt.plot(X['강수량(mm)'], model.predict(X), color='red')  # 회귀선
plt.xlabel('강수량(mm)')
plt.ylabel('대여건수')
plt.title('봄,여름,가을 강수량에 따른 대여건수 회귀 그래프(0mm제외)')
plt.show()

#weather_2023 = weather_result[weather_result['기준연도'] == 2023] #2023년
weather_snow = weather_2023[weather_2023['계절'].isin(['겨울'])]
# 회귀 분석에 사용할 독립변수와 종속변수를 선택합니다.
X = weather_snow['적설량(cm)']
y = weather_snow['대여건수']


# 상수항(절편)을 추가
X = sm.add_constant(X)
# 선형 회귀 모델을 만들고 피팅
model = sm.OLS(y, X).fit()
print(model.summary())

# 회귀 결과를 시각화합니다.
plt.scatter(X['적설량(cm)'], y, alpha=0.5)  # 산점도
plt.plot(X['적설량(cm)'], model.predict(X), color='red')  # 회귀선
plt.xlabel('적설량(cm)')
plt.ylabel('대여건수')
plt.title('겨울 적설량(cm)에 따른 대여건수 회귀 그래프(0cm포함)')
plt.show()

weather_snow_2 = weather_snow[weather_snow['적설량(cm)'] > 0]
X = weather_snow_2['적설량(cm)']
y = weather_snow_2['대여건수']

X = sm.add_constant(X)

model = sm.OLS(y, X).fit()
print(model.summary())

plt.scatter(X['적설량(cm)'], y, alpha=0.5)  # 산점도

plt.plot(X['적설량(cm)'], model.predict(X), color='red')  # 회귀선
plt.xlabel('적설량(cm)')
plt.ylabel('대여건수')
plt.title('겨울 적설량(cm)에 따른 대여건수 회귀 그래프(0cm제외)')
plt.show()

weather_air = dj_air.copy()
weather_air = weather_air.groupby('날짜')[['PM10','PM2.5']].mean().reset_index()
weather_air[['기준일자', '시간대']] = weather_air['날짜'].str.split(' ', expand=True)
weather_air.fillna(0,inplace=True)
weather_air = weather_air[['기준일자','시간대','PM10','PM2.5']]
weather_air['시간대'] = weather_air['시간대'].astype(int)
weather_air['시간대'] -= 1
weather_air2 = pd.merge(time_1hour,weather_air,on=['기준일자','시간대'],how='inner')
weather_air3 = weather_air2.groupby(['기준연도','기준월','기준일자']).agg({'대여건수': 'sum', '반납건수': 'sum', 'PM10':'max','PM2.5':'max'}).reset_index()

# 미세먼지 등급 생성
weather_air3['PM10_등급'] = pd.cut(weather_air3['PM10'], bins=[0, 31, 81, 151, float('inf')], labels=['좋음', '보통', '나쁨', '매우나쁨'], right=False) # PM10 등급 컬럼 생성
weather_air3['PM2.5_등급'] = pd.cut(weather_air3['PM2.5'], bins=[0, 16, 36, 76, float('inf')], labels=['좋음', '보통', '나쁨', '매우나쁨'], right=False) # PM2.5 등급 컬럼 생성

rain = weather_result.copy() #강수량,적설량 매핑
weather_air4 = pd.merge(weather_air3,rain[['기준일자','강수량(mm)','적설량(cm)']],on='기준일자',how='inner')
weather_air4_2023 = weather_air4[weather_air4['기준연도'] ==2023]
weather_air4_2023.to_excel(path_result+'//01.excel//미세먼지현황_강수량포함.xlsx',index=False)

weather_air5_2023 = weather_air4_2023[(weather_air4_2023['강수량(mm)'] == 0 ) & (weather_air4_2023['적설량(cm)'] == 0)]
weather_air5_2023.to_excel(path_result+'//01.excel//미세먼지현황_강수량0.xlsx',index=False)


weather_air5 = weather_air3.copy()
X = weather_air5['PM10']
y = weather_air5['대여건수']

# 상수항(절편)을 추가
X = sm.add_constant(X)
# 선형 회귀 모델을 만들고 피팅
model = sm.OLS(y, X).fit()
print(model.summary())

# 회귀 결과를 시각화합니다.
plt.scatter(X['PM10'], y, alpha=0.5)  # 산점도
plt.plot(X['PM10'], model.predict(X), color='red')  # 회귀선
plt.xlabel('PM10')
plt.ylabel('PM10')
plt.title('미세먼지 수치에 따른 대여건수 회귀 그래프')
plt.show()