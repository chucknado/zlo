import yaml
import configparser
from pathlib import Path

from bs4 import BeautifulSoup, Comment


def get_path_setting(target=None):
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
    loader_path = get_path_setting('loader')
    with loader_path.open() as f:
        loader_list = f.read().splitlines()
    articles_db = get_path_setting('articles_db')
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
    skip_list_path = get_path_setting('image_skip_list')
    with skip_list_path.open() as f:
        skip_list = f.read().splitlines()
    return skip_list


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
