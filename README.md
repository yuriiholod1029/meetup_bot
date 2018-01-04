Create `.token` with contents you get from `https://secure.meetup.com/meetup_api/key/` and `config.json` which has scores, for example:

```
{
  "yes, attended": 1,
  "yes, absent": -3,
  "yes, noshow": -2,
  "no, attended": -2
}
```
First part of each pair mean RSVP status, that is declaration. According to meetup API documentation:
`Member's original RSVP response. May be one of: maybe, waitlist, yes, no, havent`.

Second part is information about actual attendance of person. From documentation:
`The member's attendance status. May be one of: noshow, absent, attended`.
