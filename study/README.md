# Study tools and run files

This folder is not part of the published website (Vercel serves only `what-did-they-say-site/what-did-they-say-site`).

- `conference-coding/` — the scripts and templates that run the study and build the site.
- `run-2026-10/` — the coding decisions and site copy for October 2026, coded from the official talk texts.

The talk texts themselves are not stored here; they belong to the Church and are read from churchofjesuschrist.org.

To rebuild the site after changing a run file:

    python study/conference-coding/scripts/build_report_page.py RUN OUT/master_codebook.json OUT/history.json OUT/report.html
    python study/conference-coding/scripts/build_site.py OUT/report.json what-did-they-say-site/what-did-they-say-site https://whatdidtheysay.church

Then add the Standard of Truth podcast links (talk pages and footers), after exporting them from the Litner repo:

    node scripts/export-wdts-links.mjs <this repo>/study/run-YYYY-MM/litner_links.json     (run in the Litner repo)
    python study/conference-coding/scripts/add_litner_links.py what-did-they-say-site/what-did-they-say-site study/run-YYYY-MM/litner_links.json

