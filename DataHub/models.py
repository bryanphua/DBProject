from ModelClass.ModelClass import Model,Column

class users(Model):
    id = Column('id','int',unique=True)
    password = Column('password','char')
    email = Column('email','char',unique=True)
    display_name = Column('display_name','char')
    admin = Column('admin','int')