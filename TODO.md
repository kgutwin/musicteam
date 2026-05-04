# TODO

## Frontend

- Not yet using updateSetlistPositions when manipulating setlist positions
- Preview lyrics on hover within song list?
- Rectangle whiteout in PDF annotation??
- Allow users to upload their own profile picture, change other profile details

## Backend

- Bucket maintenance
- Bulk endpoints (all songs, all setlists, etc.)
  - Export as CSV or JSON
- Semantic search
  - pgvector holds vectors per song version (lyrics)
  - Dedicated Lambda function uses `sentence-transformers` library with selectable
    model
    - be sure to pack the model into the Lambda layer at build time
  - SQS queue distributes encoding jobs to Lambda
  - Each function
    - extracts relevant lines
    - feeds the whole song lyrics (probably) into the model
    - stores the resulting vector in the database
  - then the API functions can easily find similar songs by comparing the vector from
    one song with the rest of the database

## Bugs

## Wishful improvements

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
