# NEV Recommendation Platform

### 项目架构
- 汽车之家爬虫，参考folk源项目
    - 更新 `phantomjs` 使用方法和存放路径
    - 更新汽车之家网页结构解析方法，时间替换为2021-2022
    - 删除充电桩数据爬取
    - 删除国际原油数据爬取
- 数据分析
    - 分析单个品牌销售数据并可视化
    - 销量预测 1：非线性最小二乘 + LM 算法
    - 销量预测 2：XGBoost + LightGBM 集成学习
- 协同过滤推荐
    - ItemCF - `cosine_similarity` 分析
- 网页架构（**待完善**）
    - Flask(Python) + Bootstrap
    - 前端功能：待协商确定...

### Dependency
见 `requirements.txt`
```bash
pip install -r requirements.txt
```

### Run Project
git clone project file
```bash
git clone git@github.com:HuaHenry/Electric_Vehicle_Crawler.git
cd Electric_Vehicle_Crawler
```
Start local flask server.
```bash
python app.py
```