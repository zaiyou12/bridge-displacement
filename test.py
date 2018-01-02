import os

import matplotlib.pyplot as plt
import matplotlib.patches as patches
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


# 이미지 내 원 인식
def find_circle(image, x_start, y_start, mask=False):
    # pre-processing
    # 사전 작업
    image = rgb2gray(image)
    if mask:
        mask = image > 0.1
        image[mask] = 1
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
        # show image
        image = io.imread(file_url)
        fig, ax = plt.subplots(1)
        ax.imshow(image)
        rect1 = patches.Rectangle((y1_start, x1_start), y1_end - y1_start, x1_end - x1_start, linewidth=1,
                                  edgecolor='r', facecolor='none')
        rect2 = patches.Rectangle((y2_start, x2_start), y2_end - y2_start, x2_end - x2_start, linewidth=1,
                                  edgecolor='g', facecolor='none')
        rect3 = patches.Rectangle((y3_start, x3_start), y3_end - y3_start, x3_end - x3_start, linewidth=1,
                                  edgecolor='b', facecolor='none')
        ax.add_patch(rect1)
        ax.add_patch(rect2)
        ax.add_patch(rect3)
        plt.show()


if __name__ == '__main__':
    get_distance()
