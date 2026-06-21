from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import ForeignKey

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    display_name = Column(String, nullable=False)

    email = Column(String, nullable=False)

    username = Column(String, nullable=False, unique=True)

    password_hash = Column(String, nullable=False)

    watchlists = relationship(
        "Watchlist",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    ticker = Column(
        String,
        nullable=False
    )

    shares = Column(
        Integer,
        nullable=True
    )

    purchase_price = Column(
        Float,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="watchlists"
    )