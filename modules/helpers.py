import yaml
import configparser
from pathlib import Path

import arrow
from bs4 import BeautifulSoup, Comment
from modules.api import get_resource
from modules.aws import get_s3_bucket, get_image


def get_path(target=None):
    """
    Gets a path specified in the Files section of the settings.ini file.
    :param target: One of the variable names in the FILES section of settings.ini
    :return: A Path object from the pathlib library
    """
    if target is None:
        print('Missing argument for get_path(). Exiting.')
        exit()
    elif target not in ['handoffs', 'loader', 'image_skip_list', 'articles_db']:
        print(f'\'{target}\' is not a valid argument for get_path(). Exiting.')
        exit()
    config = configparser.ConfigParser()
    config.read('settings.ini')
    path = Path(config['FILES'][target])
    if path.exists():
        return path
    else:
        print('The path in settings.ini does not exist. Exiting.')
        exit()


def get_aws_setting(name=None):
    """
    Gets a setting specified in the AWS section of the settings.ini file.
    :param name: One of the variable names in the AWS section of settings.ini
    :return: String
    """
    if name is None:
        print('Missing argument for get_aws_setting(). Exiting.')
        exit()
    elif name not in ['bucket_name', 'key_prefix', 'loc_key_prefix']:
        print(f'\'{name}\' is not a valid argument for get_aws_setting(). Exiting.')
        exit()
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config['AWS'][name]


def get_loader_map():
    """
    Reads the handoff's loader file and looks up loader ids in the articles database to create an id:hc map.
    Exits if any loader article is not in the database
    :return: Dict of article ids and hc subdomains
    """
    article_hc_map = {}
    loader_path = get_path('loader')
    with loader_path.open() as f:
        loader_list = f.read().splitlines()
    articles_db = get_path('articles_db')
    with articles_db.open(mode='r') as f:
        articles_db = yaml.load(f)
    for article in articles_db:
        if str(article['id']) in loader_list:
            article_hc_map[article['id']] = article['hc']
            loader_list.remove(str(article['id']))
            if len(loader_list) == 0:
                return article_hc_map

    if len(loader_list) > 0:
        if len(loader_list) == 1:
            print('The following article is missing from the articles.yml file: {}'.format(loader_list[0]))
        else:
            print('Add the following articles are missing from the articles.yml file:')
            for article in loader_list:
                print(f'  - {article}')
        print('Exiting.')
        exit()


def get_image_skip_list():
    skip_list_path = get_path('image_skip_list')
    with skip_list_path.open() as f:
        skip_list = f.read().splitlines()
    return skip_list


def download_articles(article_hc_map, en_image_articles):
    """
    Downloads each article from the specified Help Center, converts the HTML into a Beautiful Soup tree, and stores it
    in a dictionary with necessary data for creating the handoff.
    :param article_hc_map: Dictionary of article ids and hc subdomains. Example {id: 123, hc: 'support'}
    :param en_image_articles: List of ids of articles with images to exclude from the handoff
    :return: Dictionary of articles. Each object consists of an article id, hc, tree, and S3 image names
    """
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

    :param handoff: A list of article dictionaries with id, hc, tree, & images properties
    :param handoff_path: A Path object that specifies the handoff folder
    :return:
    """
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


def get_article_tree(response):
    """
    Returns a BeautifulSoup tree object from the specified HTML file
    :param response: Response from the Articles API containing the article. Converted to Dict from JSON
    :return: A tree object
    """
    body = '<html>' + response['body'] + '</html>'  # to parse all the file (prevent `<p> </p>` None-type errors)
    tree = BeautifulSoup(body, 'lxml')
    if tree.html is None or tree.body is None:
        print('{}: tree.html or tree.body is None'.format(response['id']))
        return None
    comments = tree.find_all(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    head = tree.new_tag('head')
    meta = tree.new_tag('meta')
    meta['charset'] = 'utf-8'
    head.append(meta)
    tree.body.insert_before(head)
    h1 = tree.new_tag('h1')
    h1.string = response['title']
    tree.body.insert(0, h1)
    return tree


def get_article_markup(tree):
    """
    Builds HTML markup from parsed tree to write to file, and strips any HTML comments.
    :param tree: A BeautifulSoup tree object
    :return: String
    """
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    markup = xml + str(tree)
    return markup


def get_article_images(tree):
    article_images = []
    image_skip_list = get_image_skip_list()
    images = tree.find_all('img')
    for image in images:
        image_url = Path(image['src'])
        if 'zen-marketing-documentation.s3.amazonaws.com/docs/' not in str(image_url):
            continue
        if image_url.name in image_skip_list:
            continue
        article_images.append(image_url.name)
    return article_images


def write_handoff_manifest(handoff, handoff_path):
    manifest = []
    for article in handoff:
        manifest.append({'article': '{}.html'.format(article['id']), 'hc': article['hc'],
                         'images': article['images']})
    handoff_map_file = handoff_path / 'manifest.yml'
    handoff_map_file.write_text(yaml.dump(manifest, default_flow_style=False), encoding='utf-8')


def package_translation(file):
    """
    Creates a payload from an HTML file for a PUT translation request.
    :param file: A path object to an HTML file
    :return: Dictionary with a title and body property
    """
    with file.open(mode='r') as f:
        html_source = f.read()
    tree = BeautifulSoup(html_source, 'lxml')
    title = tree.h1.string.strip()
    tree.h1.decompose()
    body = str(tree.body)
    if title is None or body is None:
        print('ERROR: title or body problem in \"{}\" (extra inner tags, etc)'.format(file.name))
        exit()
    package = {
        'title': title,
        'body': body
    }
    return {'translation': package}
