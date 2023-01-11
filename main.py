from flask import Flask, jsonify, request
import pandas as pd
from demographic_filtering import output
from content_filtering import get_recommendations

articles_data = pd.read_csv('articles.csv')
all_articles = articles_data[['url' , 'title' , 'text' , 'lang' , 'total_events']]
liked_articles = []
not_liked_articles = []

app = Flask(__name__)

def assign_val():
    m_data = {
        "url": all_articles.iloc[0,0],
        "title": all_articles.iloc[0,1],
        "text": all_articles.iloc[0,2] or "N/A",
        "lang": all_articles.iloc[0,3],
        "total_events": all_articles.iloc[0,4]/2
    }
    return m_data

@app.route("/get-article")
def get_article():

    article_info = assign_val()
    return jsonify({
        "data": article_info,
        "status": "success"
    })

@app.route("/liked-article")
def liked_article():
    global all_articles
    article_info = assign_val()
    liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

@app.route("/unliked-article")
def unliked_article():
    global all_articles
    article_info = assign_val()
    not_liked_articles.append(article_info)
    all_articles.drop([0], inplace=True)
    all_articles = all_articles.reset_index(drop=True)
    return jsonify({
        "status": "success"
    })

# API to return most popular articles.
@app.route("/popular-articles")
def popular_articles():
    popular_arts = []

    for index,value in all_articles.iterrows():
        popular_dict = {
            "url": value["url"],
            "title": value["title"] ,
            "text": value["text"] ,
            "lang": value["lang"] ,
            "total_events": value["total_events"]
        }
        popular_arts.append(popular_dict)

    return jsonify({
        "data": popular_arts,
        "status":"success"
    })

# API to return top 10 similar articles using content based filtering method.
@app.route("/recommended-articles")
def recommended_articles():
    global liked_articles
    columnNames = ['url' , 'title' , 'text' , 'lang' , 'total_events']
    reco_articlesDF = pd.DataFrame(columns=columnNames)
    for i in liked_articles:
        get_reco = get_recommendations(i["title"])
        reco_articlesDF = reco_articlesDF.append(get_reco)
    reco_articlesDF.drop_duplicates(subset=["title"],inplace=True)
    recommended_arts = []

    for index,value in all_articles.iterrows():
        reco_dict = {
            "url": value["url"],
            "title": value["title"] ,
            "text": value["text"] ,
            "lang": value["lang"] ,
            "total_events": value["total_events"]
        }
        recommended_arts.append(reco_dict)
    
    return jsonify({
        "data": recommended_arts,
        "status":"success"
    })

if __name__ == "__main__":
    app.run()