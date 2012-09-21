import json
import os


def create_tags(filename=None, column='images'):
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
                f.write(json.dumps({column:[]}))


def get_tags():
    create_tags()
    return [tag.split('.')[0] for tag in os.listdir('data/tags')]


def _get_tag_info(filename):
    with open(
        'data/tags/{filename}.json'.format(filename=filename), 'r'
    ) as f:
        return json.loads(f.read())


def _get_or_create_tags(filename, column):
    create_tags(filename, column)
    return _get_tag_info(filename)


def _save_tag_info(filename, tag_data, column='images'):
    t = _get_or_create_tags(tag_data, column=column)
    t[column].append(tag_data)
    t[column] = list(set(t[column]))
    with open(
        'data/tags/{filename}.json'.format(filename=filename), 'w'
    ) as f:
        f.write(json.dumps(t))


def get_tag(tag):
    return _get_or_create_tags(tag, column='images')


def get_image_tags(gif):
    return _get_or_create_tags(gif, column='tags')


def save_image_to_tag(gif, tag):
    return _save_tag_info(gif, tag)


def save_tag_to_image_idx(gif, tag):
    return _save_tag_info(tag, gif, column='tags')


def save_tag(gif, tag):
    save_image_to_tag(gif, tag)
    save_tag_to_image_idx(gif, tag)
