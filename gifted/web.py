import os

from flask import Flask
from flask import send_file
from flask import render_template
from flask import request

import tags

app = Flask(__name__)

def get_file_paths(suffix='.gif'):
    fps = []
    for f in os.listdir('data'):
        if f.endswith(suffix):
            fps.append(f)

    return fps

def get_file(subdir, filename):
        return send_file('data/{filename}'.format(
            filename=filename,
        ))

@app.route('/tags/data/<gif>')
@app.route('/data/<gif>')
def get_image(source=None, gif=None):
    return get_file(source, gif)


def process_get():
    offset = request.args.get('offset', '')
    num = request.args.get('num', '25')
    gifs = get_file_paths()
    if offset:
        gifs = gifs[gifs.index(offset):]
    if num:
        gifs = gifs[:int(num)]

    return gifs


def process_post():
    post_data = request.form

    gif_name = post_data.get('gif')
    tag_name = post_data.get('tagname')
    flag = post_data.get('flag')

    tags.save_tag(gif_name, tag_name)


@app.route('/', methods=['POST', 'GET'])
def index():

    gifs = process_get()

    if request.method == 'POST':
        process_post()

    gif_tags = tags.get_tags_for_images(gifs)

    return render_template(
        'index.html',
        gifs=gifs,
        tags=tags.get_tags(),
        gif_tags=gif_tags
    )


@app.route('/tags/')
@app.route('/tags/<tag>')
def tag(tag=None):
    tag = tag or tags.get_tags()
    gifs = tags.get_images_for_tag(tag)

    return render_template('index.html', gifs=gifs, tags=[tag])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
