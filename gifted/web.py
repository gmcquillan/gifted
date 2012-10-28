import os

from math import ceil

from flask import Flask
from flask import abort
from flask import send_file
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import collector
import json
import tags

app = Flask(__name__)


class Pagination(object):
    """Pagination template from Armin.

    http://flask.pocoo.org/snippets/44/

    """
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


def url_for_other_page(page):
    """Programatically route pagenated views."""
    args = request.view_args.copy()
    args['page'] = page

    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page


def get_file_paths(suffix='.gif'):
    fps = []
    files = os.listdir('data')
    files.sort(
        key=lambda x: os.path.getmtime('data/{x}'.format(x=x))
    )
    files.reverse()
    for f in files:
        if f.endswith(suffix):
            fps.append(f)

    return fps


def get_file(subdir, filename):
        return send_file('data/{filename}'.format(
            filename=filename,
        ))


@app.route('/page/data/<gif>')
@app.route('/tags/data/<gif>')
@app.route('/data/<gif>')
def get_image(source=None, gif=None):
    resp = get_file(source, gif)
    file_path = 'data/%s' % gif
    resp.headers.add('Content-length', str(os.path.getsize(file_path)))
    return resp


def _format_meta_for_gif_payload(gif_payload):
    return dict(
        (
            d, sizeof_fmt(
                int(gif_payload[d]['meta']['content-length'])
            )
        ) for d in gif_payload
    )


def process_get(page):
    num = int(request.args.get('num', 10))
    gifs = get_file_paths()
    pagination = Pagination(page, num, len(gifs))
    if not gifs and page != 1:
        abort(404)

    start = page * num - num
    gif_payload = tags.get_tags_for_images(gifs)
    gif_tags = dict((d, gif_payload[d]['data']) for d in gif_payload)
    gif_meta = _format_meta_for_gif_payload(gif_payload)
    return render_template(
        'index.html',
        pagination=pagination,
        tags=sorted(tags.get_tags()),
        gifs=gifs[start:start + num],
        gif_tags=gif_tags,
        gif_meta=gif_meta,
    )


def process_post():
    post_data = request.form
    gif_name = post_data.get('gif')
    tag_name = post_data.get('tagname', '').strip().replace(
            '/', ''
    ).replace(' ', '_').replace('.', '').lower()

    flag = post_data.get('flag')
    if flag:
        tags.delete_image_data(gif_name)

    elif gif_name and tag_name:
        # If we're flagging a gif, we should remove it from all relevant tags
        # and remove the file.
        tags.save_tag(gif_name, tag_name)

    gif_tag = post_data.get('gif_tag')
    if gif_tag:
        tags.delete_tag(gif_name, gif_tag)

    args = request.view_args.copy()

    return redirect(url_for(request.endpoint, **args))


@app.context_processor
def inject_tags():
    all_tags = tags.get_tags()
    n = 1
    all_tags_dicts = []
    for tag in all_tags:
        all_tags_dicts.append(
            {
                'id': n,
                'name': tag,
            }
        )
        n = n + 1

    encoded_tags = json.dumps(all_tags_dicts)
    return dict(all_tags=encoded_tags)


@app.route('/', defaults={'page': 1}, methods=['POST', 'GET'])
@app.route('/page/<int:page>', methods=['POST', 'GET'])
def index(page):
    if request.method == 'POST':
        return process_post()

    return process_get(page)


@app.route('/tags/')
@app.route('/tags/<tag>', methods=['POST', 'GET'])
def tag(tag=None):
    if request.method == 'POST':
        return process_post()
    if not tag:
        tag_names = tags.get_tags()
    else:
        tag_names = [tag]
    gifs = tags.get_images_for_tag(tag)
    gif_payload = tags.get_tags_for_images(gifs)
    gif_tags = dict((d, gif_payload[d]['data']) for d in gif_payload)
    gif_meta = _format_meta_for_gif_payload(gif_payload)

    return render_template(
        'tags.html',
        gifs=gifs,
        tags=tag_names,
        gif_tags=gif_tags,
        gif_meta=gif_meta,
    )


@app.route('/add/', methods=['POST', 'GET'])
def add():
    """Endpoint for adding gif urls manually."""
    if request.method == 'GET':
        return render_template(
            'add.html',
        )

    post_data = request.form
    gif_url = post_data.get('url', '')
    if not gif_url:
        return redirect(url_for('add'))

    c = collector.Collector()
    c.download_gifs([gif_url])
    args = request.view_args.copy()

    return redirect(url_for('index', **args))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
