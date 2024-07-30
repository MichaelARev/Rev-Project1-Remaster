import logging


class Inventory:
    def __init__(self, db) -> None:
        self.db = db
    
    def __view(self):
        try:
            table = []
            for i, item in enumerate(self.searchResult):
                table.append([i, item['_id'], item['item_name'], float(item['price']), int(item['quantity'])])
            return table
        except Exception as e:
            print('Error - Failed to display inventory')
            logging.error(e)
            return -1


    def search(self, query = None, admin = False, searchType = 'item_name'):
        try:
            search = {}
            if(query): search[searchType] = query
            if(not admin): search['quantity'] = {'$gt': 0}
            self.searchResult = list(self.db.inventory.find(search))
            return self.__view()
        except Exception as e:
            print("Error - Search Failed")
            logging.error(e)
            return -1

    def insert(self, item_name, price, quantity):
        try:
            item = {'item_name' : item_name, 'price' : price, 'quantity' : quantity}
            if self.db.inventory.count_documents({ 'item_name': item_name }): return 0
            else: 
                self.db.inventory.insert_one(item)
                return 1
        except Exception as e:
            print("Error - Insertion Failed")
            logging.error(e)
            return -1
    
    def update(self, i, update = None, updateField = None):
        try:
            item = self.searchResult[i]
            print(item)
            if(update):
                updateQuery = {'_id' : item['_id']}
                field = {'$set' : {updateField : update}}
                self.db.inventory.update_one(updateQuery, field)
                print("ITEM UPDATED")
            else:
                self.db.inventory.delete_one({'_id':item['_id']})
                print("ITEM DELETED")
        except Exception as e:
            print("Error - Update/Delete Failed")
            logging.error(e)