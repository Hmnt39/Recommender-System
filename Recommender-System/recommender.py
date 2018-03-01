# -*- coding: utf-8 -*-
"""
Created on Sat Oct 07 18:50:15 2017

@author: Hemant Mishra
"""
import graphlab as gl
actions = gl.SFrame.read_csv('Datasets/rating.csv')

training_data, validation_data = gl.recommender.util.random_split_by_user(actions, 'user_id', 'anime_id')
model = gl.item_similarity_recommender.create(training_data, user_id='user_id', item_id='anime_id', target='rating')
model.save('mymodel')

model1=gl.popularity_recommender.create(training_data, user_id='user_id', item_id='anime_id', target='rating')
model1.save('mymodel1')
