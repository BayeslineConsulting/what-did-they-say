#!/usr/bin/env python3
"""Add Standard of Truth podcast links to the built What Did They Say? site.

  python3 study/conference-coding/scripts/add_litner_links.py what-did-they-say-site/what-did-they-say-site study/run-2026-10/litner_links.json

Run after build_site.py (it rewrites the pages). litner_links.json comes from the Litner repo:
  node scripts/export-wdts-links.mjs <this repo>/study/run-YYYY-MM/litner_links.json
It lists, for each talk, Standard of Truth episodes that read on air a scripture the talk cites.

Adds, between <!--litner--> markers so it can be rerun safely:
- on each talk page with matches, an "On the Standard of Truth podcast" section before the previous/next links
- in every page footer, a link to SOT Litner
"""
import glob, html, json, os, re, sys, urllib.parse

def main(site, links_path):
    data = json.load(open(links_path))
    litner, talks = data['litner'], data['talks']
    footer_link = ('<!--litner--> · <a href="%s">Standard of Truth podcast: search every episode</a><!--/litner-->' % html.escape(litner))
    n_talk = n_foot = 0
    for path in glob.glob(os.path.join(site, '**', 'index.html'), recursive=True):
        page = open(path, encoding='utf-8').read()
        page = re.sub(r'<!--litner-->.*?<!--/litner-->', '', page, flags=re.S)
        # footer
        m = re.search(r'(<a href="/[^"]*methodology/">Full methodology</a>)', page)
        if m:
            page = page.replace(m.group(1), m.group(1) + footer_link, 1); n_foot += 1
        # talk pages
        parts = path.replace('\\', '/').split('/')
        if 'talks' in parts and parts.index('talks') == len(parts) - 3:
            slug = parts[-2]
            eps = talks.get(slug) or []
            if eps and '<nav class="pn">' in page:
                title = re.search(r'<p class="ttl">(.*?)</p>', page)
                q = html.unescape(title.group(1)) if title else ''
                rows = ''.join(
                    '<a class="lcard" href="%s" rel="noopener"><small>%s · at %s</small><b>%s</b><span>Gerrit and Richard bring up %s on air.</span></a>'
                    % (html.escape(e['url']), html.escape(e['episode']), html.escape(e['at']), html.escape(e['title']), html.escape(e['ref']))
                    for e in eps)
                sec = ('<!--litner--><div class="sec"><h2>On the Standard of Truth podcast</h2>'
                       '<p class="note">Episodes where historian Dr. Gerrit Dirkmaat and Dr. Richard LeDuc bring up a scripture this talk cites. Each link starts at that minute.</p>'
                       '<div class="lcards">%s</div>'
                       '<p class="note" style="margin-top:10px"><a href="%s/search?q=%s">Ask the Crack Research Staff about this talk’s topic →</a></p></div><!--/litner-->'
                       % (rows, html.escape(litner), html.escape(urllib.parse.quote_plus(re.sub(r'[“”"]', '', q)))))
                page = page.replace('<nav class="pn">', sec + '<nav class="pn">', 1); n_talk += 1
        open(path, 'w', encoding='utf-8').write(page)
    print('talk pages with podcast links:', n_talk, '· footers linked:', n_foot)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
