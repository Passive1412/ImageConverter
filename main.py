from PIL import Image
import numpy as np
import copy
import argparse
import os
import glob
from operator import itemgetter
import time

Paths = \
{
"images": "folder for initial images",
"ascii": "folder for ascii converted images",
"ascii_color": "folder for ascii converted images with color",
"descale": "folder for descaled images",
"greyscale": "folder for ascii greyscale images",
"test": "test folder",
}


def create_dir(home, filename, type):
    dir_name = filename.split('/')[1].split(".")[0]
    for key in Paths.keys():
        value = os.path.join(home, key)
        if not os.path.exists(value):
            os.mkdir(value)
    return dir_name


def resolution_calc(big_number, small_number):
    divide_1 = []
    divide_2 = []
    divide_3 = []

    for i in range(1, big_number,1):
        if big_number % i == 0:
            divide_1.append(i)
        if small_number % i == 0:
            divide_2.append(i)

    for index in divide_1:
        if index in divide_2:
            divide_3.append(index)
    return divide_3


def test_range(n, test_n):
    if n in range(test_n-10, test_n+10):
        range_flag = True
    else:
        range_flag = False
    return range_flag


def test_near(n, test_n):
    difference = abs(n-test_n)
    return difference


def normalize(codec_list):
    sorted_list = list(sorted(codec_list, key=itemgetter(1)))
    norm_list = list(copy.deepcopy(sorted_list))
    min_value = 255
    max_value = 0

    for index in sorted_list:
        if index[1] < min_value:
            min_value = index[1]
        if index[1] > max_value:
            max_value = index[1]
    white_threshold = 255-min_value
    black_threshold = 0

    for counter, index in enumerate(list(sorted_list)):
        norm_list[counter][1] = round((index[1] - min_value + black_threshold)*(white_threshold/(max_value-min_value + black_threshold)))
    return norm_list


def codec(resolution, images):
    codec_dict = {}
    codec_list = [None] * len(images)

    for counter, value in enumerate(images):
        img = Image.open(value).convert('LA')
        img_resized = img.resize((resolution, resolution), Image.ANTIALIAS)
        codec_arr = np.array(img_resized)
        codec_ascii = copy.deepcopy(codec_arr)
        count = 0
        sum = 0
        sum_top = ["top", 0]
        sum_bot = ["bot", 0]
        sum_right = ["right", 0]
        sum_left = ["left", 0]

        for i in range(0,resolution,1):
            for j in range(0,resolution,1):
                count += 1
                sum += codec_arr[j][i][0]
                if i < resolution/2.0:
                    sum_right[1] += codec_arr[j][i][0]
                elif i > resolution/2.0:
                    sum_left[1] += codec_arr[j][i][0]
                if j < resolution/2.0:
                    sum_bot[1] += codec_arr[j][i][0]
                elif j > resolution/2.0:
                    sum_top[1] += codec_arr[j][i][0]

        codec_direction = [sum_top, sum_bot, sum_right, sum_left]

        max_direction = 0
        for counter_1, value_1 in enumerate(codec_direction):
            if codec_direction[counter_1][1] > max_direction:
                max_direction = codec_direction[counter_1][1]
                ascii_direction = codec_direction[counter_1][0]

        sum = round(sum/count)
        print(value, sum)
        ascii_dict = {'sum': sum,
                      'codec_ascii': codec_ascii}
        codec_dict[value] = {}
        codec_dict[value] = ascii_dict

        codec_touple = [value, sum, codec_ascii]
        codec_list[counter] = codec_touple

    codec_list = normalize(codec_list)
    return codec_dict, codec_list


def descale(output_path, resolution_list, width, height, rgb_arr):
    descale_arr = copy.deepcopy(rgb_arr)
    for resolution in resolution_list:
        for i in range(0,width,resolution):
            print(i)
            for j in range(0,height,resolution):
                count = 0
                sum_1 = 0
                sum_2 = 0
                sum_3 = 0

                for ii in range(i, i+resolution, 1):
                    for jj in range(j, j+resolution, 1):
                        sum_1 += rgb_arr[jj][ii][0]
                        sum_2 += rgb_arr[jj][ii][1]
                        sum_3 += rgb_arr[jj][ii][2]
                        count += 1

                for ii_2 in range(i, i + resolution, 1):
                    for jj_2 in range(j, j + resolution, 1):
                        descale_arr[jj_2][ii_2][0] = round(sum_1 / count)
                        descale_arr[jj_2][ii_2][1] = round(sum_2 / count)
                        descale_arr[jj_2][ii_2][2] = round(sum_3 / count)

        img_ascii = Image.fromarray(descale_arr)
        temp_name = os.path.join(output_path, str(resolution))
        img_ascii.save(temp_name + '.png')

    return


def ascii_method(output_path, img, resolution, width, height, grey_arr, codec_dict, codec_list):
    ascii_arr = copy.deepcopy(grey_arr)
    ascii_arr_2 = copy.deepcopy(grey_arr)
    ascii_arr_3 = copy.deepcopy(grey_arr)
    top = 0
    bot = 0
    right = 0
    left = 0
    middle = 0
    for i in range(0,width,resolution):
        for j in range(0,height,resolution):
            count = 0
            sum = 0
            sum_top = ["top", 0]
            sum_bot = ["bot", 0]
            sum_right = ["right", 0]
            sum_left = ["left", 0]
            for ii in range(i, i + resolution, 1):
                for jj in range(j, j + resolution, 1):
                    count += 1
                    sum += grey_arr[jj][ii][0]
                    if ii < i+resolution/2.0:
                        sum_right[1] += grey_arr[jj][ii][0]
                    elif ii > i+resolution/2.0:
                        sum_left[1] += grey_arr[jj][ii][0]
                    if jj < j+resolution/2.0:
                        sum_bot[1] += grey_arr[jj][ii][0]
                    elif jj > j+resolution/2.0:
                        sum_top[1] += grey_arr[jj][ii][0]

            codec_direction = [sum_top, sum_bot, sum_right, sum_left]
            print(type(codec_direction[0]))
            print(np.median(codec_direction))
            #direction_min = min(codec_direction)
            #direction_max = max(codec_direction)
            #if direction_max - direction_min

            codec_direction.append(middle)
            print(codec_direction)
            max_direction = 0
            for counter_1, value_1 in enumerate(codec_direction):
                if codec_direction[counter_1][1] > max_direction:
                    max_direction = codec_direction[counter_1][1]
                    ascii_direction = codec_direction[counter_1][0]

            if ascii_direction == "top":
                top += 1
            if ascii_direction == "bot":
                bot += 1
            if ascii_direction == "right":
                right += 1
            if ascii_direction == "left":
                left += 1
            sum = min(255, round(sum/count))
            distance_min = 250

            for index in codec_dict:
                distance = test_near(int(sum), int(codec_dict[index]['sum']))
                if distance < distance_min:
                    distance_min = distance
                    ascii_sign = index
            count_i = 0
            for ii_2 in range(i, i + resolution, 1):
                count_j = 0
                for jj_2 in range(j, j + resolution, 1):
                    ascii_arr[jj_2][ii_2][0] = codec_dict[ascii_sign]['codec_ascii'][count_j][count_i][0]
                    count_j += 1
                count_i += 1

            for counter, index in enumerate(codec_list):
                distance = test_near(int(sum), int(codec_list[counter][1]))
                if distance < distance_min:
                    distance_min = distance
                    ascii_sign = codec_list[counter][0]
            count_i = 0
            for ii_2 in range(i, i + resolution, 1):
                count_j = 0
                for jj_2 in range(j, j + resolution, 1):
                    ascii_arr_2[jj_2][ii_2][0] = codec_dict[ascii_sign]['codec_ascii'][count_j][count_i][0]
                    count_j += 1
                count_i += 1
    print(top, bot, right, left)
    img_grey = Image.fromarray(ascii_arr)
    temp_name = os.path.join(output_path, str(resolution))
    img_grey.save(temp_name + '.png')

    img_grey_2 = Image.fromarray(ascii_arr_2)
    temp_name_2 = os.path.join(output_path, str(resolution))
    img_grey_2.save(temp_name_2 + '_new_white_codec.png')

    img.save(temp_name_2 + '_orig.png')

    return


def main():
    ### Input options
    parser = argparse.ArgumentParser(description='Process an image')
    parser.add_argument('-f', '--filename', type=str, help='filepath and name')
    parser.add_argument("-t", '--function', type=str, help='what to do with image')
    args = parser.parse_args()

    ### read input options
    method = args.function
    type = args.function

    ### Direcs
    home_path = os.path.dirname(os.path.realpath(__file__))
    dir_name = create_dir(home_path, args.filename, type)

    ### Initial read
    img = Image.open(args.filename)
    img_grey = img.convert('LA')
    ### Image arrays
    rgb_arr = np.array(img)
    grey_arr = np.array(img_grey)

    ### Image attributes
    width = len(rgb_arr[0])
    height = len(rgb_arr)
    big_number = max(width, height)
    small_number = min(width, height)

    if method == 'descale':
        output_path = os.path.join(type, dir_name)
        resolution_list = resolution_calc(big_number, small_number)
        descale(output_path, resolution_list, width, height, rgb_arr)

    elif method == 'ascii':
        output_path = os.path.join(type, dir_name)
        images = glob.glob('codec/*')
        resolution_list = resolution_calc(big_number, small_number)

        target_res = 12
        distance = 100
        for counter, index in enumerate(resolution_list):
            test_distance = test_near(index, target_res)
            if test_distance < distance:
                distance = test_distance
                resolution = resolution_list[counter]

        codec_dict, codec_list = codec(resolution, images)
        ascii_method(output_path, img, resolution, width, height, grey_arr, codec_dict, codec_list)


if __name__ == "__main__":
    main()
