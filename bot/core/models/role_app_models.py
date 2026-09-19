from core import Base, int_uniq, str_uniq, strpk
from sqlalchemy.orm import Mapped


class RoleApplicationData(Base):

    nickname: Mapped[strpk]
    user_id: Mapped[int_uniq]
    acc_btn_cstm_id: Mapped[str_uniq]
    den_btn_cstm_id: Mapped[str_uniq]
