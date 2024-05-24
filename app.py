from flask import Flask, render_template, request, redirect, url_for, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import networkx as nx
import pandas as pd
import os
from dotenv import load_dotenv

app = Flask(__name__)

# .envファイルから環境変数を読み込む
load_dotenv()

#SpotifyAPIのアクセストークン情報
# 環境変数からSpotify APIのクライアントIDとシークレットを取得
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# アーティスト名のURIを取得
def get_artist_uri(name):
    results = sp.search(q='artist:' + name, type='artist')
    if results['artists']['items']:
        artist = results['artists']['items'][0]
        uri = artist['uri']
        return uri
    else:
        return None

# アーティストのURIを入力し，そのアーティストと関連があるアーティスト情報を出力
def get_related_artist_info(uri):
    df = pd.DataFrame()
    for artist in sp.artist_related_artists(uri)['artists']:
        tmp = pd.Series([], name=artist['name'])
        for key in ['popularity', 'uri']:
            tmp[key] = artist[key]
        # アーティストのトップトラックを取得
        top_tracks = sp.artist_top_tracks(artist['uri'])['tracks']
        top_track_names = [track['name'] for track in top_tracks]
        # トップトラックをデータフレームに追加
        tmp['top_tracks'] = ', '.join(top_track_names)
        df = pd.concat([df, pd.DataFrame(tmp).T])           
    return df

# 以下，ページランクをもとに上位10個のアーティストを取得する関数
#最初にアーティストネットワークを作成する
#次に，そのネットワークに対してpagerankを計算する
#pagerankの上位10個を出力する．
def get_top_artists(artist_name):
    G = nx.Graph()  # ページランク計算用の新しいグラフオブジェクトを生成
    uri = get_artist_uri(artist_name)
    if not uri:
        return None, None
    df = get_related_artist_info(uri)
    G.add_node(artist_name)
    for name in df.index.tolist():
        G.add_node(name)
        G.add_edge(artist_name, name)
    pr = nx.pagerank(G)
    sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True) #sorted_prリストは(アーティスト名, PageRank値)のタプル構造になっている．
    top_artists_list = [artist[0] for artist in sorted_pr[:11]] #artist[0]はsorted_prリストの「アーティスト名」を参照している．
    if artist_name in top_artists_list:  #上位10人の中で入力されたアーティスト名と同じ名前のものが入っていた場合は，除去する
        top_artists_list.remove(artist_name)
    else:   #top_artistリストの1番目は入力されたアーティスト名と同じなので，else文に来たときはpopして除去する．
        top_artists_list.pop()
    
    # アーティストごとに有名曲を5曲取得
    top_tracks_dict = {}
    for artist in top_artists_list:
        uri = get_artist_uri(artist)
        if uri:
            top_tracks = sp.artist_top_tracks(uri)['tracks'] #人気順になってる
            top_tracks_info = []
            for track in top_tracks[:6]:
                track_info = {
                    'name': track['name'],  # 曲名を取得
                    'release_date': track['album']['release_date'].split('-')[0],  # リリース年を取得
                    'image_url': track['album']['images'][0]['url']  # アルバムの画像URLを取得
                }
                top_tracks_info.append(track_info)
            # トップトラック情報をアーティスト名をキーにして辞書に追加
            top_tracks_dict[artist] = top_tracks_info
    
    return top_artists_list, top_tracks_dict

#初期画面
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#リザルト画面
@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    artist_name = data.get('artist_name')
    top_artists_list, top_tracks_dict = get_top_artists(artist_name)
    if not top_artists_list:
        return jsonify({'error': 'Artist not found'}), 404
    return jsonify({
        'top_artists_list': top_artists_list,
        'top_tracks_dict': top_tracks_dict
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
