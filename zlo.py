import argparse

import modules.handoff as ho
from modules.helpers import get_path_setting


def load(arguments):
    """
    Loads data from the _loader.csv file to the handoffs.json file, the main handoffs database.
    This is temporary until the website and db are up.
    :param arguments: handoff_name (str)
    :return: None
    """
    ho.load_handoff_data(arguments.handoff_name, arguments.custom)


def create(arguments):
    """
    Creates a handoff package in the handoffs folder specified in settings.ini.
    :param arguments: handoff_name (str)
    :return: None
    """
    handoff_path = get_path_setting('handoffs') / arguments.handoff_name
    if handoff_path.exists():
        print('A handoff with that name already exists in the handoffs folder. Exiting.')
        exit()
    handoff_manifest = ho.get_handoff_manifest(arguments.handoff_name)
    handoff = ho.download_articles(handoff_manifest)
    ho.write_articles(handoff, handoff_path)
    ho.download_images(handoff, handoff_path)
    ho.print_handoff_email(arguments.handoff_name)
    print('\nProcess done\n')


def publish(arguments):
    """
    Publishes the articles and images of a handoff deliverable to Help Centers and Amazon S3 respectively.
    :param arguments: handoff_name(str)
    :return:
    """
    delivery_path = get_path_setting('handoffs') / arguments.handoff_name / 'translations'
    if not delivery_path.exists():
        print('Folder does not exist: {}. Exiting.'.format(delivery_path))
        exit()
    deliverable = ho.get_deliverable(delivery_path, arguments.defer, arguments.subset)
    ho.register_new_localized_content(deliverable)
    ho.relink_articles(deliverable)
    ho.upload_images(deliverable)
    ho.upload_articles(deliverable)
    ho.print_publish_email(deliverable, arguments.handoff_name)
    print('\nProcess done\n')


parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='1.0.0')
subparsers = parser.add_subparsers()

# python3 zlo.py load {handoff_name} --custom
load_parser = subparsers.add_parser('load')
load_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
load_parser.add_argument('--custom', action='store_true', help='Flag for custom data source')
load_parser.set_defaults(func=load)

# python3 zlo.py create {handoff_name}
create_parser = subparsers.add_parser('create')
create_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
create_parser.set_defaults(func=create)

# python3 zlo.py publish {handoff_name} --defer {id id ...} --subset {id id ...}
publish_parser = subparsers.add_parser('publish')
publish_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
publish_parser.add_argument('--defer', nargs='*', type=int,
                            help='ids of articles to publish later')
publish_parser.add_argument('--subset', nargs='*', type=int,
                            help='ids of articles to publish (default is all)')
publish_parser.set_defaults(func=publish)

if __name__ == '__main__':      # do NOT comment out - required to call functions
    args = parser.parse_args()
    args.func(args)             # call the default function
