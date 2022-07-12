Hugo Tips
=============================


## Multiline YAML

This is important syntax to know if the front matter contains HTML or markdown. [mlyaml](https://yaml-multiline.info)

    multiline: |
    this is a multiline string.
    newline characters are preserved.

    multiline: >
    this is a multiline string.
    newline characters are not preserved

    however, a blank line is a new line

    multiline: "
    this is a multiline string.
    newline characters are not preserved

    however, a blank line is a new line

    "

## Frontmatter codes

We are defining a number of frontmatter codes in the layouts (mostly single, but may
by carried to the others) that determine the way page looks. Default on all of them
is false, but not the positive vs negative wording

- `nocontainer` do not apply a container class to the surrounding div
- `islargefont` use a large font on the page
- `ismaxwidth` apply a maxwidth to the page content
- `nonavplaceholder` do not include a placeholder for the nav menu (ie page starts under the menu!)
- `topimage` if given, interpreted as url of an image for the top of the page; note intergation with _nonavplaceholder; size 1920x400 - 1920x600

Note: the `islargefont` and `ismaxwidth` are designed to give a comfortable reading
experience on mostly-text pages.

## shortcodes

Info in shortcode vs partials [here](https://jpdroege.com/blog/hugo-shortcodes-partials/). 
Docs [here](https://gohugo.io/content-management/shortcodes/)
and [here](https://gohugo.io/templates/shortcode-templates/).

A shortcode without parameters can be accessed via

    {{% shortcodename %}}

The shortcode then has access to the page and site parameters as

    {{ $.Page }}
    {{ $.Site }}

If parameters are passed to the shortcut they can be accessed via `{{.Get 0}}` for positional
parameters and via `{{.Get "name"}}` for named ones.

An interesting question is how to get variables into shortcodes. It apparently is not possible
to do this directly. However, interesting solution is 
[here](https://discourse.gohugo.io/t/solved-passing-front-matter-variables-to-shortocode/11103).
Firstly, shortcodes can read front matter params like this `{{ .Page.Params.myParam }}`. To make this
more dynamic, the name of the variable can be passed like this

    {{ index .Page.Params (.Get "some-shortcode-param" ) }}

Now this allows for consistent formatting on one _page_. However, sometimes I may want to use
site wide parameters. 


## range

See [here](https://knausb.github.io/2014/04/hugo-template-primer/) for examples. 

    {{range $index, $element := array}}
        {{ $index }} 
        {{ $element }} 
    {{ end }}

## with

The with construct allows to render something if and only if a parameter is defined (ie it does not fail is not). For example with the frontmatter

    ---
    myparam: 123<strong>test</strong>
    ---

the expression

    {{with .Params.myparam}}
    {{ . | safeHTML }}
    {{end}}

would render `123<strong>test</strong>`. Note that in this template we define two special parameters `pagecss` and `pagejs` that are rendered into the page head section if present.


## if isset

Including / excluding items depending on paramaters. Assuming the frontmatter is as follows

    ---
    noheader: true
    noheader: true
    nofooter: true
    nofootersubscribe: true
    nofootersecondary: true
    nofooterjs: true
    layout: plain
    ---

then the following code will show _not_ show the headers

    {{ if not (isset .Params "noheader") }}
    {{- partial "std/header.html" . -}}
    {{ end }}

Also if the `test` layout is as follows

    {{ define "main" }}
    {{ .Content | safeHTML }}
    {{ end }}

then there is no pollution from the template file and main code is rendered as is.


## lists, sorting and pagination

Standard pagination using the built in partial

    {{ range .Paginator.Pages }}
        <p>
          <a href="{{.Permalink}}">{{.Params.courseid}}</a>: <strong>{{.Params.coursename}} (Level {{.Params.level}})</strong> <br/>
          {{.Params.description}}
        </p>
    {{ end }}
    {{ template "_internal/pagination.html" . }}

Without pagination

    {{ range .Pages }}
        <p>
          <a href="{{.Permalink}}">{{.Params.courseid}}</a>: <strong>{{.Params.coursename}} (Level {{.Params.level}})</strong> <br/>
          {{.Params.description}}
        </p>
    {{ end }}

Only range over certain pages

    {{ range (where .Data.Pages "Type" .Type) }}
    <p>
        <a href="{{ .Permalink }}">
            {{.Date.Format "2 Jan 2006"}} --
            {{ .Params.tagline }}
        </a>
    </p>
    {{ end }}


Sorting the pages by the `sortorder` frontmatter parameter

    {{ range sort .Pages "Params.sortorder" }}
        {{ partial "icab/concentrationvignette" . }}
    {{ end }}

In this example the partial is as follows

    <p>
        <a href="{{.Permalink}}">{{.Params.concentration}}</a>: 
        <strong>
            {{.Params.concentration}} 
            (Level {{.Params.level}})
        </strong>
        <br/>
        {{.Params.description | markdownify }}
    </p>


## page resources

This is about how to access the content that is packed together with the page proper in a page bundle, eg for inlining it as oppose to jusy referring to it 

[regisphilibert.com](https://regisphilibert.com/blog/2018/01/hugo-page-resources-and-how-to-use-them/)

Matching by type

    {{ with .Page.Resources.ByType "image" }}
        <div class="Image">
        {{ range . }}
            <img src="{{ .RelPermalink }}">
        {{ end }}
        </div>
    {{ end }}

Matching by name (in template)

    {{ with .Resources.Match "images/carousel/*" }}
        <div class="Carousel__slide">
        {{ range . }}
            <img src="{{ .RelPermalink }}">
        {{ end }}
        </div>
    {{ end }}

Creating a shortcode to inline an image (that can be used directly)

    # shortcodes/img.html
    {{ $img := $.Page.Resources.GetMatch (.Get 0)}}
    <figure>
        <img src="{{ $img.RelPermalink }}" alt="(.Get 1)" />
        <figcaption>(.Get 1)</figcaption>
    </figure>

...that's how it is used

    {{< img "*overcooked-dough*" "Those cupcakes are way overcooked!" >}}

Creating a shortcode to inline an html

    # shortcodes/inline.html
    {{ $html := $.Page.Resources.GetMatch (.Get 0)}}
    {{ $html.Content | safeHTML }}


...that's how it is used in the content section (this code exists!)

    {{< inline "myfile.html" >}}


Inlining some resource (in template)

    <script>{{ (.Resources.GetMatch "myscript.js").Content | safeJS }}</script> 
    
    <img src="{{ (.Resources.GetMatch "mylogo.png").Content | base64Encode }}">

## site map

In order to keep some pages off the sitemap (those who have page param `nositemap` set as true) one can use the following sitemap template ([src][sitemap]):

    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {{ range .Data.Pages }}
        {{ if not .Params.private }}
        <url>
            <loc>{{ .Permalink }}</loc>
            <lastmod>{{ safeHtml ( .Date.Format "2006-01-02T15:04:05-07:00" ) }}</lastmod>{{ with .Sitemap.ChangeFreq }}
            <changefreq>{{ . }}</changefreq>{{ end }}{{ if ge .Sitemap.Priority 0.0 }}
            <priority>{{ .Sitemap.Priority }}</priority>{{ end }}
        </url>
        {{ end }}
    {{ end }}

This template should be called `sitemap.xml` and be placed in `layouts` ([src][sitemap2])# Bootstrap


## partials with arguments / scratch

see [mertbakir.gitlab.io](https://mertbakir.gitlab.io/hugo/pass-arguments-in-partials-hugo/)

    {{ .Scratch.Set "index" 0 }}
    {{ range $pages }}
    {{ $.Scratch.Set "index" (add ($.Scratch.Get "index") 1) }}
    {{ .Scratch.Set "index" ($.Scratch.Get "index") }}
    {{ partial "cards/post_card_classic.html" . }}
    {{ end }}

This can be accessed in the partial by `{{.Scratch.Get "index"}}`

## References

- Content management 
    [gohugo.io](https://gohugo.io/content-management/page-resources/)
    [regisphilibert.com](https://regisphilibert.com/blog/2018/01/hugo-page-resources-and-how-to-use-them/)
    [template primer](https://knausb.github.io/2014/04/hugo-template-primer/)

- Multiline YAML [mlyaml](https://yaml-multiline.info)

- Hugo repo [templates](https://github.com/gohugoio/hugo/tree/master/tpl/tplimpl/embedded/templates)

[sitemap]:https://discourse.gohugo.io/t/how-to-omit-page-from-sitemap/1126/3
[sitemap2]:https://gohugo.io/templates/sitemap-template/


