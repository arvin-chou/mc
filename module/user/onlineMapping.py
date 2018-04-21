# Our API will expose resource (MongoDB collections): 'online'.
# In order to allow for proper data validation, we define beaviour
# and structure.
online = {
    # 'title' tag used in item links.
    'item_title': 'online',

    # most global settings can be overridden at resource level
    #'resource_methods': ['GET', 'POST', 'PUT'],

    # Schema definition, based on Cerberus grammar. Check the Cerberus project
    # (https://github.com/nicolaiarocci/cerberus) for details.
    'schema': {
        'users': {
            'type': 'objectid',
            'data_relation': {
                 'resource': 'users',
                 'field': '_id',
                 'embeddable': True
             }
        },
        # sha1, plze add salt
        'token': {
            'type': 'string',
            'minlength': 20,
            'maxlength': 20
        }
    }
}
