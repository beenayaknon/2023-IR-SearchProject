from flask import Flask, request, render_template
from markupsafe import escape
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup 
import math
import urllib3

ELASTIC_PASSWORD = "User1234"

es = Elasticsearch("https://localhost:9200", http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)

index_name = "games"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword').lower()
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1

    body = {
        'size': page_size,
        'from': page_size * (page_no - 1),
        'query': {
            'function_score': {
                'query': {
                    'bool': {
                        'should': [
                            {
                                'match': {
                                    'name_original': {
                                        'query': keyword,
                                        'boost': 3  # Boost the score for matches in 'name_original'
                                    }
                                }
                            },
                            {
                                'match': {
                                    'description': keyword
                                }
                            },
                            {
                                'match': {
                                    'tags': keyword
                                }
                            }
                        ]
                    }
                },
                'boost_mode': 'replace'
            }
        }
    }

    res = es.search(index='games', body=body)
    hits = [{'id': doc['_id'],
             'name': doc['_source']['name_original'],
             'description': BeautifulSoup(doc['_source']['description'], "html.parser").get_text(), 
             'genres': ', '.join(doc['_source']['genres']),
             'platforms': ', '.join(doc['_source']['platform']),
             'developers': ', '.join(doc['_source']['developers']),
             'publishers': ', '.join(doc['_source']['publishers']),
             'tags': ', '.join(doc['_source']['tags']),
             'img': doc['_source']['background_image']}
            for doc in res['hits']['hits']]
    page_total = math.ceil(res['hits']['total']['value'] / page_size)

    if not hits:
        return render_template('no_results.html', keyword=keyword)

    return render_template('search.html', keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)

@app.route('/details/<string:game_id>')
def details(game_id):
    doc = es.get(index='games', id=game_id)['_source']
    game = {
        'name': doc['name_original'],
        'description': BeautifulSoup(doc['description'], "html.parser").get_text(),
        'genres': ', '.join(doc['genres']),
        'platforms': ', '.join(doc['platform']),
        'developers': ', '.join(doc['developers']),
        'publishers': ', '.join(doc['publishers']),
        'tags': ', '.join(doc['tags']),
        'img': doc['background_image']
    }
    return render_template('details.html', game=game)

@app.route('/no_results')
def no_results():
    keyword = request.args.get('keyword')
    return render_template('no_results.html', keyword=keyword)

if __name__ == '__main__':
    app.run()
