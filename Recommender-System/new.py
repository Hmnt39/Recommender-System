# -*- coding: utf-8 -*-
"""
Created on Sun Oct 08 10:45:06 2017

@author: Hemant Mishra
"""
def create_model(a,b,cur):
    import graphlab as gl
    
    actions = gl.SFrame.read_csv('Datasets/rating.csv')
    new_user_number = len(set((actions['user_id'])))+1
    
    anime = a
    ratings = b
    film_count = len(anime)
    
    
    new_user_info = gl.SFrame({'user_id':[new_user_number]*film_count,'anime_id':anime, 
                               'rating':ratings})    
    model = gl.load_model("mymodel")
    results = model.recommend_from_interactions(new_user_info,k=10) 
    l = []
    for i in results['anime_id']:
        rows=cur.execute("select name from anime where anime_id = (?)",[i]).fetchone()
        l.append(rows[0])
        
    return l
def popular(cur):   
    import graphlab as gl    
    model = gl.load_model("mymodel1")
    l=[]
    nn=model.recommend_from_interactions([5000],k=10)
    for i in nn:
        rows=cur.execute("select name from anime where anime_id = (?)",[i['anime_id']]).fetchone()
        l.append((rows[0],i['rank']))
        
    return l
    
