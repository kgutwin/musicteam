# TODO

## Frontend

- in main set list, swap label and presenter columns
- Preview lyrics on hover within song list?
- Show participants in active set list sidebar
- Collapsible candidates in active set list sidebar

* Setlist templates
* Roles
  - hide edit buttons
  - Manager can change team member roles
  - Manager gets a NavBar notification for pending members
* Comments
* Media links
* Complete mobile layout
* Should be able to annotate an existing PDF and save as a new version or new sheet
* Copy existing setlist?
* Public link to lyrics for congregation
* Rectangle whiteout in PDF annotation??

## Backend

- Search across songs
- New users are pending first
- Bucket maintenance
- History endpoints

## Bugs

- PDF verse order positioning is not working in prod
- Not bolding chord lines when the line has a single Bb chord
- nuxt-auth is expecting get_session endpoint to return a token. We don't need it
  because we set our own session cookie on the response, but still it's causing errors
- the /api/auth session cookie is back......
- Adding a set list is very slow since it needs to make one request per position
  - already using Promise.all, so any speed improvement would be batching

## Performance

- Check on the performance of refresh stores
  - wonder if the Promise.all method would help there too
- A ping on every request is adding a substantial delay
  - it would be better to catch DatabaseResumingException when executing the query
    and auto retry
  - we should then find the right way to execute schema upgrades
- Probably should send presigned S3 URLs rather than downloading the object in the API
- Write a script to load test; handle errors related to Data API rate limits and
  return 429 to user

## Deployment

- More pre-commit hooks
  - eslint (but perhaps a bit relaxed)
  - all pages must have a Head tag
- GitHub action for deployment
  - GitHub identity federation

## Think through

- Do we need tags on song versions and song sheets?
  - How should they be shown, and how do we avoid confusion with song tags?

## Other

- Favicon and proper logo
- User documentation
- Tests
- Revisit login token approach, maybe improve security
