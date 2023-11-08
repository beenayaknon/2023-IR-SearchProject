from flask import Flask, request
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup 
import math

ELASTIC_PASSWORD = "User1234"

es = Elasticsearch("https://localhost:9200",http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword')
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    body = {
        'size': page_size,
        'from': page_size * (page_no-1),
        'query': {
            'multi_match': {
                'query': keyword,
                'fields': ['name_original', 'description']
            }
        }
    }
    
    res = es.search(index='games', body=body)
    hits = [{'name': doc['_source']['name_original'], 
             'description': BeautifulSoup(doc['_source']['description'], "html.parser").get_text(), 
             'genres': ', '.join(doc['_source']['genres']),
             'platforms': ', '.join(doc['_source']['platform']),
             'developers': ', '.join(doc['_source']['developers']),
             'publishers': ', '.join(doc['_source']['publishers']),
             'tags': ', '.join(doc['_source']['tags']),
             'img': ', '.join(doc['_source']['background_image'])} 
            for doc in res['hits']['hits']]
    page_total = math.ceil(res['hits']['total']['value']/page_size)
    return render_template('search.html',keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)
