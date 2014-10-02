jenkins-branch-wall
===================

A WEB page displaying status of feature branches - for GIT and maybe more ...

Jenkins is a really wonderfull tool, but is really cr**py when it comes to feature branches.

I've been using Jenkins with GIT for few years now.
It's really powerfull handling 'master' and 'next' : you can have a clear view of the status of theses branches. When it comes to features branches, specially when you have plenty, you can't have a clear view of the status of each branch.

Some plugins exists but none of them were satifing my needs. Most of them use a template to create one job per branch. At the end you have as many jobs as feature branches. Good solution if you have few features, in the other case your continous integration looks like yellow pages.

Some example of plugins:
- [Jenkins build per branch](http://entagen.github.io/jenkins-build-per-branch/)
- [Jenkins autojobs](http://gvalkov.github.io/jenkins-autojobs/)


A simple solution is to configure a special job for features branches.
Let's assume your repository have this branch naming convention :
- master : current,
- next : preparation of the next release,
- feature/xxxxxx : developpement of a new features,
- ticket/xxxxx : correction of bugs submited via your bugtracking portal.

It's easy to configure a "branches" jobs that will run on every branch except master and next (these should be tests by dedicated jobs). To achieve this you just have to specify "origin/*/*" in the "Branches to build" / "Branch Specifier (blank for 'any')" in the configuration of the job.

You have a job that runs on every branch ! Pretty cool. But ... (there's always a but after a cool) the main view of jenkins only shows the last results. It means that if the jobs ran on 3 diffent branches the main view will only show the result of the last run. The two preceding won't appear on the view. Of course you can ask jenkins to send emails, tweets, irc, ... but you will never get a simple and clear view of the state of your branches witch is really essential to me and my collegues. Having a simple and clear view just in front of your eyes is a key point to be reactive.

So I need a solution that show the result of each (feature) branch on a single page.
I wrote a little script that keep a trace of each build result and is able to build an HTML table from these. This is simple an efficient. As the script build an HTML table, it was obvious that it should be hosted on a web server.
Using the [notification plugin](https://wiki.jenkins-ci.org/display/JENKINS/Notification+Plugin), Jenkins is able to notify the build status of each job by sending a short summary of the build to an URL. In this summary, jenkins send the build result (failed / success), the SCM branch (yeessss !), a link to the build result page and others stuffs.


To use this script :
- deploy this script on a http server with python installed on it,
- add the Job Notifications plugin to Jenkins
- configure the job with a notification endpoint :
-- Format		 JSON
-- Protocol	 HTTP
-- Event		 Job finalized
-- URL       <the URL of your web server>/branches_status.py?variant=status
-- Timeout (in ms)	What you thing is ok (3000ms should be sufficient)

