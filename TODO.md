# TODO

## Frontend

- Complete mobile layout
- Should be able to annotate an existing PDF and save as a new version or new sheet
- Public link to lyrics for congregation
- Browse song revisions
- Drag to change order within candidate list / within setlist position
- Copy existing setlist?
- Preview lyrics on hover within song list?
- Rectangle whiteout in PDF annotation??
- Allow users to upload their own profile picture, change other profile details

## Backend

- Cache packets so they load faster
- Bucket maintenance
- Bulk endpoints (all songs, all setlists, etc.)
  - Export as CSV or JSON

## Bugs

- Copy to New Version option doesn't really work...
- PDF editing seems broken - there are errors in the console
  - only on Safari 17.2.1, not on 26.1 ? must test other browsers
- on mobile, the PDF embed only shows the first page and you can't really scroll
  to the next page

## Wishful improvements

- Music packet loads slowly and there is no feedback that it is working
- User-selectable PDF viewer (between browser-native and PDF.js)

## Performance

- Check on the performance of refresh stores
  - wonder if the Promise.all method would help there too
- A ping on every request is adding a substantial delay
  - it would be better to catch DatabaseResumingException when executing the query
    and auto retry
  - we should then find the right way to execute schema upgrades

## Think through

- Do we need tags on song versions and song sheets?
  - How should they be shown, and how do we avoid confusion with song tags?

## Other

- Favicon and proper logo
- User documentation
- Revisit login token approach, maybe improve security
