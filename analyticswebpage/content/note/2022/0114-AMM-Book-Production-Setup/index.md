---
title: The AMM Book production setup
draft:
date: 2022-01-14


---

This is the 3rd book I am writing -- the first one was part of the [PRMIA Handbook][prmia] and the second one was my [book on financial regulations][finreg], and every time I decided about 2 seconds after I started writing that writing in Word is _not_ and option. For the PRMIA Handbook this was a no-brainer -- I had to include a lot of formulas, and the old formula editor sucked even more than the current one, so it was clear that something like LaTeX was the only option. Of course LaTeX was not on option either, because c'mon -- LaTeX sucks as bad as Word, just in a different way. LaTeX / TeX really only works for formulas -- but this has been ported to MathJax a while back, and the most serene way of writing not too complex stuff is really **Markdown + MathJax**.

The question used to be which editor to use -- I used TextMate and then Atom -- but nowdays the question is pretty much sorted. It is extremely hard to beat Microsoft's **VSCode**. It is the Python of text editors, and it has a plugin for everything. In particular it has a plugin for Markdown that allows you to open a window that renders a preview -- formatting, formulas, even images -- and the preview scrolls together with the source. It also includes **git** integration, and even though I do prefer git from the command line (with my own shortcuts defined) this is actually quite neat. And of course git is extremely useful for keeping track of the history of the book.

For papers one may get away with a single markdown file, but for a book this becomes a bit heavy. Also at least I generally like to move things around a bit and copying and pasting in a file with 100,000 lines becomes a bit tedious. Instead I am writing everything into **numbered files**, say `100_intro.md`, `200_stuff.md` etc. I then use **Python** to find those files, sort them alphabetically, and concatenate them. And when I say I use Python I really mean I use **Jupyter Notebooks** because what better way of writing Python? And when I say I use Jupyter Notebooks then I mean I use them with JupyText. 

So what is **JupyText**? That is a pretty neat Jupyter plugin (which for some weird reason is not part of **Anaconda**) that saves Jupyter Notebooks in multiple, synchronised formats at the same time. There are various options, but I am actually saving them as raw Python files. This has a number of advantages

- **Source Control.** Jupyter notebooks suck in git because of all the json output that completely screws up the diffs. If you exclude the .ipynb and only check the .py into git the diffs suddenly become meaningful.

- **Execution.** The JupyText .py files are python executables, so rather than running nbconvert they can be run via python; so only thing that does not work is the bang execution of commands (eg `!ls`).

- **Editing.** Sometimes you just want to edit your code in a proper editor, not the one provided by the Jupyter notebook, say if you want to do some multi cursor editing, or some advanced search and replace. JupyText allows for that -- if you change the .py and reload the .ipynb it includes the changes.

Now admittedly I may go a bit overboard, but I am happy to spend a lot of time avoiding repetitive tasks and automate processes. So all my markdown files have **YAML** frontmatter, a bit like Hugo (I have done this before Hugo though). For the Finreg book this was pretty elaborate because in the second part of the book I have highly structured content, so I packed all of this into front matter (pro-tip: use `tag: |` for yaml text tags that allow multiline strings, and that allow you to in particular include markdown inside of yaml). Here it is a bit more pedestrian. I mostly use the front matter for tags. Eg here

    tags: book, paper, papertex
    ---

    # Key concepts

    There are a number of ways to formalize the response function. 

This means that this file is part of the book, part of the paper, and part of the paper that is being produced in TeX (see below). The Python code then chooses what to include.

I also have pure yaml files. Those can be section or chapter headings (this has to do with the fact that heading levels are different for the book and the paper, and I want to use `# Heading` in the markdown). More excitingly, yaml files also allow me to integrate other data sources. For example here

    type: xlstable
    md_pre: |
      ### General Glossary
    table: glossary.xlsx
    justify: left
    md_post: |
      Lorem ipsum dolor
      sit amet
    tags: book, paper

This is the glossary table. This is part of the book and the paper (but not the latex paper). Its source is the file glossary.xls, the table is left aligned, and there is markdown before and after the table (see the multiline syntax with the `|`). The `type: xlstable` is some generic table rendering code that reads the first page of the xlsx (using `pandas` of course) and renders it. I also have more specific routines. Eg `reftable` looks for specific column headings and renders the bibliography as nicely formatted list.

Once I have my markdown, what then? There are multiple pathways, and most involve **pandoc**, plus **pdflatex** from **TeX Live** and **Hugo** for the website. Specifically

1. convert markown to html using pandoc (or python)
1. convert markdown (or html) to docx using pandoc
1. convert markdown to latex using pandoc
1. convert latex to pdf using pdflatex
1. convert docx to pdf using Word
1. convert markdown or html to web pages using Hugo

Not all of those pathways are equal. 3+4 is nice as it goes straight into pdf without manual intervention. The downside is that it is ugly and that I did not get the tables to work (did I mention I hate LaTeX more than I hate Word?). So I am using this for the ugly paper. 

I am also producing a pretty version of the paper, the same way we produced the [Bancor v2.1][bancor] and [Uniswap IL][uni] papers: the docx created by pandoc uses proper Word styles. If you paste it into a template document with appropriately defined styles it looks pretty neat. Also you can deal with things like the title page, the table of contents, header, footer and page numbers in Word.

Also one thing that is pretty neat: pandoc allows you to include openxml into the md file (also html for that matter, but this is less useful). So for example to create a page break you can use that following formstring with `type=page`

    _BREAK = """```{{=openxml}}
    <w:p>
    <w:r>
        <w:br w:type="{type}"/>
    </w:r>
    </w:p>
    ```
    """

And to render `text` in style `style` you can use the following format string:

    _STYLEDTEXT = """```{{=openxml}}
    <w:p>
        <w:pPr>
        <w:pStyle w:val="{style}" />
        </w:pPr>
        <w:r>
        <w:t xml:space="preserve">{text}</w:t>
        </w:r>
    </w:p>
    ```
    """.strip()

There is a lot more you can do; you can just look this up in the docx file after unzipping it (docx files are simply zip archives containing mostly xml files).

I think that's it. May sound complex, but ultimately it saves a lot of time. And nuisance, because neither Word nor LaTeX are fit for serious writing in my view.

[prmia]:https://prmia.org/Public/PRM/PRM_Exam_Preparation_Resources.aspx
[finreg]:https://thefinregbook.xyz/
[bancor]:https://drive.google.com/file/d/1en044m2wchn85aQBcoVx2elmxEYd5kEA/view
[uni]:https://arxiv.org/pdf/2111.09192





