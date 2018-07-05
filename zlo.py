import argparse

from modules.handoffs import create_handoff


def create(arguments):
    """
    :param arguments: handoff_name (str), exclude (list of ints)
    :return: None
    """

    create_handoff(arguments.handoff_name, arguments.no_images)

# def register(arguments):
#     """
#     :param arguments: handoff_name (str), product (str), articles (bool), images (bool), locales (list), write (bool)
#     :return: void
#     """
#
#     if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
#         print('The product name is invalid. Try again.')
#         exit()
#     ho = Handoff(arguments.handoff_name, arguments.product)
#
#     if arguments.articles or arguments.images:
#         if arguments.articles:
#             ho.update_article_registry(arguments.locales, arguments.write)
#         if arguments.images:
#             ho.update_image_registry(arguments.locales, arguments.write)
#     else:
#         ho.update_article_registry(arguments.locales, arguments.write)
#         ho.update_image_registry(arguments.locales, arguments.write)
#
#
# def relink(arguments):
#     """
#     :param arguments: handoff_name (str), product (str), articles (bool), images (bool), locales (list), write (bool)
#     :return: void
#     """
#     if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
#         print('The product name is invalid. Try again.')
#         exit()
#     ho = Handoff(arguments.handoff_name, arguments.product)
#
#     if arguments.hrefs or arguments.srcs:
#         if arguments.hrefs:
#             ho.update_hrefs(arguments.locales, arguments.write)
#         if arguments.srcs:
#             ho.update_srcs(arguments.locales, arguments.write)
#     else:
#         ho.update_hrefs(arguments.locales, arguments.write)
#         ho.update_srcs(arguments.locales, arguments.write)
#
#
# def publish(arguments):
#     """
#     :param arguments: handoff_name (str), product (str), locales (list), write (bool)
#     :return: void
#     """
#     if arguments.product not in ['support', 'chat', 'help', 'bime', 'explore']:
#         print('The product name is invalid. Try again.')
#         exit()
#     ho = Handoff(arguments.handoff_name, arguments.product)
#     ho.publish_handoff(arguments.locales, arguments.write)


parser = argparse.ArgumentParser()
parser.add_argument('--version', action='version', version='1.0.0')
subparsers = parser.add_subparsers()

# python3 ho.py create {handoff_name} --exclude {id id ...}
create_parser = subparsers.add_parser('create')
create_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
create_parser.add_argument('--no_images', nargs='*', type=int,
                           help='ids of articles that use default language images in loc versions')
create_parser.set_defaults(func=create)

# # python3 ho.py register {handoff_name} {product} --articles --images --locales --write
# register_parser = subparsers.add_parser('register')
# register_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
# register_parser.add_argument('product', help='support, chat, bime, help, or explore')
# register_parser.add_argument('--articles', action='store_true', help='add only articles to registry')
# register_parser.add_argument('--images', action='store_true', help='add only images to registry')
# register_parser.add_argument('--locales', nargs='*', help='specific locales; if none specified, uses all')
# register_parser.add_argument('--write', '-w', action='store_true', help='write changes to file')
# register_parser.set_defaults(func=register)
#
# # python3 ho.py relink {handoff_name} {product} --hrefs --srcs --locales {loc loc ...} --write
# relink_parser = subparsers.add_parser('relink')
# relink_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
# relink_parser.add_argument('product', help='support, chat, bime, help, or explore')
# relink_parser.add_argument('--hrefs', action='store_true', help='update article links')
# relink_parser.add_argument('--srcs', action='store_true', help='update image links')
# relink_parser.add_argument('--locales', nargs='*', help='specific locales; if none specified, uses all')
# relink_parser.add_argument('--write', '-w', action='store_true', help='write changes to file')
# relink_parser.set_defaults(func=relink)
#
# # python3 ho.py publish {handoff_name} {product} --locales {loc loc ...} --write
# publish_parser = subparsers.add_parser('publish')
# publish_parser.add_argument('handoff_name', help='handoff name, usually yyyy-mm-dd')
# publish_parser.add_argument('product', help='support, chat, bime, help, or explore')
# publish_parser.add_argument('--locales', nargs='*', help='specific locales; if none specified, uses all')
# publish_parser.add_argument('--write', '-w', action='store_true', help='publish the files to Help Center')
# publish_parser.set_defaults(func=publish)

if __name__ == '__main__':      # do NOT comment out - required to call functions
    args = parser.parse_args()
    args.func(args)             # call the default function
