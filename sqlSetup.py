from sqlalchemy import create_engine, BigInteger, Column,  Text, VARCHAR, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import asyncpg
Base = declarative_base()

class Channels(Base):
    __tablename__ = "ChannelList"

    channel_id = Column("Channel ID", VARCHAR, primary_key=True)
    channel_name = Column("Channel Name", Text)
    channel_link = Column("Channel URL", Text)
    channel_desription = Column("Channel Description", Text)
    channel_logo = Column("Channel Logo", Text, nullable=True, default=None)
    created_at = Column(DateTime, nullable=False)
    

class Config(Base):
    __tablename__ = "Config"
    guild_id = Column("Guild ID", BigInteger, primary_key=True)
    guild_name = Column("Guild Name", Text)
    guild_channel = Column("Guild Channel ID", BigInteger)

# Create the engine
engine = create_async_engine('postgresql+asyncpg://postgres:rootfly@localhost:5432/QualityYouTubeBot')

# Create a session to manage the connection to the database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Create the tables in the database
async def create_db(engine=engine, Base=Base):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == "__main__":
    from asyncio import run

    run(create_db(engine, Base))
