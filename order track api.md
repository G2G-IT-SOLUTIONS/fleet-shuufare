Getting order track
Getting order track

Request
POST

https://fleet-api.yango.tech/v1/parks/orders/track

Query parameters
Name

Description

order_id

Type: string

Order ID

Example: d3639f5f4de4675bb23124b53f63c3d0

park_id

Type: string

Partner ID

Example: ee6f33c4562b4e1f8646d157bd70b2c4

Headers
Name

Description

X-API-Key

Type: string

API-key

Min length: 1

Example: <API key>

X-Client-ID

Type: string

Client ID

Min length: 1

Example: <Client ID>

 Responses
200 OK
A track of an order

Body
application/json
{
  "track": [
    {
      "tracked_at": "2020-09-10T13:37:00+00:00",
      "location": {
        "lat": 55.751244,
        "lon": 37.618423
      },
      "speed": 17,
      "order_status": "waiting",
      "direction": 342,
      "distance": 323.35060609
    }
  ]
}

Name

Description

track

Type: OrderTrack

Example
[
  {
    "tracked_at": "2020-09-10T13:37:00+00:00",
    "location": {
      "lat": 55.751244,
      "lon": 37.618423
    },
    "speed": 17,
    "order_status": "waiting",
    "direction": 342,
    "distance": 323.35060609
  }
]

TrackedAt
Point tracking time

Type: string<date-time>

Example: 2020-09-10T13:37:00+00:00

Latitude
Latitude in degrees

Type: number

Min value: -90

Max value: 90

Longitude
Longitude in degrees

Type: number

Min value: -180

Max value: 180

TrackLocation
Location

Name

Description

lat

Type: Latitude

Latitude in degrees

Min value: -90

Max value: 90

Example: 55.751244

lon

Type: Longitude

Longitude in degrees

Min value: -180

Max value: 180

Example: 37.618423

Example
{
  "lat": 55.751244,
  "lon": 37.618423
}

TrackSpeed
Speed in meters per second

Type: number

Min value: 0

TrackOrderStatus
Order status at the point. Allowed values:

driving - en route to start point;
waiting - is waiting at start point;
transporting - is on the ride.
Type: string

Enum: driving, waiting, transporting

TrackDirection
Direction. Angle from 0 degrees to 360 degrees from north direction, clockwise. 0 - north, 90 - east, 180 - south, 270 - west

Type: number

Min value: 0

Max value: 360

TrackDistance
Distance traveled from the first point of the track in meters

Type: number

Min value: 0

OrderTrackPoint
Name

Description

location

Type: TrackLocation

Location

Example
{
  "lat": 55.751244,
  "lon": 37.618423
}

tracked_at

Type: TrackedAt

Point tracking time

Example: 2020-09-10T13:37:00+00:00

direction

Type: TrackDirection

Direction. Angle from 0 degrees to 360 degrees from north direction, clockwise. 0 - north, 90 - east, 180 - south, 270 - west

Min value: 0

Max value: 360

Example: 342

distance

Type: TrackDistance

Distance traveled from the first point of the track in meters

Min value: 0

Example: 323.35060609

order_status

Type: TrackOrderStatus

Order status at the point. Allowed values:

driving - en route to start point;
waiting - is waiting at start point;
transporting - is on the ride.
Enum: driving, waiting, transporting

speed

Type: TrackSpeed

Speed in meters per second

Min value: 0

Example: 17

Example
{
  "tracked_at": "2020-09-10T13:37:00+00:00",
  "location": {
    "lat": 55.751244,
    "lon": 37.618423
  },
  "speed": 17,
  "order_status": "waiting",
  "direction": 342,
  "distance": 323.35060609
}

OrderTrack
Type: OrderTrackPoint[]

Example
[
  {
    "tracked_at": "2020-09-10T13:37:00+00:00",
    "location": {
      "lat": 55.751244,
      "lon": 37.618423
    },
    "speed": 17,
    "order_status": "waiting",
    "direction": 342,
    "distance": 323.35060609
  }
]

400 Bad Request
Invalid request parameters

Body
application/json
{
  "code": "example",
  "message": "Textual description of the error"
}

Name

Description

message

Type: string

Human-readable error message

Example: Textual description of the error

code

Type: string

Machine-readable error code

Example: example

401 Unauthorized
Request authorization parameters are missing

Body
application/json
{
  "code": "example",
  "message": "Textual description of the error"
}

Name

Description

message

Type: string

Human-readable error message

Example: Textual description of the error

code

Type: string

Machine-readable error code

Example: example

403 Forbidden
Insufficient rights to execute the request

Body
application/json
{
  "code": "example",
  "message": "Textual description of the error"
}

Name

Description

message

Type: string

Human-readable error message

Example: Textual description of the error

code

Type: string

Machine-readable error code

Example: example

404 Not Found
Requested resource was not found

Body
application/json
{
  "code": "example",
  "message": "Textual description of the error"
}

Name

Description

message

Type: string

Human-readable error message

Example: Textual description of the error

code

Type: string

Machine-readable error code

Example: example

429 Too Many Requests
Limit of requests was exceeded

Body
application/json
{
  "code": "example",
  "message": "Textual description of the error"
}

Name

Description

message

Type: string

Human-readable error message

Example: Textual description of the error

code

Type: string

Machine-readable error code

Example: example

500 Internal Server Error
Internal server error

Body
application/json
{
  "code": "example",
  "message": "Textual description of the error"
}

Name

Description

message

Type: string

Human-readable error message

Example: Textual description of the error

code

Type: string

Machine-readable error code

Example: example

Was the article helpful?
