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
path_result   = os.path.join(config_info["PATH_DATA_OUTPUT_RESULT"]  ,'2024-06-14')

import pandas as pd

result_data = pd.read_excel(path_result + '//01.excel//재고량평가2//대여소_seg별_재고수량.xlsx')
result_data['안전재고_최소'] = result_data['재고수량']-0.5 * result_data['재고수량_표준편차']
result_data['안전재고_최대'] = result_data['재고수량']+0.5 * result_data['재고수량_표준편차']
result_data['안전재고_최소'] = result_data['안전재고_최소'].apply(lambda x: 0 if x < 0 else x)
result_data['안전재고_최대'] = result_data['안전재고_최대'].apply(lambda x: 0 if x < 0 else x)
result_data2 = result_data[['대여소ID','평가그룹','재고수량','안전재고_최소','안전재고_최대','회수량','분배량']]
result_data2['재고수량'] = result_data2['재고수량'].astype(int)
result_data2['안전재고_최소'] = result_data2['안전재고_최소'].astype(int)
result_data2['안전재고_최대'] = result_data2['안전재고_최대'].astype(int)
result_data2.rename(columns = {'재고수량':'재고수량_평균'},inplace=True)
result_data2
result_data2.to_excel(path_result + '//01.excel//재고량평가2//최종분석결과_대여소별(안전재고,회수량,분배량).xlsx',index=False)