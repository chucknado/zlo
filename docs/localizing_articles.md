## Getting articles localized

This article describes how to use the Zendesk production tools (ZEP) to prepare localization handoffs and publish the localized articles and images returned from the vendor.

For installation instructions, see [Setting up the Zendesk production tools](https://github.com/chucknado/zep/blob/master/docs/setup.md).

Workflow for creating a handoff:

1. [Update the article database](#update_db)
2. [Create the handoff package](#create_package)
3. [Hand off the files](#handoff_files)

Workflow for publishing a handoff:

1. [Prepare the localized content](#prep_loc_content)
2. [Relink the files for Help Center](#relink)
3. [Push the files to Help Center and s3](#publish)


<!--
title: Getting articles localized
url: https://github.com/chucknado/zlo/blob/master/docs/localizing_articles.md
source: repo/zlo/docs/localizing_articles.md
-->


<h3 id="update_db">Update the article database</h3>

1. Review the handoff articles from the [loc handoff worksheet](https://docs.google.com/spreadsheets/d/1jldaCDT5iYrUdmzAT1jWwFbYOwGECVVcwK9agHJeGE8/edit#gid=0) in Google Docs.

	Make sure all new articles, including non-DITA-sourced articles such as announcements, are flagged.

2. Open the following file in our Team Drive:

	`Documentation/Zendesk User Guides/All products/production/articles.yml`

3. Add any new articles in the handoff to the **articles.yml** file.

	For each DITA-sourced article, specify the DITA filename without the file extension, the Help Center subdomain, and the article id. Example:

	```
    - dita: zug_placeholders
      hc: support
      id: 203662116
    - dita: zug_markdown
      hc: support
      id: 203661586
    ...
	```

	For articles that aren't sourced from DITA files, such as announcements, specify **null** as the `dita` value:

	```yml
	-  dita: null
	   hc: support
	   id: 2062361521
	```

	Make sure the article id is unique in the yml file. Also, don't include the **.dita** extension.

4. Save the file.

Rules:

* Indent lines as shown (it matters in yml)
* No tabs
* No EOL commas or quotation marks around strings
* No duplicate ids
* One yml item per article (indicated by the hyphen)
* No **.dita** file extension


<h3 id="create_package">Create the handoff package</h3>

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
	
4. Manually add any vector source files (.psd, .ai) to the appropriate **images** folder in the handoff. Example: Images with callouts in text layers.

	**Note**: Gerhard will query you about any bitmap image containing text that's not displayed in the UI. Translators update text layers; they don't recreate images.

5. Review the images for any that don't show a localized UI. Move any you find and add their filenames to the **production/localization/image\_skip\_list.txt** file.

The `create` command downloads the default-language articles from your Help Center into a new **handoffs/2018-12-24/** folder. 

It also downloads the articles' images from Amazon S3. It skips the following images:

- Any image in the skip list (images with no localized UI like icons)
- All images in the articles specified in the `no_images` command-line parameter
- Any image not hosted on S3, such as images hosted on Help Center
- Any image that has a more recent localized version on S3. It means the the English version hasn't been updated since the last handoff. The fr images are used for comparison



<h3 id="handoff_files">Hand off the files</h3>

The article and image files need to be zipped and uploaded to the Localizers FTP server.



1. Zip the handoff folder and upload it to the Localizers FTP server using Cyberduck.

2. Notify Gerhard and Sabine that the handoff is up.


<h3 id="prep_loc_content">Prep the localized content</h3>

After the localized content comes back from the localizers, you need to place the files in your handoff folder. You also need to scan the files to update the *links registry*. The links registry lists all the articles and images that are known to have been localized. It's used to update the links in the returned files.

Vendors ignore the HTML attributes in the files we hand off. That means the article and image links in the returned files still point to English destinations. The links registry is used to decide whether to update the links or not. If a link points to an article or image in the registry, then the link is updated. If not, the link is ignored.

1. In the folder with the other files for this handoff, create a folder named **localized**. Example:

	`handoffs/2016-12-14/support/localized/`

2. Copy the locale folders (DE, ES, FR, JA, PT) delivered by the vendor into this folder.

	**Tip**: Work with a copy of the returned files. In case something goes wrong and you need to revert, you can always make another copy of the original files.

	The folder structure should look as follows:

	```
	handoffs/
		2016-12-14/
			support/
			    articles/
			    images/
			    localized/
				    DE/
					    articles/
					    images/
				    ES/
					    articles/
					    images/

				    FR/
					    articles/
					    images/
	```

3. If the Portugese folder is named **PT**, change it to **PT-BR** so it matches the Help Center locale.

4. Check the **images** folder of each language to make sure the image files are in the root. Sometimes the folder will contain a **fullsize** and a **resized** folder. Move the images of these folders into the root and delete the subfolders.

5. Do a global search for and delete the tag `<!---delete---!>`, which is a translation artifact that screws up the parsing scripts.

6. In the CLI, navigate to the **zep** folder and run the following command to update the links registry:

	```bash
	$ python3 ho.py register {handoff_name} {product} --write
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py register 2016-08-23 bime --write
	```

	The command adds new localized articles and images to the product-specific registry. Any links that point to these resources will be updated.

	**Recommended**: Do a dry run first to check for errors by omitting the `--write` argument. The results are displayed in the console but the registry isn't updated.

	The command also has the following optional arguments:
	* `articles` - add only articles to the registry
	* `images ` - add only images to the registry
	* `locales` - scans only the files in specific locale folders

	For example, to do a dry run of (1) scanning only the de and fr folders and (2) adding only new articles:

	```bash
	$ python3 ho.py register 2016-08-23 support --articles --locales de fr
	```


<h3 id="relink">Relink the files for Help Center</h3>

Before pushing the articles to Help Center, you need to update the article and image links where applicable. This applies only to links pointing to known localized content on Help Center. Because we don't track localized content outside Help Center, we can't automate the process of updating those links.

* In CLI, run the following command to update the article and image links in the articles:

	```bash
	$ python3 ho.py relink {handoff_name} {product} --write
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py relink 2016-08-23 bime --write
	```

	The command updates article and image links.

	**Recommended**: Do a dry run first to check for errors by omitting the `--write` argument. The results are displayed in the console but the files aren't updated.

	The command also has the following optional arguments:
	* `hrefs` - update only article links (hrefs)
	* `srcs ` - update only image links (srcs)
	* `locales` - update only the files in specific locale folders

	For example, to do a dry run of updating only the article links in the es and pt-br folders:

	```bash
	$ python3 ho.py relink 2016-08-23 support --hrefs --locales es pt-br
	```


<h3 id="publish">Push the files to Help Center and S3</h3>

**Note**: If publishing to a new section in Help Center, make sure translations of the article's parent section exists (as well as translations of the section's parent category).


1. Use Cyberduck to upload all the images to the appropriate locale folders on s3.

2. In the CLI, run the following command to publish all the translations to Help Center:

	```bash
	$ python3 ho.py publish {handoff_name} {product} --write
	```

	The only valid values for `product` (for now) are **explore**, **bime**, **help**, **chat**, or **support**. Example:

	```bash
	$ python3 ho.py publish 2016-08-23 bime --write
	```

	**Recommended**: Do a dry run first to check for errors by omitting the `--write` argument. The results are displayed in the console but the files aren't actually published.

	The command also has a `locales` optional argument to publish only the content for a specific language or languages. Example:

	```bash
	$ python3 ho.py publish 2016-12-24 support --locales de es --write
	```

3. Notify the Docs team, Yoko Drain, and In Ju Hwang of the new translated articles.

4. Zip the handoff folder and upload it to **Team Drives/Documentation/All products/production/loc handoffs**.





