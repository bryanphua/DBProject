from ModelClass import Model,Column

class auth_user(Model):
    id = Column('id','int',unique=True)
    username = Column('username','char',unique=True)
    password = Column('password','char',not_null=True)
    email = Column('email','char',unique=True,not_null=True)
    first_name = Column('first_name','char', not_null=True)
    last_name = Column('last_name','char', not_null=False)
    is_staff = Column('is_staff','int', not_null=True)

class dataset_list(Model):
    id = Column('id','int',unique=True)
    name = Column('name','char',not_null=True)
    creator_user_id = Column('creator_user_id','int',not_null=True)
    endorsed_by = Column('endorsed_by','char',not_null=True)
    description = Column('description','char')
    genre = Column('genre','char',not_null=True)

class user_dataset_following(Model):
    user_id = Column('user_id','int',not_null=True)
    dataset_id = Column('dataset_id','int',not_null=True)
    datetime_followed = Column('datetime_followed','datetime') # not_null=False as default=current_timestamp
    
class comments(Model):
    id = Column('id', 'int', unique=True)
    created = Column('created', 'datetime')
    user_id = Column('user_id', 'int', not_null=True)
    content = Column('content', 'char', not_null=True)
    dataset_id = Column('dataset_id', 'int', not_null=True)
    last_modified = Column('last_modified', 'datetime')
    
class dataset_rating(Model):
    user_id = Column('user_id', 'int', not_null=True)
    dataset_id = Column('dataset_id', 'int', not_null=True)
    rating = Column('rating', 'int', not_null=True)
    
class comments_vote(Model):
    user_id = Column('user_id', 'int', not_null=True)
    comment_id = Column('comment_id', 'int', not_null=True)
    vote = Column('vote', 'int', not_null=True)
    last_modified = Column('last_modified', 'datetime')
