
## Help Center localization tool

This tool gets articles from Help Center to hand off to localization vendors, and publishes the returned localized articles to Help Center.


### Requirements

- Python 3.6 or later - https://www.python.org/downloads/

You must also install the following third-party libraries:

- Requests - http://docs.python-requests.org/en/master/
- BeautifulSoup - https://www.crummy.com/software/BeautifulSoup/
- Boto3 - https://boto3.readthedocs.io/en/latest/guide/quickstart.html
- Arrow - https://arrow.readthedocs.io/en/latest/



### Setting up

1. Map your DITA file names to their corresponding Help Center ids. To do so, create a yml file called **articles.yml**. Enter the following information for each article: DITA filename without the file extension, Help Center subdomain, and article id.

    Example:

    ```yml
    - dita: zug_placeholders
      hc: support
      id: 203662116
    - dita: zug_markdown
      hc: support
      id: 203661586
    ```

    Make sure to follow the format in the example.

    You can keep adding mappings to the same yml file. You don't need to create a yml file each time you publish.

    Make sure each article id is unique in the yml file.

    Don't include the .dita file extension.

    Save the file anywhere on your computer.

2. In the zpu project files, update the **auth.py** file with your Zendesk username and API token. Example:

    ```
    def get_auth():
        return '{}/token'.format('jdoe@example.com'), '9a8b7c6d5e4f3g2h1'
    ```

3. In the **[HC]** section of the **settings.ini** file, specify your Help Center settings. Example:

    ```text
    [HC]
    subdomain=support
    locale=en-us
	```

4. In the **[MAP]** section of the **settings.ini** file, specify the path to the **ditamap.yml** file. Example:
    
    ```text
    [MAP]
    path=/Volumes/GoogleDrive/Team Drives/Documentation/All products/production/ditamap.yml
    ```


### Publishing files

1. Use your DITA authoring tool to batch transform the DITA files to HTML.

2. Copy the transformed HTML files to the **zpu/transformed_dita_files** folder.

3. In your command line interface, navigate to your **zpu** folder on your computer.

4. Run the following command:

    ```bash
    $ python3 publish_files.py
    ```

    The tool parses each HTML file and publishes it to HC.

5. When you're done, move or delete the HTML files in the **zpu/transformed_dita_files** folder to prepare for your next batch of files.


### Terms of use

This project is open source. It's not officially supported by Zendesk. See the license for the terms of use.