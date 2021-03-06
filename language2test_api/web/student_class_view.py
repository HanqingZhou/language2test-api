from flask import request, jsonify, url_for, Blueprint, send_file
from flask import json, jsonify, Response, blueprints
from language2test_api.models.student_class import StudentClass, StudentClassSchema
from language2test_api.models.user import User, UserSchema
from language2test_api.models.user_field import UserField
from language2test_api.extensions import db, ma
from language2test_api.web.common_view import language2test_bp
from language2test_api.decorators.crossorigin import crossdomain
from language2test_api.decorators.authentication import authentication
from language2test_api.decorators.authorization import authorization
from language2test_api.providers.student_class_provider import StudentClassProvider

import pandas as pd
from io import BytesIO

student_class_schema = StudentClassSchema(many=False)
student_class_schema_many = StudentClassSchema(many=True)

provider = StudentClassProvider()

@language2test_bp.route("/student_classes/count", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-student-class'])
def get_student_classes_count():
    return provider.get_count(StudentClass)

@language2test_bp.route("/student_classes", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['read-student-class'])
def get_student_class():
    id = request.args.get('id')
    if id:
        properties = StudentClass.query.filter_by(id=int(id)).first()
        result = student_class_schema.dump(properties)
        return jsonify(result)

    name = request.args.get('name')
    if name:
        properties = StudentClass.query.filter_by(name=name)
        result = student_class_schema.dump(properties)
        return jsonify(result)

    display = request.args.get('display')
    if display:
        properties = StudentClass.query.filter(StudentClass.display == display).first()
        result = student_class_schema.dump(properties)
        return jsonify(result)

    properties = provider.query_all(StudentClass)
    result = student_class_schema_many.dump(properties)
    return jsonify(result)

@language2test_bp.route("/student_classes", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['create-student-class'])
def add_student_class():
    try:
        data = request.get_json()
        student_class = provider.add(data)
        db.session.commit()
        result = student_class_schema.dump(student_class)
        response = jsonify(result)
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/student_classes", methods=['PUT'])
@crossdomain(origin='*')
@authentication
@authorization(['update-student-class'])
def update_student_class():
    try:
        data = request.get_json()
        student_class = StudentClass.query.filter_by(id=data.get('id')).first()
        if not student_class:
            student_class = StudentClass.query.filter_by(name=data.get('name')).first()
        if student_class:
            provider.update(data, student_class)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/student_classes", methods=['DELETE'])
@crossdomain(origin='*')
@authentication
@authorization(['delete-student-class'])
def delete_student_class():
    try:
        data = request.get_json()
        test = StudentClass.query.filter_by(id=data.get('id')).first()
        if not test:
            test = StudentClass.query.filter_by(name=data.get('name')).first()
        if test:
            db.session.delete(test)
            db.session.commit()
            response = Response(json.dumps(data), 200, mimetype="application/json")
        else:
            response = Response(json.dumps(data), 404, mimetype="application/json")
    except Exception as e:
        error = { "exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")

    return response

@language2test_bp.route("/student_classes/export", methods=['GET'])
@crossdomain(origin='*')
@authentication
@authorization(['export-student-class'])
def export_student_class():
    specific_id = request.args.get('id')
    if specific_id is None:
        try:
            records = []
            studentClasses = StudentClass.query.all()
            for c in studentClasses:
                records.append({
                    "id": c.id,
                    "name": c.name,
                    "instructor": c.instructor.name})

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(records).to_excel(writer,
                                               sheet_name="Student Class summary",
                                               index=False)
                workbook = writer.book
                worksheet = writer.sheets['Student Class summary']
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 25, format)
                worksheet.set_column('C:C', 20, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                             attachment_filename='Student Class Summary' + '.xlsx',
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

    if specific_id is not None:
        try:
            name = request.args.get('name')
            if name is None:
                sc_id = request.args.get('id')
                sc = StudentClass.query.filter_by(id=sc_id).first()
                result = student_class_schema.dump(sc)
                name = sc.name
            else:
                sc = StudentClass.query.filter_by(name=name).first()
                result = student_class_schema.dump(sc)
            student_classes = result['student_student_class']
            student_class_infos = []
            for student_class in student_classes:
                if student_class['fields'] == []:
                    student_id = ''
                    first_language = ''
                    email = ''
                    phone = ''
                    address = ''
                    education = ''
                else:
                    for info in student_class['fields']:
                        if info['name'] == 'student_id':
                            student_id = info['value']
                            break
                        else:
                            student_id = ''
                    for info in student_class['fields']:
                        if info['name'] == 'first_language':
                            first_language = info['value']
                            break
                        else:
                            first_language = ''
                    for info in student_class['fields']:
                        if info['name'] == 'email':
                            email = info['value']
                            break
                        else:
                            email = ''
                    for info in student_class['fields']:
                        if info['name'] == 'phone':
                            phone = info['value']
                            break
                        else:
                            phone = ''
                    for info in student_class['fields']:
                        if info['name'] == 'address':
                            address = info['value']
                            break
                        else:
                            address = ''
                    for info in student_class['fields']:
                        if info['name'] == 'education':
                            education = info['value']
                            break
                        else:
                            education = ''
                student_class_infos.append({
                    " Class Id": result['id'],
                    "Class Name": result['name'],
                    "Instructor": result['instructor']['name'],
                    "Student Id": student_class['id'],
                    "Student Username": student_class['name'],
                    "First Name": student_class['first_name'],
                    "Last Name": student_class['last_name'],
                    "Student ID": student_id,
                    "First Language": first_language,
                    "Email": email,
                    "Phone": phone,
                    "Address": address,
                    "Education": education
                    })

            output = BytesIO()

            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(student_class_infos).to_excel(writer,
                                                    sheet_name="{} summary".format(name), index=False)
                workbook = writer.book
                worksheet = writer.sheets["{} summary".format(name)]
                format = workbook.add_format()
                format.set_align('center')
                format.set_align('vcenter')
                worksheet.set_column('A:A', 13, format)
                worksheet.set_column('B:B', 25, format)
                worksheet.set_column('C:C', 20, format)
                worksheet.set_column('D:D', 20, format)
                worksheet.set_column('E:E', 20, format)
                worksheet.set_column('F:G', 20, format)
                worksheet.set_column('H:H', 20, format)
                worksheet.set_column('I:I', 20, format)
                worksheet.set_column('J:J', 28, format)
                worksheet.set_column('K:M', 20, format)
                writer.save()

            output.seek(0)
            return send_file(output,
                                attachment_filename= name + '.xlsx',
                                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                as_attachment=True, cache_timeout=-1)
        except Exception as e:
            error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
            response = Response(json.dumps(error), 404, mimetype="application/json")
            return response

@language2test_bp.route("/student_classes/upload", methods=['POST'])
@crossdomain(origin='*')
@authentication
@authorization(['import-student-class'])
def upload_student_class():
    raw_data = request.get_data()
    data = pd.read_excel(raw_data, engine="openpyxl")
    try:
        scs = {}
        for _, row in data.iterrows():
            d = dict(row)
            exist_sc = StudentClass.query.filter_by(name=d["class_name"]).first()
            sc = scs.get(d["class_name"])
            if sc is None and exist_sc is None:
                sc_data = {}
                sc_data["name"] = d["class_name"]
                sc_data["display"] = "-".join(d["class_name"].split("_"))
                sc_data["id"] = provider.generate_id(field=StudentClass.id)
                instructor = User.query.filter_by(name=d["instructor_name"]).first()
                sc = StudentClass(sc_data)
                if "Instructor" in map(lambda e: e.name, instructor.roles):
                    sc.instructor_id = instructor.id
                    sc.instructor = instructor
                scs[d["class_name"]] = sc
            user = User.query.filter_by(name=d["student_name"]).first()
            if user is not None:
                marked = {}
                for field in user.fields:
                    if field.name == "student_id":
                        marked["student_id"] = True
                        field.value = d["student_id"]
                    elif field.name == "first_language":
                        marked["first_language"] = True
                        field.value = d["first_language"]
                    elif field.name == "email":
                        marked["email"] = True
                        field.value = d["email"]
                    elif field.name == "education":
                        marked["education"] = True
                        field.value = d["education"]
                if not marked.get("student_id", False):
                    user.fields.append(UserField(
                        {"name": "student_id", "type": "student_id", "value": d["student_id"], "user_id": user.id}))
                if not marked.get("first_language", False):
                    user.fields.append(UserField(
                        {"name": "first_language", "type": "first_language",
                         "value": d["first_language"], "user_id": user.id}))
                if not marked.get("email", False):
                    user.fields.append(UserField(
                        {"name": "email", "type": "email", "value": d["email"], "user_id": user.id}))
                if not marked.get("education", False):
                    user.fields.append(UserField(
                        {"name": "education", "type": "education", "value": d["education"], "user_id": user.id}))
            if "Test Taker" in map(lambda e: e.name, user.roles):
                if exist_sc is not None:
                    if user not in exist_sc.student_student_class:
                        exist_sc.student_student_class.append(user)
                else:
                    if user not in scs[d["class_name"]].student_student_class:
                        scs[d["class_name"]].student_student_class.append(user)

            db.session.add_all(scs.values())
            db.session.commit()
        response = Response(json.dumps({"success": True}), 200, mimetype="application/json")
    except Exception as e:
        error = {"exception": str(e), "message": "Exception has occurred. Check the format of the request."}
        response = Response(json.dumps(error), 500, mimetype="application/json")
    return response