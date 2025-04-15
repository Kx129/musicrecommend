import math
import random
import numpy as np
from sklearn.decomposition import NMF
from .models import ListenRecord
import json
import datetime
from .user_score import UserScore

def adjusted_cosine_similarity(score_matrix, user1, user2):
    """计算调整余弦相似度"""
    item_count = len(score_matrix[0])
    numerator = 0
    denominator1 = 0
    denominator2 = 0
    user1_mean = np.mean([score for score in score_matrix[user1] if score != 0])
    user2_mean = np.mean([score for score in score_matrix[user2] if score != 0])
    for i in range(item_count):
        if score_matrix[user1][i] != 0 and score_matrix[user2][i] != 0:
            numerator += (score_matrix[user1][i] - user1_mean) * (score_matrix[user2][i] - user2_mean)
            denominator1 += (score_matrix[user1][i] - user1_mean) ** 2
            denominator2 += (score_matrix[user2][i] - user2_mean) ** 2
    if denominator1 == 0 or denominator2 == 0:
        return 0
    return numerator / (math.sqrt(denominator1) * math.sqrt(denominator2))

def fill_matrix_nmf(score_matrix, n_components=10, max_iter=200):
    """
    使用非负矩阵分解（NMF）填充评分矩阵
    :param score_matrix: 评分矩阵
    :param n_components: 潜在特征的数量
    :param max_iter: 最大迭代次数
    :return: 填充后的评分矩阵
    """
    # 创建 NMF 模型
    model = NMF(n_components=n_components, init='random', random_state=0, max_iter=max_iter)
    # 分解矩阵
    W = model.fit_transform(score_matrix)
    H = model.components_
    # 重构矩阵
    filled_matrix = np.dot(W, H)
    return filled_matrix

def calculate_metrics(ground_truth, recommended):
    true_positives = len(set(recommended).intersection(set(ground_truth)))
    precision = true_positives / len(recommended) if len(recommended) > 0 else 0
    recall = true_positives / len(ground_truth) if len(ground_truth) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1

class RecommendUtil:
    @staticmethod
    def recommend(current_user_id, user_list, item_list, data):
        # 初始化评分矩阵
        score_matrix = [[0 for i in range(len(item_list))] for j in range(len(user_list))]

        # 填充评分矩阵
        for data_item in data:
            for row_idx, val1 in enumerate(score_matrix):
                for col_idx, val2 in enumerate(val1):
                    if data_item.user_id == user_list[row_idx] and data_item.item_id == item_list[col_idx]:
                        score_matrix[row_idx][col_idx] = data_item.score
                        break

        score_matrix = np.array(score_matrix)

        # 检查并处理负值
        score_matrix = np.maximum(score_matrix, 0)

        # 基于 NMF 填充矩阵
        score_matrix = fill_matrix_nmf(score_matrix)

        # 打印评分矩阵
        print("评分矩阵：")
        for i in score_matrix:
            print(i)

        # 初始化相似度矩阵
        similar_matrix = [[0 for i in range(len(user_list))] for j in range(len(user_list))]

        # 计算相似度矩阵，应用调整余弦相似度
        for i in range(len(user_list)):
            for j in range(len(user_list)):
                if i == j:
                    similar_matrix[i][j] = 1
                    continue
                elif i < j:
                    continue
                else:
                    similar = adjusted_cosine_similarity(score_matrix, i, j)
                    similar_matrix[i][j] = similar
                    similar_matrix[j][i] = similar

        print("相似度矩阵：")
        for i in similar_matrix:
            print(i)

        # 矩阵倒置，倒置后的矩阵方便计算每个样本的平均值，比如一个商品，那要计算用户对这个商品的平均评分
        new_score_matrix = [[score_matrix[j][i] for j in range(len(score_matrix))] for i in
                            range(len(score_matrix[0]))]
        # 打印倒置后的评分矩阵
        print("转置后的评分矩阵：")
        for item in new_score_matrix:
            print(item)

        # 相似度矩阵*评分矩阵=推荐分数矩阵
        recommend_score_matrix = [[0 for i in range(len(item_list))] for j in range(len(user_list))]
        for i in range(len(user_list)):
            for j in range(len(item_list)):
                list1 = similar_matrix[i]
                list2 = new_score_matrix[j]
                recommend_score = 0
                for k in range(len(list1)):
                    recommend_score += list1[k] * list2[k]
                recommend_score_matrix[i][j] = recommend_score

        # 推荐矩阵
        print("推荐矩阵:")
        for item in recommend_score_matrix:
            print(item)

        # index 代表计算后的矩阵哪一行是当前用户的目标评分，因为矩阵的每一行数据代表用户对每首歌曲的评分，取出那一行数据再进行排序即可
        index = 0
        for user_id in user_list:
            if user_id == current_user_id:
                break
            index = index + 1

        result_score_arr = recommend_score_matrix[index]
        print("当前用户对歌曲的推荐评分为：")
        # 转换为普通浮点数列表并输出
        result_score_arr_float = [float(score) for score in result_score_arr]
        print(result_score_arr_float)

        item_score_list = []
        for i, song_id in enumerate(item_list):
            item_score = ItemScore(song_id, result_score_arr[i])
            item_score_list.append(item_score)

        # 检查 item_score_list 是否正确生成
        print("item_score_list:", item_score_list)

        new_item_score_list = sorted(item_score_list, key=lambda x: x.score, reverse=True)

        # 检查 new_item_score_list 是否正确排序
        print("new_item_score_list:", new_item_score_list)

        # 调整推荐列表长度
        recommend_item_id_list = [item_score.item_id for item_score in new_item_score_list[:20]]

        # 检查 recommend_item_id_list 是否为空
        if not recommend_item_id_list:
            print("推荐列表为空，可能存在问题，请检查。")

        # 从 simulated_listening_data.json 加载数据
        file_path = 'index/simulated_listening_data.json'
        with open(file_path, 'r') as f:
            simulated_data = json.load(f)

        # 将字符串转换为 datetime 对象
        listening_data = [(user_id, song_id, datetime.datetime.fromisoformat(listen_date), num) for user_id, song_id, listen_date, num in simulated_data]

        # 为当前用户生成 ground_truth
        ground_truth = [song_id for user_id, song_id, _, _ in listening_data if user_id == current_user_id]

        # 计算评估指标
        precision, recall, f1 = calculate_metrics(ground_truth, recommend_item_id_list)

        print(f"召回率: {recall}")
        print(f"精确度: {precision}")
        print(f"F1 指标: {f1}")

        return recommend_item_id_list

class ItemScore:
    item_id = 0
    score = 0

    def __init__(self, item_id, score):
        self.item_id = item_id
        self.score = score

    def __repr__(self):
        return f"ItemScore(item_id={self.item_id}, score={self.score})"