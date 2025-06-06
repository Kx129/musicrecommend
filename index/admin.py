from django.contrib import admin
from .models import Label,Song,Dynamic,Comment
# 修改title和header
admin.site.site_title = '♥♥音乐推荐系统后台'
admin.site.site_header = '♥♥协同过滤音乐推荐系统'

class LabelAdmin(admin.ModelAdmin):
    # 设置模型字段，用于Admin后台数据的表头设置
    list_display = ['label_id', 'label_name']
    # 设置可搜索的字段并在Admin后台数据生成搜索框，如有外键应使用双下划线连接两个模型的字段
    search_fields = ['label_name']
    # 设置排序方式
    ordering = ['label_id']


class SongAdmin(admin.ModelAdmin):
    # 设置模型字段，用于Admin后台数据的表头设置
    list_display = ['song_id','song_name','song_singer','song_album','song_languages','song_release']
    # 设置可搜索的字段并在Admin后台数据生成搜索框，如有外键应使用双下划线连接两个模型的字段
    search_fields = ['song_name','song_singer','song_album','song_languages']
    # 设置过滤器，在后台数据的右侧生成导航栏，如有外键应使用双下划线连接两个模型的字段
    list_filter = ['song_singer','song_album','song_languages']
    # 设置排序方式
    ordering = ['song_id']

class DynamicAdmin(admin.ModelAdmin):
    # 设置模型字段，用于Admin后台数据的表头设置
    list_display = ['dynamic_id','song','dynamic_plays','dynamic_search','dynamic_down']
    # 设置可搜索的字段并在Admin后台数据生成搜索框，如有外键应使用双下划线连接两个模型的字段
    search_fields = ['song']
    # 设置过滤器，在后台数据的右侧生成导航栏，如有外键应使用双下划线连接两个模型的字段
    list_filter = ['dynamic_plays','dynamic_search','dynamic_down']
    # 设置排序方式
    ordering = ['dynamic_id']

class CommentAdmin(admin.ModelAdmin):
    # 设置模型字段，用于Admin后台数据的表头设置
    list_display = ['comment_id','comment_text','comment_user','song','comment_date']
    # 设置可搜索的字段并在Admin后台数据生成搜索框，如有外键应使用双下划线连接两个模型的字段
    search_fields = ['comment_user','song','comment_date']
    # 设置过滤器，在后台数据的右侧生成导航栏，如有外键应使用双下划线连接两个模型的字段
    list_filter = ['song','comment_date']
    # 设置排序方式
    ordering = ['comment_id']

admin.site.register(Label, LabelAdmin)
admin.site.register(Song,SongAdmin)
admin.site.register(Dynamic,DynamicAdmin)
admin.site.register(Comment,CommentAdmin)