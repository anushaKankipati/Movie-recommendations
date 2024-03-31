import math
import collections
import sys
import random

user_ratings = {}
test_ratings = {}



"""
user_ratings = {
    1 (user): {101 (movie): 4 (rating), 102: 3, 105: 5},
    2: {101: 2, 103: 4, 104: 3},
    # ...
}    
same format for test_ratings
"""

def read_training_data(filename):

    with open(filename, 'r') as file:
        contents = file.read()
        lines = contents.split('\n')
        for line in lines:
            user_id, movie_id, rating = map(int, line.split())
            if user_id not in user_ratings:
                user_ratings[user_id] = {}
            user_ratings[user_id][movie_id] = rating
    
    print("done reading train")


def read_test_data(filename):
    #global test_lines
    with open(filename, 'r') as file:
            contents = file.read()
            test_lines = contents.split('\n')
            for line in test_lines:
                user_id, movie_id, rating = map(int, line.split())
                if user_id not in test_ratings:
                    test_ratings[user_id] = {}
                test_ratings[user_id][movie_id] = rating
    print("done reading "+filename)

def get_num_users():
    numUsers = 0
    for user in test_ratings:
        numUsers +=1
    return numUsers


def write_data(read_file, write_file):
    with open(write_file, "w") as new_file:
        #print("here")
        with open (read_file, "r") as read:
            contents = read.read()
            input_lines = contents.split('\n')
            for line in input_lines:
                #print("here 1")
                if line.strip():
                    #print(line)
                    user_id, movie_id, rating = map(int, line.split())
                    #print("here 3")
                    if rating == 0:
                        updated_rating = test_ratings[user_id][movie_id]
                        new_file.write(f"{user_id} {movie_id} {updated_rating}\n")
    
    print("wrote to "+ write_file)



def caseModification(weights):
	new_weights = []
	for weight in weights:
		new_weights.append(weight * abs(weight)**2.5)
	return new_weights



def generateAverage(user):
	avg, count = 0, 0
	for rating in user:
		if rating == 0:
			continue
		else:
			avg += rating
			count += 1
	if(count != 0):
		return avg/count
	else:
		return 0

def cosine_similarity(test_user, train_user): #test_user & train_user is one line of dict

    cross_product = 0
    test_user_len, train_user_len = 0, 0
    #Loop through keys (movies) in test_user.ratings 
    #test_user[103] gives us rating 4: 2: {101: 2, 103: 4, 104: 3}
    for key in test_user:

        #If key is present in train_user.ratings, compute the product of the corresponding elements, then add them to the running total
        if key in train_user:
            cross_product += float(int(test_user[key]) * int(train_user[key]))
            train_user_len += math.pow(train_user[key], 2)
            test_user_len += math.pow(test_user[key], 2)

    #Calculate numerator/denominator of the equation, check for zeroes
    numerator = float(cross_product)
    denominator = math.sqrt(train_user_len) * math.sqrt(test_user_len)
    if denominator == 0:
        cos_sim = 0
    else:
        cos_sim = numerator/denominator
    
    print(cos_sim)
    return cos_sim


def pearson_similarity(test_user, train_user, iuf_flag, case_mod_flag):    
    numUsers = get_num_users()
    # Same deal as cosine similarity, but subtract average rating from each part of cross product
    cross_product = 0
    m_j = 0
    train_user_length, test_user_length = 0, 0

    test_user_avg = generateAverage(test_user)
    train_user_avg = generateAverage(train_user)
    
    for key in test_user:
        
        if key in train_user:
            m_j +=1
            cross_product += (test_user[key] - test_user_avg) * (train_user[key] - train_user_avg)
            train_user_length += (train_user[key] - train_user_avg) ** 2
            test_user_length += (test_user[key] - test_user_avg) ** 2

    numerator = float(cross_product)
    denominator = ((train_user_length ** 0.5) * (test_user_length ** 0.5))
    iuf = math.log(numUsers/m_j)
    if denominator == 0:
        return 0
    pearson_sim = numerator / denominator
    if iuf_flag==1:
        pearson_sim = (numerator / denominator)*iuf
    if case_mod_flag ==1:
        pearson_sim = pearson_sim * (abs(pearson_sim) **2.5)
    
    #print(pearson_sim)
    return pearson_sim

def custom_similarity(test_user, train_user):
    set_test_movies = set(test_user.keys())
    set_train_movies = set(train_user.keys())

    intersection_size = len(set_test_movies.intersection(set_train_movies))
    union_size = len(set_test_movies.union(set_train_movies))

    if union_size == 0:
        return 0  # Both users have not rated any common movies

    jaccard_sim = intersection_size / union_size
    
    return jaccard_sim

def get_sim_users(test_user, movie, k):
    array = []

    for user in user_ratings:
        train_user = user_ratings[user]
        if movie in train_user:
            #user_similarity = cosine_similarity(test_user, train_user)
            user_similarity = pearson_similarity(test_user, train_user, 0, 0)
            #user_similarity = custom_similarity(test_user, train_user)
            if len(array) < k:
                array.append([user_similarity, user])
                array.sort(reverse=True)
            elif user_similarity > array[k-1][1]:
                array[k-1] = [user_similarity, user]
                array.sort(reverse=True)
            else:
                continue
    
    return array

def get_predicted_rating(sim_users_array, movie_id, pearson_flag):
    
    numerator, denominator = 0, 0
    
    for index, (similarity, id) in enumerate(sim_users_array):
        if pearson_flag ==1:
            user_avg = generateAverage(user_ratings[id])
            numerator += (user_ratings[id][movie_id]) * similarity 
        else:
            numerator += user_ratings[id][movie_id] * similarity 
        #print(numerator)
        denominator += abs(similarity)
    if denominator != 0:
        predicted_rating =  numerator/denominator
    else:
        predicted_rating = 3
    #print(round(predicted_rating))
    return round(predicted_rating)


    
def main(pearson_flag):
    train_filename = 'train.txt'
    test_filename = 'test5.txt'
    result_filename = 'result5.txt'
    read_training_data(train_filename)
    read_test_data(test_filename)
    for user_id in test_ratings:
    
        if(pearson_flag):
            userToPredict = generateAverage(test_ratings[user_id])
        #print(userToPredict)
        for movie_id in test_ratings[user_id]:
            if test_ratings[user_id][movie_id] == 0:
                sim_users_array = get_sim_users(test_ratings[user_id], movie_id, 100)
                if pearson_flag ==1:
                    predicted_rating =  get_predicted_rating(sim_users_array, movie_id, 1)
                    if round(predicted_rating)==0:
                        test_ratings[user_id][movie_id] = 1
                    elif round(predicted_rating)>5:
                        test_ratings[user_id][movie_id] = 5
                    else:
                        test_ratings[user_id][movie_id] = round(predicted_rating)
                    
                else:
                    predicted_rating = get_predicted_rating(sim_users_array, movie_id, 0)
                    test_ratings[user_id][movie_id] = predicted_rating
    write_data(test_filename, result_filename)

main(1)
