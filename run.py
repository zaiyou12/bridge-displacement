import os
import glob
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
import numpy as np
from skimage import io
from skimage.transform import hough_ellipse
from skimage.feature import canny
from skimage.color import rgb2gray


# 환경설정
def initial_setting():
    if os.path.exists('setting.env'):
        print('Importing environment from setting.env...')
        for line in open('setting.env'):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]
                # print(var[0], '=', var[1])


# 최근 파일 불러오기
# def get_latest_file(file_url):
#     list_of_files = glob.glob(file_url)
#     if not list_of_files:
#         print('File directory', file_url, 'is empty')
#         return None
#     else:
#         latest_file = max(list_of_files, key=os.path.getctime)
#         return latest_file


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
def get_distance():
    # update all variable
    initial_setting()
    file_url = os.path.join(os.getcwd(), os.environ.get('file_url'))
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
        print('Some variable is none, please check setting.env')
    else:
        # get images and pre-processing
        # 이미지를 불러온뒤 전처리
        image_1 = io.imread(file_url)[x1_start:x1_end, y1_start:y1_end]
        image_2 = io.imread(file_url)[x2_start:x2_end, y2_start:y2_end]
        image_3 = io.imread(file_url)[x3_start:x3_end, y3_start:y3_end]
        # find circles and get center of the circles
        # 원과 원의 중심 찾기
        yc1, xc1 = find_circle(image_1, x_start=x1_start, y_start=y1_start)
        yc2, xc2 = find_circle(image_2, x_start=x2_start, y_start=y2_start)
        yc3, xc3 = find_circle(image_3, x_start=x3_start, y_start=y3_start,)
        # calculate distance
        # 거리 계산
        v1 = np.array([yc2, xc2]) - np.array([yc1, xc1])  # vector form point 1 to point 2
        v2 = np.array([yc3, xc3]) - np.array([yc1, xc1])  # vector form point 1 to point 3
        delta = np.vdot(v1, v2) / (np.linalg.norm(v1))  # get distance between point 1 and point 2
        result = delta / np.linalg.norm(v1)  # ratio of the current distance to the reference distance
        print(datetime.now(), 'The result is', result)


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(get_distance, 'interval', seconds=30, next_run_time=datetime.now())
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
