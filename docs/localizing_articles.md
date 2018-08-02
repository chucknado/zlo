## Getting articles localized

This article describes how to use the Zendesk localization tools (ZLO) to prepare localization handoffs and publish the localized articles and images returned from the vendor.

For installation instructions, see [Setting up the Zendesk production tools](https://github.com/chucknado/zep/blob/master/docs/setup.md).

Workflow for creating a handoff:

1. [Update the article database](#update_db)
2. [Create the handoff](#create_handoff)
3. [Hand off the files](#handoff_files)

Workflow for publishing a handoff:

1. [Prep the deliverable](#prep_loc_content)
2. [Publish the deliverable](#publish)


<!--
title: Getting articles localized
url: https://github.com/chucknado/zlo/blob/master/docs/localizing_articles.md
source: repo/zlo/docs/localizing_articles.md
-->


<h3 id="update_db">Update the article database</h3>

1. Review the handoff articles from the [loc handoff worksheet](https://docs.google.com/spreadsheets/d/1jldaCDT5iYrUdmzAT1jWwFbYOwGECVVcwK9agHJeGE8/edit#gid=0) in Google Docs.

2. Open your **articles.yml** file in a text editor. See [Setting up](#) in the README.MD file. 

3. Add the articles in the handoff spreadsheet to the **articles.yml** file. If the file is already in **articles.yml**, you can skip it.

	At minimum, specify the Help Center subdomain and the article id. Example:

	```
    - hc: support
      id: 203662116
    - hc: support
      id: 203661586
	```

	Though not necessary for loc handoffs, you can specify other properties for each article. For example, the Zendesk Docs team includes the name of each DITA-sourced article to map it to its corresponding Help Center article. 

	```
    - dita: zug_placeholders
      hc: support
      id: 203662116
    - dita: zug_markdown
      hc: support
      id: 203661586
	```

	Make sure the article id is unique in the yml file.
	
	After a while, **articles.yml** will list most of your articles and this step will be much quicker. You'd only add articles that were created since the last handoff.

4. Save the file.

Rules:

* The `hc` and `id` keys are required. All other keys are optional
* Indent lines as shown (it matters in yml)
* No tabs
* No EOL commas or quotation marks around strings
* No duplicate ids
* One yml item per article (indicated by the hyphen)


<h3 id="create_handoff">Create the handoff</h3>

1. Get the list of article ids from the [loc handoff worksheet](https://docs.google.com/spreadsheets/d/1jldaCDT5iYrUdmzAT1jWwFbYOwGECVVcwK9agHJeGE8/edit#gid=0) in Google Docs and add their ids as a column in the **/handoffs/\_loader.txt** file. Each id should be on one line with no other characters. Example:

	**\_loader.txt**
	```
	207323377
	213170757
	212533138
	...
	```

	**Caution**: Don't leave a blank line at the end of the list.

3. In the CLI, navigate to the **zlo** folder and run the following command:

	```bash
	$ python3 zlo.py create {handoff_name} --no_images {id id ...}
	```

	Example:

	```bash
	$ python3 zlo.py create 2018-12-24
	```

	Specify the `no_images` argument if some articles have been flagged to use English images in the localized versions of the article. Specify the article ids to exclude. Example:

	```bash
	$ python3 zlo.py create 2018-12-24 --no_images 203660036 203663816
	```

4. Manually add any vector image files (.psd, .ai) to the appropriate **images** folder in the handoff. Example: Images with callouts in text layers.

5. Review the images for any that don't show a localized UI. Remove any you find and add their filenames to the **production/localization/data/image\_skip\_list.txt** file.

	Images in the skip list are ignored when creating handoffs.

The `create` command downloads the default-language articles from your Help Center into a new handoffs folder. The folder name is the same as the handoff name you specified in the `create` command. In the example above, the folder name would be **2018-12-24**.

It also downloads the article images from Amazon S3. It skips the following images:

- Any image in the skip list (images with no localized UI such as icons)
- All images in the articles specified in the `no_images` command-line parameter
- Any image not hosted on S3, such as images hosted on Help Center
- Any image that has a more recent localized version on S3. It means the the English version hasn't been updated since the last handoff


<h3 id="handoff_files">Hand off the files</h3>

The article and image files need to be zipped and uploaded to the vendor's FTP server.

1. Zip the handoff folder and upload it to the vendor FTP server.

2. Notify the vendor that the handoff is up.

	The `print_handoff_email()` function in the **handoff.py** file contains an email template that you can modify for this purpose.


<h3 id="prep_deliverable">Prep the deliverable</h3>

After the localized content comes back from the vendor, place the files in the initial handoff folder in **/production/localization/handoffs/** as described below. 

1. In the folder containing the files that were handed off, create a folder named **translations**. Example:

	`/handoffs/2018-12-14/translations/`

2. Copy the locale folders (DE, ES, FR, JA, PT-BR) delivered by the vendor into this folder.

	**Tip**: Work with a copy of the returned files. In case something goes wrong and you need to revert, you can always make another copy of the original files.

	The folder structure should look as follows:

	```
	handoffs/
		2016-12-14/
			translations/
				DE/
					support/
					    articles/
					    images/
					chat/
					    articles/
					    images/
					...
				ES/
					...
				...
	```

	Make sure the locale folder names match the locales used in Help Center. For example, if the Portuguese folder is named **PT**, change it to **PT-BR** so it matches the corresponding Help Center locale.


<h3 id="publish">Publish the deliverable</h3>

**Note**: If publishing to a new section in Help Center, make sure translations of the article's parent section exists (as well as translations of the section's parent category).

1. In the CLI, navigate to the **zlo** folder and run the following command to publish the deliverable:

	```bash
	python3 zlo.py publish {handoff_name}
	```
	
	Example:

	```bash
	$ python3 zlo.py publish 2018-08-23
	```

2. Notify the team that translated articles have been published.

	The `print_publish_email()` function in the **handoff.py** file contains an email template that you can modify for this purpose.




