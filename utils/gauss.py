#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scipy.stats as stats
import numpy as np
import threading
import csv


def gauss(mu, sigma, number):
    '''
    返回指定number大小的截断高斯分布

    Args:
        mu (int/float): 均值
        sigma (int/float): 方差
        number (int): 高斯分布随机变量个数

    Returns:
        np.ndarray: 指定number大小的截断高斯分布
    '''
    lower, upper = -3, 3
    X = stats.truncnorm(lower, upper, loc=mu, scale=sigma)
    return X.rvs(size=number)


def gaussion(mu1, mu2, sigma1, sigma2, inf, change_point):
    '''
    生成两段的截断高斯分布

    Args:
        mu1 (int/float): 均值
        mu2 (int/float): 均值
        sigma1 (int/float): 方差
        sigma2 (int/float): 方差
        inf (int): 无限的大小
        change_point (int): 转折点

    Returns:
        list: 一整个过程
    '''
    yn = gauss(mu1, sigma1, change_point)
    xn = gauss(mu2, sigma2, inf - change_point)
    return np.append(yn, xn).tolist()


def gauss_list(mu1, mu2, sigma1, sigma2, inf, change_point, list_length):
    '''
    生成list_length组过程

    Args:
        mu1 (int/float): 均值
        mu2 (int/float): 均值
        sigma1 (int/float): 方差
        sigma2 (int/float): 方差
        inf (int): 无限的大小
        change_point (int): 转折点
        list_length (int): 过程的总数量

    Returns:
        list of list: 若干组过程
    '''
    gauss_list = []
    for i in range(list_length):
        X = gaussion(mu1, mu2, sigma1, sigma2, inf, change_point)
        gauss_list.append(X)
    print(len(gauss_list), 'Gauss Process generated!')
    return gauss_list


def calculate(change_point, inf, a, b, xy):
    '''
    计算c^2

    Args:
        change_point (int): 转折点
        inf (int): 无限的大小
        a (float): 参数
        b (float): 参数
        xy (list): 一组过程

    Returns:
        float: c^2
    '''
    sum1 = 0
    sum2 = 0
    for i in range(change_point):
        sum1 = sum1 + a * (1 - a)**i * xy[i]
    for i in range(change_point, inf):
        sum2 = sum2 + a * (1 - a)**i * xy[i]
    down = (sum1 + sum2) * (sum1 + sum2)
    sum_a = 0
    for i in range(change_point):
        sum_x = 0
        sum_y = 0
        for j in range(i, change_point):
            sum_y = sum_y + a * (1 - a)**(j - i) * xy[j]
        for j in range(change_point, inf):
            sum_x = sum_x + a * (1 - a)**(j - i) * xy[j]
        sum_a = sum_a + b * (1 - b)**i * (xy[i] - sum_y - sum_x) * (xy[i] - sum_y - sum_x)
    sum_b = 0
    for i in range(change_point, inf):
        sum_x = 0
        for j in range(i, inf):
            sum_x = sum_x + a * (1 - a)**(j - i) * xy[j]
        sum_b = sum_b + b * (1 - b)**i * (xy[i] - sum_x) * (xy[i] - sum_x)
    up = sum_a + sum_b
    c2 = up / down
    return c2


def calculate_b(a, xy):
    b_list = []
    for b in range(1, 10000):
        c2_list = []
        for elem in xy:
            c2 = calculate(10, 100, a / 100, b / 10000, elem)
            c2_list.append(c2)
        b_list.append(abs(np.mean(c2_list) - 0.05277))
    print(b_list[np.argmin(np.array(b_list))])
    return np.argmin(np.array(b_list)) + 1


class multi_calculate(threading.Thread):
    def __init__(self, aa, xy):
        threading.Thread.__init__(self)
        self.aa = aa
        self.xy = xy

    def run(self):
        # c2_list = []
        # for bb in range(1, 100):
        #     for elem in self.xy:
        #         c2 = calculate(10, 100, self.aa / 100, bb / 100, elem)
        #         c2_list.append(c2)
        # csvFile = open("data/" + str(self.aa) + ".csv", "w")
        # writer = csv.writer(csvFile)
        # writer.writerow(c2_list)
        # csvFile.close()
        # print(str(self.aa) + ' done!')
        b = [calculate_b(self.aa, self.xy)]
        csvFile = open("data_run/" + str(self.aa) + ".csv", "w")
        writer = csv.writer(csvFile)
        writer.writerow(b)
        csvFile.close()
        print(str(self.aa) + ' done!')


def main():
    xy = gauss_list(mu1=16,
                    mu2=20,
                    sigma1=3,
                    sigma2=4,
                    inf=100,
                    change_point=10,
                    list_length=100)
    for aa in range(1, 100):
        t = multi_calculate(aa, xy)
        t.start()


if __name__ == "__main__":
    main()
