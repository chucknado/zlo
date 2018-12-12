## Getting articles localized

This article describes how to use the Zendesk localization tools (ZLO) to prepare localization handoffs and publish the localized articles and images returned from the vendor.

For set up instructions, see the project's [README](https://github.com/chucknado/zlo/blob/master/README.md).

To localize specific articles, ask the writers to add the articles to a shared spreadsheet on an ongoing basis.

To localize entire Help Centers or categories, specify the Help Centers and categories in a JSON file. See the [example file](https://github.com/chucknado/zlo/blob/master/docs/_custom_loader.json) for the format.

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

**Note**: This will eventually be replaced with a sqlite database that writers can update from a web application.

<h4 id="">Handing off specific articles</h4>

The writers should be adding new or updated articles to a shared spreadsheet on an ongoing basis.

**To update the database**

1. Review the articles in the [loc handoff worksheet](https://docs.google.com/spreadsheets/d/1jldaCDT5iYrUdmzAT1jWwFbYOwGECVVcwK9agHJeGE8/edit#gid=0) in Google Sheets.

	This tool expects the following 8 worksheet columns, in order:
	- article title
	- article id so the tool knows what to download (required)
	- article id for upload, if different from the download id. Otherwise, leave blank. Example: An article in a drafts section can be handed off to loc but the content will later be pasted into an existing article. When the localized articles come back, they need to be uploaded using the existing article id, not the draft article id 
	- Help Center subdomain, such as "chat" or "explore". The tool assumes "support" as the default subdomain. You can change the default in the `load_handoff_data()` function in the **handoff.py** file
	- whether the article's images should remain in the default language. Indicate yes or leave blank
	- whether it's ok to bump the article to the next handoff. Indicate yes or leave blank. Used to keep the size of handoffs manageable for the translators
	- writer's name or initials, if any questions about the article come up
	- comments 
	
	</br>Example:
	
	![Example sheet](https://github.com/chucknado/zlo/blob/master/docs/loc_handoffs_sheet_example.png)

2. Copy and paste the handoff data from the Google sheet into a new sheet without the column headings, [cn- delete the dita column (col E),] then download the sheet (**File** > **Download**) as a CSV file.

3. Rename the downloaded file **_loader.csv** and move it to the **/localization/data** folder.

    **Tip**: You can also paste the handoff data into a new Excel sheet, then save the file as a CSV file named **_loader.csv** in the **/localization/data** folder.


4. In the CLI, navigate to the **zlo** folder and run the following command:

	```bash
	$ python3 zlo.py load {handoff_name}
	```

	Example:

	```bash
	$ python3 zlo.py load 2018-12-24
	```

<h4 id="">Handing off Help Center categories</h4>

**To update the database**

1. Specify the Help Centers and categories in a JSON file. See the [example file](https://github.com/chucknado/zlo/blob/master/docs/_custom_loader.json) for the format.

2. Name the JSON file **_custom_loader.json** and save it to the **/localization/data** folder.

3. In the CLI, navigate to the **zlo** folder and run the following command:

	```bash
	$ python3 zlo.py load {handoff_name} --custom
	```

	Example:

	```bash
	$ python3 zlo.py load 2018-12-suite --custom
	```


<h3 id="create_handoff">Create the handoff</h3>

1. In the CLI, navigate to the **zlo** folder and run the following command:

	```bash
	$ python3 zlo.py create {handoff_name}
	```

	Example:

	```bash
	$ python3 zlo.py create 2018-12-24
	```

2. Manually add any vector image files (.psd, .ai) to the appropriate **images** folder in the handoff. Example: Images with callouts in text layers.

3. Review the images for any that don't show a localized UI. Remove any you find and add their filenames to the **production/localization/data/image\_skip\_list.txt** file.

	Images in the skip list are ignored when creating handoffs.

The `create` command downloads the default-language articles from your Help Center into a new handoffs folder. The folder name is the same as the handoff name you specified in the `create` command. In the example above, the folder name would be **2018-12-24**.

It also downloads the article images from Amazon S3. It skips the following images:

- Any image in the skip list (images with no localized UI such as icons)
- All images in the articles specified in the `no_images` command-line parameter
- Any image not hosted on S3, such as images hosted on Help Center
- Any image that has a more recent localized version on S3. It means the the English version hasn't been updated since the last handoff


<h3 id="handoff_files">Hand off the files</h3>

1. Zip the handoff folder and upload it to the vendor FTP server.

2. Notify the vendor that the handoff is up.

	The `create` command prints an email template that you can modify for your purpose.



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

1. Check the loc spreadsheet for any articles marked for deferral. Check with writer if the defer status still applies.

2. In the CLI, navigate to the **zlo** folder and run the following command to publish the deliverable:

	```bash
	$ python3 zlo.py publish {handoff_name} -defer {id} {id}
	```
	
	Example:

	```bash
	$ python3 zlo.py publish 2018-08-23
	```
	
	If you need to defer certain articles from the push, specify the article upload ids with the `defer` option. Use this option when documented features aren't GA yet. Specify the id in the "ID for upload" column. Example:
	
	```bash
	$ python3 zlo.py publish 2018-08-08 --defer 115003676907 115005204787
	```

	If you want to publish only a subset of articles from the deliverable, specify the article upload ids with the `subset` option. Use this option if deferred articles in a previous push are ready to go live. Example:
	
	```bash
	$ python3 zlo.py publish 2018-08-08 --subset 115003676907 115005204787
	```

2. Notify the team that translated articles have been published.

	The `publish` command prints an email template that you can modify for your purpose.




