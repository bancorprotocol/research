The AMM Book Webiste
=============================

[Gitlab][urlGitlab] - [Deploy][urlDeploy] - [Netlify][urlNetlifyControl]

[urlGitlab]:https://gitlab.com/oditorium/leaptest
[urlDeploy]:https://happy-bohr-aab536.netlify.app/
[urlNetlifyControl]:https://app.netlify.com/sites/happy-bohr-aab536/overview


## Hugo

To serve the site locally from 'vscode' run (default port:1313)

    hugo server --buildDrafts --buildFuture --watch -p 8080

If you want to check how it'll look on Netlify (without drafts and future) use

    hugo server --watch -p 8080

Note: if this command fails on MacOS, try

    hugo server --watch=False
    
To simply create the site run (in this directory) Hugo

    hugo


## Leap

**Note: the directory `static/vendor` is effectively the theme `asset` directory

### Manually browse pages

- unzip the zip file
- start at `file://path/to/theme/pages/index.html`

### Initial setup

- install node 14 (it breaks with node 16; use nvm)
- unzip the zip file (and look at the readme)
- run `npm install -g gulp-cli`
- go into the theme directory
- run `npm install`
- run `gulp`


### Links

- [Preview][leappreview]
- [Doc][leapdoc]
- [Support][leapsupp] [specific](mailto:support@mrare.co) (from gmail)




## References

- Content management 
    [gohugo.io](https://gohugo.io/content-management/page-resources/)
    [regisphilibert.com](https://regisphilibert.com/blog/2018/01/hugo-page-resources-and-how-to-use-them/)
    [template primer](https://knausb.github.io/2014/04/hugo-template-primer/)

- Multiline YAML [mlyaml](https://yaml-multiline.info)

- Hugo repo [templates](https://github.com/gohugoio/hugo/tree/master/tpl/tplimpl/embedded/templates)

- Some example code for parallax scrolling is [here](https://www.webnots.com/how-to-create-full-width-parallax-page-with-bootstrap-4-jumbotron/)
Note that is uses bootstrap's [jumbotron component](https://getbootstrap.com/docs/4.0/components/jumbotron/)

- Some info on image background repeat [here](https://stackoverflow.com/questions/41025630/css-background-image-stretch-horizontally-and-repeat-vertically)
Also on background image [here](https://www.w3schools.com/cssref/pr_background-image.asp)

- Sites with a nice layout we can borrow from
[inatba](https://inatba.org/) (*see the way the present the news*)
([members page](https://inatba.org/members/),
[events page](https://inatba.org/events/)
[news page](https://inatba.org/news/) (*not as nice as the front page...*)
[become a member](https://inatba.org/become-a-member/) (*has a nice Schedule a Call feature*)
[brochure](https://inatba.org/wp-content/uploads/2021/03/INATBA-Brochure-2021.pdf)
)
[sitemap]:https://discourse.gohugo.io/t/how-to-omit-page-from-sitemap/1126/3
[sitemap2]:https://gohugo.io/templates/sitemap-template/

# analytics-webpage



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/NIXBNT/analytics-webpage.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://gitlab.com/NIXBNT/analytics-webpage/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Automatically merge when pipeline succeeds](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing(SAST)](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://gitlab.com/-/experiment/new_project_readme_content:b43446066ca4942805d89909ebf7fff6?https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!).  Thank you to [makeareadme.com](https://www.makeareadme.com) for this template.

## Suggestions for a good README
Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.

