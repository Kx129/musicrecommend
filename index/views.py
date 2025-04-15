from datetime import timedelta, datetime, time
import random
from django.db.models import Count
from django.db.models.functions import TruncHour, ExtractHour, ExtractMonth
from django.http import JsonResponse
from django.shortcuts import render
from .models import *
from .recommend_util import RecommendUtil, calculate_metrics  # 导入计算指标的函数
from .user_score import UserScore

# Create your views here.
def indexView(request):
    # 热搜歌曲
    search_song = Dynamic.objects.select_related('song').order_by('-dynamic_search').all()[:8]
    # 音乐分类
    label_list = Label.objects.all()
    # 热门歌曲
    play_hot_song = Dynamic.objects.select_related('song').order_by('-dynamic_plays').all()[:10]
    # 个性化推荐
    recommend_song = []
    current_user = request.user
    precision, recall, f1 = 0, 0, 0  # 初始化指标值

    if current_user.username:
        # 为true代表已登陆，则通过写协同过滤算法计算推荐
        all_user = MyUser.objects.all()
        all_song = Song.objects.all()
        all_user_song_record = UserSongRecord.objects.all()
        user_list = []
        item_list = []
        user_score_list = []
        for user in all_user:
            user_list.append(user.id)
        for song in all_song:
            item_list.append(song.song_id)
        for user_song_record in all_user_song_record:
            if user_song_record.num > 10:
                user_song_record.num = 10
            user_score = UserScore(user_song_record.user_id, user_song_record.song_id, user_song_record.num)
            user_score_list.append(user_score)
        recommend_item_id_list = RecommendUtil.recommend(current_user.id, user_list, item_list, user_score_list)
        # 只排除用户最近 10 次听过的歌曲
        recent_listened_songs = ListenRecord.objects.filter(user_id=current_user.id).order_by('-listen_date')[:10]
        limit_id_list = [record.song_id for record in recent_listened_songs]

        # 过滤已听过的歌，剩余推荐为
        new_id_list = []
        for id in recommend_item_id_list:
            if id not in limit_id_list:
                new_id_list.append(id)
        print(new_id_list)

        for recommend_item_id in new_id_list:
            recommend_song.append(Song.objects.all().filter(song_id=recommend_item_id).first())

        # 获取实际相关的项目列表，这里假设是用户最近的听歌记录
        recent_listened_songs = ListenRecord.objects.filter(user_id=current_user.id).order_by('-listen_date')[:10]
        relevant_item_id_list = [record.song_id for record in recent_listened_songs]


    else:
        # 没登陆则推荐新歌
        recommend_song = Song.objects.order_by('-song_release').all()[:3]
    # 热门搜索、热门下载
    search_ranking = search_song[:6]
    down_ranking = Dynamic.objects.select_related('song').order_by('-dynamic_down').all()[:6]
    all_ranking = [search_ranking, down_ranking]
    return render(request, 'index.html', locals())


def chat1(request):
    song_type_stats = Song.objects.values('label__label_name').annotate(total_listen=Count('listenrecord'))
    list = []
    for item in song_type_stats:
        print(item)
        return_item = {'name': item['label__label_name'], 'value': item['total_listen']}
        list.append(return_item)

    print(list)
    return JsonResponse(list, safe=False)


def chat2(request):
    listening_stats = ListenRecord.objects.annotate(hour=ExtractHour('listen_date')) \
        .values('hour').annotate(total_listen=Count('id')).order_by('hour')
    label_list = []
    data_list = []
    for item in listening_stats:
        hour = item['hour']
        total_listen = item['total_listen']
        label_list.append(hour)
        data_list.append(total_listen)

    res = {'labelList': label_list, 'dataList': data_list}

    print(res)
    return JsonResponse(res, safe=False)


def chat3(request):
    top_songs = ListenRecord.objects.values('song_id__song_name').annotate(listen_count=Count('song_id')).order_by(
        '-listen_count')[:10]
    label_list = []
    data_list = []
    for item in top_songs:
        print(item)
        data_list.append(item['listen_count'])
        label_list.append(item['song_id__song_name'])

    res = {'labelList': label_list, 'dataList': data_list}

    print(res)
    return JsonResponse(res, safe=False)


def chat4(request):
    label_list = []
    all_label = Label.objects.all()
    for label in all_label:
        label_list.append(label.label_name)
    top_songs = ListenRecord.objects.annotate(month=ExtractMonth('listen_date')).values('song_id__label_id__label_name',
                                                                                        'listen_date__month').annotate(
        listen_count=Count('id')).order_by('song_id__label_id__label_name', 'month')
    item_list = []
    for label_name in label_list:
        data_list = []
        for top in top_songs:
            if top['song_id__label_id__label_name'] == label_name:
                data_list.append(top['listen_count'])
        item = {
            "name": label_name,
            "type": 'line',
            "stack": 'Total',
            "data": data_list
        }
        item_list.append(item)
    res = {'labelList': label_list, 'dataList': item_list}

    print(res)
    return JsonResponse(res, safe=False)


def random_user(request):
    for i in range(5, 100):
        MyUser.objects.create(password='pbkdf2_sha256$120000$2iB1B7zUHFge$HumF96CiB2ETvP+oa+ZHvHcKuiArGnNwlpaG8KelqzA=',
                              is_superuser=0, username='user' + str(i), is_staff=0, is_active=1,
                              mobile='134170000' + str(i))
    return JsonResponse('random user insert', safe=False)


def random_data(request):
    all_user = MyUser.objects.all()
    all_song = list(Song.objects.all())
    for user in all_user:
        random.shuffle(all_song)
        random_number = random.randint(50, 100)
        for i in range(0, random_number):
            ListenRecord.objects.create(user_id=user.id, song_id=all_song[i].song_id, listen_date=get_random_date())

    return JsonResponse('random data inser', safe=False)

# 在 views.py 中调用 random_data 函数
import random
from django.http import JsonResponse
from .models import ListenRecord, MyUser, Song
from datetime import datetime, time, timedelta

def get_random_date():
    start_date = datetime(2025, 1, 1).date()
    end_date = datetime(2025, 12, 31).date()

    # 定义时间段权重
    time_slots = [
        (time(0, 0), time(6, 0), 5),
        (time(6, 0), time(10, 0), 10),
        (time(10, 0), time(18, 0), 12),
        (time(18, 0), time(22, 0), 15),
        (time(22, 0), time(23, 0), 8),
    ]

    # 随机生成一个日期
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    # 随机生成一个时间段
    random_time_slot = random.choices(time_slots, weights=[weight for _, _, weight in time_slots])[0]
    start_time, end_time, _ = random_time_slot

    # 随机生成一个时间
    if start_time <= end_time:
        if start_time <= time(23, 0) <= end_time:
            random_time = time(random.randint(start_time.hour, 23),
                               random.randint(0, 59),
                               random.randint(0, 59))
        else:
            random_time = time(random.randint(start_time.hour, end_time.hour - 1),
                               random.randint(0, 59),
                               random.randint(0, 59))
    return datetime.combine(random_date, random_time)

def random_data(request):
    all_user = MyUser.objects.all()
    all_song = list(Song.objects.all())
    for user in all_user:
        random.shuffle(all_song)
        # 确保 random_number 不会超过 all_song 列表的长度
        random_number = min(random.randint(50, 100), len(all_song))
        for i in range(0, random_number):
            ListenRecord.objects.create(user_id=user.id, song_id=all_song[i].song_id, listen_date=get_random_date())

    return JsonResponse('random data inserted', safe=False)
# 自定义404和500的错误页面
def page_not_found(request):
    return render(request, 'error404.html', status=404)