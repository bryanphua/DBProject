from datetime import datetime

class Column():
    """
    name should be the column name in the existing table
    type can only be int,float,datetime and char (for now)
    """
    valid_types = ['int', 'float', 'datetime', 'char']

    def __init__(self, name, col_type, not_null=False, unique=False):
        if col_type not in Column.valid_types:
            raise TypeError("invalid column types")
        if type(unique) is not bool:
            raise TypeError('unique must be a boolean')
        if type(not_null) is not bool:
            raise TypeError('not_null must be a boolean')
        self.name = str(name)
        self.col_type = col_type
        self.unique = unique
        self.not_null = not_null

    def wrap_value(self, value):
        """return the value as a string to be palced into sql statement"""
        if self.col_type == 'int':
            return str(int(value))

        elif self.col_type == 'float':
            return str(float(value))

        elif self.col_type == 'char':
            return "'{}'".format(value)

        elif self.col_type == 'datetime':
            if type(value) != datetime:
                raise TypeError('datetime column needs to be a datetime object')
            return "DATE('{}')".format(value.strftime('%Y-%m-%d %H:%M:%S'))


    def unwrap_value(self, value):
        """unwrap it from database query result to python type"""
        # @TODO isit even required? how is datetime returned in python
        pass

    def __str__(self):
        return 'Column-Object<\'{}\'>'.format(self.name)

    def __repr__(self):
        return self.__str__()