import json
import sqlite3



with open('imdb.json') as f:
    json_data = json.load(f)

    conn = sqlite3.connect('imdb_movies.db')
    cursor = conn.cursor()

    query_1 = "CREATE table movies_info(id integer primary key, name text,  imdb_score real, \
                director text, popularity real);"
    cursor.execute(query_1)
    query_2 = "CREATE table genre_master(id integer primary key, genre_name text);"
    cursor.execute(query_2)
    query_3 = "CREATE table movie_genre_map(movie_id integer,genre_id integer ,FOREIGN KEY(movie_id) \
                references movies(id) ,FOREIGN KEY(genre_id) references genre_master(id));"
    cursor.execute(query_3)

    conn.commit()

    ## entering data into movies_info table
    sql_query = "INSERT INTO movies_info(name , imdb_score, director, popularity) \
          VALUES (? , ?, ? , ?)"
    data_list = []
    unique_genre_list = []
    for data_dict in json_data:
        data_tuple = (data_dict['name'], data_dict['imdb_score'], data_dict['director'], \
            data_dict['99popularity'])
        data_list.append(data_tuple)
        movie_genre_list = data_dict['genre']


        for movie_genre in movie_genre_list:
            if movie_genre not in unique_genre_list:
                unique_genre_list.append(movie_genre)

    cursor.executemany(sql_query,data_list)
    conn.commit()

    for genre in unique_genre_list:
        cursor.execute("INSERT INTO genre_master(genre_name) values ( ? )", (genre,))

    conn.commit()
    cursor.execute("SELECT * from genre_master")
    movie_genre_map = cursor.fetchall()
    movie_genre_dict = {}

    for row in movie_genre_map:
        movie_genre_dict[row[1]] = row[0]

    for data_dict in json_data:
        cursor.execute("SELECT id from movies_info where name  = ?", (data_dict['name'],))
        movie_id = cursor.fetchall()[0][0]

        genre_list = data_dict['genre']
        for genre in genre_list:
            cursor.execute("SELECT id from genre_master where genre_name  = ?", (genre,))
            genre_id = cursor.fetchall()[0][0]

            cursor.execute("INSERT INTO movie_genre_map(movie_id, genre_id) values ( ? , ?)", \
                 (movie_id, genre_id))

    conn.commit()
    conn.close()





