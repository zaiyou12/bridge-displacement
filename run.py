# import glob
import os
import sys
import logging
import logging.handlers
# import csv

import numpy as np
import cx_Oracle
from skimage import io
from skimage.transform import hough_ellipse
from skimage.feature import canny
from skimage.color import rgb2gray


# 환경설정
def initial_setting():
    if os.path.exists('setting.env'):
        for line in open('setting.env'):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]
    else:
        logger.error('Start. No setting.env Err!-- NOK.')
        sys.exit(1)


# DB에서 파일 불러오기
def get_file_from_db():
    db_path = os.environ.get('db_path')
    sql_1 = os.environ.get('sql_1')
    sql_2 = os.environ.get('sql_2')
    sql_3 = os.environ.get('sql_3')
    if any(v is None for v in [db_path, sql_1, sql_2, sql_3]):
        logger.error('Start. Initial_Setting Variable Err!-- NOK.')
        sys.exit(1)
    conn = cx_Oracle.connect(os.environ.get('db_path'))
    cur = conn.cursor()
    cur.execute(sql_1)
    for result in cur:
        MSMN_SEQ, MSIS_SNSR_ID, _, _, _, _, _, _, _, _, IMG_FLNM, IMG_PATH_NM, _, FSTTM_RGSR_ID, FSTTM_RGST_DTTM, _, _ = result
        result = get_distance(IMG_FLNM + IMG_PATH_NM)
        cur.execute(sql_2, (MSMN_SEQ, MSIS_SNSR_ID, result, FSTTM_RGSR_ID, FSTTM_RGST_DTTM))
        cur.execute(sql_3, (MSMN_SEQ, MSIS_SNSR_ID))
    cur.close()
    conn.close()

    """ 자체 폴더에서 불러올시 사용
    cur_path = os.getcwd()
    with open('output.csv', 'a', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['image', 'result'])
        for image in glob.glob('./data/*.jpg'):
            file_url = os.path.join(cur_path, image[2:])
            result = get_distance(file_url)
            image_data = str(image)
            result_data = str(result)
            writer.writerow([image_data, result_data])
            print(image_data, result_data) 
    """


# 이미지 내 원 인식
def find_circle(image, x_start, y_start):
    # pre-processing
    # 사전 작업
    image = rgb2gray(image)
    image = canny(image, sigma=1.75, low_threshold=0.55, high_threshold=0.8)
    # Perform a hough Transform
    # The accuracy corresponds to the bin size of a major axis.
    # The value is chosen in order to get a single high accumulator.
    # The threshold eliminates low accumulators
    # 허프 변환 수행
    # 정확도는 장축의 크기에 따라 달라집니다
    # 하나의 높은 값을 얻기 위한 계산이며
    # 임계값은 낮은 정확도의 값을 제거 합니다.
    result = hough_ellipse(image)
    result.sort(order='accumulator')

    # Estimated parameters for the ellipse
    best = list(result[-1])
    xc, yc, a, b = [int(round(x)) for x in best[1:5]]
    return yc + y_start, xc + x_start


# 거리 계산하기
def get_distance(file_url):
    reference_distance = os.environ.get('reference_distance')
    x1_start = int(os.environ.get('x1_start'))
    x1_end = int(os.environ.get('x1_end'))
    y1_start = int(os.environ.get('y1_start'))
    y1_end = int(os.environ.get('y1_end'))
    x2_start = int(os.environ.get('x2_start'))
    x2_end = int(os.environ.get('x2_end'))
    y2_start = int(os.environ.get('y2_start'))
    y2_end = int(os.environ.get('y2_end'))
    x3_start = int(os.environ.get('x3_start'))
    x3_end = int(os.environ.get('x3_end'))
    y3_start = int(os.environ.get('y3_start'))
    y3_end = int(os.environ.get('y3_end'))

    # check all variables before get distance from image
    # 모든 변수가 있는지 확인
    if any(v is None for v in [file_url, reference_distance, x1_start, x1_end, y1_start, y1_end, x2_start,
                               x2_end, y2_start, y2_end, x3_start, x3_end, y3_start, y3_end]):
        logger.error('Start. Initial_Setting Variable Err!-- NOK.')
        sys.exit(1)
    else:
        # get images and pre-processing
        # 이미지를 불러온뒤 전처리
        image_1 = io.imread(file_url)[x1_start:x1_end, y1_start:y1_end]
        image_2 = io.imread(file_url)[x2_start:x2_end, y2_start:y2_end]
        image_3 = io.imread(file_url)[x3_start:x3_end, y3_start:y3_end]
        # find circles and get center of the circles
        # 원과 원의 중심 찾기
        try:
            yc1, xc1 = find_circle(image_1, x_start=x1_start, y_start=y1_start)
            yc2, xc2 = find_circle(image_2, x_start=x2_start, y_start=y2_start)
            yc3, xc3 = find_circle(image_3, x_start=x3_start, y_start=y3_start)
        except:
            logger.error('Start. input_img. Analysis. Analysis Err! -- NOK.')
            return 'Analysis Err!'
        # calculate distance
        # 거리 계산
        v1 = np.array([yc2+25, -xc2]) - np.array([yc1, -xc1])  # vector form point 1 to point 2
        v2 = np.array([yc3+25, -xc3]) - np.array([yc1, -xc1])  # vector form point 1 to point 3
        delta = np.vdot(v1, v2) / (np.linalg.norm(v1))  # get distance between point 1 and point 2
        result = (delta / np.linalg.norm(v1)) - 0.5  # ratio of the current distance to the reference distance
        logger.info('Start. input_img. Analysis. [' + str(result) + '] output_img. End. -- OK.')
        return result * 320


def set_log():
    # 로그 설정
    set_logger = logging.getLogger('logger')
    # 포매터 생성
    formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
    # 스트림과 파일로 로그 출력하는 핸들러
    file_max_byte = 1024 * 1024 * 100  # 100MB
    file_handler = logging.handlers.RotatingFileHandler('./logger.log', maxBytes=file_max_byte, backupCount=10)
    stream_handler = logging.StreamHandler()
    # 핸들러에 포매터 지정
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    # 로거 인스턴스에 스티림 핸들러와 파일 핸들러 추가
    set_logger.addHandler(file_handler)
    set_logger.addHandler(stream_handler)
    set_logger.setLevel(logging.DEBUG)
    return set_logger


if __name__ == '__main__':
    logger = set_log()
    initial_setting()
    get_file_from_db()
    logger.info('===========================')
