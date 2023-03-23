import flask
from flask import Flask, request, redirect, url_for , flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from main import assign_digital_signature , check_signature
import os
import sqlite3
import random, string
from PIL import Image
from WMarkStamp import stamp_watermark


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def index():

    return flask.render_template('index.html')


@app.route('/avtore')
def avtors():
    flash('Вы успешно вошли в систему')
    return flask.render_template('team_inf.html')


@app.route('/check_photo', methods=['GET', 'POST'])
def upload_file_check():
    if request.method == 'POST':
        # получаем файл из запроса
        file = request.files['file2']
        if file:
            # создаем безопасное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл в папку uploads на сервере
            file.save('static/photos_check/' + filename)

            return flask.redirect(url_for('check_photo2', filename=filename))

    return flask.render_template('check_photo.html')



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # получаем файл из запроса
        file = request.files['file']
        if file:
            # создаем безопасное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл в папку uploads на сервере
            file.save('static/photos/' + filename)
            return flask.redirect(url_for('uploaded_file', filename=filename))

    return flask.render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    print(f'static/photos/{filename}')

    stamp_watermark(f'static/photos/{filename}', 'static/photos_water_marks/' + filename, random_id)

    signature, public_key = assign_digital_signature(f'static/photos_water_marks/{filename}')


    try:
        connection = sqlite3.connect('static/data/database.db')
        cursor = connection.cursor()
        photo_blob_with_features = open(f'static/photos/{filename}', 'rb').read()

        photo_blob_without_features = photo_blob_with_features[:-len(signature) - len(public_key)]
        cursor.execute(f"INSERT INTO database_hakaton VALUES(?, ?, ?, ?, ?);", (f"{random_id}",
                                                                            f"{public_key}",
                                                                            f"{signature}",
                                                                            f"{photo_blob_without_features}",
                                                                            f"{photo_blob_with_features}"))
        connection.commit()
    except Exception as ex:

        return flask.render_template('error.html')

    return flask.render_template('download.html', filename=filename)


@app.route('/check_photo2/<filename>')
def check_photo2(filename):

    photo_blob = open(f'static/photos_check/{filename}', 'rb').read()

    connection = sqlite3.connect('static/data/database.db')

    cursor = connection.cursor()

    try:
        photo_blob = str(photo_blob)
        without_key_and_signature = photo_blob.split("-----BEGIN PUBLIC KEY-----")[1]
        key = without_key_and_signature.split("-----END PUBLIC KEY-----")[1]
        query = f"SELECT photo_with_added_features FROM database_hakaton WHERE photo_with_added_features = ?"
        cursor.execute(query, (photo_blob, ))
        return flask.render_template('show_check_photo.html', filename=filename)

    except:

        return flask.render_template('photo_not_verifeed.html')



if __name__ == '__main__':
    app.run(debug=True)