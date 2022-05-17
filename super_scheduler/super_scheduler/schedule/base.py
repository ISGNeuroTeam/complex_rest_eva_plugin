from pydantic import BaseModel as BaseModelFormat


class BaseFormat(BaseModelFormat):
    """
    Example:
        id: int
        name = 'John Doe'
        signup_ts: Optional[datetime] = None
        friends: List[int] = []
    """
    pass


class BaseSchedule:

    def __init__(self):
        pass

    def create(self, kwargs: BaseFormat):
        raise NotImplementedError



