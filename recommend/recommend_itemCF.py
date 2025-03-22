import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 读取CSV文件（确保编码和路径正确）
df = pd.read_csv("../crawler/2101_2212新能源汽车总体销量数据.csv", header=None, skiprows=1)

# 重命名列
df.columns = ['idx', '序号', '车型', '销量', '车企', '最低售价', '最高售价', '网址', '年月']
df = df.drop(columns=['idx', '序号', '网址'])  # 删除无用列

# 构建车型-月份销量矩阵
pivot = df.pivot_table(index='车型', columns='年月', values='销量', fill_value=0)

# 计算车型之间的相似度（余弦相似度）
similarity = cosine_similarity(pivot)
similarity_df = pd.DataFrame(similarity, index=pivot.index, columns=pivot.index)

# 推荐函数：给定一个车型名，推荐top-N相似车型
def recommend_similar_models(model_name, top_n=5):
    if model_name not in similarity_df.index:
        print(f"未找到车型：{model_name}")
        return []

    similar_models = similarity_df[model_name].sort_values(ascending=False)[1:top_n+1]
    return similar_models

# 示例推荐：与“宏光MINIEV”相似的车型
# print("与宏光MINIEV相似的推荐车型：")
# print(recommend_similar_models("宏光MINIEV", top_n=5))

# 示例推荐：与“蔚来EC6”相似的车型，存储到csv文件中
recommendations = recommend_similar_models("蔚来EC6", top_n=5)
recommendations.to_csv("recommendations_蔚来EC6.csv", header=False)
