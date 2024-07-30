import FreeSimpleGUI as sg
from users import Users
from inventory import Inventory
from orders import Orders
import operator

class Menu:
    def __init__(self, db):
        self.db = db
        
    
    def welcome(self):
        self.users = Users(self.db)
        layout = [[sg.Text("Joe's Hardware Store")],
                  [sg.Text("Login or Sign-up")],
                  [sg.Button('Login', auto_size_button=False)],
                  [sg.Button('Sign-up', auto_size_button=False)],
                  [sg.Button('Exit', auto_size_button=False)]]
        window = sg.Window('Welcome', layout, element_justification='c')
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                break
            
            if(event == 'Login'): self.login()
            else: self.signup()
        window.close()
    
    def login(self):
        layout = [[sg.Text("Username")],
                  [sg.Input(key='-USERNAME-')],
                  [sg.Text("Password")],
                  [sg.Input(key='-PASSWORD-', password_char='*')],
                  [sg.Text(size = (20, 1), key = '-OUTPUT-')],
                  [sg.Button('Login'), sg.Button('Exit')]]
        window = sg.Window("Login", layout)

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                window.close()
                break
            uname = values['-USERNAME-']
            passw = values['-PASSWORD-']
            query = {'username' : uname, 'password' : passw}
            result = self.users.search(query)
            if(len(result) == 0):
                window['-OUTPUT-'].update('Invalid login!', text_color = 'red')
                continue
            else:
                result = result[0]
                auth = {'_id' : result[1], 'username' : result[4], 'first_name' : result[2], 'last_name' : result[3], 'admin' : result[7]}
                window.close()
                self.storeMenu(auth)
                break

    def signup(self):
        layout = [[sg.Text("First Name")],
                  [sg.Input(key='-FNAME-')],
                  [sg.Text("Last Name")],
                  [sg.Input(key='-LNAME-')],
                  [sg.Text("Create a username")],
                  [sg.Input(key='-USERNAME-')],
                  [sg.Text("Enter Password")],
                  [sg.Input(key='-PASSWORD1-', password_char='*')],
                  [sg.Text("Enter Password Again")],
                  [sg.Input(key='-PASSWORD2-', password_char='*')],
                  [sg.Text(size = (20, 1), key = '-OUTPUT-')],
                  [sg.Checkbox('Admin', default = False, key = '-ADMIN-')],
                  [sg.Button('Sign Up'), sg.Button('Exit')]]
        window = sg.Window("Sign-Up", layout)

        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                window.close()
                break
            if values['-PASSWORD1-'] != values['-PASSWORD2-']:
                window['-OUTPUT-'].update('Passwords do not match', text_color = 'red')
                continue
            fname = values['-FNAME-']
            lname = values['-LNAME-']
            uname = values['-USERNAME-']
            passw = values['-PASSWORD1-']
            id = self.users.insert(fname, lname, uname, passw, values['-ADMIN-'])
            if(id == 0):
                window['-OUTPUT-'].update('Error - User insertion failed!', text_color = 'red')
                continue
            elif(id == 2):
                window['-OUTPUT-'].update('Username already in use!', text_color = 'red')
                continue
            else:
                window.close()
                break

    
    def storeMenu(self, auth):
        layout = []
        layout.append([sg.Text('Welcome {}!'.format(auth['first_name']))])
        if(auth['admin']):
            layout.append([sg.Text('ADMIN MENU')])
            layout.append([sg.Button('User Management', key = '-USERS-', expand_x = True)])
            layout.append([sg.Button('Order Management', key = '-ORDERS-', expand_x = True)])
            layout.append([sg.Button('Inventory Management', key = '-INVENTORY-', expand_x = True)])
        else:
            layout.append([sg.Text('Please Select An Option: ')])
            layout.append([sg.Button('Browse/Order Items', key = '-BROWSE-', expand_x = True)])
            layout.append([sg.Button('View my Orders', key = '-VIEW-', expand_x = True)])
        layout.append([sg.Button('Exit', key = 'Exit')])

        window = sg.Window("Store Menu", layout, element_justification = 'c')
        while True:
            event, values = window.read()
            if event == sg.WINDOW_CLOSED or event == 'Exit':
                window.close()
                break
            if event == '-BROWSE-' or event == '-INVENTORY-':
                self.inventory(auth)
            if event == '-VIEW-' or event == '-ORDERS-':
                self.orders(auth)
            if event == '-USERS-':
                self.userMan()
        return
    
    
    def sort_table(self, table, cols, flip):
        for col in reversed(cols):
            try:
                table = sorted(table, key=operator.itemgetter(col), reverse = flip)
            except Exception as e:
                sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
        return table
    

    def userMan(self):
        flip = 0
        users = Users(self.db)
        res = users.search()
        if (res == -1): return 0
        headers = ['Index', 'user id', 'first name', 'last name', 'user name', 'total orders', 'total spent', 'admin']
        layout = [[sg.Table(values=res, headings=headers, max_col_width=25,
                    auto_size_columns=True,
                    justification='left',
                    num_rows=10,
                    key='-TABLE-',
                    expand_x=True,
                    expand_y=True,
                    enable_events=True,
                    enable_click_events=True)],
          [sg.Button('Create User', key = '-CREATE-')],
          [sg.Button('Update', visible = False, key = '-UPDATE-')],
          [sg.Button('Delete', visible = False, key = '-DELETE-')],
          [sg.Button('Reset Password', visible = False, key = '-RESET-')],
          [sg.Button('Exit')]]
        
        window = sg.Window('Orders', layout,
                        resizable=True)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == '-CREATE-':
                fname = sg.popup_get_text("Enter User First Name: ")
                lname = sg.popup_get_text("Enter User Last Name: ")
                uname = sg.popup_get_text("Enter Username: ")
                passw = sg.popup_get_text("Enter Password: ")
                admin = sg.popup_yes_no("Is user admin?")
                if(admin == 'Yes'): admin = True
                else: admin = False
                result = users.insert(fname, lname, uname, passw, admin = admin)
                if(result == 2): sg.popup("Username already in use!")
                elif(result == 0): sg.popup("ERROR - Insert failed")
                else: 
                    sg.popup("USER ADDED")
                    new_table = users.search()
                    window['-TABLE-'].update(new_table)
                    res = new_table
            if event == '-UPDATE-':
                layout = [[sg.Button('First Name'), sg.Button('Last Name'), sg.Button('Username'), sg.Button('Admin Status')]]
                updatewindow = sg.Window('Select Field to Update', layout)
                event, values = updatewindow.read()
                index = selection[2][0]
                i = res[index][0]
                match event:
                    case 'First Name':
                        fname = sg.popup_get_text("Enter new first name: ")

                        users.update(i, fname, 'first_name')
                        if(result == 1): sg.popup('USER UPDATED')
                        else: sg.popup('ERROR - UPDATE FAILED')
                    case 'Last Name':
                        lname = sg.popup_get_text("Enter new last name: ")
                        
                        users.update(i, lname, 'last_name')
                        if(result == 1): sg.popup('USER UPDATED')
                        else: sg.popup('ERROR - UPDATE FAILED')
                    case 'Username':
                        uname = sg.popup_get_text("Enter new username: ")
                        result = users.update(i, uname, 'username')
                        if(result == 1): sg.popup('USER UPDATED')
                        elif(result == 0): sg.popup('UPDATE FAILED - USERNAME TAKEN')
                        else: sg.popup('ERROR - UPDATE FAILED')
                    case 'Admin Status':
                        confirm = sg.popup_yes_no('Confirm Admin Status Change')
                        if(confirm == 'Yes'):
                            result = users.update(i, True, 'admin')
                            if(result == 1): sg.popup('ADMIN STATUS CHANGED')
                            else: sg.popup('ERROR - STATUS CHANGE FAILED')
                new_table = users.search()
                window['-TABLE-'].update(new_table)
                res = new_table
                updatewindow.close()
            if event == '-RESET-':
                confirm = sg.popup_yes_no('Confirm Password Reset')
                index = selection[2][0]
                i = res[index][0]
                if(confirm == 'Yes'):
                    result = users.update(i, 'pass', 'password')
                    if(result == 1): sg.popup('PASSWORD RESET')
                    else: sg.popup('ERROR - PASSWORD RESET FAILED')
            if event == '-DELETE-':
                index = selection[2][0]
                confirm = sg.popup_yes_no("Confirm Deletion")
                if(confirm == 'Yes'):
                    i = res[index][0]
                    users.update(i)
                    new_table = users.search()
                    window['-TABLE-'].update(new_table)
                    res = new_table
            if isinstance(event, tuple):
                if event[0] == '-TABLE-':
                    selection = event
                    print(selection)
                    if event[2][0] == -1:
                        print(event[2][1])
                        col_num_clicked = event[2][1]
                        cols = (col_num_clicked, 0)
                        new_table = self.sort_table(res, cols, flip)
                        flip = 1-flip
                        window['-TABLE-'].update(new_table)
                        res = new_table
                    window['-UPDATE-'].update(visible = True)
                    window['-RESET-'].update(visible = True)
                    window['-DELETE-'].update(visible = True)

        window.close()
        return 1
        
    def orders(self, auth):
        flip = 0
        orders = Orders(self.db)
        res = orders.search(admin = auth['admin'], user_id = auth['_id'])
        if (res == -1): return 0
        if(auth['admin']):
            headers = ['Index', 'order id', 'customer id', 'customer username', 'order date', 'item name', 'unit price', 'quantity', 'total']
        else:
            headers = ['Index', 'order id', 'order date', 'item name', 'unit price', 'quantity', 'total']
            for row in res:
                del row[2]
                del row[2]
        layout = [[sg.Table(values=res, headings=headers, max_col_width=25,
                    auto_size_columns=True,
                    justification='left',
                    num_rows=10,
                    key='-TABLE-',
                    expand_x=True,
                    expand_y=True,
                    enable_events=True,
                    enable_click_events=True)],
          [sg.Button('Cancel', visible = False, key = '-DELETE-')],
          [sg.Button('Exit')]]
        
        window = sg.Window('Orders', layout,
                        resizable=True)
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == '-DELETE-':
                index = selection[2][0]
                confirm = sg.popup_yes_no("Confirm Cancellation?")
                if(confirm == 'Yes'):
                    i = res[index][0]
                    orders.update(i)
                    new_table = orders.search(admin = auth['admin'], user_id = auth['_id'])
                    window['-TABLE-'].update(new_table)
                    res = new_table
            if isinstance(event, tuple):
                if event[0] == '-TABLE-':
                    selection = event
                    print(selection)
                    if event[2][0] == -1:
                        print(event[2][1])
                        col_num_clicked = event[2][1]
                        cols = (col_num_clicked, 0)
                        new_table = self.sort_table(res, cols, flip)
                        flip = 1-flip
                        window['-TABLE-'].update(new_table)
                        res = new_table
                    elif(auth['admin']):
                        window['-DELETE-'].update(visible=True)
        window.close()
        return 1

    def inventory(self, auth):
        flip = 0
        orders = Orders(self.db)
        inventory = Inventory(self.db)
        res = inventory.search(admin = auth['admin'])
        if (res == -1): return 0
        headers = ['Index', 'item id', 'Name', 'Price', "Quantity"]
        layout = [[sg.Table(values=res, headings=headers, max_col_width=25,
                    auto_size_columns=True,
                    justification='left',
                    num_rows=10,
                    key='-TABLE-',
                    expand_x=True,
                    expand_y=True,
                    enable_events=True,
                    enable_click_events=True)],
          [sg.Button('Purchase', visible = False, key = '-PURCHASE-')],
          [sg.Button('Create Item', visible = auth['admin'], key = '-CREATE-')],
          [sg.Button('Update', visible = False, key = '-UPDATE-'), sg.Button('Delete', visible = False, key = '-DELETE-')],
          [sg.Button('Exit')]]
        
        window = sg.Window('Inventory', layout,
                        resizable=True)
        
        while True:
            event, values = window.read()


            if event == sg.WIN_CLOSED or event == 'Exit':
                break


            if event == '-PURCHASE-':
                quantity = sg.popup_get_text('Enter Quantity')
                quantity = int(quantity)
                index = int(selection[2][0])
                res = orders.insert(auth['_id'], res[index][1], quantity)
                if(res == 1):
                    sg.popup('Order Created Successfully!')
                    new_table = inventory.search(admin = auth['admin'])
                    window['-TABLE-'].update(new_table)
                    res = new_table
                elif(res == 0):
                    sg.popup('Order Failed - Invalid Quantity')
                else: sg.popup('ERROR - Order Not Created')


            if event == '-CREATE-':
                name = sg.popup_get_text("Enter Item Name: ")
                price = sg.popup_get_text("Enter Item Price: ")
                quantity = sg.popup_get_text("Enter item quantity: ")
                if(not quantity.isdigit()): sg.popup("ITEM NOT CREATED - Invalid Quantity")
                else:
                    try:
                        price = float(price)
                        quantity = int(quantity)
                        inventory.insert(name, price, quantity)
                        new_table = inventory.search(admin = auth['admin'])
                        window['-TABLE-'].update(new_table)
                        res = new_table
                        sg.popup("ITEM ADDED")
                    except:
                        sg.popup("ITEM NOT CREATED - Invalid Price")


            if event == '-UPDATE-':
                layout = [[sg.Button('Name'), sg.Button('Price'), sg.Button('Quantity')]]
                updatewindow = sg.Window('Select Field to Update', layout)
                event, values = updatewindow.read()
                index = selection[2][0]
                i = res[index][0]
                match event:
                    case 'Name':
                        name = sg.popup_get_text("Enter new item name: ")

                        inventory.update(i, name, 'item_name')
                    case 'Price':
                        price = sg.popup_get_text("Enter new item price: ")
                        try:
                            price = float(price)
                            inventory.update(i, update = price, updateField = 'price')
                        except:
                            sg.popup("Invalid Price!")
                    case 'Quantity':
                        quantity = sg.popup_get_text("Enter new quantity: ")
                        if(quantity):
                            if(quantity.isnumeric()):
                                quantity = int(quantity)
                                inventory.update(i, update = quantity, updateField = 'quantity')
                            else:
                                sg.popup("Invalid Quantity!")
                new_table = inventory.search(admin = auth['admin'])
                window['-TABLE-'].update(new_table)
                res = new_table
                updatewindow.close()

            if(event == '-DELETE-'):
                index = selection[2][0]
                i = res[index][0]
                name = res[index][1]
                confirm = sg.popup_yes_no('Confirm Deletion of {}'.format(name))
                if(confirm == 'Yes'):
                    inventory.update(i)
                    new_table = inventory.search(admin = auth['admin'])
                    window['-TABLE-'].update(new_table)
                    res = new_table
                
            if isinstance(event, tuple):
                if event[0] == '-TABLE-':
                    selection = event
                    print(selection)
                    if event[2][0] == -1:
                        print(event[2][1])
                        col_num_clicked = event[2][1]
                        cols = (col_num_clicked, 0)
                        print(res)
                        print(type(res))
                        new_table = self.sort_table(res, cols, flip)
                        flip = 1-flip
                        window['-TABLE-'].update(new_table)
                        res = new_table
                    elif(auth['admin']):
                        window['-UPDATE-'].update(visible=True)
                        window['-DELETE-'].update(visible=True)
                    else:
                        window['-PURCHASE-'].update(visible=True)

        window.close()
        return 1

