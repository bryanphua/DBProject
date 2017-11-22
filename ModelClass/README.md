# Model Class Documentation
## Defining a Model/Table Class

We will first be defining a class to represent an existing table in our database and store the metadata of that table.
The Column object is used to store the data type and constraints of a particular column

Column(name, col_type, not_null=False, unique=False)
- name(string): column name in database table
- col_type(string): column type, current supported types are ['int', 'float', 'datetime', 'char']
- not_null(bool): if True, column holds a not null constraint
- unique(bool): if True, column holds a unique constraint

```
from ModelClass import Model

class users(Model):
    id = Column('id','int',unique=True)
    password = Column('password','char',not_null=True)
    email = Column('email','char',unique=True,not_null=True)
    display_name = Column('display_name','char', not_null=True)
    admin = Column('admin','int', not_null=True)
```

## Methods
* **get_entries(column_list=None, cond_dict=None, max_rows=5, row_numbers=False):**
    * column_list(list/None): list of column names to select in query. If None, select all columns defined in class
    * cond_dict(dict/None): dictionary that specifies the equals condition of the sql query (e.g key=value)
    * max_rows(int/None): maximum number of rows to be returned. Default max_rows=5. If None, return all rows
    * row_numbers: boolean
    * return(tuple): tuple(tuple of column names, tuple of query results) if row_numbers=False
    * return(int): row count of the query if row_numbers=True

* **check_exists(cond_dict):**
    * cond_dict(dict/None): a dictionary {column:column_value} to be searched in sql query
    * return(bool): True if 1 or more row is returned from the query, False otherwise

* **insert_new_entry(value_dict)**
    * value_dict(dict): {column:column_value} of new entry
    * return: None

* **delete_entries(cond_dict)**
    * cond_dict(dict): condition {column:column_value} to delete entries

* **update_entries(value_dict,cond_dict=None)**
    * value_dict(dict): {column:column_value} to set
    * cond_dict(dict): condition {column:column_value} to update entries
    *return: None

## Examples
#### Getting Entries

```
>> users.get_entries(column_list = ['display_name','email'],
                     cond_dict = {'admin':1}
                     max_rows=2
                     )
```
is equivalent to
```SELECT display_name,email FROM users WHERE admin=1```
 and returns a nested tuple
in the form ( (column names), (query results) ) with a maximum of 2 rows
```
>> (('display_name','email'),(('bob','bob@email.com),('Sally','sally@email.com')))
```

#### Getting number of rows
Find out the number of admins in users table (e.g 5 admins)

```
>> users.get_entries(cond_dict = {'admin':1}
                     row_numbers=True
                     )
>> 5
```

#### Checking if exists
Check if there are any users with display_name='Bob' and who is an admin
```
>> users.check_exists(cond_dict={'display_name':'Bob',
                                 'admin':1
                                 })
>> True
```

#### Inserting a single entry
```
>> users.insert_new_entry({'display_name':'Bob',
                           'email':'bob@sutd.edu.sg',
                           'admin':0,
                           'password':'secretpw')
```
is equivalent to
``` INSERT INTO users (display_name,email,admin,password) VALUES ('Bob','bob@sutd.edu.sg',0,'secretpw')```

#### Updating Entry/Entries
```
>> users.update_entries({'admin':0},cond_dict={'display_name':'tan'})
```
is equivalent to
```UPDATE users SET admin=0 WHERE display_name='tan'```

#### Deleting Entries
```
users.delete_entries({'admin':0})
```
is equivalent to
```DELETE FROM users WHERE admin=0```

## Exceptions
- **InvalidColumnNameException**
    - raised when invalid keys for table, most likely fault of the programmer

- **UniqueConstraintException**
    - raised when attempt to insert,update an entry that fails unique constraints

- **NotNullException**
    - raised when attempt to insert an entry without value for a column that has not null constraint

import these exceptions and catch them by
```
from ModelClass import InvalidColumnNameException,
                       UniqueConstraintException,
                       NotNullException

try:
    users.insert_new_entry({'display_name':'Bob',
                           'email':'bob@sutd.edu.sg',
                           'admin':0,
                           'password':'secretpw')

except UniqueConstraintException:
    # do something
    pass

except:
    # catch other exceptions like db connection issues
    pass
```


## :collision::collision: **Important** :collision::collision:

- Validity of foreign keys is NOT checked
    (You have to check if it exists first using Model functions)
- Type checking for column values is NOT done
- Does not handle other unexpected database errors for example
    - DB connection issues
    - Other constraints like inequality constraints example age>0
        and foreign key constraints as mentioned

- primary key ids should be unique but not_null=False if it is default AUTO_INCREMENT
- foreign keys should be not_null=False

