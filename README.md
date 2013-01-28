# PÿronBlogger

Originally by Nelson Elhage for MIT Iron Bloggers, adapted by Marcus "chaosblog", finally hacked to pieces by me.

*Use if you like, don't use if you don't, complaints will be ignored, patches will be welcomed.*

## Installation

1. Clone this repo

    `git clone git@github.com:moeffju/iron-blogger.git`

2. Create a virtualenv in the repo:

    `cd iron-blogger`  
    `virtualenv .`  
    `source bin/activate`

3. Install the required dependencies:

    `pip install lxml pyyaml feedparser dateutils mako xmlrpclib`
    
    You will also need to install `ledger` and `mutt`, preferably using your distro's package manager. For Debian, simply use `apt-get install ledger mutt`.

## Configuration

1. Configure your settings:

  `cp settings.cfg.dist settings.cfg`  
  `vi settings.cfg`

  In the `[general]` block, configure the e-mail address that receives the reports, and the start date of your iron blogger run (in YYYY/MM/DD format).

  In the `[blogsettings]` block, set `xmlrpc_endpoint` to the full URI of your blog's XMLRPC endpoint (for WordPress blogs, that is the blog's base URI + /xmlrpc.php). `blog_id` is usually 0, if not, you will know. `username` and `password` are the user data of a user that is allowed to write new entries (for the reports) and edit pages (for the participants list). `participants_page_id` is the ID of a page that will be overwritten with the participants list. Get the ID from the URL when you edit the page.

2. Configure your bloggers:

  `vi bloggers.yml`

  For each participant, add one entry like this:
  
    ```
    twitter_nick:
      links:
      - ['Title of the first blog', 'http://example.org/blog']
      - ['Second blog title', 'http://example.com/', 'http://example.com/author/mattness/rss']
      name: 'Name of this blogger'
      start: 2012/12/31
      twitter: yes
    ```

  `twitter_nick` must either be the participants Twitter nickname, or if they don't have a Twitter account, something that would work as a Twitter nickname (i.e. no spaces, no dashes, no high-ascii characters, etc.). If someone doesn't have a Twitter account, also change `twitter: yes` to `twitter: no`.
  
  Each participant can have any number of blogs. If they post in either of them during one week, they are being counted. If they fail to blog in any, they will count as missing that week. For each blog, add a line in the format `- ['Title', 'Blog URL', 'Feed URL']`. Feed URL is optional (see first example line); the `import-feeds.py` script will try to complete feed URLs if they are missing. However, sometimes the script fails to find a feed, so you will have to know where to add it to the list.
  
  The `name` can be anything. If it contains single quotes, just escape them by doubling them, like this: `name: 'Matthias''s cool blog!'`.
  
  The `start` date is the date of the first day in the first time period in which this blogger participates in the iron blogging, in YYYY/MM/DD format.

3. Find missing feeds

  Run `./import-feeds.py` to try and automatically find missing feed URLs.

4. Create the working git branch

  All data is kept in a `ledger` file in a `ledger` git branch, so create one:
  
  `git branch ledger`

## Test run

Run `./scan-feeds.py` to download and parse all feeds and write a report file (`out/report.yml`). This will throw errors or even fail catastrophically on broken or invalid feeds. If that happens, take those feeds out of your config and yell at the people who provide invalid feeds. Point them to [feedvalidator.org](http://feedvalidator.org/). Repeat until you get a successful run of the script.

Now get some test output: Run `./weekly-update.py -n YYYY-MM-DD`, replacing YYYY-MM-DD with the first day in the time period you want to run a report on. This date must be *after* the start date you specified in `settings.cfg`, obviously. You will get a weekly report on the standard output. No mail will be sent, ledger entries won't be persisted, and no report will be posted to your blog. If the output looks erroneous, good luck finding and fixing the error. Otherwise, you're good to go.

## Normal periodical run

Once everything is configured, the periodical run looks like this:

```
./update-participants.py
./scan-feeds.py
./weekly-update.py 2013-01-07
```

You can automate this in a shell script that you run from cron. To calculate the correct date to give to `weekly-update.py`, you can use `date`. If you don't know how, you should be running the script manually, or maybe not at all.

## Adding and removing bloggers

To add new bloggers, just add them to `bloggers.yml` with the correct `start` date and run `./import-feeds.py`.

To remove bloggers, either add an `end: YYYY/MM/DD` key to their entry in `bloggers.yml`, or just delete their entry.

## Skipping weeks

To let someone skip one or several weeks, simply add a key `skip: [MM/DD/YYYY, MM/DD/YYYY, …]` to their record. (Yes, this is a different date format. Not my fault. I didn't code it, and I'm too lazy to fix it. Patches are welcome, though.)

