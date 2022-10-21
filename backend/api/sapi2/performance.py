#from flask_sqlalchemy import get_debug_queries
#from flask import current_app, abort
#from . import api


#@api.after_app_request
#def after_request(response):
    #for query in get_debug_queries():
        #if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            #current_app.logger.warning(
                #'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                #% (query.statement, query.parameters, query.duration,
                   #query.context))
    #return response

#@api.route('/shutdown')
#def server_shutdown():
    #if not current_app.testing:
        #abort(404)
    #shutdown = request.environ.get('werkzeug.server.shutdown')
    #if not shutdown:
        #abort(500)
    #shutdown()
    #return 'Shutting down...'