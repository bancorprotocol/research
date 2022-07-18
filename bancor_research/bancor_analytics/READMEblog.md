# How to create blogs

## Looping through pages

- extremely good article on ranges by [markusantonwolf][range]
- here on [ordering][order]

[order]:https://gohugo.io/templates/lists/#order-content
[range]:https://www.markusantonwolf.com/blog/loop-through-sorted-content-in-hugo/

Loop through a section

    <div class="my-12">
        {{ range where .Site.RegularPages "Section" "blog" }}
            <a href="{{ .RelPermalink }}" class="block">
                {{ .Title }} / {{ dateFormat "January 2006" .Date }}
            </a>
        {{ else }}
            <p>
                No articles found!
            </p>
        {{ end }}
    </div>

Sorted loops

    <div class="my-12">
        {{ range (where .Site.RegularPages "Section" "blog").ByTitle }}
            <a href="{{ .RelPermalink }}" class="block">
                {{ .Title }} / {{ dateFormat "January 2006" .Date }}
            </a>
        {{ end }}
    </div>

Built-in methods [here][order]: `ByTitle`, `ByWeight`, `ByDate`, `ByPublishDate`, `ByLength`. Also possible by parameter

    <!-- Ranges through content according to the "rating" field set in front matter -->
    {{ range (.Pages.ByParam "rating") }}
    <!-- ... -->
    {{ end }}

Reverse order eg by `range .Pages.ByDate.Reverse`



## APPENDIX

### Layout `postlist.html`

This is the part of the list layout that iterates over the posts; it requires the 
partial `pagination.html` below as well as the layout `summary.html` rendering 
a post summary. It must be located in the `layouts\default` folder.


    {{/* Iterate only over pages of the same type as this section. */}}
    {{ $paginator := .Paginate (where .Data.Pages "Type" .Type) }}
    {{ range $paginator.Pages }}
    {{ .Render "summary" }}
    {{ end }}
    {{ partial "pagination.html" . }}
    
### Partial `pagination.html`

This is the `pagination.html` partial that is needed by the `postlist` layout. It must be located in the `partials` folder.

    {{ if or (.Paginator.HasPrev) (.Paginator.HasNext) }}
    <div class="pagination-bar">
        <ul class="pagination">
        {{ if .Site.Params.swapPaginator }}
            {{ if .Paginator.HasPrev }}
            <li class="pagination-prev">
                <a class="btn btn--default btn--small" href="{{ .Paginator.Prev.URL }}">
                <i class="fa fa-angle-left text-base icon-mr"></i>
                <span>{{ i18n "pagination.older_posts" }}</span>
                </a>
            </li>
            {{ end }}
            {{ if .Paginator.HasNext }}
            <li class="pagination-next">
                <a class="btn btn--default btn--small" href="{{ .Paginator.Next.URL }}">
                <span>{{ i18n "pagination.newer_posts" }}</span>
                <i class="fa fa-angle-right text-base icon-ml"></i>
                </a>
            </li>
            {{ end }}
        {{ else }}
            {{ if .Paginator.HasPrev }}
            <li class="pagination-prev">
                <a class="btn btn--default btn--small" href="{{ .Paginator.Prev.URL }}">
                <i class="fa fa-angle-left text-base icon-mr"></i>
                <span>{{ i18n "pagination.newer_posts" }}</span>
                </a>
            </li>
            {{ end }}
            {{ if .Paginator.HasNext }}
            <li class="pagination-next">
                <a class="btn btn--default btn--small" href="{{ .Paginator.Next.URL }}">
                <span>{{ i18n "pagination.older_posts" }}</span>
                <i class="fa fa-angle-right text-base icon-ml"></i>
                </a>
            </li>
            {{ end }}
        {{ end }}
        <li class="pagination-number">{{ i18n "pagination.page" . }} {{ i18n "pagination.of" . }}</li>
        </ul>
    </div>
    {{ end }}

### Layout `summary.html`

This is the `summary` layout referred to in `postlist.html` (using the command `{{ .Render "summary" }}`). It is located in the `layouts\_default` folder. This is a pretty complex 
example because it has some advanced thumnail handling.

- `thumbnailImage`
- `autothumbnailimage`
- `gallery`
- `coverimage`
- `thumbnailimageposition`
- `readingtime`


    {{ if .Site.Params.thumbnailImage }}
    {{ if .Params.thumbnailimage }}
        {{ .Scratch.Set "thumbnailImage" (.Params.thumbnailimage | absURL) }}
    {{ else }}
        {{ if or .Params.autothumbnailimage (and .Site.Params.autoThumbnailImage (ne .Params.autothumbnailimage false)) }}
        {{ if .Params.gallery }}
            {{ range first 1 .Params.gallery }}
            {{ range first 1 (split . " ") }}
                {{ $.Scratch.Set "thumbnailImage" (. | absURL) }}
            {{ end }}
            {{ end }}
        {{ else }}
            {{ if .Params.coverimage }}
            {{ .Scratch.Set "thumbnailImage" (.Params.coverimage | absURL) }}
            {{ end }}
        {{ end }}
        {{ end }}
    {{ end }}
    {{ end }}
    {{ if or .Params.thumbnailimageposition .Site.Params.thumbnailimageposition }}
    {{ .Scratch.Set "thumbnailImagePosition" (.Params.thumbnailimageposition | default .Site.Params.thumbnailimageposition) }}
    {{ else }}
    {{ .Scratch.Set "thumbnailImagePosition" "bottom" }}
    {{ end }}
    <article class="postShorten postShorten--thumbnailimg-{{ .Scratch.Get "thumbnailImagePosition" }}" itemscope itemType="http://schema.org/BlogPosting">
    <div class="postShorten-wrap">
        {{ if and (.Scratch.Get "thumbnailImage") (eq (.Scratch.Get "thumbnailImagePosition") "top")}}
        <a href="{{ .Permalink }}">
            <div class="postShorten-thumbnailimg">
            <img alt="" itemprop="image" src="{{ .Scratch.Get "thumbnailImage" }}"/>
            </div>
        </a>
        {{ end }}
        <div class="postShorten-header">
        <h1 class="postShorten-title" itemprop="headline">
            <a class="link-unstyled" href="{{ .Permalink }}">
            {{ .Title }}
            </a>
        </h1>
        {{ partial "post/meta" . }}
        </div>
        <div class="postShorten-excerpt" itemprop="articleBody">
        {{ if .Params.Summary }}
            {{ .Params.Summary | markdownify }}
        {{ else }}
            {{ .Summary }}
        {{ end }}
        <p>
            <a href="{{ .Permalink }}" class="postShorten-excerpt_link link">{{ i18n "post.read_more" }}</a>
            {{ with .Params.readingtime }}
            <span class="postShorten-readingtime">
                {{ printf " - %s min read" . }}
            </span>
            {{ end }}
        </p>
        </div>
    </div>
    {{ if and (.Scratch.Get "thumbnailImage") (ne (.Scratch.Get "thumbnailImagePosition") "top")}}
        <a href="{{ .Permalink }}">
        <div class="postShorten-thumbnailimg">
            <img alt="" itemprop="image" src="{{ .Scratch.Get "thumbnailImage" }}"/>
        </div>
        </a>
    {{ end }}
    </article>
 
#### Example front matter

Example front matter for `summary.html`

    ---
    title: What is Ampleforth? 
    pcurlshort: What-is-Ampleforth-ehhic6
    date: 2020-07-30
    draft: false

    tags:
    keywords:
    categories:
    summary: |
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque 
        et consectetur erat, a ornare odio. Donec euismod, sapien ut aliquet 
        egestas, odio mauris gravida libero, pharetra lacinia nisi justo et nunc.

    autoThumbnailImage: true
    thumbnailImagePosition: left
    thumbnailImage: https://theshortstory-podcast.com/2020/07/what-is-ampleforth/coverimage_750x422.jpg
    coverImage: https://theshortstory-podcast.com/2020/07/what-is-ampleforth/coverimage_1920x1080.jpg
    metaAlignment: center
    coverMeta: out
    ---

#### Simplified `summary.html`

    <article class="postShorten" }}" itemscope itemType="http://schema.org/BlogPosting">

        <div class="postShorten-header">
            <h1>
                <a href="{{ .Permalink }}">{{ .Title }}</a>
            </h1>
            {{ partial "post/meta" . }}
        </div>

        <div class="postShorten-excerpt" itemprop="articleBody">
            {{ if .Params.Summary }}
                {{ .Params.Summary | markdownify }}
            {{ else }}
                {{ .Summary }}
            {{ end }}

            <p>
                <a href="{{ .Permalink }}" class="postShorten-excerpt_link link">
                    {{ i18n "post.read_more" }}
                </a>
            </p>
        </div>

    </article>

### Partial `post\meta.html`

This partial (located in partials) is used by `summary.html` to render meta data

    {{ if not (eq .Params.showMeta false) }}
    <div class="postShorten-meta post-meta">
        {{ if not (eq .Params.showDate false)  }}
        <time itemprop="datePublished" datetime="{{ .Date.Format "2006-01-02T15:04:05Z07:00" }}">
            {{ partial "internal/date.html" . }}
        </time>
        {{ end }}
        {{ partial "post/category.html" . }}
    </div>
    {{ end }}