import uuid
import random
import json
import string
import psycopg2

import pandas as pd
import matplotlib.pyplot as plt

from collections import defaultdict

from Backend import config
from Backend.config import categories_config

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host =      config.DB_HOST,
            database =  config.DB_DATABASE_NAME,
            user =      config.DB_USER,
            password =  config.DB_PASSWORD,
            port =  int(config.DB_PORT))
        
        self.cur = self.conn.cursor()
    
    # -------------------- SETs / CREATEs ------------------   
    def create_user(self, user_id, user_name, login_name, password, is_admin) -> str:
        ''' create user in 'users' table '''
        #validate login_name #NOTE: XXX: !NICE TO HAVE! more validation cases
        if len(login_name) < config.LOGIN_NAME_MIN_LENGTH: return None
        if len(login_name) > config.LOGIN_NAME_MAX_LENGTH: return None
        
        #set new login_name in db
        self.cur.execute(f"INSERT INTO users (pk_id, user_name, login_name, password, is_admin) VALUES ('{user_id}', '{user_name}', '{(login_name).lower()}', '{password}', '{is_admin}')")
        self.conn.commit()
        
        return login_name

    def create_group(self, group_id, group_name):
        ''' create group in 'groups' table '''
        self.cur.execute(f"INSERT INTO groups (pk_id, group_name) VALUES ('{group_id}', '{group_name}')")
        self.conn.commit()
    
    def set_login_name(self, user_id, login_name) -> str:
        ''' set new login_name for user_id, return None if failed, return login_name if valid '''
        #validate login_Name #NOTE: XXX: !NICE TO HAVE! more validation cases
        if len(login_name) < config.LOGIN_NAME_MIN_LENGTH: return None
        if len(login_name) > config.LOGIN_NAME_MAX_LENGTH: return None
        
        #set new login_Name in db
        self.cur.execute(f"UPDATE users SET login_name = '{login_name}' WHERE pk_id = {user_id}")
        self.conn.commit()
        
        return login_name
    
    def set_password(self, user_id, password) -> str:
        ''' set new password for user_id, return None if failed, return password if valid '''
        #validate password #NOTE: XXX: !NICE TO HAVE! more validation cases
        if len(password) < config.PASSWORD_MIN_LENGTH: return None
        if len(password) > config.PASSWORD_MAX_LENGTH: return None
        
        #set new password in db
        self.cur.execute(f"UPDATE users SET password = '{password}' WHERE pk_id = {user_id}")
        self.conn.commit()
        
        return password
    
    def create_usergroups(self, user_id, group_id, is_group_admin) -> None:
        """ create connection (row) in 'usergroups' table """
        # Convert boolean to integer
        role_value = 1 if is_group_admin else 0
        self.cur.execute(
            f"INSERT INTO usergroups (fk_user_id, fk_group_id, role) VALUES (%s, %s, %s)",
            (user_id, group_id, role_value)
        )
        self.conn.commit()
    
    
    def new_expense(self, user_id, group_id, category, price):
        """Insert a new expense into the userproducts table."""
        # Ensure the group and user exist before inserting expense
        if not self.is_group_exists(group_id):
            raise ValueError(f"Group ID {group_id} does not exist.")
        if not self.is_user_exists(user_id):
            raise ValueError(f"User ID {user_id} does not exist.")
        
        self.cur.execute(
            "INSERT INTO userproducts (fk_user_id, fk_group_id, category_name, amount) VALUES (%s, %s, %s, %s)",
            (user_id, group_id, category, price)
        )
        self.conn.commit()
    

    # -------------------- GETs ------------------
    def get_password(self, user_id) -> str:
        ''' Get password from 'users' table following given user_id '''
        #get password following given user_id
        self.cur.execute(f"select password from users where pk_id = {user_id}")
        password = self.cur.fetchall()[0][0] #return list of tuples thats why
        if password:
            return password
        else:
            return None
        

    def get_login(self, user_id) -> str:
        ''' Get login_name from 'users' table following given user_id '''
        #get login_name following given user_id
        self.cur.execute(f"select login_name from users where pk_id = {user_id}")
        login_name = self.cur.fetchall()[0][0] #return list of tuples thats why
        if login_name:
            return login_name
        else:
            return None
        
    # -------------------- IS_EXISTS ------------------
    def is_user_exists(self, user_id):
        ''' Check if user exists.\n
            Return (True, string of the details about the user) if exists,\n
            Return (False, None) if not exists'''
            
        #check if user_id exists
        self.cur.execute(f"select * from users where pk_id = {user_id}")
        user = self.cur.fetchall() #return list of tuples
        if user:
            return True, user
        else:
            #create random username
            #new_user_name = generate_random_username()
            #self.add_user(user_id,user_name, new_user_name)
            return False, None
    
    def is_usergroups_row_exists(self, user_id, group_id) -> bool:
        ''' return True if user-group row is already exists '''
        self.cur.execute(f"SELECT * FROM usergroups WHERE fk_user_id = {user_id} AND fk_group_id = {group_id}")
        row = self.cur.fetchall() #return list of tuples
        if row:
            return True
        else:
            return False
    
    def is_group_exists(self, group_id):
        ''' Check if group exists, return True / False'''
        #check if group_id exists
        self.cur.execute(f"select * from groups where pk_id = {group_id}")
        group = self.cur.fetchall() #return list of tuples
        if group:
            return True
        else:
            return False
        
    def is_exists(self, user_id, user_name, group_id, group_name, group_admin_flag: bool= False, update=None):
        """ activate on report. check if user, group and usergroups exists - else create them for tracking the report """

        #check if user exists
        if not self.is_user_exists(user_id):
            #if not create random user
            while True:
                login_name = generate_random_username().lower()
                self.cur.execute(f"select * from users where login_name = '{login_name}'") #make sure login_name not exists
                user = self.cur.fetchall()
                if not user:
                    break
            temp_password = f"{uuid.uuid4()}" #generate new password
            self.create_user(user_id, user_name, login_name, temp_password, is_admin=0)

        # check if group exists
        if not self.is_group_exists(group_id):
            self.create_group(group_id=group_id, group_name=group_name)

        # check if user-group connection exists:
        if not self.is_usergroups_row_exists(user_id,group_id):
            self.create_usergroups(user_id=user_id, group_id=group_id, is_group_admin=1)
    
    # def is_exists(self, user_id, user_name, group_id, group_name, group_admin_flag: bool = False, update=None):
    #     """Activate on report. Check if user, group, and usergroups exist, else create them for tracking the report."""
    #
    #     # Check if user exists
    #     if not self.is_user_exists(user_id):
    #         while True:
    #             login_name = generate_random_username().lower()
    #             self.cur.execute(
    #                 f"select * from users where login_name = '{login_name}'")  # Make sure login_name not exists
    #             user = self.cur.fetchall()
    #             if not user:
    #                 break
    #         temp_password = f"{uuid.uuid4()}"  # Generate new password
    #         self.create_user(user_id, user_name, login_name, temp_password, is_admin=0)
    #
    #     # Check if group exists
    #     if not self.is_group_exists(group_id):
    #         self.create_group(group_id=group_id, group_name=group_name)
    #
    #     # Check if user-group connection exists
    #     if not self.is_usergroups_row_exists(user_id, group_id):
    #         self.create_usergroups(user_id=user_id, group_id=group_id, is_group_admin=1)
    
    # -------------------- FUNCTIONS ------------------
    def insert(self, message_id, group_id, group_name, user_id, user_name, category, price):
        self.cur.execute("INSERT INTO db VALUES (?,?,?,?,?,?,?)",(message_id, group_id, group_name, user_id, user_name, category, price))
        self.conn.commit()

    def delete(self,group_id, user_id,delete_date):
        self.cur.execute(f"select role from usergroups where fk_group_id = {group_id} and fk_user_id = {user_id} ")
        user_role = self.cur.fetchone()[0]
        if user_role == 1:
            if delete_date == 'latest':
                query = f'''select *
           FROM userproducts
           WHERE fk_group_id = {group_id}
           ORDER BY "pk_id" DESC
           LIMIT 1;'''
                self.cur.execute(query)
                exepense_id = self.cur.fetchone()[0]
                self.cur.execute(f"DELETE FROM userproducts WHERE pk_id = {exepense_id}")
                #self.cur.execute(f"""DELETE FROM userproducts WHERE fk_group_id = {group_id} ORDER BY date_created DESC LIMIT 1)""")
            elif delete_date == 'today':
                self.cur.execute(f"DELETE FROM userproducts WHERE fk_group_id = {group_id} and EXTRACT(DAY FROM date_created) = EXTRACT(DAY FROM CURRENT_DATE)")
            elif delete_date == 'month':
                self.cur.execute(f"DELETE FROM userproducts WHERE fk_group_id = {group_id} and EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE)")
            elif delete_date == 'all':
                self.cur.execute(f"DELETE FROM userproducts WHERE fk_group_id = {group_id}")
            else:
                return "invalid format"
        else:
            return "Only the admin of the group can delete expenses!"
        self.conn.commit()
        
        return "Succesfuly deleted!"

    # def toExcel(self, group_id):
    #     query = f"select u.user_name as user, category_name as category, amount as price from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id}"
    #     df = pd.read_sql(query, self.conn)
    #     try:
    #         df.to_excel("expenses.xlsx", index=False)
    #     except Exception as e:
    #         print(f"Error export data: {e}")
    # def toExcel(self, group_id):
    #     query = f"select u.user_name as user, category_name as category, amount as price from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id}"
    #     df = pd.read_sql(query, self.conn)
    #     try:
    #         df.to_excel("expenses.xlsx", index=False)
    #         print("Data successfully exported to expenses.xlsx")
    #     except Exception as e:
    #         print(f"Error exporting data: {e}")
    def toExcel(self, group_id):
        query = f"SELECT u.user_name AS user, category_name AS category, amount AS price FROM userproducts up JOIN users u ON up.fk_user_id = u.pk_id WHERE fk_group_id = {group_id}"
        df = pd.read_sql(query, self.conn)
        try:
            # Specify the engine as 'xlsxwriter'
            df.to_excel("expenses.xlsx", index=False, engine="xlsxwriter")
            print("Data successfully exported to expenses.xlsx")
        except Exception as e:
            print(f"Error exporting data: {e}")
            
    def piechart(self, group_id, date):
        if date == "This Month":
            query = f"SELECT category_name, SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY category_name"
        elif date == "Last Month":
            query = f"SELECT category_name, SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE) -1 AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY category_name"
        else:
            query = f"SELECT category_name, SUM(amount) FROM userproducts where fk_group_id = {group_id} GROUP BY category_name"
        
        self.cur.execute(query)
        data = self.cur.fetchall()
        # create lists of categories and total prices
        categories = [row[0][::1] for row in data]
        prices = [row[1] for row in data]

        plt.pie(prices, labels=categories, autopct='%1.1f%%')
        plt.axis('equal')
        plt.title('Expenses')
        plt.savefig('my_plot.png')
        plt.clf()

    def barchart(self,group_id, date):
        if date == "This Month":
            query = f"select u.user_name, sum(amount) from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} AND EXTRACT(MONTH FROM up.date_created) = EXTRACT(MONTH FROM CURRENT_DATE) group by u.user_name"
        elif date == "Last Month":
            query = f"select u.user_name, sum(amount) from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} AND EXTRACT(MONTH FROM up.date_created) = EXTRACT(MONTH FROM CURRENT_DATE) -1 group by u.user_name"
        else:
            query = f"select u.user_name, sum(amount) from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} group by u.user_name"
        
        self.cur.execute(query)
        data = self.cur.fetchall()
        # create lists of categories and total prices
        users = [row[0][::1] for row in data]
        prices = [row[1] for row in data]

        plt.bar(users, prices)
        plt.xlabel('user')
        plt.ylabel('amount spend')
        plt.title('Expenses by users')
        plt.savefig('my_plot2.png')
        plt.clf()

    def total_expenses(self, group_id, date):
        if date == "This Month":
            self.cur.execute(f'SELECT SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE)')

        elif date == "Last Month":
            self.cur.execute(f'SELECT SUM(amount) FROM userproducts where fk_group_id = {group_id} AND EXTRACT(MONTH FROM date_created) = EXTRACT(MONTH FROM CURRENT_DATE)-1 AND EXTRACT(YEAR FROM date_created) = EXTRACT(YEAR FROM CURRENT_DATE)')
        else:
           self.cur.execute(f'SELECT SUM(amount) FROM userproducts where fk_group_id = {group_id}') 
        return self.cur.fetchone()[0]


    def brake_even(self, group_id):
        
        self.cur.execute(f"select u.user_name, sum(amount)from userproducts up join users u on up.fk_user_id = u.pk_id where fk_group_id = {group_id} group by u.user_name")
        data = self.cur.fetchall()
        if not data:
            return "No expenses to split"
        balances = []
        sum = 0
        average = 0
        result = ""
        # avg payment calculation for each user
        for person in data:
            sum += person[1]
        average = sum / len(data)
        # balance calculation for each user
        for person in data:
            balances.append([person[0], average - person[1]])
        for b1 in balances:
            if b1[1] > 0:
                for b2 in balances:
                    if b2[1] < 0:
                        if b1[1] <= -b2[1]: # b1 pay all his debt to b2
                            result += b1[0] + " owe " + b2[0] + " " + str(round(b1[1])) + " ₪\n"
                            b2[1] = b2[1] + b1[1]
                            b1[1] = 0
                            break
                        else: # b1 pay part of his debt to b2
                            result += b1[0] + " owe " + b2[0] + " " + str(round(-b2[1])) + " ₪\n"
                            b1[1] = b1[1] + b2[1]
                            b2[1] = 0
        return result
    
    def add_category(self, category_name):
        try:
            # Assuming you have a table called "categories" in your database
            query = "INSERT INTO categories (category_name) VALUES (%s)"
            cursor = self.conn.cursor()
            cursor.execute(query, (category_name,))
            self.conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Error adding category to database: {e}")
    # end of class


#other functions:

def write_category(group_id, new_category):
    if not open("categories.json").read(1):
        # file is empty
        data = {}
    else:
        # file is not empty, read JSON file into a dictionary
        with open("categories.json", "r") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                # file is not in valid JSON format
                data = {}
    # add a new key-value pair with a string value to the dictionary
    
    if group_id in data:
        if new_category in data[group_id] or new_category in categories_config:
            return "Category already exists!"
        else:
            data[group_id].append(new_category) # add new category to the group

    # group not exist. add new group
    else:
        data[group_id] = [new_category]
    # write the updated dictionary to the same JSON file
    with open("categories.json", "w") as f:
        json.dump(data, f)
    return "Category added successfuly!"



def get_categories(group_id):
    
    try:
        with open("categories.json", "r") as f:
            data = json.load(f)
            if group_id in data:
                return data[group_id]
            return []
    except:
        data = {}
        json_string = json.dumps(data)
        with open("categories.json", "w") as f:
            f.write(json_string)
        return []



def remove_category(group_id, category):
    if not open("categories.json").read(1):
        # file is empty
        return "category not exist"
    else:
        # file is not empty, read JSON file into a dictionary
        with open("categories.json", "r") as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                # file is not in valid JSON format
                return "category not exist"
    if group_id in data:
        if category in data[group_id]:
            data[group_id].remove(str(category))
            with open("categories.json", "w") as f:
                json.dump(data, f)
            return "category removed successfuly!"
    else:
        return "category not exist"


def generate_random_username(length=8):
    """Generate a random username."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# def generate_random_username(length=config.LOGIN_NAME_MIN_LENGTH+2):
#     characters = string.ascii_letters + string.digits  # Letters + Digits
#     username = ''.join(random.choice(characters) for _ in range(length))
#     return username


def validate_input(input):

    if not input.isnumeric():
        return "You must enter a number"

    if int(input) < 0:
        return "Expense must be greater than 0"
    
    if int(input) > 10000000:
        return "Expense must be less than 10,000,000"
