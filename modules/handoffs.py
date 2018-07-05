import yaml

import arrow
from modules.helpers import get_path_setting, get_article_tree, get_article_markup, get_article_images, get_aws_setting
from modules.api import get_resource
from modules.aws import get_s3_bucket, get_image


def download_articles(article_hc_map, en_image_articles):
    """
    Downloads each article from the specified Help Center, converts the HTML into a Beautiful Soup tree, and stores it
    in a dictionary with necessary data for creating the handoff.
    :param article_hc_map: Dictionary of article ids and hc subdomains. Example {id: 123, hc: 'support'}
    :param en_image_articles: List of ids of articles with images to exclude from the handoff
    :return: Dictionary of articles. Each object consists of an article id, hc, tree, and S3 image names
    """
    print('\nDownloading articles from Help Center')
    handoff = []
    for article in article_hc_map:
        root = 'https://{}.zendesk.com/api/v2/help_center'.format(article_hc_map[article])
        url = root + '/articles/{}.json'.format(article)
        print(f'- {article}')
        response = get_resource(url)
        if response is False:
            print('Double-check the article id in loc spreadsheet and the master articles file.')
            exit()
        tree = get_article_tree(response)
        if tree is None:
            continue

        if en_image_articles and article in en_image_articles:
            images = []
        else:
            images = get_article_images(tree)

        handoff.append({'id': article,
                        'hc': article_hc_map[article],
                        'tree': tree,
                        'images': images})
    return handoff


def write_articles(handoff, handoff_path):
    """
    Writes downloaded articles to the handoff folder.
    :param handoff: A list of article dictionaries returned by download_articles(), with id, hc, tree, & images
    properties.
    :param handoff_path: A Path object that specifies the handoff folder
    :return:
    """
    print('\nWriting articles to file')
    for article in handoff:
        markup = get_article_markup(article['tree'])
        if markup is None:
            print('The {} article {} in Help Center has no content. Skipping.'.format(article['hc'], article['id']))
            continue
        handoff_article_folder = handoff_path / article['hc'] / 'articles'
        if not handoff_article_folder.exists():
            handoff_article_folder.mkdir(parents=True)
        filename = '{}.html'.format(article['id'])
        article_path = handoff_article_folder / filename
        article_path.write_text(markup,  encoding='utf-8')
        print('- /{}/{}'.format(article['hc'], filename))


def download_images(handoff, handoff_path):
    """
    Downloads the images for each article from S3.
    :param: handoff: A list of article dictionaries with id, hc, tree, & images properties
    :param: handoff_path: A Path object that specifies the handoff folder
    :return:
    """
    print('\nDownloading images to folders')
    bucket_name = get_aws_setting('bucket_name')
    key_prefix = get_aws_setting('key_prefix')
    loc_key_prefix = get_aws_setting('loc_key_prefix')
    bucket = get_s3_bucket(bucket_name)

    for article in handoff:
        if not article['images']:   # article contains no images: go to next article
            continue
        for image_name in article['images']:
            image_qualifies = True
            print(f'\nChecking {image_name}')

            key = key_prefix + image_name
            print(f'- getting {key}')
            image = get_image(bucket, key)
            if image == 'error':
                continue

            loc_key = loc_key_prefix + image_name
            print(f'- getting {loc_key} for comparison')
            localized_image = get_image(bucket, loc_key)
            if localized_image == 'error':
                continue

            if localized_image:
                if arrow.get(localized_image.last_modified) > arrow.get(image.last_modified):
                    image_qualifies = False

            if image_qualifies:
                handoff_image_folder = handoff_path / article['hc'] / 'images'
                if not handoff_image_folder.exists():
                    handoff_image_folder.mkdir(parents=True)
                print('- writing {}/{}'.format(article['hc'], image_name))
                filename = '{}/{}'.format(str(handoff_image_folder), image_name)
                image.download_file(filename)
            else:
                print('- skipping (localized image is newer on s3, so the English version hasn\'t been updated '
                      'since the last handoff)')
                article['images'].remove(image_name)


def write_manifest(handoff, handoff_path):
    print('\nWriting handoff manifest to {}\n'.format(handoff_path))
    manifest = []
    for article in handoff:
        manifest.append({'article': '{}.html'.format(article['id']), 'hc': article['hc'],
                         'images': article['images']})
    handoff_map_file = handoff_path / 'manifest.yml'
    handoff_map_file.write_text(yaml.dump(manifest, default_flow_style=False), encoding='utf-8')


def publish_handoff(name):
    """

    :param name:
    :return:
    """
    handoff_path = get_path_setting('handoffs') / name
    if not handoff_path.exists():
        print('A handoff with that name doesn\'t exist. Exiting.')
        exit()
    handoff_map_file = handoff_path / 'handoff_map.yml'
    with handoff_map_file.open(mode='r') as f:
        handoff_map = yaml.load(f)
    print(f'Publishing handoff {name}')
    print(handoff_map)
