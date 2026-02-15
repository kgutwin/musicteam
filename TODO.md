# TODO

## Frontend

- Complete mobile layout
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

- on mobile, the PDF embed only shows the first page and you can't really scroll
  to the next page
- After adding a new sheet, it takes a while for the sheet to appear and there's
  no loading indicator to let you know it's reloading
- After editing a song's authors (or adding a new tag) the Filter option in the
  song listing doesn't reflect the new author/tag
- When toggling to two-page view in the setlist music packet, the existing PDF
  should go away and the Loading... pane should re-appear

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
