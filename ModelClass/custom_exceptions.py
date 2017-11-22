class InvalidColumnNameException(Exception):
    """raised when invalid keys for table, most likely fault of the programmer"""
    pass

class UniqueConstraintException(Exception):
    """raised when attempt to insert an entry that fails unique constraints"""
    pass

class NotNullException(Exception):
    """raised when one attempts to insert entry without a value for a not null Column"""
    pass