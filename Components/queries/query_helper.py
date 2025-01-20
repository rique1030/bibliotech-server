# from flask import request
from sqlalchemy import Row, asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect

class QueryHelper:
    def __init__(self, session: Session):
        self.session = session

    def get_paged_data(
            self, model,
            page: int = 0,
            per_page:  int = 15,
            filters: dict = None, 
            order_by: str = "id", 
            order_direction: str = "asc"
            ):
        
        query = self.session.query(model)
        
        # Handle search
        if filters:
            for column, value in filters.items():
                try:
                    query = query.filter(getattr(model, column).like(f"%{value}%"))
                except Exception as e:
                    raise Exception(f"Invalid filter: {e}")
        

        total_count = query.count()

        # Handle ordering
        if order_by:
            try:
                order_column = getattr(model, order_by, model.id)
                if order_direction.lower() == "asc":
                    order_column = asc(order_column)
                elif order_direction.lower() == "desc":
                    order_column = desc(order_column)
                query = query.order_by(order_column)
            except Exception as e:
                raise Exception(f"Invalid order: {order_column}")
            
        # Handle pagination
        offset = page * per_page
        query = query.offset(offset).limit(per_page)
        result = query.all()
        # return { "data": self.model_to_dict(result), "total_count": total_count }
        return { "data": self.model_to_dict(result), "total_count": total_count }
                
    def model_to_dict(self, model):
        if isinstance(model, list):
            return [self.model_to_dict(m) for m in model]
        elif isinstance(model, Row):
            return {column: model[column] for column in model.keys()}  
        return {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}
