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
import geopandas as gpd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from shapely.geometry import Point
from sklearn.preprocessing import MinMaxScaler

# 대여이력정보 최종 분석 데이터
result_bike_data = pd.read_pickle(path_data_output+'//1.pretreatment//02.내부//01.대여반납이력//result_bike_data_0430.pkl')
bike_data_1year = result_bike_data[(result_bike_data['대여일자'] >= '2023-03-01') & (result_bike_data['대여일자'] <= '2024-03-31')]
station_locations_gpkg = gpd.read_file(path_data_output+'//3.result//2024-04-25//03.shp//대여소_위치정보.gpkg', driver='GPKG') # 타슈 대여소 내역 데이터 위치좌표

clust_station = bike_data_1year.copy()
clust_station2 = clust_station[['대여_구','대여_대여소ID', '대여_대여소명', '반납_대여소ID', '반납_대여소명','이용거리(km)', '대여_X좌표', '대여_Y좌표', '반납_X좌표', '반납_Y좌표']]

clust_station2['대여_대여소명'].nunique()

# 대여_대여소 기준 타슈관련 대여소 제거
filter_values = ['타슈관제센터 정비대기', '타슈관제센터 정비입고', '타슈관제센터']
clust_station2 = clust_station2[~clust_station2['대여_대여소명'].isin(filter_values)]

rental_counts = clust_station2['대여_대여소명'].value_counts().reset_index()
rental_counts.columns = ['대여_대여소명', '대여건수']
df_sorted = rental_counts.sort_values(by='대여건수', ascending=False)

top_25_percent_index = int(0.25 * len(df_sorted))
top_25_percent_rental_stations = df_sorted.iloc[:top_25_percent_index]['대여_대여소명']

# 컬럼 이름 변경
top_25_percent_rental_stations = top_25_percent_rental_stations.rename('상위25_대여소명')

# 조인 수행
clust_station3 = pd.merge(clust_station2, top_25_percent_rental_stations, how='inner', left_on='대여_대여소명', right_on='상위25_대여소명')
top_stations = pd.merge(clust_station3, top_25_percent_rental_stations, how='inner', left_on='반납_대여소명',right_on='상위25_대여소명')

clust_data = top_stations.groupby(['대여_대여소ID','대여_대여소명','반납_대여소ID','반납_대여소명'])['이용거리(km)'].mean().reset_index()  # 대여-> 반납 데이터 기준 평균 이용거리 산출
# 자기회귀 건수 삭제
clust_data_pr = clust_data[clust_data['대여_대여소명'] != clust_data['반납_대여소명']]  # '대여_대여소명'과 '반납_대여소명' 컬럼값이 같은 행을 삭제
# print( clust_data2['이용거리(km)'].describe()) #요약통계량 산출
clust_data2 = clust_data_pr[clust_data_pr['이용거리(km)'] <= 20.0]  # 20km 이상 제거
stations = sorted(set(clust_data2['대여_대여소ID']).union(set(clust_data2['반납_대여소ID'])))  # 대여소ID 목록 추출
distance_matrix = pd.DataFrame(index=stations, columns=stations)  # 대여소ID 간 이용거리 행렬 생성

# 이용거리 값 할당
for i, row in clust_data2.iterrows():
    distance_matrix.at[row['대여_대여소ID'], row['반납_대여소ID']] = row['이용거리(km)']
# 대각선을 기준으로 대칭 행렬 생성
for i in range(len(stations)):
    for j in range(i + 1, len(stations)):
        if pd.isna(distance_matrix.iloc[i, j]) and pd.notna(distance_matrix.iloc[j, i]):
            distance_matrix.iloc[i, j] = distance_matrix.iloc[j, i]

distance_matrix.fillna(0, inplace=True)  # NaN 값은 0으로 채우기

# 최소-최대 스케일링을 위한 MinMaxScaler 객체 생성
scaler = MinMaxScaler()
coordinates_scaled = scaler.fit_transform(distance_matrix)
data_minmax_scaled_df = pd.DataFrame(coordinates_scaled, columns=distance_matrix.columns, index=distance_matrix.index)

wcss = []
max_clusters = 20
for i in range(1, max_clusters + 1):
    kmeans = KMeans(n_clusters=i, random_state=42)
    kmeans.fit(data_minmax_scaled_df)
    wcss.append(kmeans.inertia_)

    # 팔꿈치 시각화
plt.figure(figsize=(10, 6))
plt.plot(range(1, max_clusters + 1), wcss, marker='o', linestyle='--')
plt.title('Elbow Method For Optimal k')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.xticks(range(1, max_clusters + 1))
plt.grid(True)
plt.show()

kmeans = KMeans(n_clusters=10, random_state=42)
clusters = kmeans.fit_predict(data_minmax_scaled_df)

result_df = pd.DataFrame({'대여소ID': data_minmax_scaled_df.index, 'kmeans': clusters})
station_list = clust_station[['대여_대여소ID', '대여_대여소명', '대여_구', '대여_Y좌표', '대여_X좌표']]  # 결과데이터에 원천 데이터 정보 merge
station_list.drop_duplicates(subset=['대여_대여소명'], inplace=True)
clust_result = pd.merge(result_df, station_list, left_on='대여소ID', right_on='대여_대여소ID', how='left')

# 좌표를 이용한 군집분석
clust_result_21 = clust_result[['대여소ID','대여_대여소명','대여_구','대여_Y좌표', '대여_X좌표']]
clust_result_21.columns = ['대여소ID','대여소명','대여_구','X좌표','Y좌표']  #X,Y값 컬럼명 뒤바뀜 그래서 변경함.

# '도심' 컬럼 추가
clust_result_21['도심'] = ''
# 대여_구가 서구 또는 유성구인 경우 '신도심' 값 할당
clust_result_21.loc[clust_result_21['대여_구'].isin(['서구', '유성구']), '도심'] = '신도심'
# 대여_구가 중구, 동구, 대덕구인 경우 '구도심' 값 할당
clust_result_21.loc[clust_result_21['대여_구'].isin(['중구', '동구', '대덕구']), '도심'] = '구도심'

clust_result_21.groupby('도심')['대여소ID'].size()


clust_result_21_int = clust_result_21[['X좌표','Y좌표']] #숫자형 컬럼 표준화 대상
clust_result_2 = clust_result_21[['대여소ID','대여소명','X좌표','Y좌표']]

scaler = MinMaxScaler()
coordinates_scaled = scaler.fit_transform(clust_result_21_int)
coordinates_scaled_df = pd.DataFrame(coordinates_scaled, columns=['X좌표_scaled', 'Y좌표_scaled'])
clust_result_2 = pd.concat([clust_result_2, coordinates_scaled_df], axis=1)

# K-평균 군집화
kmeans = KMeans(n_clusters=10 ,random_state=42)
clust_result_2['군집'] = kmeans.fit_predict(clust_result_2[['X좌표_scaled', 'Y좌표_scaled']])
geometry = [Point(xy) for xy in list(zip(clust_result_2['X좌표'], clust_result_2['Y좌표']))]
gdf2 = gpd.GeoDataFrame(clust_result_2, geometry=geometry, crs="EPSG:4326")

#gdf2.to_file(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year.gpkg', driver='GPKG')
#gdf2.to_csv(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year.csv',encoding='cp949',index=False)
#gdf2.to_pickle(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year.pkl')


# 군집 시각화
plt.scatter(clust_result_2['X좌표'], clust_result_2['Y좌표'], c=clust_result_2['군집'], cmap='viridis')
plt.xlabel('X좌표')
plt.ylabel('Y좌표')
plt.title('Bike Rental Stations Clustering')
plt.colorbar(label='Cluster')
plt.show()


###################도심별 구분 #####################

clust_station = bike_data_1year.copy()
clust_station_city = clust_station[['대여_구','대여_대여소ID', '대여_대여소명', '반납_대여소ID', '반납_대여소명','이용거리(km)', '대여_X좌표', '대여_Y좌표', '반납_X좌표', '반납_Y좌표']]

clust_station_city['대여_대여소명'].nunique()

# 대여_대여소 기준 타슈관련 대여소 제거
filter_values = ['타슈관제센터 정비대기', '타슈관제센터 정비입고', '타슈관제센터']
clust_station_city = clust_station_city[~clust_station_city['대여_대여소명'].isin(filter_values)]

# '도심' 컬럼 추가
clust_station_city['도심'] = ''
# 대여_구가 서구 또는 유성구인 경우 '신도심' 값 할당
clust_station_city.loc[clust_station_city['대여_구'].isin(['서구', '유성구']), '도심'] = '신도심'
# 대여_구가 중구, 동구, 대덕구인 경우 '구도심' 값 할당
clust_station_city.loc[clust_station_city['대여_구'].isin(['중구', '동구', '대덕구']), '도심'] = '구도심'

clust_newcity = clust_station_city[clust_station_city['도심'] == '신도심']
clust_oldcity = clust_station_city[clust_station_city['도심'] == '구도심']


rental_count_newcity = clust_newcity[['도심','대여_대여소명']].value_counts().reset_index()
rental_count_oldcity = clust_oldcity[['도심','대여_대여소명']].value_counts().reset_index()

rental_count_newcity.columns = ['도심','대여_대여소명', '대여건수']
rental_count_oldcity.columns = ['도심','대여_대여소명', '대여건수']


# 대여건수를 기준으로 내림차순 정렬
df_sorted_new = rental_count_newcity.sort_values(by='대여건수', ascending=False)
df_sorted_old = rental_count_oldcity.sort_values(by='대여건수', ascending=False)

top_25_percent_index_new = int(0.25 * len(df_sorted_new))
top_25_percent_rental_stations_new = df_sorted_new.iloc[:top_25_percent_index_new]['대여_대여소명']
top_25_percent_rental_stations_new = top_25_percent_rental_stations_new.rename('상위25_대여소명')
top_25_percent_rental_stations_new

top_25_percent_index_old = int(0.25 * len(df_sorted_old))
top_25_percent_rental_stations_old = df_sorted_old.iloc[:top_25_percent_index_old]['대여_대여소명']
top_25_percent_rental_stations_old = top_25_percent_rental_stations_old.rename('상위25_대여소명')
top_25_percent_rental_stations_old
combined_df = pd.concat([top_25_percent_rental_stations_new, top_25_percent_rental_stations_old], ignore_index=True)


# 조인 수행
clust_station_city2 = pd.merge(clust_station_city, combined_df, how='inner', left_on='대여_대여소명', right_on='상위25_대여소명') # 결과데이터에 원천 데이터 정보 merge

clust_result_city = clust_station_city2[['대여_대여소ID', '대여_대여소명','도심', '대여_구', '대여_Y좌표', '대여_X좌표']]
clust_result_city.drop_duplicates(subset=['대여_대여소명'], inplace=True)
clust_result_city= clust_result_city.reset_index(drop=True)

# 좌표를 이용한 군집분석
clust_result_21 = clust_result_city[['대여_대여소ID','대여_대여소명','도심','대여_Y좌표', '대여_X좌표']]
clust_result_21.columns = ['대여소ID','대여소명','도심','X좌표','Y좌표']  #X,Y값 컬럼명 뒤바뀜 그래서 변경함.

clust_result_21_int = clust_result_21[['X좌표','Y좌표']] #숫자형 컬럼 표준화 대상
clust_result_2 = clust_result_21[['대여소ID','대여소명','X좌표','Y좌표']]

scaler = MinMaxScaler()
coordinates_scaled = scaler.fit_transform(clust_result_21_int)
coordinates_scaled_df = pd.DataFrame(coordinates_scaled, columns=['X좌표_scaled', 'Y좌표_scaled'])
clust_result_2 = pd.concat([clust_result_2, coordinates_scaled_df], axis=1)


wcss = []
max_clusters = 20
for i in range(1, max_clusters + 1):
    kmeans = KMeans(n_clusters=i, random_state=42)
    kmeans.fit(coordinates_scaled_df)
    wcss.append(kmeans.inertia_)

    # 팔꿈치 시각화
plt.figure(figsize=(10, 6))
plt.plot(range(1, max_clusters + 1), wcss, marker='o', linestyle='--')
plt.title('Elbow Method For Optimal k')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.xticks(range(1, max_clusters + 1))
plt.grid(True)
plt.show()

# K-평균 군집화
kmeans = KMeans(n_clusters=10 ,random_state=42)
clust_result_2['군집'] = kmeans.fit_predict(clust_result_2[['X좌표_scaled', 'Y좌표_scaled']])
geometry = [Point(xy) for xy in list(zip(clust_result_2['X좌표'], clust_result_2['Y좌표']))]
gdf2 = gpd.GeoDataFrame(clust_result_2, geometry=geometry, crs="EPSG:4326")

# 군집 시각화
plt.scatter(clust_result_2['X좌표'], clust_result_2['Y좌표'], c=clust_result_2['군집'], cmap='viridis')
plt.xlabel('X좌표')
plt.ylabel('Y좌표')
plt.title('Bike Rental Stations Clustering')
plt.colorbar(label='Cluster')
plt.show()

gdf2['군집'].unique()


gdf2.to_file(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year_city.gpkg', driver='GPKG')
gdf2.to_csv(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year_city.csv',encoding='cp949',index=False)
gdf2.to_pickle(path_result + '\\03.shp\\지리적군집분석\\지리적_군집분석결과_1year_city.pkl')