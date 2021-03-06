from language2test_api.extensions import db, ma
from sqlalchemy import func
from flask import json, request, Response
from language2test_api.models.test_category import TestCategory, TestCategorySchema
from sqlalchemy.sql import text

class BaseProvider():
    def generate_id(self, offset=0, field=None):
        max_id = db.session.query(func.max(field)).scalar()
        max_id = max_id + 1 if max_id else 1
        return max_id + offset

    def get_count(self, field):
        count = db.session.query(field.id).count()
        dict = {"count": count}
        response = Response(json.dumps(dict), 200, mimetype="application/json")
        return response

    def query_all(self, field):
        query = field.query
        limit = request.args.get('limit')
        offset = request.args.get('offset')

        #default values
        column = 'id'
        order = 'asc'

        if 'column' in request.args:
            column = request.args.get('column')

        if 'order' in request.args:
            order = request.args.get('order')

        p = column + ' ' + order

        #query = query.order_by(text("id desc"))
        query = query.order_by(text(p))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = query.all()

        return result

    def query_all_by_subquery(self, query):
        limit = request.args.get('limit')
        offset = request.args.get('offset')

        #default values
        column = 'id'
        order = 'asc'

        if 'column' in request.args:
            column = request.args.get('column')

        if 'order' in request.args:
            order = request.args.get('order')

        p = column + ' ' + order
        query = query.order_by(text(p))

        #query = query.order_by(text("id desc"))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        result = query.all()
        return result


    def add_category_to_data(self, data):
        data_test_category = data.get('test_category')
        if data_test_category:
            data['test_category_id'] = data_test_category['id']
        return data

    def fill_out_name_based_on_display(self, data):
        data['name'] = data.get('display') if data.get('name') is None else data.get('name')
        return data