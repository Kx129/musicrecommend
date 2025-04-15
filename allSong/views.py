from django.shortcuts import render

from django.shortcuts import render
from index.models import *
def allSongView(request):
    label_id = request.GET.get("label_id")
    print(label_id)
    if label_id is not None:
        label = Label.objects.all().filter(label_id=label_id).first()
        title = label.label_name
        song_list = Song.objects.all().filter(label_id=label_id)
    else:
        title = "全部歌曲"
        song_list = Song.objects.all()
    return render(request, 'allSong.html', locals())


# 通用视图
from django.views.generic import ListView
class RankingList(ListView):
    # context_object_name设置Html模版的某一个变量名称
    context_object_name = 'song_info'
    # 设定模版文件
    template_name = 'ranking.html'
    # 查询变量song_info的数据
    def get_queryset(self):
        # 获取请求参数
        song_type = self.request.GET.get('type', '')
        if song_type:
            song_info = Dynamic.objects.select_related('song').filter(song__song_type=song_type).order_by('-dynamic_plays').all()[:10]
        else:
            song_info = Dynamic.objects.select_related('song').order_by('-dynamic_plays').all()[:10]
        return song_info

    # 添加其他变量
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 搜索歌曲
        context['search_song'] = Dynamic.objects.select_related('song').order_by('-dynamic_search').all()[:4]
        # 所有歌曲分类
        context['All_list'] = Song.objects.values('song_type').distinct()
        return context


from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import ExtractHour, ExtractMonth
from index.models import Dynamic, Song, ListenRecord


# 接口1：不同歌曲类型的听歌次数比例（饼图）
def chat1(request):
    data = Dynamic.objects.values('song__song_type').annotate(
        total_plays=Count('dynamic_plays')
    )
    formatted_data = [
        {"name": item["song__song_type"], "value": item["total_plays"]}
        for item in data
    ]
    return JsonResponse(formatted_data, safe=False)


# 接口2：不同时段听歌次数（折线图）
def chat2(request):
    hourly_data = ListenRecord.objects.annotate(
        hour=ExtractHour('listen_date')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')

    hours = list(range(24))
    counts = [0] * 24
    for item in hourly_data:
        counts[item['hour']] = item['count']
    return JsonResponse({"labelList": hours, "dataList": counts})


# 接口3：热门播放歌曲（柱状图）
def chat3(request):
    top_songs = Dynamic.objects.select_related('song').order_by('-dynamic_plays')[:10]
    labels = [song.song.song_name for song in top_songs]
    plays = [song.dynamic_plays for song in top_songs]
    return JsonResponse({"labelList": labels, "dataList": plays})


# 接口4：1-12月播放量变化（折线图）
def chat4(request):
    monthly_data = ListenRecord.objects.annotate(
        month=ExtractMonth('listen_date')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    months = list(range(1, 13))
    counts = [0] * 12
    for item in monthly_data:
        if 1 <= item['month'] <= 12:
            counts[item['month'] - 1] = item['count']
    return JsonResponse({"labelList": months, "dataList": counts})