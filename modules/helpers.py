import json
import configparser
from pathlib import Path

from bs4 import BeautifulSoup, Comment
from modules.api import get_resource_list


def get_path_setting(name=''):
    """
    Gets a path specified in the Files section of the settings.ini file.
    :param name: One of the variable names in the FILES section of settings.ini
    :return: Path object from the pathlib library
    """
    config = configparser.ConfigParser()
    config.read('settings.ini')
    try:
        config['PATHS'][name]
    except KeyError:
        print(f'\'{name}\' is not a valid argument for get_path(). Exiting.')
        exit()
    path = Path(config['PATHS'][name])
    if path.exists():
        return path
    else:
        print('The path in settings.ini does not exist on your system. Exiting.')
        exit()


def get_aws_setting(name=''):
    """
    Gets a setting specified in the AWS section of the settings.ini file.
    :param name: One of the variable names in the AWS section of settings.ini
    :return: String
    """
    config = configparser.ConfigParser()
    config.read('settings.ini')
    try:
        config['AWS'][name]
    except KeyError:
        print(f'\'{name}\' is not a valid argument for get_aws_path(). Exiting.')
        exit()
    return config['AWS'][name]


def get_image_skip_list():
    skip_list_path = get_path_setting('image_skip_list')
    with skip_list_path.open() as f:
        skip_list = f.read().splitlines()
    return skip_list


def write_json(file, data):
    with file.open(mode='w', encoding='utf-8') as f:
        return json.dump(data, f, sort_keys=True, indent=2)


def read_json(file):
    with file.open(mode='r') as f:
        return json.load(f)


def create_tree_from_api(response):
    """
    Returns a BeautifulSoup tree object from the HTML returned by the HC API
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


def create_tree_from_file(path):
    html = path.read_text(encoding='utf-8')
    tree = BeautifulSoup(html, 'lxml')
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


def get_article_image_names(handoff_name, handoff_manifest, article_list):
    handoff_path = get_path_setting('handoffs')
    image_names = []
    manifest_articles = []
    for article in handoff_manifest:
        if article['id'] in article_list:
            manifest_articles.append(article)
    for article in manifest_articles:
        article_path = handoff_path / handoff_name / article['hc'] / 'articles' / '{}.html'.format(article['id'])
        tree = create_tree_from_file(article_path)
        images = get_article_images(tree)
        image_names.extend(images)
    return image_names


def get_http_method(article_id, article_locale, hc):
    """
    Check if any missing translations of the article exist. Use post for them, otherwise put.
    :param article_id:
    :param article_locale:
    :param hc:
    :return:
    """
    root = 'https://{}.zendesk.com/api/v2/help_center'.format(hc)
    url = root + '/articles/{}/translations/missing.json'.format(article_id)
    response = get_resource_list(url, list_name='locales', paginate=False)
    if response is False:
        print('\nError getting missing translations for {}. Exiting.'.format(article_id))
        exit()
    missing_translations = response
    if article_locale in missing_translations:  # get http method to use for article
        return 'post'
    else:
        return 'put'
