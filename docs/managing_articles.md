## Managing articles

This article describes how to use the Zendesk production tools (ZEP) to perform the following tasks:

* [Pushing staged articles](#push)
* [Listing the followers of a content item](#follow)
* [Listing the votes of a content item](#votes)
* [Taking a snapshot of the knowledge base](#snap)
* [Adding a placeholder community post](#add_post)
- [Updating a placeholder community post](#update_post)
* [Deleting article comments](#comments)

<!--* [Archiving articles](#archive)-->

For installation instructions, see [Setting up the Zendesk production tools](https://support.zendesk.com/hc/en-us/articles/215841938).

<!--
title: Managing articles
url: https://support.zendesk.com/hc/en-us/articles/217117137
source: Zendesk Internal/Zendesk User Guides/production/zep/docs/managing_articles.md
-->

<h3 id="push">Pushing staged articles</h3>

This section describes how to push id-named articles to Help Center. This is typically done when you download a bunch of articles from Help Center, make some changes to them, and then need to upload them again.

**Note**: To download the files, use the ho.py loader file and `create` command.

1. In the CLI, run the following command:

    ```
    $ python3 hc.py push_staged {product} {folder_name} --locale {locale} --write
    ```

    where `{product}` is **bime**, **chat**, or **support** and `{folder_name}` is the name of the folder on staging containing your transformed HTML files. The default locale is 'en-us', so you can omit the optional locale argument.

	**Recommended**: Omit the `--write` argument to do a dry run to check for errors. The results are displayed in the console but the files aren't actually push to Help Center.

    Example:

    ```bash
	$ python3 hc.py push_staged bime classic_eol support --write
	```


<h3 id="follow">Listing the followers of a content item</h3>

You can list the followers of any article, section, topic, or post in Help Center.

* In the CLI, navigate to the **zep** folder and run the following command:

    ```
    $ python3 hc.py followers {product} [-a -s -p -t] {item_id}
    ```

	where one of `-a`, `-s`, `-p`, or `-t` identifies the content type of the item (article, section, post, or topic). For example, to list all the followers of the post with the id of 203458666:

     ```
    $ python3 hc.py followers chat -p 203458666
    ```

	The tool displays the list of followers of the post in the console.

	The only valid values for `product` (for now) are **bime**, **chat**, **help**, **explore**, or **support**.


<h3 id="votes">Listing the votes of a content item</h3>

You can list the votes on any article or post in Help Center. The information includes whether it was an up or down vote, the name of the person who voted, and their Zendesk user id.

* In the CLI, navigate to the **zep** folder and run the following command:

    ```
    $ python3 hc.py votes {product} [-a -p] {item_id}
    ```

	where one of `-a` or `-p` identifies the content type of the item (article or post). For example, to list all the votes for the Zopim post with the id of 210314047:

     ```
    $ python3 hc.py votes chat -p 210314047
    ```

	The tool displays the vote info in the console.

	The only valid values for `product` (for now) are **bime**, **chat**, or **support**.


<h3 id="snap">Taking a snapshot of the knowledge base</h3>

You can take a snapshot of all active, public articles in the knowledge base and record it in a JSON and an Excel file. The snapshot takes the following information about each article: **id**, **title**, **dita source**, **author**, **section id**, and **url**.

The tool skips any section that's viewable only by agents and managers. It also skips any articles in Draft mode.

1. In the CLI, navigate to the **zep** folder and run the following command:

    ```
    $ python3 hc.py snapshot {product}
    ```

	**Caution**: It takes a few moments to get all the information from Help Center. Be patient. For the same bandwidth reasons, don't run this command too often. The tool caches the data because the article inventory doesn't change that much over time.

	You can use the optional `categories` argument to take an inventory of specific categories. The default categories are defined in the **tools.ini** file during setup (typically the agent, admin, and developer categories). The `categories` argument overrides the default categories.

	Example:

	```bash
	$ python3 hc.py snapshot support --categories 23476576 24398732
	```

2. Open the **kb\_article\_inventory.xlsx** file in Excel. The file is located in the folder specified by the `public_data` setting in the **tools.ini** file. Example:

	`/Users/yourname/production/reports`


<h3 id="add_post">Adding a placeholder community post</h3>

You can use the ZEP tools to create a placeholder post authored by a specific author in the Zendesk, Bime, or Zopim communities. To prevent triggering notifications to subscribers for an empty placeholder post, the post is created in a restricted Drafts topic in each product's community -- 'support': 200133376, 'chat': 200661807, 'bime': 200674538.

**Note**: The API doesn't let you change the author of a community post once it's created.

#### What you need

To create the post, you need the Zendesk **user id** of the author, which you can get from the Zendesk admin interface by searching for the user and copying the id from their user profile's URL.


#### Add the community post


* In the CLI, navigate to the **zep** folder and run the following command:

    ```
    $ python3 hc.py create_post {product} {author_id}
    ```

	where `{product}` is **bime**, **chat**, or **support**, and `{user_id}` is the Zendesk user ID of the new author. If you don't specify a topic id, the post is created in the [Zendesk Drafts topic](https://support.zendesk.com/hc/en-us/community/topics/200133376).

	Example:

	```bash
	$ python3 hc.py create_post support 1801814128
	```

	The command creates a post titled "Placeholder post" by the specified user in the specified community. Go to the community's Drafts topic to verify it exists.


<h3 id="update_post">Updating a placeholder community post</h3>

Manually pasting content in a post results in extra line spaces and an ugly mess. There's no way to remove the extra spaces -- they keep coming back on update. It's a bug.

You can create and format the content in an HTML file and use the API to add it to the placeholder post with the formatting intact.

1. Create a HTML file with the content you'd like to publish in the post. Make sure the post title is an h1 heading.

2. Save the file in the **production/staging/posts** folder.

3. In the CLI, navigate to the **zep** folder and run the following command:

    ```
    $ python3 hc.py update_post {product} {post_id} {filename}
    ```

	where `{product}` is **bime**, **chat**, or **support**, `{post_id}` is the ID of the post to update (make sure it's accurate or you'll overwrite somebody's post!), and `{filename}` is the name of the HTML file in the **production/staging/posts** folder.

	Example:

	```bash
	$ python3 hc.py update_post support 209947128 my_post.html
	```

	The command adds the content of **my_post.html** to post 209947128. Go to the post to verify the content was added with no formatting problems.


<h3 id="comments">Deleting article comments</h3>

You can use the ZEP tools to delete some or all the comments of any knowledge base article in the Zendesk, Bime, or Zopim Help Centers.

The comments are saved in a backup file, just in case.

* In the CLI, navigate to the **zep** folder and run the following command:

    ```
    $ python3 hc.py archive_comments {product} {article_id} --before yyyy-mm-dd
    ```

	where `{product}` is **bime**, **chat**, or **support**.

	For example, to delete all comments created before 2016 in article 203661815, enter:

	```bash
	$ python3 hc.py archive_comments support 203661815 --before 2016-01-01
	```

	To delete all the comments, omit the `--before` argument:

	```bash
	$ python3 hc.py archive_comments support 203661815
	```

	Go to the article in Help Center to verify the change.


<!--
<h3 id="archive">Archiving articles</h3>

As of this writing, you can archive articles in the Announcements, Release Notes, or API Updates sections in the Zendesk HC. Each section has different archiving rules and different archive sections. These are specified in the cache/{product}/archiving_rules.json file.

* In the CLI, navigate to the **zep** folder and run the following command:

    ```
    $ python3 hc.py archive {product} {section_name} --write
    ```

	where `{section_name}` is **announcements**, **api_updates**, or **release_notes**, and  `{product}` is **bime**, **chat**, or **support** (although only **support** is supported for now).

	Example:

	```bash
	$ python3 hc.py archive support announcements --write
	```

	The command archives the articles based on the rules for the Announcements section in the cache/{product}/archiving_rules.json file. Go to the specified archive section to verify that the articles were archived.
-->



