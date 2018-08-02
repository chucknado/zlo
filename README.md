
## Help Center localization tool

This tool gets articles from Help Center to hand off to localization vendors, and publishes the returned localized articles to Help Center.

The tool assumes your image files are hosted on Amazon S3, which has an API that lets you download and upload images. You can modify the tool if your images are hosted elsewhere.

### Requirements

- Python 3.6 or later - https://www.python.org/downloads/

You must also install the following third-party libraries:

- Requests - http://docs.python-requests.org/en/master/
- BeautifulSoup - https://www.crummy.com/software/BeautifulSoup/
- Boto3 - https://boto3.readthedocs.io/en/latest/guide/quickstart.html
- Arrow - https://arrow.readthedocs.io/en/latest/


### Setting up

1. Download or clone this project.

2. Create a file called **articles.yml**.

    This file will eventually list all the articles you've handed off for localization.

    Save the file anywhere on your computer or on a shared drive. The Zendesk Docs team keeps the file in our Google Team Drive so that all the writers can access it:

	`Documentation/Zendesk User Guides/All products/production/articles.yml`

    See [Update the article database](https://github.com/chucknado/zlo/blob/master/docs/localizing_articles.md#update-the-article-database) in the zlo documentation.

3. In the zlo project files, update the **modules/auth.py** file with your Zendesk username and API token. Example:

    ```
    def get_auth():
        return '{}/token'.format('jdoe@example.com'), '9a8b7c6d5e4f3g2h1'
    ```

4. In the **[PATHS]** section of the **settings.ini** file, specify the paths to various folders and files used by the tool, including the path to the **articles.yml** file you created above. Create the other folders and files.

5. In the **[AWS]** section of the **settings.ini** file, specify the name of your S3 bucket, the key prefix of the default-language image files, and one key prefix of your translated image files.

    The loc key prefix is used to compare the default language images against the images in a different language to determine whether to include them in the handoff.

6. Create an AWS credential file on your system. See [Configuration](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration) in the Boto 3 Quickstart guide.


### Terms of use

This project is open source. It's not officially supported by Zendesk. See the license for the terms of use.