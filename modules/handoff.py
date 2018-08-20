import re
import csv
from urllib.parse import urlparse
from shutil import copyfile

import arrow
import modules.helpers as helpers
import modules.api as api
import modules.aws as aws


def load_handoff_data(handoff_name):
    """
    Reads the handoff's _loader.csv file and updates the handoffs.json file.
    :param handoff_name: Name of handoff specified on the command line
    :return:
    """
    handoff = {}
    articles = []
    file = helpers.get_path_setting('data') / 'handoffs.json'
    handoffs = helpers.read_json(file)
    loader_file = helpers.get_path_setting('loader')
    with loader_file.open() as f:
        reader = csv.reader(f)
        for row in reader:
            article = {'title': row[0],
                       'id': int(row[1]) if row[1] else None,
                       'deferred_id': int(row[2]) if row[2] else None,
                       'hc': row[3].lower() if row[3] else 'support',
                       'dita_name': row[4] if row[4] else None,
                       'en_images': True if row[5] else False,
                       'bump_ok': True if row[6] else False,
                       'writer': row[7],
                       'comments': row[8]}
            articles.append(article)

    handoff['articles'] = articles
    handoff['status'] = 'in progress'
    handoffs[handoff_name] = handoff
    helpers.write_json(file, handoffs)
    print('Successfully loaded the handoff data from _loader.csv to handoffs.json\n')


def get_handoff_manifest(handoff_name):
    """
    Gets the properties of the articles in the specified handoff from the handoffs database.
    :param handoff_name: Name of handoff specified on the command line
    :return: List articles and their properties
    """
    file = helpers.get_path_setting('data') / 'handoffs.json'
    handoffs = helpers.read_json(file)
    handoff_manifest = handoffs[handoff_name]['articles']
    return handoff_manifest


def download_articles(handoff_manifest):
    """
    Downloads each article from the specified Help Center, converts the HTML into a Beautiful Soup tree, and stores it
    in a dictionary with necessary data for creating the handoff.
    :param handoff_manifest: List of articles in the handoff and their properties
    :return: Dictionary of articles. Each object consists of an article id, hc, tree, and S3 image names
    """
    print('\nDownloading articles from Help Center')

    download_list = {}
    for article in handoff_manifest:
        download_list[article['id']] = article['hc']    # assign id:hc value

    handoff = []
    for article in handoff_manifest:
        hc = article['hc']
        root = f'https://{hc}.zendesk.com/api/v2/help_center'
        url = root + '/articles/{}.json'.format(article['id'])
        print('- {} -> {}'.format(hc, article['id']))
        response = api.get_resource(url)
        if response is False:
            print('\nDouble-check the article id in loc spreadsheet.\n')
            exit()
        tree = helpers.create_tree_from_api(response)
        if tree is None:
            continue

        if article['en_images']:
            images = []
        else:
            images = helpers.get_article_images(tree)

        handoff.append({'id': article['id'] if article['deferred_id'] is None else article['deferred_id'],
                        'hc': hc,
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


def get_deliverable(delivery_path, defer=None, subset=None):
    if defer and subset:
        print('\nError. Can only specify defer or subset arguments, not both. Exiting.\n')
        exit()

    print('\nGetting the deliverable...')
    deliverable = {'images': [], 'articles': []}
    image_names = []
    if defer or subset:
        handoff_name = delivery_path.parts[-2]
        handoff_manifest = get_handoff_manifest(handoff_name)
        article_list = defer if defer else subset
        image_names = helpers.get_article_image_names(handoff_name, handoff_manifest, article_list)

    image_paths = sorted(delivery_path.glob('**/images/*.*'))
    for image_path in image_paths:
        name = image_path.name
        if defer and name in image_names:
            continue
        if subset and name not in image_names:
            continue
        parts = image_path.parts
        locale = parts[-4].lower()
        if locale == 'pt-br':
            key = 'docs/pt/{}'.format(name)
        else:
            key = 'docs/{}/{}'.format(locale, name)
        deliverable['images'].append({'locale': locale, 'name': name, 'key': key, 'path': image_path})

    article_paths = sorted(delivery_path.glob('**/*.html'))
    for article_path in article_paths:
        source_id = article_path.name[:-5]
        if defer and int(source_id) in defer:
            continue
        if subset and int(source_id) not in subset:
            continue

        tree = helpers.create_tree_from_file(article_path)
        if tree is None:
            continue
        parts = article_path.parts
        deliverable['articles'].append({'locale': parts[-4].lower(), 'hc': parts[-3],
                                        'source_id': source_id, 'tree': tree})

    return deliverable


def register_new_localized_content(deliverable):
    print('\nRegistering new localized content...')
    file = helpers.get_path_setting('data') / 'localized_content.json'
    localized_content = helpers.read_json(file)
    is_updated = False
    for image in deliverable['images']:
        if image['name'] not in localized_content[image['locale']]['images']:
            localized_content[image['locale']]['images'].append(image['name'])
            is_updated = True
    for article in deliverable['articles']:
        if int(article['source_id']) not in localized_content[article['locale']]['articles']:
            localized_content[article['locale']]['articles'].append(int(article['source_id']))
            is_updated = True
    if is_updated:
        file = helpers.get_path_setting('data') / 'localized_content.json'
        backup_file = helpers.get_path_setting('data') / 'localized_content_backup.json'
        copyfile(file, backup_file)
        helpers.write_json(file, localized_content)


def relink_articles(deliverable):
    print('\nUpdating article links...')
    file = helpers.get_path_setting('data') / 'localized_content.json'
    localized_content = helpers.read_json(file)
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
            if int(article_id) in localized_content[locale]['articles']:
                link['href'] = re.sub(r'hc/en-us', 'hc/{}'.format(locale), link['href'])
                # print(' - updated xref - {}'.format(link['href']))

        imgs = tree.find_all('img', src=re.compile('/docs/en/'))
        for link in imgs:
            image_name = link['src'].split('/docs/en/')[1]
            if image_name in localized_content[locale]['images']:
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
