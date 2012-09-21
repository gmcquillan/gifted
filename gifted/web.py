import os

from flask import Flask
from flask import send_file
from flask import render_template

app = Flask(__name__)

def get_file_paths(suffix='.gif'):
    fps = []
    for f in os.listdir('data'):
        for k in os.listdir('/'.join(['data', f])):
            if k.endswith(suffix):
                fps.append(
                    'data/{subdir}/{filename}'.format(subdir=f, filename=k)
                )

    return fps

def get_file(subdir, filename):
        return send_file('data/{subdir}/{filename}'.format(
            subdir=subdir,
            filename=filename,
        ))

@app.route('/num/data/<source>/<gif>')
@app.route('/data/<source>/<gif>')
def get_image(source=None, gif=None):
    return get_file(source, gif)



@app.route('/<offset>/<num>')
@app.route('/offset/<offset>')
@app.route('/num/<num>')
@app.route('/')
def index(offset=None, num=25):
    gifs = get_file_paths()
    if offset:
        gifs = gifs[gifs.index(int(offset)):]
    if num:
        gifs = gifs[:int(num)]

    return render_template('index.html', gifs=gifs)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
