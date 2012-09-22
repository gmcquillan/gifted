import json
import os


def create_tags(filename=None):
    tag_dir = 'data/tags'
    if not os.path.exists(tag_dir):
        os.mkdir('data/tags')
    if filename:
        if not os.path.exists(
            '{tag_dir}/{filename}.json'.format(
                tag_dir=tag_dir,
                filename=filename
            )
        ):
            with open(
                'data/tags/{filename}.json'.format(filename=filename), 'w'
            ) as f:
                f.write(json.dumps({'data':[]}))


def get_tags():
    create_tags()
    return [tag.split('.')[0] for tag in os.listdir('data/tags')]


def _get_tag_info(filename):
    with open(
        'data/tags/{filename}.json'.format(filename=filename), 'r'
    ) as f:
        return json.loads(f.read())


def _get_or_create_tags(filename):
    create_tags(filename)
    return _get_tag_info(filename)


def _add_tag_info(filename, tag_data):
    t = _get_or_create_tags(filename)
    t['data'].append(tag_data)
    t['data'] = list(set(t['data']))
    print tag_data, 'tag_data'
    print t
    with open(
        'data/tags/{filename}.json'.format(filename=filename), 'w'
    ) as f:
        f.write(json.dumps(t))


def get_tag(tag):
    return _get_or_create_tags(tag)


def get_image_tags(gif):
    return _get_or_create_tags(gif)


def save_tag_to_image(gif, tag):
    """Saves gif filename in <tag>.json."""
    return _add_tag_info(gif, tag)


def save_image_to_tag(gif, tag):
    """Saves tag name in <gif>.json."""
    return _add_tag_info(tag, gif)


def save_tag(gif, tag):
    save_image_to_tag(gif, tag)
    save_tag_to_image(gif, tag)
