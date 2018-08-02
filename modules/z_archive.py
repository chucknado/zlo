# def write_manifest(handoff, handoff_path):
#     """
#     Writes a yml file listing the articles in the handoff and their corresponding Help Centers.
#     :param handoff: A list of article dictionaries returned by download_articles()
#     :param handoff_path: A Path object that specifies the handoff folder
#     :return:
#     """
#     manifest = []
#     for article in handoff:
#         manifest.append({'article': '{}.html'.format(article['id']), 'hc': article['hc']})
#     handoff_map_file = handoff_path / 'manifest.yml'
#     handoff_map_file.write_text(yaml.dump(manifest, default_flow_style=False), encoding='utf-8')


# def combine_latest_registries_tmp():
#     locales = ['de', 'es', 'fr', 'ja', 'pt-br']
#     localized_content = {'de': {'articles': [], 'images': []},
#                          'es': {'articles': [], 'images': []},
#                          'fr': {'articles': [], 'images': []},
#                          'ja': {'articles': [], 'images': []},
#                          'pt-br': {'articles': [], 'images': []}}
#     zep_root = Path('/Users/cnadeau/production/zep/cache/')
#     folders = ['bime', 'chat', 'explore', 'help', 'support']
#     for folder in folders:
#         path = zep_root / folder / 'localized_articles.json'
#         with path.open() as f:
#             articles = json.load(f)
#         for locale in locales:
#             localized_content[locale]['articles'].extend(articles[locale])
#
#         path = zep_root / folder / 'localized_images.json'
#         with path.open() as f:
#             images = json.load(f)
#         for locale in locales:
#             localized_content[locale]['images'].extend(images[locale])
#
#     # remove duplicates
#     for locale in locales:
#         localized_content[locale]['articles'] = list(set(localized_content[locale]['articles']))
#         localized_content[locale]['images'] = list(set(localized_content[locale]['images']))
#
#     file = get_path_setting('data') / 'localized_content.json'
#     with file.open(mode='w') as f:
#         json.dump(localized_content, f, sort_keys=True, indent=2)
