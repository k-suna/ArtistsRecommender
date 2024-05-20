import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

client_id = '44a92c7fdc2b4c46ba0592c5bd1fc4fb'
client_secret = '22fd6a34d57842348acfa41f10d6f6ae'

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

name = None
popularity = None
uri = None
G = nx.Graph()
popularity_list = []

#アーティスト名のURIを取得
def get_artist_uri(name):
    artist = sp.search(q='artist:' + name, type='artist')['artists']['items'][0]
    uri = artist['uri']
    return uri

#アーティストのURIを入力し，そのアーティストと関連があるアーティスト情報を出力
def get_related_artist_info(uri):
    df = pd.DataFrame()
    for artist in sp.artist_related_artists(uri)['artists']:
        tmp = pd.Series([], name=artist['name'])
        for key in ['popularity', 'uri']:
            tmp[key] = artist[key]
        df = pd.concat([df, pd.DataFrame(tmp).T])           
    return df

#ノードの作成（ノード：アーティスト）
def add_nodes(df, name):        
    if name not in G.nodes:
        G.add_node(name)
        popularity_list.append(popularity)       
    for name in df.index.tolist():
        if name not in G.nodes:
            G.add_node(name)
            popularity_list.append(df.loc[name, 'popularity'])

#エッジの作成（エッジ：関連↓）
#Get Spotify catalog information about artists similar to a given artist. 
#Similarity is based on analysis of the Spotify community's listening history.
def add_edges(target_name, df):
    for name in df.index.tolist():
        if (target_name, name) not in G.edges:
            G.add_edge(target_name, name)

#ノードの色の設定
def node_color(popularity):
        color_list = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
        #「赤」→「橙」→「黄」→「緑」→「青」→「紫」
        
        if popularity is not None and popularity >= 70:
            return color_list[0]
        elif popularity is not None and popularity >= 60:
            return color_list[1]
        elif popularity is not None and popularity >=50:
            return color_list[2]
        elif popularity is not None and popularity >= 40:
            return color_list[3]
        elif popularity is not None and popularity >= 30:
            return color_list[4]
        else:
            return color_list[5]

#ネットワーク作成
def draw_artist_network(artist_name):

    print("*---------------------ネットワーク作成開始------------------------------*\n")

    uri = get_artist_uri(artist_name)
    df = get_related_artist_info(uri)
    add_nodes(df, artist_name)
    add_edges(artist_name, df)  
    for name in df.index.tolist():
        tmp_df = get_related_artist_info(df.loc[name, 'uri'])            
        add_nodes(tmp_df, name)
        add_edges(name, tmp_df)

    pos = nx.spring_layout(G, seed=1, k=0.08) #レイアウトの取得

    #ネットワーク図の作成
    plt.figure(figsize=[20, 20])
    nx.draw_networkx_labels(G, pos, font_color='k', font_family='IPAexGothic')
    nx.draw_networkx_nodes(G, pos, alpha=0.8, node_shape='o', linewidths=1, 
                           #popularityの値によってノードの色を変化
                           node_color=list(map(node_color, popularity_list)))
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    plt.axis('off')
    plt.show()

    #次数中心性をもとにしたネットワーク図の作成
    dc = nx.degree_centrality(G)
    plt.figure(figsize=[20, 20])
    nx.draw_networkx_labels(G, pos, font_color='k', font_family='IPAexGothic')
    nx.draw_networkx_nodes(G, pos, alpha=0.8, node_shape='o', linewidths=1, 
                           #次数中心性の値が高いアーティストほどノードの大きさが大きくなる
                           node_size=[6000*v for v in dc.values()], 
                           #popularityの値によってノードの色を変化
                           node_color=list(map(node_color, popularity_list)))
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    plt.axis('off')
    plt.show()

    #媒介中心性をもとにしたネットワーク図の作成
    bc = nx.betweenness_centrality(G)
    plt.figure(figsize=[20, 20])
    nx.draw_networkx_labels(G, pos, font_color='k', font_family='IPAexGothic')
    nx.draw_networkx_nodes(G, pos, alpha=0.8, node_shape='o', linewidths=1, 
                           #媒介中心性の値が高いアーティストほどノードの大きさが大きくなる
                           node_size=[6000*v for v in bc.values()], 
                           #popularityの値によってノードの色を変化
                           node_color=list(map(node_color, popularity_list)))
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    plt.axis('off')
    plt.show()

    #近接中心性をもとにしたネットワーク図の作成
    cc = nx.betweenness_centrality(G)
    plt.figure(figsize=[20, 20])
    nx.draw_networkx_labels(G, pos, font_color='k', font_family='IPAexGothic')
    nx.draw_networkx_nodes(G, pos, alpha=0.8, node_shape='o', linewidths=1, 
                           #近接中心性の値が高いアーティストほどノードの大きさが大きくなる
                           node_size=[6000*v for v in cc.values()], 
                           #popularityの値によってノードの色を変化
                           node_color=list(map(node_color, popularity_list)))
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    plt.axis('off')
    plt.show()

    #PageRankをもとにしたネットワーク図の作成
    pr = nx.pagerank(G)
    plt.figure(figsize=[20, 20])
    nx.draw_networkx_labels(G, pos, font_color='k', font_family='IPAexGothic')
    nx.draw_networkx_nodes(G, pos, alpha=0.8, node_shape='o', linewidths=1, 
                           #PageRankの値が高いアーティストほどノードの大きさが大きくなる
                           node_size=[100000*v for v in pr.values()], 
                           #popularityの値によってノードの色を変化
                           node_color=list(map(node_color, popularity_list)))
    nx.draw_networkx_edges(G, pos, alpha=0.3)
    plt.axis('off')
    plt.show()

    print("*---------------------ネットワーク作成終了------------------------------*\n")

    print("*------------------------解析開始------------------------------*\n")

    #次数中心性解析
    dc_sorted_list = sorted(dc.items(), key=lambda x:x[1], reverse=True)    #次数中心性の値を降順に並び替えて表示
    print("次数中心性の値\n")
    for count, dc in enumerate(dc_sorted_list):
        if count==0:
            print(f"{count+1}st.{dc}")
        elif count==1:
            print(f"{count+1}nd.{dc}")
        elif count==2:
            print(f"{count+1}rd.{dc}")
        else:
            print(f"{count+1}th.{dc}")
    print("*------------------------------------------------------*\n")

    #媒介中心性解析
    bc_sorted_list = sorted(bc.items(), key=lambda x:x[1], reverse=True)    #媒介中心性の値を降順に並び替えて表示
    print("媒介中心性の値\n")
    for count, bc in enumerate(bc_sorted_list):
        if count==0:
            print(f"{count+1}st.{bc}")
        elif count==1:
            print(f"{count+1}nd.{bc}")
        elif count==2:
            print(f"{count+1}rd.{bc}")
        else:
            print(f"{count+1}th.{bc}")
    print("*------------------------------------------------------*\n")

    #近接中心性解析
    cc_sorted_list = sorted(cc.items(), key=lambda x:x[1], reverse=True)    #近接中心性の値を降順に並び替えて表示
    print("近接中心性の値\n")
    for count, cc in enumerate(cc_sorted_list):
        if count==0:
            print(f"{count+1}st.{cc}")
        elif count==1:
            print(f"{count+1}nd.{cc}")
        elif count==2:
            print(f"{count+1}rd.{cc}")
        else:
            print(f"{count+1}th.{cc}")
    print("*------------------------------------------------------*\n")

    #PageRank解析
    pr_sorted_list = sorted(pr.items(), key=lambda x:x[1], reverse=True)    #PageRankの値を降順に並び替えて表示
    print("PageRankの値\n")
    for count, pr in enumerate(pr_sorted_list):
        if count==0:
            print(f"{count+1}st.{pr}")
        elif count==1:
            print(f"{count+1}nd.{pr}")
        elif count==2:
            print(f"{count+1}rd.{pr}")
        else:
            print(f"{count+1}th.{pr}")
    print("*------------------------------------------------------*\n")

    #平均クラスタリング係数の計算
    ave_cc = nx.average_clustering(G)
    print("平均クラスタリング係数の値\n")
    print(ave_cc)
    print("*------------------------------------------------------*\n")

    #起点のアーティストノードのクラスタリング係数の計算
    cc_dict = nx.clustering(G)
    print(artist_name + "のノードのクラスタリング係数の値\n")
    print(cc_dict[artist_name])
    print("*------------------------解析終了------------------------------*\n")

#以下のアーティストを起点にネットワーク図を作成
artist_name = input("好きなアーティストを英語表記（ex.ARASHI, Gen␣Hoshino）で入力してください：")
draw_artist_network(artist_name)