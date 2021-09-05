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


def read_ini(newLastTime=0, type='lastTime'):
    """
    读取配置文件
    :return:
    """

    cfg = configparser.ConfigParser()
    cfg.read("./save.ini")

    data = cfg.get("time", type)
    if type == 'lastTime':
        if newLastTime > int(data):
            cfg.set("time", "lastTime", str(newLastTime))
            cfg.write(open("save.ini", "w"))
    return data


def update_ini(tag, key, value):
    """
    更新配置文件
    :param tag: 标记
    :param key: 键
    :param value: 值
    :return:
    """
    cfg = configparser.ConfigParser()
    cfg.read("./save.ini")
    data = cfg.get(tag, key)
    if data != '':
        cfg.set(tag, key, str(data + ',' + str(value)))
    else:
        cfg.set(tag, key, str(value))
    cfg.write(open("save.ini", "w"))


def save_file(data):
    """
    保存文件
    :return:
    """
    timeName = time.strftime('%Y{y}%m{m}%d{d}', time.localtime()).format(y='年', m='月', d='日')
    fileHead = time.strftime('%Y{y}%m{m}%d{d}%H{h}', time.localtime()).format(y='年', m='月', d='日', h='点')
    root = "./docs/"
    # 时间命名文件
    path = root + timeName + '.md'
    # 固定
    path = root + "2021年09月03日.md"
    old = ''
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            next(f)
            next(f)
            next(f)
            old = f.read()
            f.close()

    newLastTime = data['data'][0]['dateline']
    lastTime = read_ini()
    with open(path, 'w+', encoding='utf-8') as f:
        f.seek(0)
        for item in data["data"]:
            newLastTime = item["dateline"]
            if newLastTime > int(lastTime):
                # 更新配置文件
                update_ini('cpost', 'posts', item["id"])

                # 标题 + 日期
                timestamp = int(item["dateline"]) + 8 * 60 * 60
                messageTitle = item["message_title"]
                if messageTitle != '':
                    f.write('\n\n ## [{} {}](./cpost/{}.md) '.format(messageTitle, str(stamp_to_datetime(timestamp)), item["id"]))
                else:
                    f.write('\n\n ## [{}](./cpost/{}.md) '.format(str(stamp_to_datetime(timestamp)), item["id"]))

                # 内容
                f.write('\n\n [{}]({}) ：{} '.format(item["username"], item["shareUrl"], item["message"]))

                # 附带图片
                picArr = item["picArr"]
                for i in range(0, len(picArr)):
                    if i == 0:
                        f.write('\n\n<div class="album">')
                    if picArr[i] != "":
                        f.write('\n<img class="img-item" src="{}" />'.format(picArr[i]))
                    if i == len(picArr) - 1:
                        f.write('\n</div>')

                # 是否转发
                if ("forwardSourceFeed" in item):
                    forwardSourceFeed = item["forwardSourceFeed"]
                    if forwardSourceFeed is None:
                        f.write('\n\n> {} '.format("原贴已不存在"))
                    else:
                        # 标题
                        oldTimestamp = int(forwardSourceFeed["dateline"]) + 8 * 60 * 60
                        oldMessageTitle = forwardSourceFeed["message_title"]
                        if messageTitle != '':
                            f.write('\n\n> [{} {}](./cpost/{}.md)'.format(oldMessageTitle, stamp_to_datetime(oldTimestamp),
                                                                          forwardSourceFeed["id"]))
                        else:
                            f.write('\n\n> [{}](./cpost/{}.md) '.format(stamp_to_datetime(oldTimestamp), forwardSourceFeed["id"]))
                        # 转发内容
                        f.write(
                            '\n> [{}]({}) : {} '.format(forwardSourceFeed["username"], forwardSourceFeed["shareUrl"],
                                                        str(forwardSourceFeed["message"])))
                        # 附带图片
                        oldPicArr = forwardSourceFeed["picArr"]
                        for item in oldPicArr:
                            if item != "":
                                f.write('\n[图片]({})'.format(item))
                f.write('\n\n ------- \n\n')

        f.write(old)

        f.close()

    # 文件头部信息
    with open(path, 'r+', encoding='utf-8') as f:
        old = f.read()
        f.seek(0)
        f.write('> {}更新\n'.format(fileHead))
        f.write(
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/taotie6/sampleJSON@main/css/photo_show.css">\n')
        f.write('<meta name="referrer" content="no-referrer" />\n')
        f.write(old)
    f.close()


def save_detail_file(data):
    timeName = time.strftime('%Y{y}%m{m}%d{d}', time.localtime()).format(y='年', m='月', d='日')
    fileHead = time.strftime('%Y{y}%m{m}%d{d}%H{h}', time.localtime()).format(y='年', m='月', d='日', h='点')
    root = "./docs/cpost/"

    data = data["data"]
    oldDateline = int(read_ini())

    for post in data:
        # 文件路径
        path = root + str(post["id"]) + ".md"
        old = ''
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                next(f)
                next(f)
                next(f)
                old = f.read()
                f.close()
        url = 'https://api.coolapk.com/v6/feed/detail?id=' + str(post["id"])
        detailData = request_cool(get_token(), url)["data"]
        read_ini(detailData["dateline"])
        if detailData["dateline"] <= oldDateline:
            break
        with open(path, 'w+', encoding='utf-8') as f:
            f.seek(0)
            timestamp = int(detailData["dateline"]) + 8 * 60 * 60
            messageTitle = detailData["message_title"]
            if messageTitle != '':
                f.write('\n\n ## {} {}'.format(messageTitle, str(stamp_to_datetime(timestamp))))
            else:
                f.write('\n\n ## {} '.format(str(stamp_to_datetime(timestamp))))

            # 内容
            f.write('\n\n [{}]({}) ：{} '.format(detailData["username"], detailData["shareUrl"], detailData["message"]))

            # 附带图片
            picArr = detailData["picArr"]
            for i in range(0, len(picArr)):
                if i == 0:
                    f.write('\n\n<div class="album">')
                if picArr[i] != "":
                    f.write('\n<img class="img-item" src="{}" />'.format(picArr[i]))
                if i == len(picArr) - 1:
                    f.write('\n</div>')

            # 是否转发 空：原创 feed：转发+评论
            if ("forwardSourceFeed" in detailData):
                forwardSourceFeed = detailData["forwardSourceFeed"]
                if forwardSourceFeed is None:
                    f.write('\n\n> {} '.format("原贴已不存在"))
                else:
                    oldTimestamp = int(forwardSourceFeed["dateline"]) + 8 * 60 * 60
                    oldMessageTitle = forwardSourceFeed["message_title"]
                    if messageTitle != '':
                        f.write('\n\n> {} {}'.format(oldMessageTitle, stamp_to_datetime(oldTimestamp)))
                    else:
                        f.write('\n\n> {} '.format(stamp_to_datetime(oldTimestamp)))
                    # 转发内容
                    f.write('\n> [{}]({}) : {} '.format(forwardSourceFeed["username"], forwardSourceFeed["shareUrl"],
                                                        str(forwardSourceFeed["message"])))
                    # 附带图片
                    oldPicArr = forwardSourceFeed["picArr"]
                    for item in oldPicArr:
                        if item != "":
                            f.write('\n[图片]({})'.format(item))
            f.write('\n\n ------- \n\n')

        f.close()

        # 文件头部信息
        with open(path, 'r+', encoding='utf-8') as f:
            old = f.read()
            f.seek(0)
            f.write('> {}更新\n'.format(fileHead))
            f.write(
                '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/taotie6/sampleJSON@main/css/photo_show.css">\n')
            f.write('<meta name="referrer" content="no-referrer" />\n')
            f.write(old)
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


def multi_repuest(count):
    """
    获取全部动态信息
    :param count: 总页数
    :return:
    """
    for i in range(count, 0, -1):
        url = "https://api.coolapk.com/v6/user/feedList?uid=1081091&page=" + str(i)
        print(url)
        data = request_cool(token, url)
        save_file(data)
        save_detail_file(data)


if __name__ == '__main__':
    token = get_token()
    url = "https://api.coolapk.com/v6/user/feedList?uid=1081091&page=1"
    data = request_cool(token, url)
    # multi_repuest(16)
    save_file(data)
    save_detail_file(data)
