# MangaDex repository (for my manga reader)

A tiny repository with one source: **MangaDex**, through its official public API.
Sources here are plain JSON files that describe an API. They contain no code and cannot run anything on a user's PC.

```
index.json            <- the link users paste into the app (generated)
sources/mangadex.json <- the source definition
tools/make_index.py   <- regenerates index.json with SHA-256 checksums
.gitattributes        <- forces LF line endings so checksums stay valid
```

## Publish it on GitHub (free)

1. Create a **public** repository on GitHub (for example `my-manga-repo`).
2. Run, with your own details:
   `python tools/make_index.py --base-url https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main`
3. Upload all files to the repo (keep the folder layout), branch `main`.
4. The link to paste into the app's Repositories screen is:
   `https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/index.json`

If the app reports a checksum mismatch: the file on GitHub is not byte-identical to the one that was hashed
(usually Windows CRLF line endings, or you edited a source without running `make_index.py` again).

## Updating

Edit the source file, raise its `"version"`, run `make_index.py`, upload both files.

## index.json format

```
{ "name": str, "version": int,
  "sources": [ { "id", "name", "language", "version", "url", "sha256", "domains": [..], "description" } ] }
```

`domains` is copied from the source file. The app shows it to the user before installing and must refuse any request to a host not on the list. A leading `*.` matches subdomains.

## Source format (schema_version 1)

Top level: `schema_version, id, name, version, languages, default_language, description, official_api, domains, headers, search, chapters, pages`.

**Variables** usable inside URLs, params and templates:
`{query}` search text, `{offset}` computed from the page number and `page_size`, `{lang}` selected language,
`{manga_id}` id of the manga, `{chapter_id}` id of the chapter.

**Requests:** `url` plus `params`. A list value becomes a repeated parameter (`"includes[]": ["a"]` sends `includes[]=a`).
`params_with_query` / `params_without_query` are merged in depending on whether the search text is empty.
Only `https` URLs on declared domains.

**Field specs** (used under `fields`, evaluated against each result item):
- `"a.b.c"`: a dot path. Path segments can contain `{lang}`. A segment `*` means "the first value of that object".
- `{"path": p, "default": x}`
- `{"first_of": [p1, p2, ...], "default": x}`: first non-empty value.
- `{"template": "...{name}...", "vars": {name: spec}, "default": x}`: builds a string. If any variable is empty, `default` is used.
- `{"find": {"path": list_path, "where": {k: v}, "value": p}}`: in the list at `list_path`, take the first element whose fields match `where`, and return `value` from it.

**Chapters:** `results_path`, `pagination` (`page_size`, `total_path` for paging until everything is read),
`skip_if` (conditions `not_null` / `equals`), `dedupe_by` (keep the first item per value), `fields`.

**Pages:** one request, `vars` (paths into the response), `list_path` (list of items), `item_template` (`{item}` is each list element).

The app maps the results to its own shapes:
manga `{id, title, description, cover_url, source_name}`, chapter `{id, number, title, source_name}`, pages `[url, ...]`.

## Notes

- Unknown fields must be rejected by the app, so this format has no comments inside the JSON files.
- Read MangaDex's API documentation and terms (rate limits, acceptable use) before publishing a repository that others will use.
- Page images come from servers MangaDex picks at request time. Check during testing that the hosts you see are covered by `domains`, and add any that are missing (then bump the version and rerun `make_index.py`).
