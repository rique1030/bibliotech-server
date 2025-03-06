from sqlalchemy import Row, RowMapping, and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.inspection import inspect
from Components.tables.models import User


class QueryHelper:

    def __init__(self, session: async_sessionmaker[AsyncSession]):
        self.session = session

    async def get_paged_data(self, session, model, data, query=None):
        page = data.get("page", 0)
        per_page = data.get("per_page", 15)
        filters = data.get("filters", None)
        order_by = data.get("order_by", None)
        order_direction = data.get("order_direction", "asc")

        query = await self.apply_filters(query, filters, model)

        query = await self.apply_ordering(query, model, order_by,
                                          order_direction)

        total_count = await self.get_total_count(session, query)

        query = await self.apply_pagination(query, page, per_page)
        result = await session.execute(query)
        if len(result.keys()) == 1:
            rows = result.scalars().all(
            )  # Returns a list of single-column values
        else:
            rows = result.mappings().all()
        return {
            "data": await self.model_to_dict(rows),
            "total_count": total_count
        }

    async def apply_filters(self, query, filters, model):
        if filters:
            for column, value in filters.items():
                found = False
                if isinstance(model, list):
                    for m in model:
                        if hasattr(m, column):
                            query = query.where(
                                getattr(m, column).like(f"%{value}%"))
                            found = True
                            break
                else:
                    if hasattr(model, column):
                        query = query.where(
                            getattr(model, column).like(f"%{value}%"))
                        found = True

                if not found:
                    if column == "full_name":
                        print("full_name")
                        query = query.where(
                            and_(User.first_name.like(f"%{value}%"),
                                 User.last_name.like(f"%{value}%")))
                        found = True
                        return query
                    print(f"Column {column} not found in model {model}")
        return query

    async def apply_ordering(self,
                             query,
                             model,
                             order_column=None,
                             order_direction="asc"):
        if not order_column:
            if isinstance(model, list):
                order_column = getattr(model[0], "id")
            else:
                order_column = getattr(model, "id")
        if order_direction == "desc":
            return query.order_by(desc(order_column))
        return query.order_by(asc(order_column))

    async def get_total_count(self, session, query):
        # if isinstance(model, list):
        #     model = model[0]
        count_query = select(func.count()).select_from(query)
        result = await session.execute(count_query)
        return result.scalar()

    async def apply_pagination(self, query, page, per_page):
        return query.offset(page * per_page).limit(per_page)

    """Converts a SQLAlchemy model to a dictionary"""

    async def model_to_dict(self, rows):
        if isinstance(rows, list):
            return [await self.model_to_dict(m) for m in rows]
        elif isinstance(rows, Row):
            return {column: rows[column] for column in rows.keys()}
        elif isinstance(rows, RowMapping):
            return {key: value for key, value in rows.items()}
        return {
            c.key: getattr(rows, c.key)
            for c in inspect(rows).mapper.column_attrs
        }
