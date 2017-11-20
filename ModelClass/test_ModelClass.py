from django.test import TestCase
from django.db import connection
from DataHub.models import users

create_table_sql ="""
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

insert_sql = """
INSERT INTO users (password,email,display_name,admin) VALUES 
('password1','bobbylim@sutd.edu.sg','bobby',0),
('wordpass22','jenny@gmail.com','xiao_jen',1),
('ppww111','hankytom@hotmail.com','tomm',0),
('iforgot90','ah_seng@sutd.edu.sg','seng 2',1),
('wotwotwot','franky@yahoo.com','franky',1),
('wotwotwot2','franky2@yahoo.com','franky',1)
"""

class ModelTestCase(TestCase):
    def setUp(self):
        cursor = connection.cursor()
        # create table
        cursor.execute(create_table_sql)
        print('created table')
        # test entries
        cursor.execute(insert_sql)
        print('created entries')
        print('set up complete')
    def test_GetEntries(self):
        # column_list = None, cond_list=None
        result = users.get_entries(max_rows=None)
        self.assertEquals(result[0], ('id', 'password', 'email', 'display_name', 'admin'))
        self.assertEquals(len(result[1]), 6)

        result = users.get_entries(max_rows=3)
        self.assertEquals(len(result[1]), 3)

        # exists
        result = users.get_entries(column_list=['password','email'],cond_dict={'display_name':'bobby'})
        self.assertEquals(result,(('password','email'),(('password1','bobbylim@sutd.edu.sg'),)))

        result = users.get_entries(column_list=['admin','email'], cond_dict={'display_name': 'franky'})
        self.assertEquals(result, (('admin', 'email'), ((1,'franky@yahoo.com'),(1,'franky2@yahoo.com'))))

        # row count
        result = users.get_entries(cond_dict={'admin': 1},row_numbers=True)
        self.assertEquals(result,4)

        # does not exist
        result = users.get_entries(cond_dict={'display_name': 'bryan'}, row_numbers=True)
        self.assertEquals(result, 0)


