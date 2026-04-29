Getting list of driver profiles (couriers)
Returns a list of driver (courier) profiles associated with a given partner. It is the recommended method for obtaining profiles. The platform also supports pagination and filtering. The platform allows obtaining the following:

all driver (courier) profiles;
all driver (courier) profiles with the given status and working conditions;
driver (courier) profiles selected by ID.
Request
POST

https://fleet-api.yango.tech/v1/parks/driver-profiles/list

Headers
Name

Description

Accept-Language

Type: string

Preferred language of the response

Min length: 2

Example: ru

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

Body
application/json
{
  "query": {
    "park": {
      "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
      "driver_profile": {
        "id": [
          "2111ade6gk054dfdb9iu8c8cc9460mks"
        ],
        "work_rule_id": [
          "bc43tre6ba054dfdb7143ckfgvcby63e"
        ],
        "work_status": [
          "working"
        ]
      },
      "current_status": {
        "status": [
          "free"
        ]
      },
      "account": {
        "last_transaction_date": {
          "from": "2025-01-01T00:00:00Z",
          "to": "2025-01-01T00:00:00Z"
        }
      },
      "updated_at": {
        "from": "2025-01-01T00:00:00Z",
        "to": "2025-01-01T00:00:00Z"
      }
    },
    "text": "example"
  },
  "fields": {
    "account": [
      "balance"
    ],
    "car": [
      "color"
    ],
    "current_status": [
      "status"
    ],
    "driver_profile": [
      "last_name"
    ],
    "park": [
      "name"
    ],
    "updated_at": true
  },
  "sort_order": [
    {
      "direction": "asc",
      "field": "driver_profile.created_date"
    }
  ],
  "limit": 200,
  "offset": 0
}

Name

Description

query

Type: DriverProfilesListRequestQuery

Filters can be merged using logical "AND"

Example
{
  "park": {
    "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
    "driver_profile": {
      "id": [
        "2111ade6gk054dfdb9iu8c8cc9460mks"
      ],
      "work_rule_id": [
        "bc43tre6ba054dfdb7143ckfgvcby63e"
      ],
      "work_status": [
        "working"
      ]
    },
    "current_status": {
      "status": [
        "free"
      ]
    },
    "account": {
      "last_transaction_date": {
        "from": "2025-01-01T00:00:00Z",
        "to": "2025-01-01T00:00:00Z"
      }
    },
    "updated_at": {
      "from": "2025-01-01T00:00:00Z",
      "to": "2025-01-01T00:00:00Z"
    }
  },
  "text": "example"
}

fields

Type: DriverProfileListRequestFields

Profile fields to be retrieved. When empty, all profile fields are retrieved. To exclude a specific block of fields, pass an empty array for the corresponding section. E.g. specify "car": [] if you want to exclude vehicle information. Example:

"fields": {
    "car": [],
    "park": [],
    "driver_profile": [
        "first_name",
        "last_name",
        "id"
    ],
    "account": [
        "id",
        "balance",
        "balance_limit",
        "currency"
    ]
}

Example
{
  "account": [
    "balance"
  ],
  "car": [
    "color"
  ],
  "current_status": [
    "status"
  ],
  "driver_profile": [
    "last_name"
  ],
  "park": [
    "name"
  ],
  "updated_at": true
}

limit

Type: integer

Number of list items being requested

Default: 1000

Min value: 1

Max value: 1000

offset

Type: integer

Offset from the beginning of the list

Default: 0

Min value: 0

sort_order

Type: DriverProfileRequestSortOrder

An array of fields to define profiles order in the response

Example
[
  {
    "direction": "asc",
    "field": "driver_profile.created_date"
  }
]

ParkId
Partner ID

Type: string

Example: ee6f33c4562b4e1f8646d157bd70b2c4

ContractorProfileId
Driver's profile ID

Type: string

Example: 2111ade6gk054dfdb9iu8c8cc9460mks

WorkRuleId
Work rule ID

Type: string

Example: bc43tre6ba054dfdb7143ckfgvcby63e

WorkStatus
Driver's working status. Possible values:

working — "Is working" status.
not_working — "Not working" status;
fired — status for dismissed drivers;
Type: string

Enum: working, not_working, fired

DriverProfilesListRequestQueryParkDriverProfile
Filters by driver profile data

Name

Description

id

Type: ContractorProfileId[]

Example
[
  "2111ade6gk054dfdb9iu8c8cc9460mks"
]

work_rule_id

Type: WorkRuleId[]

Example
[
  "bc43tre6ba054dfdb7143ckfgvcby63e"
]

work_status

Type: WorkStatus[]

Example
[
  "working"
]

Example
{
  "id": [
    "2111ade6gk054dfdb9iu8c8cc9460mks"
  ],
  "work_rule_id": [
    "bc43tre6ba054dfdb7143ckfgvcby63e"
  ],
  "work_status": [
    "working"
  ]
}

DriverStatus
Driver's current state. Possible values:

offline — offline;
busy — busy;
free — available;
in_order_free - is on the ride now, available (stacked rides enabled);
in_order_busy — is on the ride now, busy (stacked rides disabled).
Type: string

Enum: offline, busy, free, in_order_free, in_order_busy

DriverProfilesListRequestQueryParkCurrentStatus
Filter by driver's current state

Name

Description

status

Type: DriverStatus[]

Example
[
  "free"
]

Example
{
  "status": [
    "free"
  ]
}

DriverProfilesListRequestQueryParkAccountLastTransactionDate
Half-interval for which a start or end point must be indicated

Name

Description

from

Type: string<date-time>

Start time as per ISO 8601

Example: 2025-01-01T00:00:00Z

to

Type: string<date-time>

End time as per ISO 8601

Example: 2025-01-01T00:00:00Z

Example
{
  "from": "2025-01-01T00:00:00Z",
  "to": "2025-01-01T00:00:00Z"
}

DriverProfilesListRequestQueryParkAccount
Filters by account data

Name

Description

last_transaction_date

Type: DriverProfilesListRequestQueryParkAccountLastTransactionDate

Half-interval for which a start or end point must be indicated

Example
{
  "from": "2025-01-01T00:00:00Z",
  "to": "2025-01-01T00:00:00Z"
}

Example
{
  "last_transaction_date": {
    "from": "2025-01-01T00:00:00Z",
    "to": "2025-01-01T00:00:00Z"
  }
}

DriverProfilesListRequestQueryParkUpdatedAt
Filters by time of latest update; Half-interval for which a start or end point must be indicated

Name

Description

from

Type: string<date-time>

Start time as per ISO 8601

Example: 2025-01-01T00:00:00Z

to

Type: string<date-time>

End time as per ISO 8601

Example: 2025-01-01T00:00:00Z

Example
{
  "from": "2025-01-01T00:00:00Z",
  "to": "2025-01-01T00:00:00Z"
}

DriverProfilesListRequestQueryPark
Partner parameters

Name

Description

id

Type: ParkId

Partner ID

Example: ee6f33c4562b4e1f8646d157bd70b2c4

account

Type: DriverProfilesListRequestQueryParkAccount

Filters by account data

Example
{
  "last_transaction_date": {
    "from": "2025-01-01T00:00:00Z",
    "to": "2025-01-01T00:00:00Z"
  }
}

current_status

Type: DriverProfilesListRequestQueryParkCurrentStatus

Filter by driver's current state

Example
{
  "status": [
    "free"
  ]
}

driver_profile

Type: DriverProfilesListRequestQueryParkDriverProfile

Filters by driver profile data

Example
{
  "id": [
    "2111ade6gk054dfdb9iu8c8cc9460mks"
  ],
  "work_rule_id": [
    "bc43tre6ba054dfdb7143ckfgvcby63e"
  ],
  "work_status": [
    "working"
  ]
}

updated_at

Type: DriverProfilesListRequestQueryParkUpdatedAt

Filters by time of latest update; Half-interval for which a start or end point must be indicated

Example
{
  "from": "2025-01-01T00:00:00Z",
  "to": "2025-01-01T00:00:00Z"
}

Example
DriverProfilesListRequestQuery
Filters can be merged using logical "AND"

Name

Description

park

Type: DriverProfilesListRequestQueryPark

Partner parameters

Example
{
  "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
  "driver_profile": {
    "id": [
      "2111ade6gk054dfdb9iu8c8cc9460mks"
    ],
    "work_rule_id": [
      "bc43tre6ba054dfdb7143ckfgvcby63e"
    ],
    "work_status": [
      "working"
    ]
  },
  "current_status": {
    "status": [
      "free"
    ]
  },
  "account": {
    "last_transaction_date": {
      "from": "2025-01-01T00:00:00Z",
      "to": "2025-01-01T00:00:00Z"
    }
  },
  "updated_at": {
    "from": "2025-01-01T00:00:00Z",
    "to": "2025-01-01T00:00:00Z"
  }
}

text

Type: string

Arbitrary full-text search request

Example: example

Example
{
  "park": {
    "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
    "driver_profile": {
      "id": [
        "2111ade6gk054dfdb9iu8c8cc9460mks"
      ],
      "work_rule_id": [
        "bc43tre6ba054dfdb7143ckfgvcby63e"
      ],
      "work_status": [
        "working"
      ]
    },
    "current_status": {
      "status": [
        "free"
      ]
    },
    "account": {
      "last_transaction_date": {
        "from": "2025-01-01T00:00:00Z",
        "to": "2025-01-01T00:00:00Z"
      }
    },
    "updated_at": {
      "from": "2025-01-01T00:00:00Z",
      "to": "2025-01-01T00:00:00Z"
    }
  },
  "text": "example"
}

VehicleField
Vehicle field

Type: string

Enum: id, status, amenities, category, callsign, brand, model, year, color, number, registration_cert, vin

VehicleFields
Vehicle data to be retrieved. Possible values:

id — identifier;
status — status;
amenities — services;
category — categories;
callsign — codename;
brand — make;
model — current model;
year — year of manufacture;
color — color;
number — registration number;
registration_cert — vehicle registration certificate;
vin — vehicle identification number (VIN).
Type: VehicleField[]

Example
[
  "color"
]

DriverProfileListRequestFields
Profile fields to be retrieved. When empty, all profile fields are retrieved. To exclude a specific block of fields, pass an empty array for the corresponding section. E.g. specify "car": [] if you want to exclude vehicle information. Example:

"fields": {
    "car": [],
    "park": [],
    "driver_profile": [
        "first_name",
        "last_name",
        "id"
    ],
    "account": [
        "id",
        "balance",
        "balance_limit",
        "currency"
    ]
}

Name

Description

account

Type: string[]

Account data to be retrieved. Possible values:

id — account ID;
type — account type;
balance — current account balance;
balance_limit — current limit;
currency — currency code as per ISO 4217.
last_transaction_date — date of the last transaction
Example
[
  "balance"
]

car

Type: VehicleFields

Vehicle data to be retrieved. Possible values:

id — identifier;
status — status;
amenities — services;
category — categories;
callsign — codename;
brand — make;
model — current model;
year — year of manufacture;
color — color;
number — registration number;
registration_cert — vehicle registration certificate;
vin — vehicle identification number (VIN).
Example
[
  "color"
]

current_status

Type: string[]

Driver state data to be retrieved. Possible values:

status — driver's current state;
status_updated_at — time of the most recent driver's current state update.
Example
[
  "status"
]

driver_profile

Type: string[]

Driver profile data to be retrieved. Possible values:

id — driver's profile ID;
park_id — partner ID;
created_date — date when the profile is created ISO 8601;
first_name — first name;
last_name — last name;
middle_name — middle name;
driver_license — information about a driver's license;
phones — phone numbers;
work_rule_id — working condition ID;
work_status — driver's working status;
check_message — feedback on a driver;
comment — other;
employment_type - driver's employment type
has_contract_issue - there are problems with confirming employment.
Example
[
  "last_name"
]

park

Type: string[]

Partner data to be retrieved. Possible values:

id — partner ID;
city — city where the partner is located;
name — name of a partner.
Example
[
  "name"
]

updated_at

Type: boolean

Whether to return time of latest update

Example
{
  "account": [
    "balance"
  ],
  "car": [
    "color"
  ],
  "current_status": [
    "status"
  ],
  "driver_profile": [
    "last_name"
  ],
  "park": [
    "name"
  ],
  "updated_at": true
}

DriverProfileRequestSortOrderField
Name

Description

direction

Type: string

Sorting direction. Possible values:

asc — ascending sorting;
desc — descending sorting.
Enum: asc, desc

field

Type: string

Field used to sort the values. Possible values:

account.current.balance — balance;
driver_profile.created_date — date of driver's profile creation;
driver_profile.last_name — last name in the driver's profile;
driver_profile.first_name — name in the driver's profile;
driver_profile.middle_name — middle name in the driver's profile;
updated_at - time of latest update.
Enum: account.current.balance, driver_profile.created_date, driver_profile.last_name, driver_profile.first_name, driver_profile.middle_name, updated_at

Example
{
  "direction": "asc",
  "field": "driver_profile.created_date"
}

DriverProfileRequestSortOrder
An array of fields to define profiles order in the response

Type: DriverProfileRequestSortOrderField[]

Example
[
  {
    "direction": "asc",
    "field": "driver_profile.created_date"
  }
]

Responses
200 OK
List of driver profiles was received successfully

Body
application/json
{
  "limit": 200,
  "offset": 0,
  "total": 728,
  "driver_profiles": [
    {
      "accounts": [
        {
          "id": "33de650c6a1a40bfa78dd981817da866",
          "type": "current",
          "balance": "700.0000",
          "balance_limit": "50",
          "currency": "RUB"
        }
      ],
      "car": {
        "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
        "status": "working",
        "amenities": [
          "wifi"
        ],
        "category": [
          "econom"
        ],
        "callsign": "123456789",
        "brand": "Mercedes-Benz",
        "model": "E-klasse",
        "year": 2019,
        "color": "Черный",
        "number": "Т8654Т99",
        "registration_cert": "123456789",
        "vin": "12345678909876543"
      },
      "current_status": {
        "status": "free",
        "status_updated_at": "2020-04-27T08:44:05.871+0000"
      },
      "driver_profile": {
        "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
        "park_id": "ee6f33c4562b4e1f8646d157bd70b2c4",
        "created_date": "2020-04-23T13:08:05.552+0000",
        "last_name": "Ivanov",
        "first_name": "Ivan",
        "middle_name": "Ivanovich",
        "driver_license": {
          "issue_date": "2020-10-28",
          "expiration_date": "2050-10-28",
          "number": "070236",
          "normalized_number": "AA00123456",
          "country": "rus",
          "birth_date": "1975-10-28"
        },
        "phones": [
          "+79999999999"
        ],
        "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
        "work_status": "working",
        "check_message": "great driver",
        "comment": "great driver",
        "employment_type": "selfemployed",
        "has_contract_issue": true
      }
    }
  ],
  "parks": [
    {
      "id": null,
      "city": "Tel Aviv",
      "name": "Mickey Mouse Company"
    }
  ]
}

Name

Description

driver_profiles

Type: DriverProfile[]

List of profiles

Example
[
  {
    "accounts": [
      {
        "id": "33de650c6a1a40bfa78dd981817da866",
        "type": "current",
        "balance": "700.0000",
        "balance_limit": "50",
        "currency": "RUB"
      }
    ],
    "car": {
      "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
      "status": "working",
      "amenities": [
        "wifi"
      ],
      "category": [
        "econom"
      ],
      "callsign": "123456789",
      "brand": "Mercedes-Benz",
      "model": "E-klasse",
      "year": 2019,
      "color": "Черный",
      "number": "Т8654Т99",
      "registration_cert": "123456789",
      "vin": "12345678909876543"
    },
    "current_status": {
      "status": "free",
      "status_updated_at": "2020-04-27T08:44:05.871+0000"
    },
    "driver_profile": {
      "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
      "park_id": "ee6f33c4562b4e1f8646d157bd70b2c4",
      "created_date": "2020-04-23T13:08:05.552+0000",
      "last_name": "Ivanov",
      "first_name": "Ivan",
      "middle_name": "Ivanovich",
      "driver_license": {
        "issue_date": "2020-10-28",
        "expiration_date": "2050-10-28",
        "number": "070236",
        "normalized_number": "AA00123456",
        "country": "rus",
        "birth_date": "1975-10-28"
      },
      "phones": [
        "+79999999999"
      ],
      "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
      "work_status": "working",
      "check_message": "great driver",
      "comment": "great driver",
      "employment_type": "selfemployed",
      "has_contract_issue": true
    }
  }
]

limit

Type: integer

Requested number of list items

offset

Type: integer

Requested offset from the beginning of the list

parks

Type: DriverProfilePark[]

List of partners

Example
[
  {
    "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
    "city": "Tel Aviv",
    "name": "Mickey Mouse Company"
  }
]

total

Type: integer

Total number of list items

AccountId
Account ID

Type: string

Example: 33de650c6a1a40bfa78dd981817da866

AccountType
Account type. Possible values:

current — current account.
Type: string

Const: current

Example: current

AccountBalance
Current account balance (fixed-point sum)

Type: string

Example: 700.0000

BalanceLimit
Balance limit

Type: string

Example: 50

Currency
Currency as per ISO 4217

Type: string

Example: RUB

DriverProfileAccount
Account information

Name

Description

balance

Type: AccountBalance

Current account balance (fixed-point sum)

Example: 700.0000

balance_limit

Type: BalanceLimit

Balance limit

Example: 50

currency

Type: Currency

Currency as per ISO 4217

Example: RUB

id

Type: AccountId

Account ID

Example: 33de650c6a1a40bfa78dd981817da866

type

Type: AccountType

Account type. Possible values:

current — current account.
Enum: current

Example
{
  "id": "33de650c6a1a40bfa78dd981817da866",
  "type": "current",
  "balance": "700.0000",
  "balance_limit": "50",
  "currency": "RUB"
}

VehicleId
Vehicle ID

Type: string

Example: 2111ade6gk054dfdb9iu8c8cc9460mks

Status
Vehicle status. Currently possible values:

unknown — status is unknown;
working — is used at the moment to complete trips;
not_working — is not used at the moment to complete trips;
repairing — is undergoing technical maintenance or repair works;
no_driver - no driver assigned to a vehicle;
pending - vehicle details processing is in progress.
Type: string

Example: working

Amenities
Vehilce amenity. Possible values:

conditioner
no_smoking
child_chair
animal_transport
universal
wifi
check
card
yamoney
newspaper
coupon
creditcard
dont_call
smoking
delivery
vip_event
woman_driver
post_terminal
bicycle
skiing
passenger_plus
cargo_clean
door_to_door
sticker
lightbox
Type: string[]

Example
[
  "wifi"
]

Categories
List of vehicle categories. Possible values:

econom — Economy class;
comfort — Comfort;
comfort_plus — Comfort+;
business — business class vehicle;
minivan — minivan;
vip — A VIP class vehicle;
wagon — multi-purpose;
pool — pool class vehicle;
start — Start class vehicle;
standart — Standart class vehicle;
ultimate — Premier;
maybach — elite class vehicle;
promo — promotion;
premium_van — cruise van;
premium_suv — premium SUV;
suv — SUV;
personal_driver — personal driver class vehicle;
express — delivery class vehicle;
cargo — a cargo vehicle.
Type: string[]

Example
[
  "econom"
]

Callsign
Vehicle code name (short name)

Type: string

Example: 123456789

Brand
Vehicle make

Type: string

Example: Mercedes-Benz

Model
Vehicle model

Type: string

Example: E-klasse

Year
Year of vehicle manufacture

Type: integer

ColorEnum
Vehicle color. Possible values:

Белый — White;
Желтый — Yellow;
Бежевый — Beige;
Черный — Black;
Голубой — Light blue;
Серый — Gray;
Красный — Red;
Оранжевый — Orange;
Синий — Dark blue;
Зеленый — Green;
Коричневый — Brown;
Фиолетовый — Purple;
Розовый — Pink.
Type: string

Enum: Белый, Желтый, Бежевый, Черный, Голубой, Серый, Красный, Оранжевый, Синий, Зеленый, Коричневый, Фиолетовый, Розовый

LicencePlateNumber
License plate number

Type: string

Example: Т8654Т99

RegistrationCertificate
Vehicle registration certificate (Required field for Russia)

Type: string

Example: 123456789

VIN
VIN (Required field for Russia)

Type: string

Example: 12345678909876543

Vehicle
Vehicle data

Name

Description

id

Type: VehicleId

Vehicle ID

Example: 2111ade6gk054dfdb9iu8c8cc9460mks

amenities

Type: Amenities

Vehilce amenity. Possible values:

conditioner
no_smoking
child_chair
animal_transport
universal
wifi
check
card
yamoney
newspaper
coupon
creditcard
dont_call
smoking
delivery
vip_event
woman_driver
post_terminal
bicycle
skiing
passenger_plus
cargo_clean
door_to_door
sticker
lightbox
Example
[
  "wifi"
]

brand

Type: Brand

Vehicle make

Example: Mercedes-Benz

callsign

Type: Callsign

Vehicle code name (short name)

Example: 123456789

category

Type: Categories

List of vehicle categories. Possible values:

econom — Economy class;
comfort — Comfort;
comfort_plus — Comfort+;
business — business class vehicle;
minivan — minivan;
vip — A VIP class vehicle;
wagon — multi-purpose;
pool — pool class vehicle;
start — Start class vehicle;
standart — Standart class vehicle;
ultimate — Premier;
maybach — elite class vehicle;
promo — promotion;
premium_van — cruise van;
premium_suv — premium SUV;
suv — SUV;
personal_driver — personal driver class vehicle;
express — delivery class vehicle;
cargo — a cargo vehicle.
Example
[
  "econom"
]

color

Type: ColorEnum

Vehicle color. Possible values:

Белый — White;
Желтый — Yellow;
Бежевый — Beige;
Черный — Black;
Голубой — Light blue;
Серый — Gray;
Красный — Red;
Оранжевый — Orange;
Синий — Dark blue;
Зеленый — Green;
Коричневый — Brown;
Фиолетовый — Purple;
Розовый — Pink.
Enum: Белый, Желтый, Бежевый, Черный, Голубой, Серый, Красный, Оранжевый, Синий, Зеленый, Коричневый, Фиолетовый, Розовый

model

Type: Model

Vehicle model

Example: E-klasse

number

Type: LicencePlateNumber

License plate number

Example: Т8654Т99

registration_cert

Type: RegistrationCertificate

Vehicle registration certificate (Required field for Russia)

Example: 123456789

status

Type: Status

Vehicle status. Currently possible values:

unknown — status is unknown;
working — is used at the moment to complete trips;
not_working — is not used at the moment to complete trips;
repairing — is undergoing technical maintenance or repair works;
no_driver - no driver assigned to a vehicle;
pending - vehicle details processing is in progress.
Example: working

vin

Type: VIN

VIN (Required field for Russia)

Example: 12345678909876543

year

Type: Year

Year of vehicle manufacture

Example: 2019

Example
{
  "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
  "status": "working",
  "amenities": [
    "wifi"
  ],
  "category": [
    "econom"
  ],
  "callsign": "123456789",
  "brand": "Mercedes-Benz",
  "model": "E-klasse",
  "year": 2019,
  "color": "Черный",
  "number": "Т8654Т99",
  "registration_cert": "123456789",
  "vin": "12345678909876543"
}

DriverProfileCurrentStatus
Name

Description

status

Type: DriverStatus

Driver's current state. Possible values:

offline — offline;
busy — busy;
free — available;
in_order_free - is on the ride now, available (stacked rides enabled);
in_order_busy — is on the ride now, busy (stacked rides disabled).
Enum: offline, busy, free, in_order_free, in_order_busy

status_updated_at

Type: string

Time of the last update of the current driver status in the ISO 8601 format.

Example: 2020-04-27T08:44:05.871+0000

Example
{
  "status": "free",
  "status_updated_at": "2020-04-27T08:44:05.871+0000"
}

LastName
Last name

Type: string

Example: Ivanov

FirstName
Name

Type: string

Example: Ivan

MiddleName
Middle name

Type: string

Example: Ivanovich

IssueDate
Date of issue of the driver's license in ISO 8601 format without time zone

Type: string

Example: 2020-10-28

ExpiryDate
Driver's license expiry date in ISO 8601 format without time zone

Type: string

Example: 2050-10-28

Number
Driver's license series and number

Type: string

Example: 070236

NormalizedNumber
Normalized series and number (Cyrillic letters have been replaced by Latin letters)

Type: string

Example: AA00123456

CountryCode
Country of issue (Three-letter code)

Type: string

Example: rus

BirthDate
Birth date in ISO 8601 format without time zone

Type: string

Example: 1975-10-28

DriverLicense
Driver's license

Name

Description

country

Type: CountryCode

Country of issue (Three-letter code)

Example: rus

normalized_number

Type: NormalizedNumber

Normalized series and number (Cyrillic letters have been replaced by Latin letters)

Example: AA00123456

number

Type: Number

Driver's license series and number

Example: 070236

birth_date

Type: BirthDate

Birth date in ISO 8601 format without time zone

Example: 1975-10-28

expiration_date

Type: ExpiryDate

Driver's license expiry date in ISO 8601 format without time zone

Example: 2050-10-28

issue_date

Type: IssueDate

Date of issue of the driver's license in ISO 8601 format without time zone

Example: 2020-10-28

Example
{
  "issue_date": "2020-10-28",
  "expiration_date": "2050-10-28",
  "number": "070236",
  "normalized_number": "AA00123456",
  "country": "rus",
  "birth_date": "1975-10-28"
}

Phone
Phone number

Type: string

Pattern: ^\+\d{1,15}$

Example: +79999999999

FeedBack
Notes (available to park employees)

Type: string

Example: great driver

Comment
Notes

Type: string

Example: great driver

EmploymentType
Driver's employment type. Possible values:

selfemployed — Self-employed;
park_employee — Park employee;
individual_entrepreneur — Individual entrepreneur;
Type: string

Enum: selfemployed, park_employee, individual_entrepreneur

HasContractIssue
There are problems with confirming employment

Type: boolean

DriverProfileModel
Driver profile

Name

Description

check_message

Type: FeedBack

Notes (available to park employees)

Example: great driver

comment

Type: Comment

Notes

Example: great driver

created_date

Type: string

Date of profile creation as per ISO 8601

Example: 2020-04-23T13:08:05.552+0000

driver_license

Type: DriverLicense

Driver's license

Example
{
  "issue_date": "2020-10-28",
  "expiration_date": "2050-10-28",
  "number": "070236",
  "normalized_number": "AA00123456",
  "country": "rus",
  "birth_date": "1975-10-28"
}

employment_type

Type: EmploymentType

Driver's employment type. Possible values:

selfemployed — Self-employed;
park_employee — Park employee;
individual_entrepreneur — Individual entrepreneur;
Enum: selfemployed, park_employee, individual_entrepreneur

first_name

Type: FirstName

Name

Example: Ivan

has_contract_issue

Type: HasContractIssue

There are problems with confirming employment

Example: true

id

Type: ContractorProfileId

Driver's profile ID

Example: 2111ade6gk054dfdb9iu8c8cc9460mks

last_name

Type: LastName

Last name

Example: Ivanov

middle_name

Type: MiddleName

Middle name

Example: Ivanovich

park_id

Type: ParkId

Partner ID

Example: ee6f33c4562b4e1f8646d157bd70b2c4

phones

Type: Phone[]

Example
[
  "+79999999999"
]

work_rule_id

Type: WorkRuleId

Work rule ID

Example: bc43tre6ba054dfdb7143ckfgvcby63e

work_status

Type: WorkStatus

Driver's working status. Possible values:

working — "Is working" status.
not_working — "Not working" status;
fired — status for dismissed drivers;
Enum: working, not_working, fired

Example
{
  "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
  "park_id": "ee6f33c4562b4e1f8646d157bd70b2c4",
  "created_date": "2020-04-23T13:08:05.552+0000",
  "last_name": "Ivanov",
  "first_name": "Ivan",
  "middle_name": "Ivanovich",
  "driver_license": {
    "issue_date": "2020-10-28",
    "expiration_date": "2050-10-28",
    "number": "070236",
    "normalized_number": "AA00123456",
    "country": "rus",
    "birth_date": "1975-10-28"
  },
  "phones": [
    "+79999999999"
  ],
  "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
  "work_status": "working",
  "check_message": "great driver",
  "comment": "great driver",
  "employment_type": "selfemployed",
  "has_contract_issue": true
}

DriverProfile
Name

Description

accounts

Type: DriverProfileAccount[]

List of accounts associated with the driver

Example
[
  {
    "id": "33de650c6a1a40bfa78dd981817da866",
    "type": "current",
    "balance": "700.0000",
    "balance_limit": "50",
    "currency": "RUB"
  }
]

car

Type: Vehicle

Vehicle data

Example
{
  "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
  "status": "working",
  "amenities": [
    "wifi"
  ],
  "category": [
    "econom"
  ],
  "callsign": "123456789",
  "brand": "Mercedes-Benz",
  "model": "E-klasse",
  "year": 2019,
  "color": "Черный",
  "number": "Т8654Т99",
  "registration_cert": "123456789",
  "vin": "12345678909876543"
}

current_status

Type: DriverProfileCurrentStatus

Example
{
  "status": "free",
  "status_updated_at": "2020-04-27T08:44:05.871+0000"
}

driver_profile

Type: DriverProfileModel

Driver profile

Example
{
  "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
  "park_id": "ee6f33c4562b4e1f8646d157bd70b2c4",
  "created_date": "2020-04-23T13:08:05.552+0000",
  "last_name": "Ivanov",
  "first_name": "Ivan",
  "middle_name": "Ivanovich",
  "driver_license": {
    "issue_date": "2020-10-28",
    "expiration_date": "2050-10-28",
    "number": "070236",
    "normalized_number": "AA00123456",
    "country": "rus",
    "birth_date": "1975-10-28"
  },
  "phones": [
    "+79999999999"
  ],
  "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
  "work_status": "working",
  "check_message": "great driver",
  "comment": "great driver",
  "employment_type": "selfemployed",
  "has_contract_issue": true
}

Example
{
  "accounts": [
    {
      "id": "33de650c6a1a40bfa78dd981817da866",
      "type": "current",
      "balance": "700.0000",
      "balance_limit": "50",
      "currency": "RUB"
    }
  ],
  "car": {
    "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
    "status": "working",
    "amenities": [
      "wifi"
    ],
    "category": [
      "econom"
    ],
    "callsign": "123456789",
    "brand": "Mercedes-Benz",
    "model": "E-klasse",
    "year": 2019,
    "color": "Черный",
    "number": "Т8654Т99",
    "registration_cert": "123456789",
    "vin": "12345678909876543"
  },
  "current_status": {
    "status": "free",
    "status_updated_at": "2020-04-27T08:44:05.871+0000"
  },
  "driver_profile": {
    "id": "2111ade6gk054dfdb9iu8c8cc9460mks",
    "park_id": "ee6f33c4562b4e1f8646d157bd70b2c4",
    "created_date": "2020-04-23T13:08:05.552+0000",
    "last_name": "Ivanov",
    "first_name": "Ivan",
    "middle_name": "Ivanovich",
    "driver_license": {
      "issue_date": "2020-10-28",
      "expiration_date": "2050-10-28",
      "number": "070236",
      "normalized_number": "AA00123456",
      "country": "rus",
      "birth_date": "1975-10-28"
    },
    "phones": [
      "+79999999999"
    ],
    "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
    "work_status": "working",
    "check_message": "great driver",
    "comment": "great driver",
    "employment_type": "selfemployed",
    "has_contract_issue": true
  }
}

DriverProfilePark
Name

Description

city

Type: string

City where the partner operates

Example: Tel Aviv

id

Type: ParkId

Partner ID

Example: ee6f33c4562b4e1f8646d157bd70b2c4

name

Type: string

Partner name

Example: Mickey Mouse Company

Example
{
  "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
  "city": "Tel Aviv",
  "name": "Mickey Mouse Company"
}

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