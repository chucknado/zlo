## Setting up the Zendesk production tools

The Zendesk production tools (ZEP) require Python 3.6 or above to run. They also use a number of third-party libraries that you must install on your system. Most of the libraries can be installed with short one-line pip commands.

This is a one-time only setup.

* [Installing Python 3](#python)
* [Installing BeautifulSoup](#bs)
* [Installing lxml](#lxml)
* [Installing requests](#reqs)
* [Installing arrow](#arrow)
* [Installing pandas](#pandas)
* [Installing YamJam](#yamjam) (a security precaution -- recommended but optional)

After installing the required libraries on your system, you can copy and configure the application:

* [Installing the ZEP files](#install_hob)
* [Configuring ZEP](#config_hob)
* [Downloading the image files](#images) (for loc handoffs)

To learn how to use the tools, see [Managing articles](https://github.com/chucknado/zep/blob/master/docs/managing_articles.md) and [Getting articles localized](https://github.com/chucknado/zep/blob/master/docs/localizing_articles.md).

<!--
title: Setting up the Zendesk production tools
url: https://support.zendesk.com/hc/en-us/articles/215841938
source: Zendesk Internal/Zendesk User Guides/production/zep/docs/setup.md
code git: ~/production/zep/
code remote: ~/Dropbox/repo/zep/
-->

<h3 id="python">Installing Python 3</h3>

Go to <http://www.python.org/download/> and install the latest stable production version of Python 3 for your operating system.

You can test the installation by running `python3 --version` on the command line. It should give you the Python version number.


<h3 id="bs">Installing BeautifulSoup</h3>

Beautiful Soup provides tools for navigating, searching, and modifying HTML trees. To learn more, see the [Beautiful Soup website](http://www.crummy.com/software/BeautifulSoup/). To install BeautifulSoup, run the following command in your CLI:

`$ pip3 install beautifulsoup4`


<h3 id="lxml">Installing lxml</h3>

The BeautifulSoup library relies on the [lxml library](http://lxml.de/) to parse HTML. To install lxml, run the following command in your CLI:

`$ pip3 install lxml`


<h3 id="reqs">Installing requests</h3>

The requests library simplifies making HTTP requests in Python. To learn more, see [Requests: HTTP for Humans](http://www.python-requests.org/en/latest/).  To install requests, run the following command in your CLI:

`$ pip3 install requests`


<h3 id="arrow">Installing arrow</h3>

The arrow library provides a human-friendly approach to creating, manipulating, formatting and converting dates, times, and timestamps in Python. To learn more, see [Arrow: better dates and times for Python](http://crsmithdev.com/arrow/). To install arrow, run the following command in your CLI:

`$ pip3 install arrow`


<h3 id="pandas">Installing pandas</h3>

The pandas library provides data structures and data analysis tools for Python. To learn more, see [pandas](http://pandas.pydata.org/). To install pandas, run the following command in your CLI:

`$ pip3 install pandas`



<h3 id="yamjam">Installing YamJam (optional but recommended)</h3>

The application uses a Zendesk API token to authenticate requests. You can use the [YamJam library](http://yamjam.readthedocs.org/en/latest/index.html) to keep your Zendesk API token more secure. It lets you keep your API token separate from your app on your system. It's especially useful for keeping sensitive data out of source control systems like git or bitbucket.

1. Get a secure API token from the Global Advocacy Ops team (contact: Jim Nestell).

2. Install and set up YamJam. See the [installation instructions](http://yamjam.readthedocs.org/en/latest/index.html#installation) in the YamJam docs.

3. Open **/.yamjam/config.yaml** in a text editor and create a variable for your API token. Example:

	```
	ZEN_API_TOKEN: soMelONgaPiTOken
	```

4. If you want to use the app to upload your handoffs to a vendor's FTP server, specify the server's login password:

	```
	VENDOR_FTP_PASSWORD: $omeftppa$$word
	```

	You'll specify the other FTP settings in the ini file.

5. Save the file.




<h3 id="install_hob">Installing the ZEP application files</h3>

Download and copy the ZEP application files to your system.

1. Go to https://github.com/chucknado/zep, click the green **Clone or Download** button on the right side, and choose **Download ZIP**.

2. Unzip and copy the folder to a folder that's easy to access from the command line. Example: **/Users/jdoe/tools/zep**.

	You'll run the app from the command line so you should keep the path short. To get to the example folder from the command line, you'd use the following command:

	```
	$ cd tools/zep
	```

3. Create a folder for your loc handoffs. This is where you'll download and manage the files in your handoffs. Example:

	**/Users/jdoe/production/handoffs**

4. Create a blank file named **_loader.txt** in your newly created **handoffs** folder. You'll use this file to list the article to download and include in any new handoff.

	**Note**: The underscore in the name ensures the file appears at the top of the alphabetical file listing.


<h3 id="config_hob">Configuring ZEP</h3>

1. Open the config file **zep/tools.ini** in a text editor.

2. In the `[HANDOFFS]` section, specify the following settings for your handoffs:
	* `locales` - List the language codes in which you translate your content. See [Language codes for Zendesk supported languages](https://support.zendesk.com/hc/en-us/articles/203761906). Example:

		```
		locales=de,es,fr,ja
		```
	* `path` - Specify the path to the handoffs folder you created in the previous section. Example:

		```
		path=/Users/jdoe/production/handoffs
		```

3. In the `[ZENDESK]` section, specify the settings for your Zendesk instance. For security reasons, you should store your Zendesk username and API token separately in local config file like a YamJam **config.yaml** file. In that case, ignore the `user` and `api_token` settings in the ini file and see [Install and configure YamJam](#yamjam).

	If you don't want to bother with YamJam, you can specify the username and API token in the ini file. Make sure to uncomment the lines (remove the semi-colon prefixes).
	* `user` - Specify your Zendesk user name, which is the email address registered in Zendesk. Example:

		```
		user=jdoe@example.com
		```
	* `api_token` - You can get the token from the Global Advocacy Ops team. Example:
		```
		api_token=qPbD4eZ67OTaXNC4aBUDs4UkHYDs6fFZlmZDjmSM
		```
	* `public_data` - (Optional) The tools can export data. Specify the folder where the tools should save the data. Example:
		```
		public_data=/Users/jdoe/production/reports
		```

4. In the `[KB]` section, specify the following settings:
	* `categories` - Specify the categories that contain your public-facing docs. Example:

		```
    	categories=200201826,200201976,200201986
    	```
    * `staging` - The tools can publish batches to articles to the KB. Specify the local folder where the tools should look for the batches. Example:
		```
		staging=/Users/jdoe/production/staging
		```

5. (Optional) If you want to use the app to upload your handoffs to your vendor's FTP server, specify the settings in the `[VENDOR]` section. You can store these settings separately in local config file like a YamJam **config.yaml** file. In that case, ignore these settings in the ini file and see [Install and configure YamJam](#yamjam).
	* `name` - the name of the vendor. Example:

		```
		name=Localizers
		```
 	* `ftp_host` - the ftp host name. Example:
 		```
 		ftp_host=ftp.locvendor.com
 		```
	* `ftp_user` - the username to log in to the server.
	* `ftp_password` - the password to log in to the server. Example:
		```
		ftp_password=lfws37i4
		```
	* `ftp_folder` - the destination folder to deliver your handoffs on the server


<h3 id="images">Downloading the image files</h3>

When putting together a localization handoff package, the tool includes the images cited in the articles' HTML. It gets the source image files from the **src** folder in the **handoffs** folder. For now, you must mirror the image files on the s3 server to your hard disk. A future version of the tools might access the images directly using the s3 API.

1. Create a folder named **src** in your **handoffs** folder. Example:

	**/Users/jdoe/production/handoffs/src**

2. In Cyberduck, go to the **/zen-marketing-documentation/docs/en** folder and select all the images.

	**Tip #1:** Filter the files on Cyberduck by file size to list the largest files at the top. Jason Maynard has some huge video files that should be ignored in the download.

	**Tip #2:** Press **Command+A** in Cyberduck to select all the images in the **en** folder. **Command-click** to deselect the files you don't want to download.

3. Select **Download To** in the **Action** menu on the toolbar, then select your new **src** folder as the destination folder to start the download.

You only need to download all the images once. In subsequent handoffs, you'll only download the subset of images that were created or updated images since the last handoff.




