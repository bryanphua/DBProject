from django.test import TestCase
from django.db import connection
from DataHub.models import users
from ModelClass.custom_exceptions import *

create_users_table_sql ="""
CREATE TABLE users
(
    id int not null auto_increment
        primary key,
    password varchar(50) not null,
    email varchar(50) not null,
    display_name varchar(50) not null,
    admin tinyint(1) not null,
    constraint unique_email
        unique (email)
)
;
"""

insert_users_sql = """
INSERT INTO users (password,email,display_name,admin) VALUES 
('password1','bobbylim@sutd.edu.sg','bobby',0),
('wordpass22','jenny@gmail.com','xiao_jen',1),
('ppww111','hankytom@hotmail.com','tomm',0),
('iforgot90','ah_seng@sutd.edu.sg','seng 2',1),
('wotwotwot','franky@yahoo.com','franky',1),
('wotwotwot2','franky2@yahoo.com','franky',1)
"""
drop_users_sql = "DROP TABLE users"

class TestGetEntries(TestCase):
    def setUp(self):
        cursor = connection.cursor()
        # create table
        cursor.execute(create_users_table_sql)
        # insert entries
        cursor.execute(insert_users_sql)

    def test_GetEntries(self):
        # column_list = None, cond_list=None
        result = users.get_entries(max_rows=None)
        self.assertEquals(result[0], ('id', 'password', 'email', 'display_name', 'admin'))
        self.assertEquals(len(result[1]), 6)

        # max rows
        result = users.get_entries(max_rows=3)
        self.assertEquals(len(result[1]), 3)

        # query entry that exists
        result = users.get_entries(column_list=['password','email'],cond_dict={'display_name':'bobby'})
        self.assertEquals(result,(('password','email'),(('password1','bobbylim@sutd.edu.sg'),)))

        result = users.get_entries(column_list=['admin','email'], cond_dict={'display_name': 'franky'})
        self.assertEquals(result, (('admin', 'email'), ((1,'franky@yahoo.com'),(1,'franky2@yahoo.com'))))

        # row count
        result = users.get_entries(cond_dict={'admin': 1},row_numbers=True)
        self.assertEquals(result,4)

        # query entry that does not exist
        result = users.get_entries(cond_dict={'display_name': 'bryan'}, row_numbers=True)
        self.assertEquals(result, 0)

    def tearDown(self):
        cursor = connection.cursor()
        # drop table
        cursor.execute(drop_users_sql)

class TestCheckExists(TestCase):
    def setUp(self):
        cursor = connection.cursor()
        # create table
        cursor.execute(create_users_table_sql)
        # insert entries
        cursor.execute(insert_users_sql)

    def test_check_exists(self):
        self.assertTrue(users.check_exists({'admin':1}))
        self.assertTrue(users.check_exists({'display_name': 'seng 2'}))
        self.assertTrue(users.check_exists({'display_name':'xiao_jen',
                                            'admin':1}))
        self.assertFalse(users.check_exists({'display_name':'tomm',
                                             'password':'ppww112'
                                             }))
        self.assertFalse(users.check_exists({'display_name':'xiao_jen',
                                            'admin':0}))

    def tearDown(self):
        cursor = connection.cursor()
        # drop table
        cursor.execute(drop_users_sql)

class TestInsertEntries(TestCase):
    def setUp(self):
        cursor = connection.cursor()
        # create table
        cursor.execute(create_users_table_sql)
        # insert entries
        cursor.execute(insert_users_sql)

    def test_InsertEntries(self):
        # insert an entry without a not null column field
        # except NotNullException raised
        try:
            users.insert_new_entry({'display_name':'notgonnahappen'})
            self.assertTrue(False)
        except NotNullException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)
        self.assertFalse(users.check_exists({'display_name': 'notgonnahappen'}))

        # insert new entry, expect success
        self.assertFalse(users.check_exists({'display_name':'Edward_test'}))
        users.insert_new_entry({'password':'idkla',
                                'email':'ededed@gmail.com',
                                'admin':0,
                                'display_name':'Edward_test'
                                })
        self.assertTrue(users.check_exists({'display_name':'Edward_test'}))
        users.delete_entries(cond_dict={'display_name':'Edward_test'})
        self.assertFalse(users.check_exists({'display_name':'Edward_test'}))

        # insert an entry with an existing unique value
        # expect UniqueConstraintException raised
        try:
            users.insert_new_entry({'password':'idkla',
                                'email':'franky2@yahoo.com',
                                'admin':0,
                                'display_name':'__'
                                })
            self.assertTrue(False)
        except UniqueConstraintException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)
        self.assertFalse(users.check_exists(cond_dict={'display_name':'__'}))
        print("Passed insert entry test")

        # insert an entry without a non required field
        # implicitly tested in previous insert examples as id is not specified

    def tearDown(self):
        cursor = connection.cursor()
        # drop table
        cursor.execute(drop_users_sql)


class TestUpdateEntries(TestCase):
    def setUp(self):
        cursor = connection.cursor()
        # create table
        cursor.execute(create_users_table_sql)
        # insert entries
        cursor.execute(insert_users_sql)

    def test_UpdateEntries(self):
        # normal update
        users.update_entries(value_dict={'display_name':'tommy',
                                        'password':'tommywashere'},
                            cond_dict={'display_name':'tomm'})
        self.assertFalse(users.check_exists({'display_name':'tomm'}))
        result = users.get_entries(column_list=['password','email','display_name','admin'],cond_dict={'display_name': 'tommy'})
        self.assertEquals(result[1],(('tommywashere','hankytom@hotmail.com','tommy',0),))

        # update a unique column with a non unique/existing value
        # expect UniqueConstraintException
        try:
            users.update_entries(value_dict={'email':'bobbylim@sutd.edu.sg'},
                                 cond_dict={'display_name': 'xiao_jen'})
            self.assertTrue(False)
        except UniqueConstraintException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

        # update a value that does not exist (nothing happens)
        users.update_entries(value_dict={'email': 'x'},
                             cond_dict={'display_name': 'does not exist'})
        self.assertFalse(users.check_exists({'display_name':'does not exist'}))


        # try to update unique columns of multiple entries with a single value
        # expect UniqueConstraintException
        try:
            users.update_entries(value_dict={'email':'admin@email.com'},
                                 cond_dict={'admin': 0})
            self.assertTrue(False)
        except UniqueConstraintException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

        # update non-unique columns of multiple entries
        self.assertTrue(users.check_exists({'admin': 0}))
        users.update_entries(value_dict={'admin':1},
                             cond_dict={'admin': 0})
        self.assertFalse(users.check_exists({'admin':0}))

    def tearDown(self):
        cursor = connection.cursor()
        # drop table
        cursor.execute(drop_users_sql)


class TestDeleteEntries(TestCase):
    def setUp(self):
        cursor = connection.cursor()
        # create table
        cursor.execute(create_users_table_sql)
        # insert entries
        cursor.execute(insert_users_sql)

    def test_DeleteEntries(self):
        # delete something that does not exist
        users.delete_entries({'display_name':'not a display name'})

        # delete 1 row
        self.assertTrue(users.check_exists({'display_name':'tomm'}))
        users.delete_entries({'display_name':'tomm'})
        self.assertFalse(users.check_exists({'display_name':'tomm'}))

        # delete multiple
        self.assertTrue(users.check_exists({'admin': 0}))
        users.delete_entries({'admin':0})
        self.assertFalse(users.check_exists({'admin':0}))

        # delete all
        self.assertTrue(users.check_exists(None)) # check if rows>0
        users.delete_entries({'admin':1})
        self.assertFalse(users.check_exists(None))  # check if rows>0

    def tearDown(self):
        cursor = connection.cursor()
        # drop table
        cursor.execute(drop_users_sql)


