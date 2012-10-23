#!/usr/bin/env python

import json
import os


def create_tags(filename=None):
    """Creates tags file.close."""
    tag_dir = 'data/tags'
    json_file_path = 'data/tags/{filename}.json'.format(
        filename=filename
    )
    gif_file_path = 'data/{filename}'.format(
        filename=filename
    )
    if not os.path.exists(tag_dir):
        os.mkdir('data/tags')
    if filename:
        json_file_path = '{tag_dir}/{filename}.json'.format(
            tag_dir=tag_dir,
            filename=filename
        )
        try:
            with open(json_file_path, 'r') as f:
                tag_payload = json.loads(f.read())
                if not 'meta' in tag_payload:
                    f.close()
                    f = open(json_file_path, 'w')
                    tag_payload['meta'] = {
                        'content-length': str(
                            os.path.getsize(gif_file_path)
                        )
                    }
                    f.write(
                        json.dumps(
                            tag_payload
                        )
                    )
                    f.close()
        except Exception as e:
            print "oops", e
            with open(
                json_file_path, 'w'
            ) as f:
                f.write(
                    json.dumps(
                        {
                            'data': [],
                            'meta': {
                                'content-length': str(
                                    os.path.getsize(json_file_path)
                                )
                            }
                        }
                    )
                )


def get_tags():
    """Get a list of all tag names."""
    create_tags()
    return [
        tag.split('.')[0] for tag in os.listdir(
            'data/tags'
        ) if not tag.endswith('.gif.json')
    ]


def _get_tag_info(filename):
    """Read and parse json from a tag file."""
    try:
        with open(
            'data/tags/{filename}.json'.format(filename=filename), 'r'
        ) as f:
            return json.loads(f.read())
    except IOError:
        return {}
    except ValueError:
        print 'data/tags/{filename}.json'.format(filename=filename)


def _get_or_create_tags(filename):
    """Return dict of tag data, or create file and return empty dict."""
    create_tags(filename)
    return _get_tag_info(filename)


def _add_tag_info(filename, tag_data):
    """Add tag data to a tag file."""
    t = _get_or_create_tags(filename)
    t['data'].append(tag_data)
    t['data'] = sorted(list(set(t['data'])))
    with open(
        'data/tags/{filename}.json'.format(filename=filename), 'w'
    ) as f:
        f.write(json.dumps(t))


def get_tag(tag):
    """Return tag information for a tag."""
    return _get_tag_info(tag)


def get_image_tags(gif):
    """Return a list of all the tags relating to a particular gif."""
    return _get_or_create_tags(gif)


def get_images_for_tag(tag):
    """Return a list of gifs relating to a particular tag."""
    return _get_tag_info(tag).get('data', [])


def get_tags_for_images(images):
    """Return all the tags for all images stored locally."""
    gif_tags = {}
    for image in images:
        payload = get_image_tags(image)
        gif_tags[image] = {
            'data': payload.get('data', []),
            'meta': payload.get('meta', {}),
        }

    return gif_tags


def save_tag_to_image(gif, tag):
    """Saves gif filename in <tag>.json."""
    return _add_tag_info(gif, tag)


def save_image_to_tag(gif, tag):
    """Saves tag name in <gif>.json."""
    return _add_tag_info(tag, gif)


def save_tag(gif, tag):
    """Convenience method to save tag data and image meta data."""
    save_image_to_tag(gif, tag)
    save_tag_to_image(gif, tag)


def delete_image_from_tag(gif_name, tag_name):
    """Remove gif from tag set."""
    t = _get_or_create_tags(tag_name)
    t['data'].remove(gif_name)
    t['data'] = sorted(list(set(t['data'])))
    if len(t.get('data', [])) == 0:
        os.remove('data/tags/{tag_name}.json'.format(tag_name=tag_name))
    else:
        with open(
            'data/tags/{tag_name}.json'.format(tag_name=tag_name), 'w'
        ) as f:
            f.write(json.dumps(t))


def delete_tag_from_image(gif_name, tag_name):
    """Remove tag from image tag set."""
    t = _get_or_create_tags(gif_name)
    t['data'].remove(tag_name)
    t['data'] = sorted(list(set(t['data'])))
    with open(
        'data/tags/{gif_name}.json'.format(gif_name=gif_name), 'w'
    ) as f:
        f.write(json.dumps(t))


def delete_tag(gif_name, tag_name):
    """Remove a tag from a particular gif."""
    delete_tag_from_image(gif_name, tag_name)
    delete_image_from_tag(gif_name, tag_name)


def delete_image_data(gif_name):
    """Remove image tag set. E.g. For inapproprate content."""
    t = _get_or_create_tags(gif_name)
    # Remove this image from all tags which contain it.
    for gif_tag in t['data']:
        delete_image_from_tag(gif_name, gif_tag)

    # Remove the tags belonging to this image
    os.remove('data/tags/{gif_name}.json'.format(gif_name=gif_name))

    # Remove the image itself.
    os.remove('data/{gif_name}'.format(gif_name=gif_name))
