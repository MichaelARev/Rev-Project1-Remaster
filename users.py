import logging


class Users:
    def __init__(self, db) -> None:
        self.db = db
    
    def __view(self):
        try:
            table = []
            for i, user in enumerate(self.searchResult):
                pipeline = [
                    {'$match' : {'customer_id' : user['_id']}},
                    {'$group' : {'_id':'null', 'total_orders':{'$count':{}}, 'total_spent':{'$sum':'$total'}}}
                ]
                orderInfo = self.db.orders.aggregate(pipeline)
                orderInfo = list(orderInfo)
                if(orderInfo):
                    orderInfo = orderInfo[0] 
                    print(orderInfo)
                    table.append([i, user['_id'], user['first_name'], user['last_name'], user['username'], orderInfo['total_orders'], '$' + str(orderInfo['total_spent']), user['admin']])
                else: table.append([i, user['_id'], user['first_name'], user['last_name'], user['username'], 0, '$0', user['admin']])
            return table
        except Exception as e:
            print('Error - Failed to display users')
            logging.error(e)
            return -1


    def search(self, queries = {}, admin = False, searchType = '_id'):
        try:
            search = {}
            if(queries):
                for querytype, query in queries.items():
                    search[querytype] = query
            logging.info(search)
            self.searchResult = list(self.db.users.find(search))
            return self.__view()
        except Exception as e:
            print("Error - Search Failed")
            logging.error(e)
    
    def insert(self, fname, lname, uname, passw, admin = False):
        try:
            if self.db.users.count_documents({'username': uname}): 
                logging.info('User attempted to use existing username...')
                return 2
            else:
                user = {'username' : uname, 'password' : passw, 'first_name' : fname, 'last_name' : lname, 'admin' : admin}
                self.db.users.insert_one(user)
                logging.info('User inserted')
                return 1
        except Exception as e:
            print('Error - User insertion failed')
            logging.error(e)
            return 0
    
    def update(self, i, update = None, updateField = None):
        try:
            item = self.searchResult[i]
            if(update):
                if(updateField == 'username' and self.db.users.count_documents({'username': update})): return 0
                else:
                    updateQuery = {'_id':item['_id']}
                    update = {'$set':{updateField : update}}
                    self.db.users.update_one(updateQuery, update)
                    print("USER UPDATED")
                    return 1
            else:
                self.db.users.delete_one({'_id':item['_id']})
                print("USER DELETED")
                return 1
        except Exception as e:
            print("Error - Update/Delete Failed")
            logging.error(e)
            return -1
    
