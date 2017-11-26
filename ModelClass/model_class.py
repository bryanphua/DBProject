from ModelClass import Column
from ModelClass.custom_exceptions import *
from django.db import connection
from functools import reduce

class Model():
    column_list = None
    column_names = None

    # sql templates
    select_sql = "SELECT {} FROM {} "
    insert_sql = "INSERT INTO {} ({}) VALUES {}"
    update_sql = "UPDATE {} SET {} "
    delete_sql = "DELETE FROM {} "
    cond_sql = "WHERE {}"

    @classmethod
    def get_columns(cls):
        """returns a list of column objects of the defined class/table"""
        if cls.column_list is None:
            var_list = [v for k,v in cls.__dict__.items() if k[0] != '_']
            cls.column_list = [var for var in var_list if type(var) == Column]
        return cls.column_list

    @classmethod
    def get_unique_columns(cls):
        """returns a list of columns that has unique constraints (column.unique=True)"""
        column_list = cls.get_columns()
        return [column for column in column_list if column.unique]

    @classmethod
    def get_not_null_columns(cls):
        """returns a list of columns that has not null constraints (column.not_null=True)"""
        column_list = cls.get_columns()
        return [column for column in column_list if column.not_null]

    @classmethod
    def get_table_name(cls):
        """returns the name of the class/table"""
        return cls.__name__

    @classmethod
    def get_column_names(cls):
        """returns a list of column names (string)"""
        if cls.column_names is None:
            cls.column_names = [c.name for c in cls.get_columns()]
        return cls.column_names

    @classmethod
    def is_valid_dict(cls,value_dict):
        """returns True if the dictionary is valid contain keys that are valid column names,False otherwise"""
        for k in value_dict.keys():
            if k not in cls.get_column_names():
                return False
        return True

    @classmethod
    def is_full_dict(cls, value_dict):
        """returns True if the dictionary contain keys that matches all the columns of a table, False otherwise"""
        return set(value_dict.keys()) == set(cls.get_column_names())

    # String formatting functions

    @staticmethod
    def key_string(value_dict):
        """returns a string 'key_1,key_2,..key_n' from the keys in dict"""
        return reduce((lambda x, y: str(x)+','+str(y)), value_dict.keys())

    @classmethod
    def all_column_string(cls):
        """
        returns a string of all the column names of a table in the format 'column1,column2,...columnN'
        """
        return reduce((lambda x, y:str(x)+','+str(y)),cls.column_names)

    @classmethod
    def key_value_string(cls,value_dict,separator):
        """
        returns a string 'key_1=value_1,key_2=value_2,..,key_n=value_n' from the items in dict
        values are parse through the wrapping function defined in the column types
        separator = 'AND'
        e.g key_1= 'name' AND value_1 = 'bob' AND column type = CHAR
        returns "name='bob'"
        Note: assumes value_dict have valid column as keys
        """
        string = ""
        for column in cls.column_list:
            if column.name in value_dict.keys():
                value = column.wrap_value(value_dict[column.name])
                string += "{}={} {} ".format(column.name,value,separator)

        if string[-len(separator)-1:-1]== separator:
            string = string[:-len(separator)-1]

        return string


    @classmethod
    def key_value_tuple(cls,value_dict):
        """
        returns a tuple of 2 strings (k,v)
        where k is the keys of the dictionary in the format 'key1,key2,..,keyN'
        and v are the values of the corresponding keys formatted as 'value1,value2,...,valueN'
        the values are being parsed through their corresponding column wrapper function wrap_value()
        """
        keys = []
        values = []
        for column in cls.column_list:
            if column.name in value_dict.keys():
                values.append(column.wrap_value(value_dict[column.name]))
                keys.append(column.name)

        column_string = reduce(lambda x,y: str(x)+','+str(y),keys)
        value_string = reduce(lambda x,y: str(x)+','+str(y),values)
        return column_string,value_string

    # Database Methods ##############################################################################################

    @classmethod
    def get_entries(cls, column_list=None, cond_dict=None, max_rows=5, row_numbers=False):
        """
        :param column_list: list of column names to select in query. If None, select all columns defined in class
        :param cond_dict: dictionary that specifies the equals condition of the sql query (e.g key=value)
        :param max_rows: maximum number of rows to be returned. Default max_rows=5. If None, return all rows
        :param row_numbers: boolean
        :return:(tuple of column names, tuple of query results) if row_numbers is False
        ,otherwise the row count of the query e.g 5

        e.g
        users.get_entries(column_list = ['display_name','email'],
                            cond_dict = {'admin':1}
                            max_rows=None
                            )
        is equivalent to
        SELECT display_name,email FROM users WHERE admin=1
        """
        # prep select statement
        if column_list is not None:
            column_dict = {c: '' for c in column_list}
            if not cls.is_valid_dict(column_dict):
                raise InvalidColumnNameException()
        else:
            column_list = cls.get_column_names()
        column_list = tuple(column_list)
        column_string = reduce(lambda x, y: str(x) + ',' + str(y), column_list)
        select_string = cls.select_sql.format(column_string, cls.get_table_name())

        # prep conditional statement
        if cond_dict is not None:
            if not cls.is_valid_dict(cond_dict):
                raise InvalidColumnNameException()
            cond_string = cls.cond_sql.format(cls.key_value_string(cond_dict, 'AND'))
        else:
            cond_string = ''

        query = select_string + cond_string
        #print(query)

        # execute sql statement
        cursor = connection.cursor()
        cursor.execute(query)
        if row_numbers:
            return cursor.rowcount
        else:
            if max_rows is None:
                return column_list,cursor.fetchall()
            else:
                if cursor.rowcount == 0:
                    return column_list,tuple()
                else:
                    return column_list, cursor.fetchmany(min(cursor.rowcount, max_rows))

    @classmethod
    def get_entries_dictionary(cls, column_list=None, cond_dict=None, max_rows=5, row_numbers=False):
        """
        :param column_list: list of column names to select in sql statement. If None, select all columns defined in class
        :param cond_dict: dictionary that specifies the equals condition of the sql query (e.g key=value)
        :param max_rows: maximum number of rows to be returned. Default max_rows=5. If None, return all rows
        :param row_numbers: boolean
        :return: list of dictionaries with column name as key if row_numbers is False
        ,otherwise the row count of the query e.g 5
        """
        entries = cls.get_entries(column_list, cond_dict, max_rows, row_numbers)
        output = []
        
        if row_numbers == True:
            return cls.get_entries(column_list, cond_dict, max_rows, row_numbers)
        
        if max_rows == 1:
            d = {}
            for i in range(len(entries[0])):
                d[entries[0][i]] = entries[1][0][i]
            return d
        
        for rows in entries[1]:
            d = {}
            for i in range(len(entries[0])):
                d[entries[0][i]] = rows[i]
            output.append(d)
        return output

    @classmethod
    def check_exists(cls,cond_dict):
        """
        :param cond_dict: a dictionary {column:column_value} to be searched in sql query
        :return: True if 1 or more row is returned from the query, False otherwise
        e.g
        cond_dict = {'name':'bob','age':23}
        check_exists will perform the query
        SELECT * FROM table WHERE name='bob' AND age=23
        if 1 or more rows are returned from the query, function will return True
        """
        result = cls.get_entries(cond_dict=cond_dict,row_numbers=True)
        if result == 0:
            return False
        return True

    @classmethod
    def insert_new_entry(cls,value_dict):
        """
        :param value_dict: dictionary containing values to add
        """
        # check validity of keys
        if not cls.is_valid_dict(value_dict):
            raise InvalidColumnNameException()

        # check if values fulfils unique constraints
        unique_cols = [column for column in cls.get_unique_columns() if column.name in value_dict.keys()]

        if len(unique_cols)>0:
            for column in unique_cols:
                key,value = column.name,value_dict[column.name]
                if cls.check_exists({key:value}):
                    raise UniqueConstraintException('{}={} is not unique'.format(key,value))

        # check if values for not_null columns present
        not_null_cols = cls.get_not_null_columns()
        if len(not_null_cols)>0:
            for col in not_null_cols:
                if col.name not in value_dict.keys():
                    raise NotNullException('Value for {} not specified'.format(col.name))

        columns,values = cls.key_value_tuple(value_dict)
        statement = cls.insert_sql.format(cls.get_table_name(),columns,'('+values+')')
        #print(statement)

        # execute sql
        cursor = connection.cursor()
        cursor.execute(statement)

        # @TODO what should this return? insert result or nothing


    @classmethod
    def delete_entries(cls,cond_dict):
        """
        Deletes entries that fulfil the conditions specified in cond_dict.
        Does not allow no conditions, to prevent deletion of entire table
        :param cond_dict:
        :return:
        """
        if not cls.is_valid_dict(cond_dict):
            raise InvalidColumnNameException()
        cond_string = cls.cond_sql.format(cls.key_value_string(cond_dict, 'AND'))
        statement = cls.delete_sql.format(cls.get_table_name()) + cond_string
        #print(statement)

        # execute sql
        cursor = connection.cursor()
        cursor.execute(statement)


    @classmethod
    def update_entries(cls,value_dict,cond_dict=None):
        if not cls.is_valid_dict(value_dict):
            raise InvalidColumnNameException()

        if cond_dict is not None:
            if not cls.is_valid_dict(cond_dict):
                raise InvalidColumnNameException()
            cond_string = cls.cond_sql.format(cls.key_value_string(cond_dict, 'AND'))
        else:
            cond_string = ''

        # check if values fulfils unique constraints
        unique_dict = {}
        for column in cls.column_list:
            if column.unique and column.name in value_dict.keys():
                unique_dict[column.name] = value_dict[column.name]
        if unique_dict != {}:
            # check for multiple entries
            if cls.get_entries(cond_dict=cond_dict,row_numbers=True)>1:
                raise UniqueConstraintException('Trying to set one unique value for multiple rows')

            # check if each value is unique
            for key, value in unique_dict.items():
                if cls.check_exists({key: value}):
                    raise UniqueConstraintException('{}={} already exists'.format(key, value))

        set_string = cls.key_value_string(value_dict, ',')
        update_statement = cls.update_sql.format(cls.get_table_name(),set_string) + cond_string
        #print(update_statement)

        cursor = connection.cursor()
        cursor.execute(update_statement)