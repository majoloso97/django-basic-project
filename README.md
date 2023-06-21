# Django Basic Project

This is a Django app started through docker, with aim to be a sandbox for exploring the django framework

## How to run it
- Ensure to have docker with docker-compose installed
- cd to the project folder: `cd django-basic-project`
- Run `docker-compose up --build` to create the image and run the container. The api should be running on `http://localhost:8010/`.

## For interview purposes
### Current behavior
- The app manages Users with the default Django auth model. However, a different model (AdditionalUser) was set up to add important fields needed for the user profile.
- The AdditionalUser contain an assignment to themselves as 'coaches', meaning that a user might have one or more coaches, who are also users.
- Coaches (with superuser access) can create UpcomingCalls and invite other users, by defining a timestamp, link and other fields (see post request - note: Authorization header has username and passwords that can be used to test)
```
curl --request POST \
  --url http://localhost:8010/api/upcoming-calls/ \
  --header 'Accept: application/json' \
  --header 'Authorization: Basic majoloso97-Abcd1234#' \
  --header 'Content-Type: application/json' \
  --data '{
	"call_name":"1:1 with Maykol",
	"timestamp":1687536000000,
	"meeting_link":"google.com",
	"recours_weekly": false,
	"participants": [2],
	"time_zone": "America/Managua"
}'
```
- As coach, you can retrive the saved upcoming calls with: 
```
curl --request GET \
  --url http://localhost:8010/api/upcoming-calls/ \
  --header 'Authorization: Basic majoloso97-Abcd1234#'
```

- If you're not a coach (with superuser access) the endpoint to retrieve the Upcoming calls that you're invited to is different: `--url http://localhost:8010/api/upcoming-calls/user_upcoming_calls/`
- For testing purposes, all users have the same password `Abcd1234#`, and there are 4 users: majoloso97 (superuser, timezone: Europe/Madrid), maykol (superuser, timezone America/Managua), itsjuanmatus (timezone: America/New York), testing (timezone: Asia/Shanghai)
- Currently, calls are not sorted by logical datetime, and sometimes don't return the right entities

### Requirements
- Have a single endpoint to retrieve calls no matter if you are creator or participant
- The Upcoming calls should be returned with the timestamp in a readable format
- The returned timestamp should also reflect the user timezone (e.g. a call created by a user in New York (GMT-4) should be reflected with a time 2 hours earlier for a user in Managua (GMT-6))
- Recurring calls should reflect the NEXT occurrence of the recurring event. For example, if the event was set up recourringly for Jun 20th, 10:00 am, if the request is made on Jun 25th, the same call should reflect Jun 27th as date (next time that call will happen)
- The Upcoming calls should be returned sorted by the actual timestamp in a readable format, so sorted by the REAL time they will happen
- Based on the detected issues and requirements, the expected output for the endpoint response is as follows:
    - If logged in as majoloso97, the response should be returned similar to the following, considering the datetime output calculated as next ocurrence for recurring events:
    ```
    [{'id': 1,
        'call_name': '1:1 with Maykol',
        'timestamp': 1687186800000,
        'meeting_link': 'google.com',
        'recours_weekly': '1',
        'user_id': 1,
        'datetime': '26/06/2023, 15:00:00'},
    {'id': 2,
        'call_name': '1:1 with Juan',
        'timestamp': 1687982400000,
        'meeting_link': 'google.com',
        'recours_weekly': '1',
        'user_id': 1,
        'datetime': '28/06/2023, 20:00:00'},
    {'id': 4,
        'call_name': 'Onboarding',
        'timestamp': 1688148000000,
        'meeting_link': 'google.com',
        'recours_weekly': '0',
        'user_id': 1,
        'datetime': '30/06/2023, 18:00:00'},
    {'id': 11,
        'call_name': 'Offboarding',
        'timestamp': 1693576800000,
        'meeting_link': 'google.com',
        'recours_weekly': '0',
        'user_id': 1,
        'datetime': '01/09/2023, 14:00:00'}]
    ```
    - If logged in as maykol, the call ids should be returned sorted as follow:
    ```
    [{'id': 1,
        'call_name': '1:1 with Maykol',
        'timestamp': 1687186800000,
        'meeting_link': 'google.com',
        'recours_weekly': '1',
        'user_id': 1,
        'datetime': '26/06/2023, 15:00:00'},
    {'id': 11,
        'call_name': 'Offboarding',
        'timestamp': 1693576800000,
        'meeting_link': 'google.com',
        'recours_weekly': '0',
        'user_id': 1,
        'datetime': '01/09/2023, 14:00:00'}]
    ```

- Give proposals to improve the database structure, api design or any other improvement opportunity
- Bonus: The helper function 'universal_notify' is currently printing a message when the notification is sent, fix by using proper logs