###########################################################
# 과 제 명: AO3_대전시_공영자전거(타슈)
# 파 일 명: 02_전처리.ipynb
# 작 성 자: 김민서
###########################################################

import os, importlib, warnings; warnings.filterwarnings(action='ignore')
from config import config_A03       as config   ; importlib.reload(config)
from utils  import functions_utils    as fu       ; importlib.reload(fu)
from utils  import functions_log      as fl       ; importlib.reload(fl)
from utils  import functions_lime     as flime    ; importlib.reload(flime)
from utils  import functions_utils_db as fud      ; importlib.reload(fud)

from shapely          import wkt #함수는 문자열로 표현된 지오메트리를 파싱하여 실제 지오메트리 객체로 변환
from shapely.geometry import Polygon, mapping, shape,Point
import geopandas as gpd
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
fl.f_log_line("02_전처리.ipynb")
###########################################################
# 모 듈 명: 모 듈 명 - 02_전처리.ipynb
# 파 일 명: 02_전처리.ipynb
# 작 성 자: 김민서
# 설    명: 대전시 타슈 분석 추가 데이터 전처리
# 파일 버전: v1.0 [2024.04.01]
# 작성 일자: 2024.04.25
# 수정 일자: 2024.04.25 00:00
###########################################################
# 1.실행 변수 정의
log.info("1.실행 변수 정의")

path_base     = "2024-04-19"

path_data_out     = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"01.외부")
path_data_in      = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"02.내부")
path_data_analyze = os.path.join(config_info["PATH_DATA_ANALYZE"])
path_data_output = os.path.join(config_info["PATH_DATA_OUTPUT"])

path_database = os.path.join(config_info["PATH_DATA_OUTPUT_DATEBASE"],path_base)
path_pretreat = os.path.join(config_info["PATH_DATA_OUTPUT_PRETREAT"],path_base)
path_middle   = os.path.join(config_info["PATH_DATA_OUTPUT_MIDDLE"]  ,path_base)
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,path_base)
# 1.1.SQLite 저장시 사용됨
##name_database = f"DB_{config_info['과제ID']}_202309.db" #
#==================================================================================================

###############################################################################
# 작성자 : 김민서
# 최초작성일자 : 2024-04-25
# 제목 : 대전교통공사 타슈 재배치 분석 추가 데이터 전처리
###############################################################################
# 필요라이브러리
import pandas as pd
import geopandas as gpd
import warnings

# 경고 무시 설정
warnings.filterwarnings("ignore")

#추가 데이터 읽어오기
dj_school = pd.read_csv(path_data_in +"//2024_0419_추가데이터 제출//대전광역시 유지원초중고대학교.csv",encoding='cp949') #대전광역시 유치원초중고대학교
dj_park = pd.read_csv(path_data_in +'//2024_0419_추가데이터 제출//대전광역시_공원 현황_20221231.csv',encoding='cp949') #대전광역시_공원 현황_20221231
dj_busstop = pd.read_csv(path_data_in+'//2024_0419_추가데이터 제출//대전광역시_버스정류장 현황_20221215.csv',encoding='cp949') #대전광역시_버스정류장 현황_20221215
dj_subway = pd.read_csv(path_data_in+'//2024_0419_추가데이터 제출//대전도시철도1호선 역정보.csv',encoding='cp949') #대전도시철도1호선 역정보
dj_air_1 = pd.read_csv(path_data_in+'//2024_0419_추가데이터 제출//에어코리아 대기오염 (2022.7.1~2023.4.1).csv',encoding='cp949') #에어코리아 대기오염 (2022.7.1~2023.4.1)
dj_air_2 = pd.read_csv(path_data_in+'//2024_0419_추가데이터 제출//에어코리아 대기오염 (2023.4.2~2023.10.31).csv',encoding='cp949')
dj_air_point = pd.read_csv(path_data_in+'//2024_0419_추가데이터 제출//에어코리아 대기오염 관측소 정보 (2023.4.2~2024.10.31).csv',encoding='cp949') #에어코리아 대기오염 관측소 정보 (2023.4.2~2024.10.31)
# 지오코딩 필요 데이터 (df_school,dj_park)
dj_school_WGS = gpd.read_file(path_data_analyze +"//02.내부//03.학교(지오코딩)//대전광역시 유지원초중고대학교_WGS.shp",encoding='cp949') #대전광역시 유치원초중고대학교
dj_park_WGS = gpd.read_file(path_data_analyze +"//02.내부//04.공원""(지오코딩)//대전광역시_공원_WGS.shp",encoding='utf-8') #대전광역시 유치원초중고대학교


# 위도와 경도를 합쳐서 Point 객체로 변환하는 함수
# 위도와 경도를 합쳐서 Point 객체로 변환
dj_busstop['geometry'] = [Point(xy) for xy in zip(dj_busstop['경도'], dj_busstop['위도'])]
# GeoDataFrame으로 변환
dj_busstop_geo = gpd.GeoDataFrame(dj_busstop, geometry='geometry')
# GeoPackage 파일로 저장
dj_busstop_geo.to_file(path_data_analyze +"//02.내부//05.버스정류장(지오코딩)//대전광역시_버스정류장.gpkg", driver="GPKG")

dj_subway['geometry'] = [Point(xy) for xy in zip(dj_subway['LONGITUDE'], dj_subway['LATITUDE'])]
dj_subway_geo = gpd.GeoDataFrame(dj_subway, geometry='geometry')
dj_subway_geo.to_file(path_data_analyze +"//02.내부//06.지하철(지오코딩)//대전광역시_지하철역.gpkg", driver="GPKG")
dj_air_point['geometry'] = [Point(xy) for xy in zip(dj_air_point['y좌표'], dj_air_point['x좌표'])]
dj_air_point_geo = gpd.GeoDataFrame(dj_air_point, geometry='geometry')
dj_air_point_geo.to_file(path_data_analyze +"//02.내부//07.에어코리아대기오염(지오코딩)//대전광역시_대기오염관측소.gpkg", driver="GPKG")

# 미세먼지 데이터 concat
# 두 데이터프레임에서 공통된 열 이름 찾기
common_columns = list(set(dj_air_1.columns) & set(dj_air_2.columns))
# 위아래로 concat하고 공통된 열만 남기기
dj_air = pd.concat([dj_air_1[common_columns], dj_air_2[common_columns]])
dj_air = dj_air[['날짜','측정소명','측정소코드','시도','오존','일산화탄소','아황산가스','이산화질소','PM10','PM2.5']]
dj_air.to_csv(path_data_analyze +'//02.내부//02.기상정보//air_data.csv',encoding='cp949',index=False)