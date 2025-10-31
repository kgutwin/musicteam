# TODO

## Frontend

- Loading indicators
  - after adding a sheet, we need either a patch or a loading indicator
  - after adding a set list
  - on saving a new song, need a spinner
- Toasts for errors
- Auto-strip chords from lyrics
- Cursor to edit in between verse order bubbles
- Edit setlists, songs, etc.
- Filter listing of songs, setlists
- Setlist templates
- Copy existing setlist
- Roles
  - hide edit buttons
  - Manager can change team member roles
  - Manager gets a NavBar notification for pending members
- Comments
- Media links
- Edit song sheets (PDF annotations etc.)
- Public link to lyrics for congregation

## Backend

- Search across songs
- Setlist packet assembly
- New users are pending first
- Bucket maintenance
- API keys
- History endpoints

## Bugs

- Login session is too short (30m)?
- Adding a set list is very slow since it needs to make one request per position
  - can it be parallelized, or batched?
- Adding a sheet as a candidate is also very slow, for some reason
  - probably should patch it

## Performance

- A ping on every request is adding a substantial delay
  - it would be better to catch DatabaseResumingException when executing the query
    and auto retry
  - we should then find the right way to execute schema upgrades
- Probably should send presigned S3 URLs rather than downloading the object in the API

## Deployment

- GitHub action for deployment
  - GitHub identity federation

## Other

- Project README
- User documentation
- Tests
