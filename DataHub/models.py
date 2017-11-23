from ModelClass.ModelClass import Model,Column

class auth_user(Model):
    id = Column('id','int',unique=True)
    password = Column('password','char', not_null=True)
    email = Column('email','char',unique=True, not_null=True)
    username = Column('username','char', unique=True, not_null=True)
    first_name = Column('first_name', 'char', not_null=True)
    is_staff = Column('is_staff','int')

class dataset_list(Model):
    id = Column('id', 'int', unique=True)
    name = Column('name', 'char')
    creator_user_id = Column('creator_user_id', 'int', not_null=True)
    endorsed_by = Column('endorsed_by', 'char', )
