# from modules.handoffs import create_handoff, publish_handoff
from modules.helpers import get_image_skip_list
# from modules.aws import get_s3_bucket, get_image

skip_list = get_image_skip_list()
print(skip_list)

# create_handoff('test8')

# publish_handoff('test5')

# bucket = get_s3_bucket()
# # loc_key = 'docs/fr/KC_insights_dashboard_select_view_only.png'      # doesn't exist
# # loc_key = 'docs/fr/plan_available_chat_ap.png'                      # exists
#
# print(f'- getting {loc_key}')
# localized_image = get_image(bucket, loc_key)
#
# if localized_image == 'error':
#     print('Non-404 error')
#
# if localized_image:
#     print(localized_image.last_modified)


# TEST command line
# $ python3 zlo.py create test9
# $ python3 zlo.py create test9 --exclude 360001562227
