import math

def read_data(filename):
    user_ratings = {}

    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if line.strip():
            user_id, movie_id, rating = map(int, line.split())
            if user_id not in user_ratings:
                user_ratings[user_id] = {}
            user_ratings[user_id][movie_id] = rating

    return user_ratings

def write_data(filename, data):
    with open(filename, 'w') as file:
        for user_id, movie_id, predicted_rating in data:
            file.write(f"{user_id} {movie_id} {predicted_rating}\n")

def calculate_cosine_similarity(item1, item2):
    cross_product = 0
    item1_len, item2_len = 0, 0

    for user in item1:
        if user in item2:
            cross_product += float(item1[user] * item2[user])
            item1_len += math.pow(item1[user], 2)
            item2_len += math.pow(item2[user], 2)

    numerator = float(cross_product)
    denominator = math.sqrt(item1_len) * math.sqrt(item2_len)

    cos_sim = numerator / denominator if denominator != 0 else 0
    return cos_sim

def calculate_item_similarities(user_ratings):
    item_similarities = {}

    for movie1 in user_ratings:
        for movie2 in user_ratings:
            if movie1 != movie2:
                if movie1 not in item_similarities:
                    item_similarities[movie1] = {}

                similarity = calculate_cosine_similarity(user_ratings[movie1], user_ratings[movie2])
                avg_rating_movie1 = sum(user_ratings[movie1].values()) / len(user_ratings[movie1])

                item_similarities[movie1][movie2] = [similarity, avg_rating_movie1]

    return item_similarities

def predicted_cosine_rating(sim_items_array, movie_id, user_id, item_ratings, item_similarities):
    numerator, denominator = 0, 0

    for similarity, other_movie_id in sim_items_array:
        if user_id in item_ratings[other_movie_id]:
            numerator += item_ratings[other_movie_id][user_id] * similarity
            denominator += max(0, similarity)

    if denominator != 0:
        predicted_rating = numerator / denominator
    else:
        return 3  # return 3 in case of the extra zeros
    return round(predicted_rating)

def get_sim_items(movie_id, k, item_similarities):
    array = []

    if movie_id not in item_similarities:
        return array

    for other_movie_id, [similarity, _] in item_similarities[movie_id].items():
        if len(array) < k:
            array.append([similarity, other_movie_id])
            array.sort(reverse=True)
        elif similarity > array[k - 1][1]:
            array[k - 1] = [similarity, other_movie_id]
            array.sort(reverse=True)
        else:
            continue

    return array

def predict_rating(user_id, movie_id, item_ratings, item_similarities):
    if movie_id not in item_ratings:
        return 3

    sim_items_array = get_sim_items(movie_id, 200, item_similarities)
    return round(predicted_cosine_rating(sim_items_array, movie_id, user_id, item_ratings, item_similarities))

def main():
    train_filename = 'train.txt'
    test_filename = 'test20.txt'
    result_filename = 'result20.txt'

    user_ratings = read_data(train_filename)
    item_similarities = calculate_item_similarities(user_ratings)

    item_ratings = {}
    for user_id, ratings in user_ratings.items():
        for movie_id, rating in ratings.items():
            if movie_id not in item_ratings:
                item_ratings[movie_id] = {}
            item_ratings[movie_id][user_id] = rating

    test_data = read_data(test_filename)

    result_data = []
    for user_id, ratings in test_data.items():
        for movie_id, _ in ratings.items():
            predicted_rating = predict_rating(user_id, movie_id, item_ratings, item_similarities)
            result_data.append((user_id, movie_id, predicted_rating))

    write_data(result_filename, result_data)

    main()