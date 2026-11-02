###########################################################
# 과 제 명: AO3_대전시_공영자전거(타슈)
# 파 일 명: 01_전처리.ipynb
# 작 성 자: 김민서
###########################################################

import os, importlib, warnings; warnings.filterwarnings(action='ignore')
from config import config_A03       as config   ; importlib.reload(config)
from utils  import functions_utils    as fu       ; importlib.reload(fu)
from utils  import functions_log      as fl       ; importlib.reload(fl)
from utils  import functions_lime     as flime    ; importlib.reload(flime)
from utils  import functions_utils_db as fud      ; importlib.reload(fud)

from shapely          import wkt
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
fl.f_log_line("01_전처리.ipynb")
###########################################################
# 모 듈 명: 모 듈 명 - 01_전처리.ipynb
# 파 일 명: 01_전처리.ipynb
# 작 성 자: 김민서
# 설    명: 대전시 타슈 분석 데이터 전처리
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
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,path_base)
# 1.1.SQLite 저장시 사용됨
##name_database = f"DB_{config_info['과제ID']}_202309.db" #
#==================================================================================================

###############################################################################
# 작성자 : 김민서
# 최초작성일자 : 2024-04-03
# 제목 : 대전교통공사 타슈 재배치 분석 데이터 전처리
###############################################################################
# 필요라이브러리
import pandas as pd
import geopandas as gpd
import glob
import os
import warnings

# 경고 무시 설정
warnings.filterwarnings("ignore")

##  수집데이터 합치기 및 pkl변환(전처리 전 사전작업)
## 대여이력정보 데이터 (2022.07 ~ 2024.03) csv 병합 및 pkl 변환
path_data_list = os.path.join(path_data_in, "타슈 데이터 분석 사업 자료(대여이력, 대여소 등)", '대전시 공영자전거 타슈 대여이력 정보*.csv')
file_paths = glob.glob(path_data_list)
all_data = []
for file_path in file_paths:
    df = pd.read_csv(file_path, encoding='cp949')
    all_data.append(df)
bike_rental_data = pd.concat(all_data)

## 기상정보 데이터 (2022.07 ~ 2024.03) xls to xlsx
import win32com.client as win32

# 변환할 파일 경로
path_data_list = os.path.join(path_data_in, "타슈 데이터 분석 사업 자료(대여이력, 대여소 등)", '대전지역 기상정보*.xls')
file_paths = glob.glob(path_data_list)
for file_path in file_paths:
    if file_path.endswith('.xls'):
        excel = win32.gencache.EnsureDispatch('Excel.Application')  # 엑셀 객체 생성
        wb = excel.Workbooks.Open(file_path)
        new_file_path = os.path.join(path_data_analyze, '02.내부', '02.기상정보',
                                     os.path.splitext(os.path.basename(file_path))[0] + '.xlsx')
        wb.SaveAs(new_file_path, FileFormat=51)  # FileFormat = 51 is for .xlsx extension
        wb.Close()
        excel.Application.Quit()

# xlsx로 변환된 파일 pkl변환
path_data_list2 = os.path.join(path_data_analyze, '02.내부', '02.기상정보', '대전지역 기상정보*.xlsx')
file_paths = glob.glob(path_data_list2)
all_data2 = []
for file_path in file_paths:
    df = pd.read_excel(file_path)
    all_data2.append(df)
weather_data = pd.concat(all_data2)

bike_rental_data.to_pickle(os.path.join(path_data_analyze, '02.내부', '01.대여반납이력',
                                        'bike_rental_data.pkl'))  # 대여이력정보 데이터 (2022.07 ~ 2024.03) 합친 후  pkl생성
weather_data.to_pickle(os.path.join(path_data_analyze, '02.내부', '02.기상정보', 'weather_data.pkl'))  # 대전시 기상데이터 합친 후 pkl생성


# 데이터 읽어오기
## 내부데이터
bike_rental_data = pd.read_pickle(path_data_analyze+'//02.내부//01.대여반납이력//bike_rental_data.pkl') #대여이력 pkl 데이터
weather_data = pd.read_pickle(path_data_analyze+'//02.내부//02.기상정보//weather_data.pkl') #기상정보 pkl 데이터
batch_management_data =  pd.read_csv(path_data_in+"//타슈 데이터 분석 사업 자료(대여이력, 대여소 등)//타슈 관리자 배치,재배치,점검요청,입고.csv",encoding='cp949') # 타슈 관리자 배치,재배치,점검요청,입고 데이터
station_locations = pd.read_csv(path_data_in+"//타슈 데이터 분석 사업 자료(대여이력, 대여소 등)//타슈 대여소 내역.csv",encoding='cp949') # 타슈 대여소 내역 데이터
daily_membership_data = pd.read_csv(path_data_in+"//타슈 데이터 분석 사업 자료(대여이력, 대여소 등)//일별 회원 가입 및 탈퇴정보.csv",encoding='cp949') #일별 회원 가입 및 탈퇴정보
## 외부데이터
kosis_pop = pd.read_excel(path_data_out+"//kosis_주민등록인구//행정구역_읍면동_별_5세별_주민등록인구_2011년__20240403143828.xlsx") #kosis 주민등록인구
SIGUNGU = gpd.read_file(path_data_out+"//센서스_행정경계//BND_SIGUNGU_PG//BND_SIGUNGU_PG.shp",encoding='utf-8')# 시군구 기준 행정경계
dj_bjd = pd.read_excel(path_data_out+'//법정동코드//법정동코드 조회자료.xls') #대전광역시 전체법정동
dj_daeduckgu = gpd.read_file(path_data_out+'//국토부_100m격자//(B100)국토통계_인구정보-총 인구 수(전체)-(격자) 100M_대전광역시 대덕구_202310//nlsp_021001001.shp',encoding='utf-8') # 100m 격자
dj_donggu =  gpd.read_file(path_data_out+'//국토부_100m격자//(B100)국토통계_인구정보-총 인구 수(전체)-(격자) 100M_대전광역시 동구_202310//nlsp_021001001.shp',encoding='utf-8')
dj_seogu =  gpd.read_file(path_data_out+'//국토부_100m격자//(B100)국토통계_인구정보-총 인구 수(전체)-(격자) 100M_대전광역시 서구_202310//nlsp_021001001.shp',encoding='utf-8')
dj_usunggu =  gpd.read_file(path_data_out+'//국토부_100m격자//(B100)국토통계_인구정보-총 인구 수(전체)-(격자) 100M_대전광역시 유성구_202310//nlsp_021001001.shp',encoding='utf-8')
dj_junggu =  gpd.read_file(path_data_out+'//국토부_100m격자//(B100)국토통계_인구정보-총 인구 수(전체)-(격자) 100M_대전광역시 중구_202310//nlsp_021001001.shp',encoding='utf-8')
BUBJUNGDONG = gpd.read_file(path_data_out + '//국토부_법정동경계//LSMD_ADM_SECT_UMD_대전//LSMD_ADM_SECT_UMD_30_202403.shp',encoding='cp949') #대전시 법정동경계 읽어오기


# 외부데이터 전처리
## kosis 주민등록인구
kosis_p= kosis_pop.copy()
kosis_p[['시점', '행정구역(동읍면)별']] = kosis_p[['시점', '행정구역(동읍면)별']].fillna(method='ffill')
# 행정구역 컬럼의 공백 제거
kosis_p = kosis_p.applymap(lambda x: x.strip() if isinstance(x, str) else x)
# 원하는 행정구역에 해당하는 행만 선택
desired_areas = ['동구', '유성구', '서구', '중구', '대덕구']
kosis_p = kosis_p[kosis_p['행정구역(동읍면)별'].isin(desired_areas)]

#연령대 컬럼 생성
kosis_p['연령대'] = None
kosis_p.loc[kosis_p['5세별'].str.contains('0 - 4세|5 - 9세|10 - 14세|15 - 19세'), '연령대'] = 10
kosis_p.loc[kosis_p['5세별'].str.contains('20 - 24세|25 - 29세'), '연령대'] = 20
kosis_p.loc[kosis_p['5세별'].str.contains('30 - 34세|35 - 39세'), '연령대'] = 30
kosis_p.loc[kosis_p['5세별'].str.contains('40 - 44세|45 - 49세'), '연령대'] = 40
kosis_p.loc[kosis_p['5세별'].str.contains('50 - 54세|55 - 59세'), '연령대'] = 50
kosis_p.loc[kosis_p['5세별'].str.contains('60 - 64세|65 - 69세'), '연령대'] = 60
kosis_p.loc[kosis_p['5세별'].str.contains('70 - 74세|75 - 79세'), '연령대'] = 70
kosis_p.loc[kosis_p['5세별'].str.contains('80 - 84세|85 - 89세'), '연령대'] = 80
kosis_p.loc[kosis_p['5세별'].str.contains('90 - 94세|95 - 99세|100+'), '연령대'] = 90
kosis_5gu_age = kosis_p.groupby(['행정구역(동읍면)별','연령대'])[['총인구수 (명)','남자인구수 (명)','여자인구수 (명)']].sum().reset_index()

## 법정동 코드
dj_bjd[['시', '구동']] = dj_bjd['법정동명'].str.split(' ', n=1, expand=True)
dj_bjd[['구', '동']] = dj_bjd['구동'].str.split(' ', expand=True)
# None 값을 '-'로 채우기
dj_bjd = dj_bjd.fillna(0)

## 100m 격자
# 격자별로 겹치는 영역에 있는 값을 합산
# 격자들을 하나로 합치기
merged_grid = gpd.GeoDataFrame(pd.concat([dj_daeduckgu, dj_donggu, dj_seogu, dj_usunggu, dj_junggu], ignore_index=True))
merged_grid = merged_grid.fillna(0)
merged_grid = merged_grid.groupby(['gid','geometry'])['val'].sum().reset_index()
merged_grid = merged_grid[['gid','val','geometry']]
merged_grid = gpd.GeoDataFrame(merged_grid, geometry='geometry')

# 대전시 행정경계 시군구 파일 저장
dj_sigungu = SIGUNGU[SIGUNGU['SIGUNGU_CD'].astype(str).str.startswith('250')]
dj_sigungu = gpd.GeoDataFrame(dj_sigungu, geometry='geometry')
dj_sigungu = dj_sigungu[['SIGUNGU_CD','SIGUNGU_NM','geometry']]
# 대전시 시군구명 컬럼 수정
def change_sigungu_name(row):
    if row['SIGUNGU_CD'] == '25010':
        return '동구'
    elif row['SIGUNGU_CD'] == '25020':
        return '중구'
    elif row['SIGUNGU_CD'] == '25030':
        return '서구'
    elif row['SIGUNGU_CD'] == '25040':
        return '유성구'
    elif row['SIGUNGU_CD'] == '25050':
        return '대덕구'
    else:
        return row['SIGUNGU_NM']
dj_sigungu['SIGUNGU_NM'] = dj_sigungu.apply(change_sigungu_name, axis=1)


#대전시 법정동경계데이터 컬럼추가
# 코드 값과 시군구명을 매핑하는 딕셔너리
code_to_sigungu = {
    '30110': '동구',
    '30140': '증구',
    '30170': '서구',
    '30200': '유성구',
    '30230': '대덕구'
}

# 시군구명 컬럼 추가
BUBJUNGDONG['시군구명'] = BUBJUNGDONG['COL_ADM_SE'].map(code_to_sigungu)
BUBJUNGDONG = BUBJUNGDONG[['EMD_CD', 'COL_ADM_SE', '시군구명', 'EMD_NM', 'geometry']]

#전처리 외부데이터 저장
kosis_5gu_age.to_csv(path_data_analyze+'//01.외부//kosis_주민등록인구//kosis_5gu_age.csv',encoding='cp949') #kosis주민등록인구 전처리 파일
dj_bjd.to_csv(path_data_analyze+'//01.외부//법정동코드//법정동코드.csv',encoding='cp949') # 법정동 코드파일 전처리
dj_sigungu.to_file(path_data_analyze+'//01.외부//행정경계_시군구//sigungu.gpkg', driver='GPKG') # 대전시 행정경계 전처리
merged_grid.to_file(path_data_analyze+'//01.외부//100m격자//grid_100.gpkg', driver='GPKG') # 대전시 100m 격자 전처리
BUBJUNGDONG.to_file(path_data_analyze + '//01.외부//법정동경계//bupjungdong.gpkg', driver='GPKG') # 법정동경계 전처리

# 내부데이터 전처리


## 대여이력 데이터 pkl 파일
pre_bike_data_du = bike_rental_data.copy() # 6,643,498행
pre_bike_data = pre_bike_data_du.drop_duplicates() #중복행 제거 : 6,642,371행

# 각 컬럼별로 널값 확인
#null_counts = pre_bike_data.isnull().sum()
#print("각 컬럼별 널값 수:")
#print(null_counts)

# 대여_구와 대여_동 중 하나라도 널값인 행 추출하여 대여_대여소주소 컬럼의 값을 이용하여 채워넣음
missing_rental = pre_bike_data[pre_bike_data['대여_구'].isnull() | pre_bike_data['대여_동'].isnull()]
missing_rental_fill = missing_rental.copy()
missing_rental_fill['대여_구'] = missing_rental_fill['대여_대여소주소'].str.extract(r'(\S+구)').fillna(missing_rental_fill['대여_구'])
missing_rental_fill['대여_동'] = missing_rental_fill['대여_대여소주소'].str.extract(r'(\S+동)').fillna(missing_rental_fill['대여_동'])

# 기존 결측치 행 삭제
pre_bike_data.dropna(subset=['대여_구', '대여_동'],inplace=True)
# 대여_구,대여_동 결측치를 채운 데이터로 업데이트
pre_bike_data = pd.concat([pre_bike_data, missing_rental_fill])

# 반납_구와 반납_동 중 하나라도 널값인 행 추출하여 반납_대여소주소 컬럼의 값을 이용하여 채워넣음
missing_return = pre_bike_data[pre_bike_data['반납_구'].isnull() | pre_bike_data['반납_동'].isnull()]
missing_return_fill = missing_return.copy()
missing_return_fill['반납_구'] = missing_return_fill['반납_대여소주소'].str.extract(r'(\S+구)').fillna(missing_return_fill['반납_구'])
missing_return_fill['반납_동'] = missing_return_fill['반납_대여소주소'].str.extract(r'(\S+동)').fillna(missing_return_fill['반납_동'])

# 기존 결측치 행 삭제
pre_bike_data.dropna(subset=['반납_구', '반납_동'],inplace=True)
# 반납_구,반납_동 결측치를 채운 데이터로 업데이트
pre_bike_data = pd.concat([pre_bike_data, missing_return_fill])


# '유상구' 값을 '유성구'로 수정
pre_bike_data['대여_구'] = pre_bike_data['대여_구'].replace('유상구', '유성구')
pre_bike_data['반납_구'] = pre_bike_data['반납_구'].replace('유상구', '유성구')
##대여일시_전처리 및 반납일시_전처리 전처리
# 대여일시_전처리 컬럼을 공백을 기준으로 분리하여 날짜와 시간 컬럼으로 나누기
pre_bike_data[['대여일자', '대여시간']] = pre_bike_data['대여일시'].str.split(expand=True)
pre_bike_data[['반납일자', '반납시간']] = pre_bike_data['반납일시'].str.split(expand=True)


# 시간 형식을 'HH:MM:SS'로 통일하는 함수
def format_time(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:  # HH:MM:SS
        h, m, s = parts
    elif len(parts) == 2:  # HH:MM
        h, m = parts
        s = '00'
    else:  # HH or other
        raise ValueError(f"Unexpected time format: {time_str}")
    h = h.zfill(2)
    m = m.zfill(2)
    s = s.zfill(2)
    return f"{h}:{m}:{s}"

# '대여시간' 컬럼에 시간 형식 통일 함수 적용
pre_bike_data['대여시간'] = pre_bike_data['대여시간'].apply(format_time)
pre_bike_data['반납시간'] = pre_bike_data['반납시간'].apply(format_time)
# 대여일자와 대여시간을 조합하여 새로운 컬럼 생성
pre_bike_data['대여일시_전처리'] = pre_bike_data['대여일자'] + ' ' + pre_bike_data['대여시간']
pre_bike_data['반납일시_전처리'] = pre_bike_data['반납일자'] + ' ' + pre_bike_data['반납시간']
#datetime
pre_bike_data['대여일시_전처리'] = pd.to_datetime(pre_bike_data['대여일시_전처리'])
pre_bike_data['반납일시_전처리'] = pd.to_datetime(pre_bike_data['반납일시_전처리'])
pre_bike_data['대여일자'] = pd.to_datetime(pre_bike_data['대여일자'])
pre_bike_data['반납일자'] = pd.to_datetime(pre_bike_data['반납일자'])

# 연도와 월을 추출하여 새로운 열 생성
pre_bike_data['대여연도'] = pre_bike_data['대여일시_전처리'].dt.year
pre_bike_data['대여월'] = pre_bike_data['대여일시_전처리'].dt.month

pre_bike_data['반납연도'] = pre_bike_data['반납일시_전처리'].dt.year
pre_bike_data['반납월'] = pre_bike_data['반납일시_전처리'].dt.month

pre_bike_data.rename(columns={'대여일시_전처리': '대여일시_시분초', '반납일시_전처리': '반납일시_시분초'}, inplace=True)
# 초 부분 삭제 및 새로운 컬럼 생성
pre_bike_data['대여일시_시분'] = pd.to_datetime(pre_bike_data['대여일시_시분초']).dt.strftime('%Y-%m-%d %H:%M')
pre_bike_data['반납일시_시분'] = pd.to_datetime(pre_bike_data['반납일시_시분초']).dt.strftime('%Y-%m-%d %H:%M')
pre_bike_data['대여일시_시분'] = pd.to_datetime(pre_bike_data['대여일시_시분'])
pre_bike_data['반납일시_시분'] = pd.to_datetime(pre_bike_data['반납일시_시분'])
pre_bike_data['대여일시_시'] = pd.to_datetime(pre_bike_data['대여일시_시분초']).dt.strftime('%Y-%m-%d %H')
pre_bike_data['반납일시_시'] = pd.to_datetime(pre_bike_data['반납일시_시분초']).dt.strftime('%Y-%m-%d %H')
pre_bike_data['대여일시_시'] = pd.to_datetime(pre_bike_data['대여일시_시'])
pre_bike_data['반납일시_시'] = pd.to_datetime(pre_bike_data['반납일시_시'])
# 기존 컬럼 삭제
pre_bike_data.drop(columns=['대여일시', '반납일시'], inplace=True)
pre_bike_data = pre_bike_data[['자전거번호', '대여일시_시분초', '대여일시_시분','대여일시_시','대여_대여소ID', '대여_대여소명',  '대여_구', '대여_동','대여_X좌표','대여_Y좌표', '대여_대여소주소',
                               '반납일시_시분초', '반납일시_시분','반납일시_시','반납_대여소ID', '반납_대여소명', '반납_구', '반납_동',  '반납_X좌표', '반납_Y좌표','반납_대여소주소',
                               '이용시간(분)', '이용거리(km)', '연령대', '성별','내외국인구분',
                               '대여일자','대여연도', '대여월', '대여시간', '반납일자', '반납시간', '반납연도', '반납월']]

bike_data = pre_bike_data.sort_values(by='대여일시_시분초')

'''
--공식대여소 기준으로 대여이력 추출 시 진행----------------------------------------------------------------------------------------
# # 대여 대여소를 기준으로 정식타슈 대여소인 1175개에 해당되지 않는 이력정보는 삭제
# not_station = bike_data[~bike_data['대여_대여소명'].isin(station_locations['name'])] #181,009건
# not_station_value_counts = not_station[['대여_대여소명','대여_대여소주소']].value_counts().reset_index() #타슈관제센터 정비입고 : 76,884건
# 
# # 'b' 데이터프레임의 값과 동일한 행을 'a' 데이터프레임에서 삭제
# pre_bike_data = bike_data[~bike_data.isin(not_station.to_dict('list')).all(axis=1)] #6,461,362
# 
# # 반납 대여소를 기준으로 정식타슈 대여소인 1175개에 해당되지 않는 이력정보는 삭제
# not_station2 = pre_bike_data[~pre_bike_data['반납_대여소명'].isin(station_locations['name'])] #146,762건
# not_station_value_counts2 = not_station2[['반납_대여소명','반납_대여소주소']].value_counts().reset_index() #타슈관제센터 정비입고 : 57,657건
# 
# # 'b' 데이터프레임의 값과 동일한 행을 'a' 데이터프레임에서 삭제
# pre_bike_data = pre_bike_data[~pre_bike_data.isin(not_station2.to_dict('list')).all(axis=1)] #6,314,600건
-----------------------------------------------------------------------------------------------------------------------------------------
'''

# 데이터건수가 부족한 2022.07 데이터 삭제
deleted_202207 = bike_data[(bike_data['대여연도'] == 2022) & (bike_data['대여월'] == 7)]
result_bike_data = bike_data[~bike_data.isin(deleted_202207.to_dict('list')).all(axis=1)]

#추가 전처리 (나중에 발견)
# 신인동의 경우 (신흥동,인동)을 포함하는 행정동 정보임으로 임의로 신흥동으로 변경하여 산출
result_bike_data[['대여_동', '반납_동']] = result_bike_data[['대여_동', '반납_동']].replace('신인동', '신흥동')
# 전민동의 경우 유성구에 해당되는 법정동인데 서구로 잘못들어가 있는 경우 2,785건 발견하여 서구에서 유성구로 변경함
result_bike_data.loc[(result_bike_data['반납_구'] == '서구') & (result_bike_data['반납_동'] == '전민동'), '반납_구'] = '유성구'
result_bike_data.loc[(result_bike_data['대여_구'] == '서구') & (result_bike_data['대여_동'] == '전민동'), '대여_구'] = '유성구'

# id 컬럼값이 'ST0219', 'ST0418'인 행의 gu 컬럼값을 '유성구'로 수정
result_bike_data.loc[result_bike_data['대여_대여소ID'].isin(['ST0219', 'ST0418']), '대여_구'] = '유성구'
result_bike_data.loc[result_bike_data['반납_대여소ID'].isin(['ST0219', 'ST0418']), '반납_구'] = '유성구'
# id 컬럼값이 'ST0423'인 행의 gu 컬럼값을 '대덕구'로 수정
result_bike_data.loc[result_bike_data['대여_대여소ID'] == 'ST0423', '대여_구'] = '대덕구'
result_bike_data.loc[result_bike_data['반납_대여소ID'] == 'ST0423', '반납_구'] = '대덕구'

#result_bike_data.to_pickle(os.path.join(path_data_output,'1.pretreatment','02.내부','01.대여반납이력','result_bike_data_0430.pkl'))

# 타슈 대여소 내역 데이터 전처리
station_locations = station_locations.drop_duplicates()
station_locations['gu'] = station_locations['gu'].replace('유상구', '유성구') # '유상구' 값을 '유성구'로 수정
# 대여소 정보 데이터 추가처리 (대여소 정보)
station_locations['dong'] = station_locations['dong'].replace('신인동', '신흥동')
# id 컬럼값이 'ST0219', 'ST0418'인 행의 gu 컬럼값을 '유성구'로 수정
station_locations.loc[station_locations['id'].isin(['ST0219', 'ST0418']), 'gu'] = '유성구'
# id 컬럼값이 'ST0423'인 행의 gu 컬럼값을 '대덕구'로 수정
station_locations.loc[station_locations['id'] == 'ST0423', 'gu'] = '대덕구'

station_locations.to_csv(os.path.join(path_data_output,'1.pretreatment','02.내부','02.대여소정보','station_locations.csv'),encoding='cp949')
station_locations_gpkg = gpd.read_file(path_data_output+'//3.result//2024-04-25//03.shp//대여소_위치정보.gpkg', driver='GPKG') # 타슈 대여소 내역 데이터 위치좌표
station_locations_gpkg['dong'] = station_locations_gpkg['dong'].replace('신인동', '신흥동')
station_locations_gpkg.to_file(path_data_output+'//3.result//2024-04-25//03.shp//대여소_위치정보.gpkg', driver='GPKG')

#2024-05-24 추가 데이터 전처리 (대여이력데이터 4-5월)
path_base     = "2024-05-24"
path_data_out     = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"01.외부")
path_data_in      = os.path.join(config_info["PATH_DATA_COLLECT"],path_base,"02.내부")

path_data_list = os.path.join(path_data_in,'대전시 공영자전거 타슈 대여이력 정보(24년 4월~5월, 관리자재배치실적)','대전시 공영자전거 타슈 대여이력 정보*.csv')
file_paths = glob.glob(path_data_list)
all_data = []
for file_path in file_paths:
    df = pd.read_csv(file_path,encoding='cp949')
    all_data.append(df)
bike_rental_data_0524 = pd.concat(all_data)
pre_bike_data_0524 = bike_rental_data_0524.copy() # 1,067,714행
pre_bike_data_0524 = pre_bike_data_0524.drop_duplicates() #중복행 제거 # 1,067,714행 : 동일 (중복행 없음)

# 각 컬럼별로 널값 확인
#null_counts = pre_bike_data_0524.isnull().sum()
#print("각 컬럼별 널값 수:")
#print(null_counts)

# 대여_구와 대여_동 중 하나라도 널값인 행 추출하여 대여_대여소주소 컬럼의 값을 이용하여 채워넣음
missing_rental = pre_bike_data_0524[pre_bike_data_0524['대여_구'].isnull() | pre_bike_data_0524['대여_동'].isnull()]
missing_rental_fill = missing_rental.copy()
missing_rental_fill['대여_구'] = missing_rental_fill['대여_대여소주소'].str.extract(r'(\S+구)').fillna(missing_rental_fill['대여_구'])
missing_rental_fill['대여_동'] = missing_rental_fill['대여_대여소주소'].str.extract(r'(\S+동)').fillna(missing_rental_fill['대여_동'])

# 기존 결측치 행 삭제
pre_bike_data_0524.dropna(subset=['대여_구', '대여_동'],inplace=True)
# 대여_구,대여_동 결측치를 채운 데이터로 업데이트
pre_bike_data_0524 = pd.concat([pre_bike_data_0524, missing_rental_fill])

# 반납_구와 반납_동 중 하나라도 널값인 행 추출하여 반납_대여소주소 컬럼의 값을 이용하여 채워넣음
missing_return = pre_bike_data_0524[pre_bike_data_0524['반납_구'].isnull() | pre_bike_data_0524['반납_동'].isnull()]
missing_return_fill = missing_return.copy()
missing_return_fill['반납_구'] = missing_return_fill['반납_대여소주소'].str.extract(r'(\S+구)').fillna(missing_return_fill['반납_구'])
missing_return_fill['반납_동'] = missing_return_fill['반납_대여소주소'].str.extract(r'(\S+동)').fillna(missing_return_fill['반납_동'])

# 기존 결측치 행 삭제
pre_bike_data_0524.dropna(subset=['반납_구', '반납_동'],inplace=True)
# 반납_구,반납_동 결측치를 채운 데이터로 업데이트
pre_bike_data_0524 = pd.concat([pre_bike_data_0524, missing_return_fill])
# '유상구' 값을 '유성구'로 수정
pre_bike_data_0524['대여_구'] = pre_bike_data_0524['대여_구'].replace('유상구', '유성구')
pre_bike_data_0524['반납_구'] = pre_bike_data_0524['반납_구'].replace('유상구', '유성구')

# 신인동의 경우 (신흥동,인동)을 포함하는 행정동 정보임으로 임의로 신흥동으로 변경하여 산출
pre_bike_data_0524[['대여_동', '반납_동']] = pre_bike_data_0524[['대여_동', '반납_동']].replace('신인동', '신흥동')
# 전민동의 경우 유성구에 해당되는 법정동인데 서구로 잘못들어가 있는 경우 2,785건 발견하여 서구에서 유성구로 변경함
pre_bike_data_0524.loc[(pre_bike_data_0524['반납_구'] == '서구') & (pre_bike_data_0524['반납_동'] == '전민동'), '반납_구'] = '유성구'
pre_bike_data_0524.loc[(pre_bike_data_0524['대여_구'] == '서구') & (pre_bike_data_0524['대여_동'] == '전민동'), '대여_구'] = '유성구'

# id 컬럼값이 'ST0219', 'ST0418'인 행의 gu 컬럼값을 '유성구'로 수정
pre_bike_data_0524.loc[pre_bike_data_0524['대여_대여소ID'].isin(['ST0219', 'ST0418']), '대여_구'] = '유성구'
pre_bike_data_0524.loc[pre_bike_data_0524['반납_대여소ID'].isin(['ST0219', 'ST0418']), '반납_구'] = '유성구'
# id 컬럼값이 'ST0423'인 행의 gu 컬럼값을 '대덕구'로 수정
pre_bike_data_0524.loc[pre_bike_data_0524['대여_대여소ID'] == 'ST0423', '대여_구'] = '대덕구'
pre_bike_data_0524.loc[pre_bike_data_0524['반납_대여소ID'] == 'ST0423', '반납_구'] = '대덕구'
##대여일시_전처리 및 반납일시_전처리 전처리
# 대여일시_전처리 컬럼을 공백을 기준으로 분리하여 날짜와 시간 컬럼으로 나누기
pre_bike_data_0524[['대여일자', '대여시간']] = pre_bike_data_0524['대여일시'].str.split(expand=True)
pre_bike_data_0524[['반납일자', '반납시간']] = pre_bike_data_0524['반납일시'].str.split(expand=True)


# 시간 형식을 'HH:MM:SS'로 통일하는 함수
def format_time(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:  # HH:MM:SS
        h, m, s = parts
    elif len(parts) == 2:  # HH:MM
        h, m = parts
        s = '00'
    else:  # HH or other
        raise ValueError(f"Unexpected time format: {time_str}")
    h = h.zfill(2)
    m = m.zfill(2)
    s = s.zfill(2)
    return f"{h}:{m}:{s}"

# '대여시간' 컬럼에 시간 형식 통일 함수 적용
pre_bike_data_0524['대여시간'] = pre_bike_data_0524['대여시간'].apply(format_time)
pre_bike_data_0524['반납시간'] = pre_bike_data_0524['반납시간'].apply(format_time)
# 대여일자와 대여시간을 조합하여 새로운 컬럼 생성
pre_bike_data_0524['대여일시_전처리'] = pre_bike_data_0524['대여일자'] + ' ' + pre_bike_data_0524['대여시간']
pre_bike_data_0524['반납일시_전처리'] = pre_bike_data_0524['반납일자'] + ' ' + pre_bike_data_0524['반납시간']
#datetime
pre_bike_data_0524['대여일시_전처리'] = pd.to_datetime(pre_bike_data_0524['대여일시_전처리'])
pre_bike_data_0524['반납일시_전처리'] = pd.to_datetime(pre_bike_data_0524['반납일시_전처리'])
pre_bike_data_0524['대여일자'] = pd.to_datetime(pre_bike_data_0524['대여일자'])
pre_bike_data_0524['반납일자'] = pd.to_datetime(pre_bike_data_0524['반납일자'])

# 연도와 월을 추출하여 새로운 열 생성
pre_bike_data_0524['대여연도'] = pre_bike_data_0524['대여일시_전처리'].dt.year
pre_bike_data_0524['대여월'] = pre_bike_data_0524['대여일시_전처리'].dt.month

pre_bike_data_0524['반납연도'] = pre_bike_data_0524['반납일시_전처리'].dt.year
pre_bike_data_0524['반납월'] = pre_bike_data_0524['반납일시_전처리'].dt.month

pre_bike_data_0524.rename(columns={'대여일시_전처리': '대여일시_시분초', '반납일시_전처리': '반납일시_시분초'}, inplace=True)
# 초 부분 삭제 및 새로운 컬럼 생성
pre_bike_data_0524['대여일시_시분'] = pd.to_datetime(pre_bike_data_0524['대여일시_시분초']).dt.strftime('%Y-%m-%d %H:%M')
pre_bike_data_0524['반납일시_시분'] = pd.to_datetime(pre_bike_data_0524['반납일시_시분초']).dt.strftime('%Y-%m-%d %H:%M')
pre_bike_data_0524['대여일시_시분'] = pd.to_datetime(pre_bike_data_0524['대여일시_시분'])
pre_bike_data_0524['반납일시_시분'] = pd.to_datetime(pre_bike_data_0524['반납일시_시분'])
pre_bike_data_0524['대여일시_시'] = pd.to_datetime(pre_bike_data_0524['대여일시_시분초']).dt.strftime('%Y-%m-%d %H')
pre_bike_data_0524['반납일시_시'] = pd.to_datetime(pre_bike_data_0524['반납일시_시분초']).dt.strftime('%Y-%m-%d %H')
pre_bike_data_0524['대여일시_시'] = pd.to_datetime(pre_bike_data_0524['대여일시_시'])
pre_bike_data_0524['반납일시_시'] = pd.to_datetime(pre_bike_data_0524['반납일시_시'])
# 기존 컬럼 삭제
pre_bike_data_0524.drop(columns=['대여일시', '반납일시'], inplace=True)
pre_bike_data_0524 = pre_bike_data_0524[['자전거번호', '대여일시_시분초', '대여일시_시분','대여일시_시','대여_대여소ID', '대여_대여소명',  '대여_구', '대여_동','대여_X좌표','대여_Y좌표', '대여_대여소주소',
                               '반납일시_시분초', '반납일시_시분','반납일시_시','반납_대여소ID', '반납_대여소명', '반납_구', '반납_동',  '반납_X좌표', '반납_Y좌표','반납_대여소주소',
                               '이용시간(분)', '이용거리(km)', '연령대', '성별','내외국인구분',
                               '대여일자','대여연도', '대여월', '대여시간', '반납일자', '반납시간', '반납연도', '반납월']]

bike_data_0524 = pre_bike_data_0524.sort_values(by='대여일시_시분초')
bike_data_0524.to_pickle(os.path.join(path_data_output,'1.pretreatment','02.내부','01.대여반납이력','result_bike_data_0524.pkl'))


#타슈 관리자 배치,재배치,점검요청,입고(관리자실적)_2024_0523 데이터 pkl 변환
batch_management_0524 = pd.read_csv(path_data_in+'\\대전시 공영자전거 타슈 대여이력 정보(24년 4월~5월, 관리자재배치실적)\\타슈 관리자 배치,재배치,점검요청,입고(관리자실적)_2024_0523.csv',encoding='cp949')
batch_management_0524 = batch_management_0524[['parking_type','parking_type.1','station','bike','reg_date']]
batch_management_0524.to_pickle(os.path.join(path_data_output,'1.pretreatment','02.내부','03.배치_재배치','batch_management_0524.pkl'))