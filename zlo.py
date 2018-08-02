import argparse

import modules.handoff as ho
from modules.helpers import get_path_setting, get_download_list


def create(arguments):
    """
    Creates a handoff package in the handoffs folder specified in settings.ini.
    :param arguments: handoff_name (str), no_images (list of ints)
    :return: None
    """
    handoff_path = get_path_setting('handoffs') / arguments.handoff_name
    if handoff_path.exists():
        print('A handoff with that name already exists in the handoffs folder. Exiting.')
        exit()
    download_list = get_download_list()
    handoff = ho.download_articles(download_list, arguments.no_images)
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
    deliverable = ho.get_deliverable(delivery_path)
    ho.register_new_localized_content(deliverable)
    ho.relink_articles(deliverable)
    ho.upload_images(deliverable)
    ho.upload_articles(deliverable)
    ho.print_publish_email(deliverable, arguments.handoff_name)
    print('\nProcess done\n')


parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='1.0.0')
subparsers = parser.add_subparsers()

# python3 zlo.py create {handoff_name} --no_images {id id ...}
create_parser = subparsers.add_parser('create')
create_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
create_parser.add_argument('--no_images', nargs='*', type=int,
                           help='ids of articles that use default language images in loc versions')
create_parser.set_defaults(func=create)

# python3 zlo.py publish {handoff_name}
publish_parser = subparsers.add_parser('publish')
publish_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
publish_parser.set_defaults(func=publish)

if __name__ == '__main__':      # do NOT comment out - required to call functions
    args = parser.parse_args()
    args.func(args)             # call the default function
