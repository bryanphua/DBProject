from ModelClass.ModelClass import Model,Column

class auth_user(Model):
    id = Column('id','int',unique=True)
    password = Column('password','char')
    email = Column('email','char',unique=True)
    username = Column('username','char')
    is_staff = Column('is_staff','int')
