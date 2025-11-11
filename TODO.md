# TODO

## Frontend

- Filter on authors and tags

* When creating a new song, do a similarity search to existing songs and warn
  in case there is another song with the same title or CCLI number
* Should be able to annotate an existing PDF and save as a new version or new sheet
* Setlist templates
* Roles
  - hide edit buttons
  - Manager can change team member roles
  - Manager gets a NavBar notification for pending members
* Comments
* Media links
* Copy existing setlist?
* Auto-strip chords from lyrics?
* Public link to lyrics for congregation

## Backend

- Endpoints for all tags and all authors
- Flag to disable auto verse order on sheet PDF

* Set list data model updates
  - Title (sermon title)
  - Participants (scheduled team members)
* Search across songs
* New users are pending first
* Bucket maintenance
* History endpoints

## Bugs

- sometimes login fails with 403 error
  - getting "invalid request state" now; going back and reloading login page fixes
    it for the session
- Login session is too short (30m)?
- MtArrayInput needs improvements
  - can't insert in between elements (important for verse order)
  - cursor acts strange when there are multiple lines
  - experienced but did not reproduce wonky delete behavior (I think with song tags)
- Adding a set list is very slow since it needs to make one request per position
  - can it be parallelized, or batched?

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
