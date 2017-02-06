
from AllMovies_imdb import get_all_movies, add_empty_data, get_connections, get_business_of_movie, check_worksheets, get_companycredits_of_movie, get_fullcredits_of_movie, get_releaseinfo_of_movie, get_techinfo_of_movie, get_detail_of_movie, register_toServer, upload_data, init_page
import Config

#Here's the main
while True:
    session= register_toServer() # 1. try to register
    todo = check_worksheets(session) # 2. obtain the todo list

    if todo is None:    # 3. if no longer things to do, exit
        print "Done."
        break
    else:
        fileuri= get_all_movies(session, todo, Config.SINGLE_TEST_MODE)   # 4. if it has things to do, do work.
        if fileuri == "":
            print "There's no file."
            todo.status = "done"
            todo.save()
        else:
            upload_data(session, todo, fileuri)