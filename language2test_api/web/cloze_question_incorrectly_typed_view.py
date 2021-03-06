from flask import request
from flask import json, jsonify, Response, blueprints
from language2test_api.models.cloze_question_incorrectly_typed import ClozeQuestionIncorrectlyTyped, ClozeQuestionIncorrectlyTypedSchema
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.cloze_provider import ClozeProvider
from language2test_api.providers.base_provider import BaseProvider

cloze_question_incorrectly_typed_schema = ClozeQuestionIncorrectlyTypedSchema(many=False)
cloze_question_incorrectly_typed_schema_many = ClozeQuestionIncorrectlyTypedSchema(many=True)

provider = BaseProvider()
cloze_provider = ClozeProvider()

@language2test_bp.route("/cloze_question_incorrectly_typed/count/<cloze_question_id>", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def get_cloze_question_incorrectly_typed_count_by_cloze_question_id(cloze_question_id):
    return cloze_provider.get_count(ClozeQuestionIncorrectlyTyped, cloze_question_id)

@language2test_bp.route("/cloze_question_incorrectly_typed/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def get_cloze_question_incorrectly_typed_count():
    return provider.get_count(ClozeQuestionIncorrectlyTyped)

@language2test_bp.route("/cloze_question_incorrectly_typed", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def get_cloze_question_incorrectly_typed():
    id = request.args.get('id')
    if id:
        properties = ClozeQuestionIncorrectlyTyped.query.filter_by(id=id).first()
        result = cloze_question_incorrectly_typed_schema.dump(properties)
        return jsonify(result)

    text = request.args.get('text')
    if text:
        properties = ClozeQuestionIncorrectlyTyped.query.filter_by(text=text).first()
        result = cloze_question_incorrectly_typed_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(ClozeQuestionIncorrectlyTyped)
    result = cloze_question_incorrectly_typed_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/cloze_question_incorrectly_typed/<cloze_question_id>", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def get_cloze_question_incorrectly_typed_by_cloze_question_id(cloze_question_id):
    id = request.args.get('id')
    if id:
        properties = ClozeQuestionIncorrectlyTyped.query.filter_by(id=id).first()
        result = cloze_question_incorrectly_typed_schema.dump(properties)
        return jsonify(result)

    text = request.args.get('text')
    if text:
        properties = ClozeQuestionIncorrectlyTyped.query.filter_by(text=text).first()
        result = cloze_question_incorrectly_typed_schema.dump(properties)
        return jsonify(result)

    properties = cloze_provider.query_all(ClozeQuestionIncorrectlyTyped, cloze_question_id)
    result = cloze_question_incorrectly_typed_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/cloze_question_incorrectly_typed", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def add_cloze_question_incorrectly_typed():
    try:
        data = request.get_json()
        data['id'] = provider.generate_id(field=ClozeQuestionIncorrectlyTyped.id)
        cloze_question_incorrectly_typed = ClozeQuestionIncorrectlyTyped(data)
        db.session.add(cloze_question_incorrectly_typed)
        db.session.commit()
        result = cloze_question_incorrectly_typed_schema.dump(cloze_question_incorrectly_typed)
        response = jsonify(result)
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/cloze_question_incorrectly_typed", methods=['PUT'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def update_cloze_question_incorrectly_typed():
    try:
        data = request.get_json()
        cloze_question_incorrectly_typed = ClozeQuestionIncorrectlyTyped.query.filter_by(id=data.get('id')).first()
        if not cloze_question_incorrectly_typed:
            cloze_question_incorrectly_typed = ClozeQuestionIncorrectlyTyped.query.filter_by(text=data.get('text')).first()
        if cloze_question_incorrectly_typed:
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/cloze_question_incorrectly_typed", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
@authorization(['create-cloze'])
def delete_cloze_question_incorrectly_typed():
    try:
        data = request.get_json()
        cloze_question_incorrectly_typed = ClozeQuestionIncorrectlyTyped.query.filter_by(id=data.get('id')).first()
        if not cloze_question_incorrectly_typed:
            cloze_question_incorrectly_typed = ClozeQuestionIncorrectlyTyped.query.filter_by(text=data.get('text')).first()
        if cloze_question_incorrectly_typed:
            db.session.delete(cloze_question_incorrectly_typed)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response
