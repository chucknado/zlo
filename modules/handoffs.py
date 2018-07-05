import yaml

from modules.helpers import get_path, get_loader_map, download_articles, write_articles, download_images, \
    write_handoff_manifest


def create_handoff(name, no_image_articles=None):
    """
    Creates a handoff package in the handoffs folder specified in settings.ini.
    :param name: Handoff name. Example: 2018-06-21.
    :param no_image_articles: List of ids of articles with images to exclude from handoff.
    :return: None
    """
    handoff_path = get_path('handoffs') / name
    if handoff_path.exists():
        print('A handoff with that name already exists. Exiting.')
        exit()
    loader_map = get_loader_map()

    print('\nDownloading articles from Help Center')
    handoff = download_articles(loader_map, no_image_articles)

    print('\nWriting articles to file')
    write_articles(handoff, handoff_path)

    print('\nDownloading images to folders')
    download_images(handoff, handoff_path)

    print('\nHandoff manifest written to {}\n'.format(handoff_path))
    write_handoff_manifest(handoff, handoff_path)


def publish_handoff(name):
    """

    :param name:
    :return:
    """
    handoff_path = get_path('handoffs') / name
    if not handoff_path.exists():
        print('A handoff with that name doesn\'t exist. Exiting.')
        exit()
    handoff_map_file = handoff_path / 'handoff_map.yml'
    with handoff_map_file.open(mode='r') as f:
        handoff_map = yaml.load(f)
    print(f'Publishing handoff {name}')
    print(handoff_map)
