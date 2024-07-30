import logging
from datetime import date

class Orders:
    def __init__(self, db) -> None:
        self.db = db

    def __view(self):
        try:
            table = []
            for i, item in enumerate(self.searchResult):
                table.append([i, item['_id'], item['customer_id'], item['customer_uname'], item['date'], item['item_name'], item['unit_price'], item['quantity'], item['total']])
            return table
        except Exception as e:
            print('Error - Failed to display inventory')
            logging.error(e)
            return -1


    def search(self, query = None, admin = False, user_id = None, searchType = 'username'):
        try:
            search = {}
            if(not admin): search['customer_id'] = user_id
            if(query): search[searchType] = query
            self.searchResult = list(self.db.orders.find(search))
            return self.__view()
        
        except Exception as e:
            print("Error - Search Failed")
            logging.error(e)

    
    def insert(self, user_id, item_id, quantity):
        try:
            user = self.db.users.find({'_id' : user_id})
            item = self.db.inventory.find({'_id' : item_id})
            user, item = user[0], item[0]

            if(quantity > item['quantity']):
                print("Order Failed - Invalid Quantity")
                return 0
            
            today = str(date.today())

            order = {'customer_id' : user['_id'],
                     'customer_uname' : user['username'],
                     'date' : today, 
                     'item_name' : item['item_name'], 
                     'unit_price' : item['price'], 
                     'quantity' : quantity, 
                     'total' : float(item['price']*quantity)}
            
            self.db.orders.insert_one(order)
            print("ORDER CREATED")

            newQuantity = item['quantity'] - quantity
            self.db.inventory.update_one( {'_id' : item['_id']}, {'$set': {'quantity' : newQuantity}})
            return 1

        except Exception as e:
            print("Error - Insertion Failed")
            logging.error(e)
            return -1
    
    def update(self, i, update = None, updateField = None):
        try:
            order = self.searchResult[i]
            if(update):
                updateQuery = [{'_id' : order['_id']}, {'$set' : {updateField : update}}]
                self.db.orders.update_one(updateQuery)
                print("ITEM UPDATED")
            else:
                self.db.orders.delete_one({'_id':order['_id']})
                
                updateQuery = {'item_name' : order['item_name']}
                update = {'$inc' : {'quantity' : order['quantity']}}
                self.db.inventory.update_one(updateQuery, update)
                print("ITEM DELETED")
        except Exception as e:
            print("Error - Update/Delete Failed")
            logging.error(e)