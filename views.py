from flask_user import login_required, roles_required
from flask_restful import Resource, reqparse
import sqlite3


parser = reqparse.RequestParser()
db_name = "imdb_movies.db"


def excute_query(sql_query,args_tuple,fetch=False):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute(sql_query, args_tuple)
    if fetch:
        data = cursor.fetchall()
        conn.close()
        return data
    else:
        conn.commit()
        conn.close()


class MovieViewset(Resource):

    @login_required
    def get(self, movie_id):
        movie_dict_list = excute_query('SELECT * from movies_info where id = ?',(movie_id,),fetch=True)
        results = []

        if len(movie_dict_list) == 0:
            return {'message':'Not Found'}, 404

        for movie_dict in  movie_dict_list:
            results.append({'id' : movie_dict[0],
                'name': movie_dict[1],
                'imdb_score': movie_dict[2],
                'director': movie_dict[3],
                'popularity':movie_dict[4]
            })
        return results

    @login_required
    @roles_required('Admin')
    def delete(self, movie_id):
        movie_dict_list = excute_query('DELETE from movies_info where id = ?',(movie_id,))
        return {'Status': 'OK'}, 201


class AllMoviesViewset(Resource):

    @login_required
    def get(self):
        movie_dict_list = excute_query('SELECT * from movies_info',(),fetch=True)
        results = []
        for movie_dict in  movie_dict_list:
            results.append({'id' : movie_dict[0],
                'name': movie_dict[1],
                'imdb_score': movie_dict[2],
                'director': movie_dict[3],
                'popularity':movie_dict[4]
            })
        return results

    @login_required
    @roles_required('Admin')
    def post(self):
        parser.add_argument('name', type=str)
        parser.add_argument('imdb_score', type=str)
        parser.add_argument('director', type=str)
        parser.add_argument('popularity', type=str)

        args = parser.parse_args()

        name = args['name']
        imdb_score = args['imdb_score']
        director = args['director']
        popularity = args['popularity']

        ## make sure same movie does not exist
        if (name is None) or (director is None):
            return {'error': 'name and director can\'t be null'}, 400

        ## storing the movie in db
        sql_query = "INSERT INTO movies_info(name , imdb_score, director, popularity) \
              VALUES (? , ?, ? , ?)"
        excute_query(sql_query, (name, imdb_score, director, popularity))

        ## fetching the id of newly created movie
        sql_query = "SELECT * from movies_info where name = ? and director = ? "
        movie_id = excute_query(sql_query, (name,  director), fetch =True)[0][0]

        return {'movie_id': movie_id}, 201
