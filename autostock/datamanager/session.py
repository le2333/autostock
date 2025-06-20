from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session

from autostock.database.engine import engine


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    提供一个数据库会话的上下文管理器。

    该函数确保会话在使用后能够被正确地提交事务和关闭。
    如果在使用过程中发生任何异常，事务将被回滚。

    用法:
        with get_session() as session:
            # 在这里执行数据库操作
            session.add(some_object)
            ...
    """
    db_session = Session(engine)
    try:
        yield db_session
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    finally:
        db_session.close()
