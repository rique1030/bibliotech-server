from quart import Quart
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from Components.config import *
from Components.tables.models import Base

class Database:
    def __init__(self, app: Quart, main) -> None:
        self.register_routes(app)
        self.main = main
        self.SQL_CONFIG = None

        if DEPLOYMENT_MODE == DeploymentMode.DEVELOPMENT:
            self.SQL_CONFIG = DEVELOPMENT_CONFIG
        else:
            self.SQL_CONFIG = PRODUCTION_CONFIG

        self.engine = create_async_engine(
            f"mysql+aiomysql://{self.SQL_CONFIG['DB_USER']}:{self.SQL_CONFIG['DB_PASSWORD']}@"
            f"{self.SQL_CONFIG['DB_HOST']}:{self.SQL_CONFIG['DB_PORT']}/{self.SQL_CONFIG['DB_NAME']}",
            pool_size=20,
            max_overflow=10,
            pool_timeout=120,
            pool_recycle=3600,
            pool_pre_ping=False
        )
        
        self.Session = async_sessionmaker(
            bind=self.engine,
            expire_on_commit=False
        )

    def register_routes(self, app: Quart):
        @app.route("/reset_tables", methods=["GET"])
        async def reset_tables():
            if not DEPLOYMENT_MODE == DeploymentMode.DEVELOPMENT:
                return "You can only reset tables in development mode"
            try:
                async with self.engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
                    await conn.run_sync(Base.metadata.create_all)
                    await self.main.populate_tables()
                    return "Tables reset successfully"
            except Exception as e:
                print(f"Error dropping tables: {e}")
                return "Tables reset failed"

    async def init_db(self):
        try:
            from .tables.models import Base
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")

    async def get_session(self):
        async with self.Session() as session:
            yield session

