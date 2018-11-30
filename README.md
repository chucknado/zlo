
##  Zendesk loc handoff (ZLO) tools

Use these tools to prepare localization handoffs and to publish the deliverables returned by the localization vendor. The articles and translations are published to one or more Zendesk Help Centers.

The tool assumes article image files are hosted on Amazon S3. You can modify the tool if your images are hosted elsewhere.


### Requirements

- Python 3.6 or later - https://www.python.org/downloads/

You must also install the following third-party Python libraries:

- Requests - http://docs.python-requests.org/en/master/
- BeautifulSoup - https://www.crummy.com/software/BeautifulSoup/
- lxml - https://lxml.de/
- Boto 3 - https://boto3.readthedocs.io/en/latest/guide/quickstart.html
- Arrow - https://arrow.readthedocs.io/en/latest/


### Setting up

1. Download or clone this project.

2. In the zlo project files, update the **modules/auth.py** file with your Zendesk username and API token. Example:

    ```
    def get_auth():
        return '{}/token'.format('jdoe@example.com'), '9a8b7c6d5e4f3g2h1'
    ```

3. In the **[PATHS]** section of the **settings.ini** file, specify the paths to various folders and files used by the tool. Create the other folders and files.

4. In the **[AWS]** section of the **settings.ini** file, specify the name of your S3 bucket, the key prefix of the default-language image files, and one key prefix of your translated image files.

    The loc key prefix is used to compare the default language images against the images in a different language to determine whether to include them in the handoff.

5. Create an AWS credential file on your system. See [Configuration](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration) in the Boto 3 Quickstart guide.


### Terms of use

This project is not officially supported by Zendesk. See the license for the terms of use.