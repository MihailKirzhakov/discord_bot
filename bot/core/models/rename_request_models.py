from core import Base, int_uniq, str_uniq, strpk
from sqlalchemy.orm import Mapped


class RenameRequestModel(Base):

    old_nickname: Mapped[strpk]
    new_nickname: Mapped[str_uniq]
    user_id: Mapped[int_uniq]
