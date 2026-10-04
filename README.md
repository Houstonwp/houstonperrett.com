# Houston Perrett's homepage

Source for https://houstonp.com/. The vendored Split theme and original attribution/license are preserved.

## Build and check

Use **Hugo extended 0.167.0** from the [official Hugo release](https://github.com/gohugoio/hugo/releases/tag/v0.167.0), and Python 3.12 or newer for the offline checks:

```sh
hugo --gc --minify
python scripts/check_site.py
hugo server
```

Netlify reads the same Hugo pin, build command, and `public` output directory from `netlify.toml`. GitHub Actions builds and checks the output without deploying. The CI installer verifies the official release archive checksum. Generated output, Hugo caches, and IDE state do not belong in Git.

## Metadata and domains

`config.toml` sets the canonical origin to `https://houstonp.com/`. The existing background photo is also the social-sharing image; its URL must resolve to an actual published asset. No analytics are loaded; a future analytics integration should be a deliberate choice.

Domain redirects live only in `netlify.toml`, preserve paths, and target HTTPS. The legacy and `www` aliases must already be attached to the same Netlify site with valid DNS/TLS for those rules to apply. Review domain ownership/settings and verify redirects after an authorized deployment; a local smoke check cannot prove the host's live routing.

The smoke check validates the homepage metadata, image, relative assets/internal links, removed Universal Analytics, template attribution, and redirect rules. It does not crawl external websites or replace visual review at mobile and desktop sizes.

## Browser checks

CI also installs the pinned Playwright test dependency from `requirements-test.txt`, checks 320/390/768/1280px layouts for horizontal overflow and broken images, and saves screenshots as the `site-previews` artifact. The resume check also produces Letter/A4 PDFs for human print review; generating a PDF alone is not a visual pagination approval. Run locally with:

```sh
python -m pip install -r requirements-test.txt
python -m playwright install chromium
python scripts/check_render.py
```
