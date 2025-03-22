# Flask后端主要架构
from flask import Flask

app=Flask(__name__)

@app.route("/")
def home():
    return "网页前端尚未搭建"

if __name__=='__main__':
    app.run()