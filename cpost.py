#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from datetime import datetime

import requests
import hashlib
import base64
import time
import json
import configparser
import os
import re


def get_token(deviceId="34de7eef-8400-3300-8922-a1a34e7b9b4f"):
    """
    创建访问必要的token
    :param deviceId:  设备id
    :return: token
    """
    ctime = int(time.time())
    md5Timestamp = hashlib.new('md5', str(ctime).encode()).hexdigest()
    arg1 = "token://com.coolapk.market/c67ef5943784d09750dcfbb31020f0ab?" + md5Timestamp + "$" + deviceId + "&com.coolapk.market"
    md5Str = hashlib.new('md5', base64.b64encode(arg1.encode())).hexdigest()
    token = md5Str + deviceId + str(hex(ctime))
    return token


def request_cool(token, url):
    headers = {"X-App-Token": token,
               "X-App-Version": "10.5.3",
               "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; Nexus 6P Build/MMB29M) (#Build; google; Nexus 6P; MMB29M; 6.0.1) +CoolMarket/10.5.3-2009271",
               "X-Api-Version": "10",
               "X-App-Device": "QZDIzVHel5EI7UGbn92bnByOpV2dhVHSgszQyoTMzoDM2oTQCpDMwoDNyAyOsxWduByO2ADO4kjNxIDM2gjN3YDOgsDZiBTYykzYkZDNlBzY0ITZ",
               "Accept-Encoding": "gzip",
               "X-Dark-Mode": "0",
               "X-Requested-With": "XMLHttpRequest",
               "X-App-Code": "2009271",
               "X-App-Id": "com.coolapk.market"
               }
    # 隐藏警告
    requests.packages.urllib3.disable_warnings()
    r = requests.get(url, headers=headers, verify=False)
    data = json.loads(r.text)

    return data


def read_ini(type='posts'):
    """
    读取配置文件
    :return:
    """

    cfg = configparser.ConfigParser()
    cfg.read("./save.ini")

    if type == "posts":
        data = cfg.get("cpost", type).split(',')
        return data
    elif type == 'clear':
        cfg.set("cpost", "posts", '')
        cfg.write(open("save.ini", "w"))


def update_single_file(id):
    """
    增加帖子评论
    :param id: 帖子id
    :return:
    """
    fileHead = time.strftime('%Y{y}%m{m}%d{d}%H{h}', time.localtime()).format(y='年', m='月', d='日', h='点')
    # root = "./docs/cpost/"
    root = "./docs/test/"

    print("休眠10秒，即将开始{}".format(id))
    time.sleep(10)
    path = root + id + '.md'
    page = 1
    data = [1]

    # 获取评论
    while len(data) != 0:
        url = 'https://api.coolapk.com/v6/feed/replyList?listType=lastupdate_desc&id={}&feedType=feed&discussMode=1&page={}'.format(id, page)
        page += 1
        token = get_token()
        data = request_cool(token, url)["data"]

        with open(path, 'a', encoding='utf-8') as f:
            for item in data:
                timestamp = int(item["dateline"]) + 8 * 60 * 60
                f.write('- {} [{}](uid={}) : {} '.format(stamp_to_datetime(timestamp), item["username"], item["uid"], item["message"]))
                if item['pic'] == '':
                    f.write('\n\n')
                else:
                    f.write('[图片]({})\n\n'.format(item['pic']))
                # 回复评论
                if item["replyRowsMore"] > 0:
                    # 展开更多评论
                    fpage = 1
                    fdata = [1]
                    while len(fdata) != 0:
                        furl = "https://api.coolapk.com/v6/feed/replyList?feedType=feed_reply&discussMode=0&id={}&listType=&fromFeedAuthor=0&blockStatus=0&page={}".format(item['id'], fpage)
                        fpage += 1
                        ftoken = get_token()
                        fdata = request_cool(ftoken, furl)["data"]
                        for fitem in fdata:
                            ftimestamp = int(fitem["dateline"]) + 8 * 60 * 60
                            if fitem['rusername'] != "":
                                f.write('    - {} [{}](uid={}) 回复 [{}](uid={}): {} '.format(stamp_to_datetime(ftimestamp), fitem['username'], fitem['uid'],
                                                                                            fitem['rusername'], fitem['ruid'],
                                                                                            fitem['message']))
                            else:
                                f.write(
                                    '    - {} [{}](uid={}) : {} '.format(stamp_to_datetime(ftimestamp), fitem["username"], fitem["uid"], fitem["message"]))
                            if fitem['pic'] == '':
                                f.write('\n\n')
                            else:
                                f.write('[图片]({})\n\n'.format(fitem['pic']))


                else:
                    for item2 in item["replyRows"]:
                        timestamp = int(item2["dateline"]) + 8 * 60 * 60
                        if item2['rusername'] != "":
                            f.write('    - {} [{}](uid={}) 回复 [{}](uid={}): {} '.format(stamp_to_datetime(timestamp), item2['username'], item2['uid'],
                                                                                        item2['rusername'], item2['ruid'],
                                                                                        item2['message']))
                        else:
                            f.write('    - {} [{}](uid={}) : {} '.format(stamp_to_datetime(timestamp), item2["username"], item2["uid"], item2["message"]))
                        if item2['pic'] == '':
                            f.write('\n\n')
                        else:
                            f.write('[图片]({})\n\n'.format(item2['pic']))
                # for item2 in item["replyRows"]:
                #     timestamp = int(item2["dateline"]) + 8 * 60 * 60
                #     if item2['rusername'] != "":
                #         f.write('    - {} [{}](uid={}) 回复 [{}](uid={}): {} '.format(stamp_to_datetime(timestamp), item2['username'], item2['uid'],
                #                                                                     item2['rusername'], item2['ruid'],
                #                                                                     item2['message']))
                #     else:
                #         f.write('    - {} [{}](uid={}) : {} '.format(stamp_to_datetime(timestamp), item2["username"], item2["uid"], item2["message"]))
                #     if item2['pic'] == '':
                #         f.write('\n\n')
                #     else:
                #         f.write('[图片]({})\n\n'.format(item2['pic']))
    # 文件头部信息
    with open(path, 'r+', encoding='utf-8') as f:
        f.seek(0)
        f.write('> {}更新\n'.format(fileHead))
    f.close()


def update_all_file():
    """
    更新全部帖子评论，现只能第一次添加。费时，少用
    TODO：增量评论
    :return:
    """
    timeName = time.strftime('%Y{y}%m{m}%d{d}', time.localtime()).format(y='年', m='月', d='日')
    fileHead = time.strftime('%Y{y}%m{m}%d{d}%H{h}', time.localtime()).format(y='年', m='月', d='日', h='点')
    root = "./docs/cpost/"

    # 获取文件
    fileNames = os.listdir(root)
    for fileName in fileNames:
        print("休眠10秒，即将开始{}".format(fileName))
        time.sleep(10)
        id, fileType = os.path.splitext(fileName)
        path = root + fileName
        page = 1
        data = [1]

        # 获取评论
        while len(data) != 0:
            url = 'https://api.coolapk.com/v6/feed/replyList?listType=lastupdate_desc&id={}&feedType=feed&discussMode=1&page={}'.format(id, page)
            page += 1
            token = get_token()
            data = request_cool(token, url)["data"]

            with open(path, 'a', encoding='utf-8') as f:
                for item in data:
                    # 回复post
                    timestamp = int(item["dateline"]) + 8 * 60 * 60
                    f.write('- {} [{}](uid={}) : {} '.format(stamp_to_datetime(timestamp), item["username"], item["uid"], item["message"]))
                    if item['pic'] == '':
                        f.write('\n\n')
                    else:
                        f.write('[图片]({})\n\n'.format(item['pic']))
                    # 回复评论
                    if item["replyRowsMore"] > 0:
                        # 展开更多评论
                        fpage = 1
                        fdata = [1]
                        while len(fdata) != 0:
                            furl = "https://api.coolapk.com/v6/feed/replyList?feedType=feed_reply&id={}&page={}".format(item['fid'], fpage)
                            fpage += 1
                            ftoken = get_token()
                            fdata = request_cool(ftoken, furl)["data"]
                            for fitem in fdata:
                                ftimestamp = int(fitem["dateline"]) + 8 * 60 * 60
                                if fitem['rusername'] != "":
                                    f.write('    - {} [{}](uid={}) 回复 [{}](uid={}): {} '.format(stamp_to_datetime(ftimestamp), fitem['username'], fitem['uid'],
                                                                                                fitem['rusername'], fitem['ruid'],
                                                                                                fitem['message']))
                                else:
                                    f.write(
                                        '    - {} [{}](uid={}) : {} '.format(stamp_to_datetime(ftimestamp), fitem["username"], fitem["uid"], fitem["message"]))
                                if fitem['pic'] == '':
                                    f.write('\n\n')
                                else:
                                    f.write('[图片]({})\n\n'.format(fitem['pic']))


                    else:
                        for item2 in item["replyRows"]:
                            timestamp = int(item2["dateline"]) + 8 * 60 * 60
                            if item2['rusername'] != "":
                                f.write('    - {} [{}](uid={}) 回复 [{}](uid={}): {} '.format(stamp_to_datetime(timestamp), item2['username'], item2['uid'],
                                                                                            item2['rusername'], item2['ruid'],
                                                                                            item2['message']))
                            else:
                                f.write('    - {} [{}](uid={}) : {} '.format(stamp_to_datetime(timestamp), item2["username"], item2["uid"], item2["message"]))
                            if item2['pic'] == '':
                                f.write('\n\n')
                            else:
                                f.write('[图片]({})\n\n'.format(item2['pic']))
        # 文件头部信息
        with open(path, 'r+', encoding='utf-8') as f:
            f.seek(0)
            f.write('> {}更新\n'.format(fileHead))
        f.close()


def stamp_to_datetime(stamp):
    """
    将时间戳(1539100800)转换为 datetime2018-10-09 16:00:00格式并返回
    :param stamp:
    :return:
    """
    timeStampArray = datetime.utcfromtimestamp(stamp)
    dateTime = timeStampArray.strftime("%Y-%m-%d %H:%M:%S")
    # 如果直接返回 date_time则为字符串格式2018-10-09 16:00:00
    date = datetime.strptime(dateTime, "%Y-%m-%d %H:%M:%S")
    return date


def datetime_to_stamp(date_time):
    """
    将字符串日期格式转换为时间戳  2018-10-09 16:00:00==>1539100800
    :param date_time:
    :return:
    """
    # 字符类型的时间
    time_array = time.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    time_stamp = int(time.mktime(time_array))
    return time_stamp


if __name__ == '__main__':
    data = read_ini()
    if data[0] != '':
        print("update list:")
        print(data)
        for id in data:
            update_single_file(id)
        read_ini("clear")
