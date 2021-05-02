import os, subprocess, sys
from flask import Flask, flash, request, redirect, render_template, Response
from flask import send_file
from werkzeug.utils import secure_filename
from shelljob import proc

app=Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Get current path
path = os.getcwd()

app.config['UPLOAD_FOLDER'] = {'csv': 'paysimplus/src/main/resources/paramFiles',
                               'properties': 'paysimplus/'}
app.config['UPLOAD_FOLDER']['graphml'] = app.config['UPLOAD_FOLDER']['csv'] + \
                                         '/typologies'

def allowed_file(filename):
    is_extension = filename.rsplit('.', 1)[1].lower() in app.config['UPLOAD_FOLDER']
    return '.' in filename and is_extension


@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/run')
def run():
    g = proc.Group()
    p = g.run('./run.sh')

    def read_process():
        while g.is_pending():
            lines = g.readlines()
            for proc, line in lines:
                line_spaces = line.decode('utf-8').replace(' ', '&nbsp;')
                yield f"data: {line_spaces} \n\n"
    return Response(read_process(), mimetype='text/event-stream')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                extension = filename.rsplit('.', 1)[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'][extension],
                                       filename))

                flash('File(s) successfully uploaded')
            else:
                flash('Error uploading files!')
                flash('Allowed extensions: .csv | .properties | .graphml')
        return redirect('/')

@app.route('/download', methods=['GET'])
def get_output():
    p = subprocess.call('./get_fold.sh')

    # Get zip name
    directory = os.listdir()
    dir_corr = list(filter(lambda x: '.' in x, directory))
    zip_name = list(filter(lambda x: x.rsplit('.', 1)[1] == 'zip', dir_corr))[0]

    return send_file(zip_name, mimetype='application/zip', cache_timeout=0,
                     as_attachment=True)


if __name__ == "__main__":
    app.run(host='127.0.0.1',port=5000,debug=False,threaded=True)
