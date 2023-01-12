from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from transpiler import generator
import os


SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'example'


class UploadForm(FlaskForm):
    upload = FileField(validators=[
        FileRequired(),
        FileAllowed(['java'])
    ])


def text_to_array(code):
    line_array = []
    index = 1
    for line in code.split("\n"):
        line_array.append({'index': index, 'line': line})
        index += 1
    return line_array


@app.route('/', methods=['GET', 'POST'])
def main():
    form = UploadForm()
    if form.is_submitted():
        form.upload.data.save(os.path.join(app.config["UPLOAD_FOLDER"], 'text.txt'))
    try:
        code = text_to_array(generator.compiler(app))
        exception = None
    except Exception as e:
        exception = e
        code = None

    return render_template('main.jinja.html', code_file=form, code=code, exception=exception)


if __name__ == '__main__':
    app.run()
