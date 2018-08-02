import re
from urllib.parse import urlparse

import arrow
import modules.helpers as helpers
import modules.api as api
import modules.aws as aws


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
        hc = article_hc_map[article]
        root = f'https://{hc}.zendesk.com/api/v2/help_center'
        url = root + '/articles/{}.json'.format(article)
        print(f'- {hc} -> {article}')
        response = api.get_resource(url)
        if response is False:
            print('Double-check the article id in loc spreadsheet and the master articles file.')
            exit()
        tree = helpers.create_tree_from_api(response)
        if tree is None:
            continue

        if en_image_articles and article in en_image_articles:
            images = []
        else:
            images = helpers.get_article_images(tree)

        handoff.append({'id': article,
                        'hc': article_hc_map[article],
                        'tree': tree,
                        'images': images})
    return handoff


def write_articles(handoff, handoff_path):
    """
    Writes downloaded articles to the handoff folder.
    :param handoff: A list of article dictionaries returned by download_articles()
    :param handoff_path: A Path object that specifies the handoff folder
    :return:
    """
    print('\nWriting downloaded articles to the handoff folder')
    for article in handoff:
        markup = helpers.get_article_markup(article['tree'])
        if markup is None:
            print('- the {} article {} in Help Center has no content. Skipping.'.format(article['hc'], article['id']))
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
    Downloads the images for each article from S3 to the handoff folder.
    :param: handoff: A list of article dictionaries returned by download_articles()
    :param: handoff_path: A Path object that specifies the handoff folder
    :return:
    """
    print('\nDownloading images to the handoff folder')
    bucket_name = helpers.get_aws_setting('bucket_name')
    key_prefix = helpers.get_aws_setting('key_prefix')
    loc_key_prefix = helpers.get_aws_setting('loc_key_prefix')
    bucket = aws.get_s3_bucket(bucket_name)

    for article in handoff:
        if not article['images']:   # article contains no images: go to next article
            continue
        for image_name in article['images']:
            image_qualifies = True

            key = key_prefix + image_name
            image = aws.download_image(bucket, key)
            if image == 'error':
                continue

            # get loc version of image for comparison
            loc_key = loc_key_prefix + image_name
            localized_image = aws.download_image(bucket, loc_key)
            if localized_image == 'error':
                continue

            if localized_image:
                if arrow.get(localized_image.last_modified) > arrow.get(image.last_modified):
                    image_qualifies = False

            if image_qualifies:
                handoff_image_folder = handoff_path / article['hc'] / 'images'
                if not handoff_image_folder.exists():
                    handoff_image_folder.mkdir(parents=True)
                print('- /{}/{}'.format(article['hc'], image_name))
                filename = '{}/{}'.format(str(handoff_image_folder), image_name)
                image.download_file(filename)
            else:
                # skipping - localized image is newer on s3, so en-us translation has not been updated
                #     since the last handoff
                article['images'].remove(image_name)


def print_handoff_email(handoff_name):
    """
    Prints the text for the email to the loc vendor.
    :param handoff_name: Name for the handoff specified on the command line
    :return:
    """
    utc = arrow.utcnow()
    local = utc.to('US/Pacific')
    date = local.format('YYYY-MM-DD')
    print('\n---TEMPLATE START---')
    print('\nZendesk docs {} handoff\n'.format(date))
    print('\nHi Gerhard and Sabine,')
    print('\nWe uploaded the following handoff package to your server:')
    print('\n- {}.zip'.format(handoff_name))
    print('\nContent questions should go to the people on the cc line.')
    print('\nThanks!')
    print('\n---TEMPLATE END---\n')


def get_deliverable(delivery_path):
    print('\nGetting the deliverable...')
    deliverable = {'images': [], 'articles': []}
    image_paths = sorted(delivery_path.glob('**/images/*.*'))
    for image_path in image_paths:
        parts = image_path.parts
        locale = parts[-4].lower()
        if locale == 'pt-br':
            key = 'docs/pt/{}'.format(image_path.name)
        else:
            key = 'docs/{}/{}'.format(locale, image_path.name)
        deliverable['images'].append({'locale': locale, 'name': image_path.name, 'key': key, 'path': image_path})
    article_paths = sorted(delivery_path.glob('**/*.html'))
    for article_path in article_paths:
        tree = helpers.create_tree_from_file(article_path)
        if tree is None:
            continue
        parts = article_path.parts
        deliverable['articles'].append({'locale': parts[-4].lower(), 'hc': parts[-3],
                                        'source_id': article_path.name[:-5], 'tree': tree})
    return deliverable


def register_new_localized_content(deliverable):
    print('\nRegistering new localized content...')
    localized_content_registry = helpers.get_localized_content_registry()
    is_updated = False
    for image in deliverable['images']:
        if image['name'] not in localized_content_registry[image['locale']]['images']:
            localized_content_registry[image['locale']]['images'].append(image['name'])
            is_updated = True
    for article in deliverable['articles']:
        if int(article['source_id']) not in localized_content_registry[article['locale']]['articles']:
            localized_content_registry[article['locale']]['articles'].append(int(article['source_id']))
            is_updated = True
    if is_updated:
        helpers.write_localized_content_registry(localized_content_registry)


def relink_articles(deliverable):
    print('\nUpdating article links...')
    registry = helpers.get_localized_content_registry()
    for article in deliverable['articles']:
        tree = article['tree']
        locale = article['locale']

        hrefs = tree.find_all('a', href=re.compile('/hc/en-us/articles'))
        for link in hrefs:
            parsed_link = urlparse(link['href'])
            if '/hc/en-us/articles/' not in parsed_link.path:
                continue
            article_id = parsed_link.path.split('/articles/')[1]        # remove the url path prefix
            article_id = article_id.split('-')[0]                       # remove dasherized title suffix
            article_id = re.sub('[^0-9]', '', article_id)               # remove any remaining non-numeric characters
            if int(article_id) in registry[locale]['articles']:
                link['href'] = re.sub(r'hc/en-us', 'hc/{}'.format(locale), link['href'])
                # print(' - updated xref - {}'.format(link['href']))

        imgs = tree.find_all('img', src=re.compile('/docs/en/'))
        for link in imgs:
            image_name = link['src'].split('/docs/en/')[1]
            if image_name in registry[locale]['images']:
                if locale == 'pt-br':
                    link['src'] = re.sub(r'docs/en', 'docs/{}'.format('pt'), link['src'])
                else:
                    link['src'] = re.sub(r'docs/en', 'docs/{}'.format(locale), link['src'])
                # print(' - updated src  - {}'.format(link['src']))

        article['tree'] = tree


def upload_images(deliverable):
    print('\nUploading images...')
    bucket_name = helpers.get_aws_setting('bucket_name')
    bucket = aws.get_s3_bucket(bucket_name)
    for image in deliverable['images']:
        print(' - uploading {}'.format(image['key']))
        response = aws.upload_image(bucket, image['path'], image['key'])
        if response == 'error':
            continue


def upload_articles(deliverable):
    print('\nUploading articles...')
    for article in deliverable['articles']:
        article_id = article['source_id']
        locale = article['locale']
        print(f' - uploading {locale} translation of {article_id}')
        if article_id == 203661746:  # if glossary, paste in HC by hand
            print(' - warning! glossary, 203661746, skipped. Enter manually.')
            continue
        tree = article['tree']
        title = ' '.join(tree.h1.stripped_strings)
        tree.h1.decompose()
        http_method = helpers.get_http_method(article_id, locale, article['hc'])
        root = 'https://{}.zendesk.com/api/v2/help_center'.format(article['hc'])
        if http_method == 'post':
            data = {'translation': {'locale': locale, 'title': title, 'body': str(tree), 'draft': False}}
            url = root + '/articles/{}/translations.json'.format(article_id)
            api.post_resource(url, data)
        else:
            data = {'translation': {'title': title, 'body': str(tree), 'draft': False}}
            url = root + '/articles/{}/translations/{}.json'.format(article_id, locale)
            api.put_resource(url, data)
        article['title'] = title


def print_publish_email(deliverable, handoff_name):
    utc = arrow.utcnow()
    local = utc.to('US/Pacific')
    date = local.format('YYYY-MM-DD')
    published_articles = ''
    for article in deliverable['articles']:
        if str(article['source_id']) in published_articles:
            continue
        published_articles += '{} - {}\n'.format(article['hc'].capitalize(), article['source_id'])

    print('\n---TEMPLATE START---')
    print('\nLocalized docs published {}\n'.format(date))
    print(('We published the following localized articles today. For details, '
           'see the \"{}\" section in the following spreadsheet:\n'.format(handoff_name)))
    print(('https://docs.google.com/a/zendesk.com/spreadsheets/'
           'd/1jldaCDT5iYrUdmzAT1jWwFbYOwGECVVcwK9agHJeGE8/edit?usp=sharing'))
    print('\nArticles:\n')
    print(published_articles)
    print('Thanks')
    print('\n---TEMPLATE END---\n')
