import os
from lxml import etree
import json
import pymysql

import requests
import re

# 定义一个函数
# 这个函数用来创建连接(连接数据库用)

def mysql_db():
    # 连接数据库肯定需要一些参数
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        database="music_recommend_python",
        charset="utf8",
        user="root",
        passwd="root"
    )
    return conn

filename = "static\songFile"
imgName = "static\songImg"
songLyric = "static\songLyric"

if not os.path.exists(filename):
    os.mkdir(filename)

if not os.path.exists(imgName):
    os.mkdir(imgName)

if not os.path.exists(songLyric):
    os.mkdir(songLyric)

# 下载图片
def downloadImage(url):
    response = requests.get(url)
    print("下载路径：" + url)
    path = 'static/songImg/' + f'{id}.jpg'
    with open(path, 'wb') as f:
        f.write(response.content)
    return f'{id}.jpg'

# 下载歌曲
def downloadSong(song_id, name):
    url = f'http://music.163.com/song/media/outer/url?id={song_id}.mp3'
    response = requests.get(url)
    print("下载路径：" + url)
    path = 'static/songFile/' + f'{name}.mp3'
    with open(path, 'wb') as f:
        f.write(response.content)
    return f'{name}.mp3'

# 下载歌词
def downloadLyric(song_id, name):
    url  = 'http://music.163.com/api/song/lyric?id={}&lv=-1&kv=-1&tv=-1'.format(song_id)
    response = requests.get(url)
    print("下载路径：" + url)
    jsonStr = response.text
    obj = json.loads(jsonStr)
    path = 'static/songLyric/' + f'{name}.txt'
    with open(path, 'wb') as f:
        f.write(bytes(obj['lrc']['lyric'],'utf-8'))
    return f'{name}.txt'

url = "https://music.163.com/discover/toplist?id=3778678"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Cookie":"_ntes_nnid=f19445c4e53e0bb579e26bc19b054424,1660769030826; _ntes_nuid=f19445c4e53e0bb579e26bc19b054424; NMTID=00Osfk7bPD7s7JZikAGn6pQ8KvnDBwAAAGCrYxP6g; WEVNSM=1.0.0; WNMCID=xlgnep.1660769031160.01.0; WM_TID=V8C1YCosKQBEAVAVUQLQCJ3zwOF3SOHb; __bid_n=18485de7b06322bb9f4207; vinfo_n_f_l_n3=f895f43f9023794d.1.1.1674059979275.1674061799948.1674064052232; FPTOKEN=aU3ZOzMZHp/ma/cRIgT/SI9WV/+3prbJpO9dBhbc8+vBkdhgZKYvlXIjDSzqKUxM2BB6uxRicjMNAyqzBXQmlT7YYG1nxBnyG9c4xXQx1ronrkhbyioih49xacKPyOcyWsDeXdFryv+pKGlRy23bQgdG2W07XKoPeao3xu12HI+UpXjYOrV1IzxqQGcGzDTU0qL1Q0nefl7wbsLLn+SE2xXAdW/NI4B/oIsZn5ntiuuCCWuSvXz1BdahMJcx03zVM9TQMDrZmMih9Mwt66cFOl93J3Vma5D6pQGnmRCJVTvBptqWdL+35YU0XAWp3q0Y3hiUAgmBYsQiBnhBn6ifVghnxAN66bVH9o/ZJpVR2e8mkx70wd0MRMLSYQ7mMDJarprqAqICnGt2OaDDcxJVwA==|X6jinIgivXgf/TIKydPHWzjiu1X8lxhqb2rYps70K9E=|10|fc06dbd63aa81ab0129cbc52711570c1; WM_NI=ZsonERsLN/Gem79lGIp14226SOEw1FKbJzLwGgEBPRS6u8JIRIIRg1VDuVBdBhn36MfQoHhodSIxJbdhu1Kk2+ocxhBMQltrd/4WvaEzYD1DVMsyeAs9fcDhBXEbnP83bk4=; WM_NIKE=9ca17ae2e6ffcda170e2e6eeadd963978da6adc66698ef8aa3d44a939f8f82c56f949f99a3b164a19ab6adc82af0fea7c3b92a9aada18fc85ab19482d0c66fafe9f78dc643b4effcd3b13e91918b98b44e89be869bcf7d85b98ba3d35a91eabbd9c943929787b3e63b969cbbb7c17082b8a2d4b547a68fa1a9eb65a88d8799c96aa8b8bbd2ca61f2f5a184fb6482939f8df77aa8f1fcb8f56b87a697a5b4509693bd9ae84bb1e7aa84c76482888b83ed5cfcedae8cb737e2a3; JSESSIONID-WYYY=IkisChIgAjetRu4GuJ\A+2PgM0tyyFQt9OSo5tjHTwbItlvczhImb/MTnCEUjgBZpxQWXYygKOHSkX\OA8yf1UNAJI2WO8/DjJADvl00vPFQ7nKRks6GTTBcnAx7E92VzVQTcurCg73OZjW6kqEuWSld5J\H5slk1EogqEenCCUvBQfB:1678284609831; _iuqxldmzr_=33"
}
# 爬虫在这里！
response = requests.get(url=url,headers=headers)
print(response.text)
# id和名称
patten = '<li><a href="/song\?id=(\d+)">(.*?)</a></li>'
songListHtml = re.findall(patten, response.text)
i = 0
for id, name in songListHtml:
    print("当前歌曲为：" + id + "---" + name)
    if name.find("/") >= 0:
        continue
    songDetailUrl = "https://music.163.com/song?id=" + id
    response = requests.get(url=songDetailUrl,headers=headers)
    text = response.text
    html = etree.HTML(text)
    print(text)
    image_url_arr = html.xpath('//img/@data-src')
    imagePath = ''
    for url in image_url_arr:
        imagePath = downloadImage(url)
    songPath = downloadSong(id, name)
    lyricPath = downloadLyric(id, name)
    arr = html.xpath('//p[@class="des s-fc4"]//a[@class="s-fc7"]')
    # 将数据插入到数据库中
    # 打开数据库可能会有风险，所以添加异常捕捉
    conn = mysql_db()
    try:
        with conn.cursor() as cursor:
            # 准备SQL语句
            sql = f'insert into index_song (song_name, song_singer, song_time, song_album, song_languages, song_type, song_release, song_img, song_lyrics, song_file, label_id) value (' \
                  f'"{name}", "{arr[0].text}", "", "{arr[1].text}", "国语", "1", "", "static/songImg/{imagePath}", "static/songLyric/{lyricPath}", "static/songFile/{songPath}", 1)'
            print(sql)
            # 执行SQL语句
            cursor.execute(sql)
            # 执行完SQL语句后的返回结果都是保存在cursor中
            # 所以要从cursor中获取全部数据
            conn.commit()
    except Exception as e:
        print("数据库操作异常：\n", e)
    finally:
        # 不管成功还是失败，都要关闭数据库连接
        conn.close()

    i = i + 1
    if i == 100:
        break


# 匹配图片下载的正则表达式
# songDetail = requests.get()
# picUrlPattern = ''







# for id, name in fileDownUrl:
#     down_url = f'http://music.163.com/song/media/outer/url?id={id}.mp3'
#     response = requests.get(down_url)
#     with open(filename + f'{name}.mp3', 'wb') as f:
#         f.write(response.content)
#     print(name)


