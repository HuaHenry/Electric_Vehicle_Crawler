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

def encode_autopilot(level):
    mapping = {'L2': 1, 'L2+': 2, 'L3': 3, 'L4': 4}
    return mapping.get(level, 0)

def build_car_features():
    """
    构建【每个车型】的综合特征矩阵：
    - 平均销量时间序列
    - 加入结构化特征：尺寸、电池类型、续航、智能驾驶等级
    """
    cars = Car.query.all()
    rows = []
    for car in cars:
        if not car.month or car.sales is None:
            continue
        rows.append({
            'name': car.name,
            'month': car.month,
            'sales': car.sales,
            'size': car.size,
            'battery': car.battery_type,
            'range_km': car.range_km,
            'autopilot_level': encode_autopilot(car.autopilot_level)
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return None

    # ------- 1. 销量行为特征 -------
    sales_pivot = df.pivot_table(index='name', columns='month', values='sales', aggfunc='sum', fill_value=0)

    # ------- 2. 模型结构化特征 -------
    # 保证每个车型只保留一个结构化特征（取第一个）
    struct_df = df.groupby('name').first()[['size', 'battery', 'range_km', 'autopilot_level']].copy()

    # One-hot 编码：尺寸 + 电池类型
    struct_encoded = pd.get_dummies(struct_df[['size', 'battery']], prefix=['size', 'battery'])

    # 合并连续值（续航、自动驾驶等级）
    struct_encoded['range_km'] = struct_df['range_km'].fillna(0)
    struct_encoded['autopilot_level'] = struct_df['autopilot_level'].fillna(0)

    # 合并结构化和销量特征
    full_feature_df = pd.concat([struct_encoded, sales_pivot], axis=1).fillna(0)

    return full_feature_df

# def recommend_for_user(preferred_models, top_n_per_model=30, n_components=20):
#     """
#     工业版协同过滤推荐系统
#     - 使用销量矩阵
#     - SVD降维到隐空间
#     - 隐空间计算余弦相似度
#     """
#     pivot = build_item_matrix()
#     if pivot is None or pivot.empty:
#         return []

#     # 1. 隐式特征提取
#     svd = TruncatedSVD(n_components=min(n_components, pivot.shape[1]-1))
#     item_features = svd.fit_transform(pivot)

#     # 2. 车型列表
#     model_names = pivot.index.tolist()

#     # 3. 构建车型隐特征 DataFrame
#     item_feature_df = pd.DataFrame(item_features, index=model_names)

#     # 4. 计算隐空间余弦相似度
#     similarity_matrix = cosine_similarity(item_feature_df)
#     similarity_df = pd.DataFrame(similarity_matrix, index=model_names, columns=model_names)

#     # 5. 开始推荐
#     recommendations = []
#     for model in preferred_models:
#         if model in similarity_df.index:
#             similar_models = similarity_df[model].sort_values(ascending=False)[1:top_n_per_model+1]
#             recommendations.extend(similar_models.index.tolist())

#     # 去重，排除已喜欢的车型
#     recommendations = list(dict.fromkeys(recommendations))
#     recommendations = [model for model in recommendations if model not in preferred_models]

#     return recommendations[:100]  # 最多返回10个

def recommend_for_user(preferred_models, top_n_per_model=30, n_components=50):
    """
    推荐系统升级版：
    - 综合结构化特征 + 销量序列
    - 使用 SVD + 余弦相似度做车型推荐
    """
    feature_df = build_car_features()
    if feature_df is None or feature_df.empty:
        return []

    model_names = feature_df.index.tolist()

    # SVD 降维
    svd = TruncatedSVD(n_components=min(n_components, feature_df.shape[1]-1))
    latent_features = svd.fit_transform(feature_df)
    latent_df = pd.DataFrame(latent_features, index=model_names)

    # 相似度矩阵
    similarity_matrix = cosine_similarity(latent_df)
    similarity_df = pd.DataFrame(similarity_matrix, index=model_names, columns=model_names)

    # 推荐逻辑
    recommendations = []
    for model in preferred_models:
        if model in similarity_df.index:
            similar_models = similarity_df[model].sort_values(ascending=False)[1:top_n_per_model+1]
            recommendations.extend(similar_models.index.tolist())

    # 去重 + 排除已喜欢
    recommendations = list(dict.fromkeys(recommendations))
    recommendations = [model for model in recommendations if model not in preferred_models]

    return recommendations[:100]