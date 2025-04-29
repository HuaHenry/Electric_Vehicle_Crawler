# -*-coding:utf-8 -*-
'''
@File    :   recommend.py
@Modify  :   2025/04/21 17:01:03
@Version :   1.0
@Desc    :   工业级协同过滤推荐算法

- 使用矩阵分解（SVD，奇异值分解）
- 直接对车型×月份销量矩阵做低秩近似，提取隐因子
- 用隐因子做相似度计算，推荐相似车型
- 支持大数据量，不怕稀疏矩阵
'''


# recommend.py
from models import Car
import pandas as pd
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

def build_item_matrix():
    """
    构建车型-月份销量矩阵，直接从数据库Car表。
    """
    cars = Car.query.all()

    data = []
    for car in cars:
        if car.month and car.sales is not None:
            data.append({
                '车型': car.name,
                '年月': car.month,
                '销量': car.sales
            })
    
    if not data:
        return None

    df = pd.DataFrame(data)

    pivot = df.pivot_table(index='车型', columns='年月', values='销量', fill_value=0)

    return pivot

def recommend_for_user(preferred_models, top_n_per_model=30, n_components=20):
    """
    工业版协同过滤推荐系统
    - 使用销量矩阵
    - SVD降维到隐空间
    - 隐空间计算余弦相似度
    """
    pivot = build_item_matrix()
    if pivot is None or pivot.empty:
        return []

    # 1. 隐式特征提取
    svd = TruncatedSVD(n_components=min(n_components, pivot.shape[1]-1))
    item_features = svd.fit_transform(pivot)

    # 2. 车型列表
    model_names = pivot.index.tolist()

    # 3. 构建车型隐特征 DataFrame
    item_feature_df = pd.DataFrame(item_features, index=model_names)

    # 4. 计算隐空间余弦相似度
    similarity_matrix = cosine_similarity(item_feature_df)
    similarity_df = pd.DataFrame(similarity_matrix, index=model_names, columns=model_names)

    # 5. 开始推荐
    recommendations = []
    for model in preferred_models:
        if model in similarity_df.index:
            similar_models = similarity_df[model].sort_values(ascending=False)[1:top_n_per_model+1]
            recommendations.extend(similar_models.index.tolist())

    # 去重，排除已喜欢的车型
    recommendations = list(dict.fromkeys(recommendations))
    recommendations = [model for model in recommendations if model not in preferred_models]

    return recommendations[:100]  # 最多返回10个