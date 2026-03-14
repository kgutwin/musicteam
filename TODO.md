# TODO

## Frontend

- Preview lyrics on hover within song list?
- Rectangle whiteout in PDF annotation??
- Allow users to upload their own profile picture, change other profile details

## Backend

- Bucket maintenance
- Bulk endpoints (all songs, all setlists, etc.)
  - Export as CSV or JSON

## Bugs

## Wishful improvements

- Music packet loads slowly and there is no feedback that it is working
- User-selectable PDF viewer (between browser-native and PDF.js)
- Browse song revisions
- Drag to change order within candidate list / within setlist position
- Copy existing setlist?

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
- How do we represent "which version/sheet do I prefer?"

## Other

- Favicon and proper logo
- User documentation
- Revisit login token approach, maybe improve security
