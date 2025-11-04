# TODO

## Frontend

- Filter, sort listing of songs, setlists
- Copy setlist to clipboard
- Download PDF

* Cursor to edit in between verse order bubbles
* Loading indicators
  - after adding a sheet, we need either a patch or a loading indicator
* Setlist templates
* Copy existing setlist
* Auto-strip chords from lyrics
* Roles
  - hide edit buttons
  - Manager can change team member roles
  - Manager gets a NavBar notification for pending members
* Comments
* Media links
* Edit song sheets (PDF annotations etc.)
* Public link to lyrics for congregation

## Backend

- error responses need bodies (esp. 500)
- Setlist packet assembly
- API keys
  - include link to swagger

* Tags and authors endpoints
* Set list data model updates
  - Title (sermon title)
  - Participants (scheduled team members)
* Search across songs
* New users are pending first
* Bucket maintenance
* History endpoints

## Bugs

- MtArrayInput needs improvements
  - can't insert in between elements (important for verse order)
  - cursor acts strange when there are multiple lines
  - experienced but did not reproduce wonky delete behavior (I think with song tags)
- Login session is too short (30m)?
- Adding a set list is very slow since it needs to make one request per position
  - can it be parallelized, or batched?
- sometimes login fails with 403 error?? maybe only with dev frontend?

## Performance

- Check on the performance of refresh stores
  - wonder if the Promise.all method would help there too
- A ping on every request is adding a substantial delay
  - it would be better to catch DatabaseResumingException when executing the query
    and auto retry
  - we should then find the right way to execute schema upgrades
- Probably should send presigned S3 URLs rather than downloading the object in the API

## Deployment

- GitHub action for deployment
  - GitHub identity federation

## Think through

- Do we need tags on song versions and song sheets?
  - How should they be shown, and how do we avoid confusion with song tags?

## Other

- Project README
- User documentation
- Tests
