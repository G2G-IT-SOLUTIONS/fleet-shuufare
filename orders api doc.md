Getting list of orders
Getting list of orders

Request
POST

https://fleet-api.yango.tech/v1/parks/orders/list

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

Body
application/json
{
  "query": {
    "park": {
      "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
      "order": {
        "ids": [
          "c8d40acf182b4b32af72f6ad2029031b"
        ],
        "short_ids": [
          248
        ],
        "booked_at": {
          "from": "2019-08-08T11:58:01+03:00",
          "to": null
        },
        "ended_at": null,
        "type": {
          "ids": [
            null
          ]
        },
        "statuses": [
          "complete"
        ],
        "payment_methods": [
          "card"
        ],
        "providers": [
          "platform"
        ],
        "categories": [
          "econom"
        ],
        "price": {
          "from": "12345.1434",
          "to": null
        }
      },
      "driver_profile": {
        "id": "33de650c6a1a40bfa78dd981817da866"
      },
      "car": {
        "id": "5011ade6ba054dfdb7143c8cc9460dbc"
      }
    }
  },
  "limit": 100,
  "cursor": "example"
}

Name

Description

limit

Type: OrdersListLimit

Upper limit of the number of orders per response

Min value: 1

Max value: 500

Example: 100

query

Type: OrdersListQuery

Example
{
  "park": {
    "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
    "order": {
      "ids": [
        "c8d40acf182b4b32af72f6ad2029031b"
      ],
      "short_ids": [
        248
      ],
      "booked_at": {
        "from": "2019-08-08T11:58:01+03:00",
        "to": null
      },
      "ended_at": null,
      "type": {
        "ids": [
          "4964b852670045b196e526d59915b777"
        ]
      },
      "statuses": [
        "complete"
      ],
      "payment_methods": [
        "card"
      ],
      "providers": [
        "platform"
      ],
      "categories": [
        "econom"
      ],
      "price": {
        "from": "12345.1434",
        "to": null
      }
    },
    "driver_profile": {
      "id": "33de650c6a1a40bfa78dd981817da866"
    },
    "car": {
      "id": "5011ade6ba054dfdb7143c8cc9460dbc"
    }
  }
}

cursor

Type: RequestCursor

Cursor for obtaining the next data chunk, the value must be taken from the response to the previous request

Min length: 1

Example: example

ParkId
Partner ID

Type: string

Min length: 1

Max length: 100

Example: ee6f33c4562b4e1f8646d157bd70b2c4

OrderId
Order ID

Type: string

Min length: 1

Max length: 100

Example: c8d40acf182b4b32af72f6ad2029031b

OrderIds
Type: OrderId[]

Min items: 1

Max items: 100

Example
[
  "c8d40acf182b4b32af72f6ad2029031b"
]

OrderShortId
Index number of the order (with canceled orders taken into account)

Type: integer

Min value: 0

OrderShortIds
Type: OrderShortId[]

Min items: 1

Max items: 100

Example
[
  248
]

DateTime
ISO 8601 with time zone

Type: string<date-time>

Example: 2019-08-08T11:58:01+03:00

DateTimeInterval
Name

Description

from

Type: DateTime

ISO 8601 with time zone

Example: 2019-08-08T11:58:01+03:00

to

Type: DateTime

ISO 8601 with time zone

Example: 2019-08-08T11:58:01+03:00

Example
{
  "from": "2019-08-08T11:58:01+03:00",
  "to": null
}

OrderTypeId
Order type ID

Type: string

Min length: 1

Example: 4964b852670045b196e526d59915b777

OrderTypeIds
Type: OrderTypeId[]

Min items: 1

Max items: 100

Example
[
  "4964b852670045b196e526d59915b777"
]

QueryParkOrderType
Name

Description

ids

Type: OrderTypeIds

Min items: 1

Max items: 100

Example
[
  "4964b852670045b196e526d59915b777"
]

Example
{
  "ids": [
    "4964b852670045b196e526d59915b777"
  ]
}

OrderStatus
Order status. Possible values:

none — no status;
driving — en route;
waiting — is waiting for the client;
transporting — is on the ride now;
complete — order completed;
cancelled — cancelled;
calling — status for a technical error;
expired — status for a technical error;
failed — status for a technical error;
Type: string

Enum: none, driving, waiting, transporting, complete, cancelled, calling, expired, failed

Statuses
Type: OrderStatus[]

Min items: 1

Example
[
  "complete"
]

PaymentMethod
Payment method. Possible values:

cash — cash;
cashless — non-cash;
card — card;
internal — internal;
other — other;
corp — corporate account;
prepaid — advance payment.
Type: string

Enum: cash, cashless, card, internal, other, corp, prepaid

PaymentMethods
Type: PaymentMethod[]

Min items: 1

Example
[
  "card"
]

Provider
Type: string

Enum: none, partner, platform

Providers
Type: Provider[]

Min items: 1

Example
[
  "platform"
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

Amount
Fixed-point sum

Type: string

Max length: 20

Example: 12345.1434

PriceInterval
Name

Description

from

Type: Amount

Fixed-point sum

Max length: 20

Example: 12345.1434

to

Type: Amount

Fixed-point sum

Max length: 20

Example: 12345.1434

Example
{
  "from": "12345.1434",
  "to": null
}

OrdersListQueryParkOrder
Either booked_at or ended_at is required

Name

Description

booked_at

Type: DateTimeInterval

Example
{
  "from": "2019-08-08T11:58:01+03:00",
  "to": null
}

categories

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

ended_at

Type: DateTimeInterval

Example
{
  "from": "2019-08-08T11:58:01+03:00",
  "to": null
}

ids

Type: OrderIds

Min items: 1

Max items: 100

Example
[
  "c8d40acf182b4b32af72f6ad2029031b"
]

payment_methods

Type: PaymentMethods

Min items: 1

Example
[
  "card"
]

price

Type: PriceInterval

Example
{
  "from": "12345.1434",
  "to": null
}

providers

Type: Providers

Min items: 1

Example
[
  "platform"
]

short_ids

Type: OrderShortIds

Min items: 1

Max items: 100

Example
[
  248
]

statuses

Type: Statuses

Min items: 1

Example
[
  "complete"
]

type

Type: QueryParkOrderType

Example
{
  "ids": [
    "4964b852670045b196e526d59915b777"
  ]
}

Example
{
  "ids": [
    "c8d40acf182b4b32af72f6ad2029031b"
  ],
  "short_ids": [
    248
  ],
  "booked_at": {
    "from": "2019-08-08T11:58:01+03:00",
    "to": null
  },
  "ended_at": null,
  "type": {
    "ids": [
      "4964b852670045b196e526d59915b777"
    ]
  },
  "statuses": [
    "complete"
  ],
  "payment_methods": [
    "card"
  ],
  "providers": [
    "platform"
  ],
  "categories": [
    "econom"
  ],
  "price": {
    "from": "12345.1434",
    "to": null
  }
}

DriverProfileId
Driver ID

Type: string

Min length: 1

Max length: 100

Example: 33de650c6a1a40bfa78dd981817da866

OrdersListQueryParkDriverProfile
Name

Description

id

Type: DriverProfileId

Driver ID

Min length: 1

Max length: 100

Example: 33de650c6a1a40bfa78dd981817da866

Example
{
  "id": "33de650c6a1a40bfa78dd981817da866"
}

CarId
Vehicle ID

Type: string

Min length: 1

Max length: 100

Example: 5011ade6ba054dfdb7143c8cc9460dbc

OrdersListQueryParkCar
Name

Description

id

Type: CarId

Vehicle ID

Min length: 1

Max length: 100

Example: 5011ade6ba054dfdb7143c8cc9460dbc

Example
{
  "id": "5011ade6ba054dfdb7143c8cc9460dbc"
}

OrdersListQueryPark
Name

Description

id

Type: ParkId

Partner ID

Min length: 1

Max length: 100

Example: ee6f33c4562b4e1f8646d157bd70b2c4

order

Type: OrdersListQueryParkOrder

Either booked_at or ended_at is required

Example
{
  "ids": [
    "c8d40acf182b4b32af72f6ad2029031b"
  ],
  "short_ids": [
    248
  ],
  "booked_at": {
    "from": "2019-08-08T11:58:01+03:00",
    "to": null
  },
  "ended_at": null,
  "type": {
    "ids": [
      "4964b852670045b196e526d59915b777"
    ]
  },
  "statuses": [
    "complete"
  ],
  "payment_methods": [
    "card"
  ],
  "providers": [
    "platform"
  ],
  "categories": [
    "econom"
  ],
  "price": {
    "from": "12345.1434",
    "to": null
  }
}

car

Type: OrdersListQueryParkCar

Example
{
  "id": "5011ade6ba054dfdb7143c8cc9460dbc"
}

driver_profile

Type: OrdersListQueryParkDriverProfile

Example
{
  "id": "33de650c6a1a40bfa78dd981817da866"
}

Example
{
  "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
  "order": {
    "ids": [
      "c8d40acf182b4b32af72f6ad2029031b"
    ],
    "short_ids": [
      248
    ],
    "booked_at": {
      "from": "2019-08-08T11:58:01+03:00",
      "to": null
    },
    "ended_at": null,
    "type": {
      "ids": [
        "4964b852670045b196e526d59915b777"
      ]
    },
    "statuses": [
      "complete"
    ],
    "payment_methods": [
      "card"
    ],
    "providers": [
      "platform"
    ],
    "categories": [
      "econom"
    ],
    "price": {
      "from": "12345.1434",
      "to": null
    }
  },
  "driver_profile": {
    "id": "33de650c6a1a40bfa78dd981817da866"
  },
  "car": {
    "id": "5011ade6ba054dfdb7143c8cc9460dbc"
  }
}

OrdersListQuery
Name

Description

park

Type: OrdersListQueryPark

Example
{
  "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
  "order": {
    "ids": [
      "c8d40acf182b4b32af72f6ad2029031b"
    ],
    "short_ids": [
      248
    ],
    "booked_at": {
      "from": "2019-08-08T11:58:01+03:00",
      "to": null
    },
    "ended_at": null,
    "type": {
      "ids": [
        "4964b852670045b196e526d59915b777"
      ]
    },
    "statuses": [
      "complete"
    ],
    "payment_methods": [
      "card"
    ],
    "providers": [
      "platform"
    ],
    "categories": [
      "econom"
    ],
    "price": {
      "from": "12345.1434",
      "to": null
    }
  },
  "driver_profile": {
    "id": "33de650c6a1a40bfa78dd981817da866"
  },
  "car": {
    "id": "5011ade6ba054dfdb7143c8cc9460dbc"
  }
}

Example
{
  "park": {
    "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
    "order": {
      "ids": [
        "c8d40acf182b4b32af72f6ad2029031b"
      ],
      "short_ids": [
        248
      ],
      "booked_at": {
        "from": "2019-08-08T11:58:01+03:00",
        "to": null
      },
      "ended_at": null,
      "type": {
        "ids": [
          "4964b852670045b196e526d59915b777"
        ]
      },
      "statuses": [
        "complete"
      ],
      "payment_methods": [
        "card"
      ],
      "providers": [
        "platform"
      ],
      "categories": [
        "econom"
      ],
      "price": {
        "from": "12345.1434",
        "to": null
      }
    },
    "driver_profile": {
      "id": "33de650c6a1a40bfa78dd981817da866"
    },
    "car": {
      "id": "5011ade6ba054dfdb7143c8cc9460dbc"
    }
  }
}

OrdersListLimit
Upper limit of the number of orders per response

Type: integer

Min value: 1

Max value: 500

RequestCursor
Cursor for obtaining the next data chunk, the value must be taken from the response to the previous request

Type: string

Min length: 1

Example: example

Responses
200 OK
List of orders

Body
application/json
{
  "orders": [
    {
      "id": "c8d40acf182b4b32af72f6ad2029031b",
      "short_id": 248,
      "status": "complete",
      "created_at": "2019-08-08T11:58:01+03:00",
      "booked_at": null,
      "provider": "platform",
      "category": "econom",
      "amenities": [
        "wifi"
      ],
      "address_from": {
        "address": "8 Liberty Street",
        "lat": 55.762235,
        "lon": 37.609651
      },
      "route_points": [
        null
      ],
      "events": [
        {
          "event_at": null,
          "order_status": null
        }
      ],
      "ended_at": null,
      "payment_method": "card",
      "driver_profile": {
        "id": "33de650c6a1a40bfa78dd981817da866",
        "name": "Smith, John Richard"
      },
      "car": {
        "id": "5011ade6ba054dfdb7143c8cc9460dbc",
        "brand_model": "BMW 5er",
        "license": {
          "number": "AA01234567"
        },
        "callsign": "123456789"
      },
      "type": {
        "id": "4964b852670045b196e526d59915b777",
        "name": "Yandex.Cashless"
      },
      "price": "12345.1434",
      "driver_work_rule": {
        "id": "e26a3cf21acfe01198d50030487e046b",
        "name": "Rental"
      },
      "mileage": "example",
      "cancellation_description": "example",
      "park_details": {
        "tariff": {
          "id": "example",
          "name": "example"
        },
        "passenger": {
          "name": "example",
          "phones": [
            null
          ]
        },
        "company": {
          "id": "example",
          "name": "example",
          "slip": "example",
          "comment": "example"
        }
      }
    }
  ],
  "limit": 100,
  "cursor": ""
}

Name

Description

limit

Type: OrdersListLimit

Upper limit of the number of orders per response

Min value: 1

Max value: 500

Example: 100

orders

Type: OrdersList

Example
[
  {
    "id": "c8d40acf182b4b32af72f6ad2029031b",
    "short_id": 248,
    "status": "complete",
    "created_at": "2019-08-08T11:58:01+03:00",
    "booked_at": null,
    "provider": "platform",
    "category": "econom",
    "amenities": [
      "wifi"
    ],
    "address_from": {
      "address": "8 Liberty Street",
      "lat": 55.762235,
      "lon": 37.609651
    },
    "route_points": [
      null
    ],
    "events": [
      {
        "event_at": null,
        "order_status": null
      }
    ],
    "ended_at": null,
    "payment_method": "card",
    "driver_profile": {
      "id": "33de650c6a1a40bfa78dd981817da866",
      "name": "Smith, John Richard"
    },
    "car": {
      "id": "5011ade6ba054dfdb7143c8cc9460dbc",
      "brand_model": "BMW 5er",
      "license": {
        "number": "AA01234567"
      },
      "callsign": "123456789"
    },
    "type": {
      "id": "4964b852670045b196e526d59915b777",
      "name": "Yandex.Cashless"
    },
    "price": "12345.1434",
    "driver_work_rule": {
      "id": "e26a3cf21acfe01198d50030487e046b",
      "name": "Rental"
    },
    "mileage": "example",
    "cancellation_description": "example",
    "park_details": {
      "tariff": {
        "id": "example",
        "name": "example"
      },
      "passenger": {
        "name": "example",
        "phones": [
          "example"
        ]
      },
      "company": {
        "id": "example",
        "name": "example",
        "slip": "example",
        "comment": "example"
      }
    }
  }
]

cursor

Type: ResponseCursor

Cursor for obtaining the next data chunk

Example: ``

Category
Vehicle category. Possible values:

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
child_tariff — Kids service class;
ultimate — Premier;
maybach — elite class vehicle;
promo — promotion;
premium_van — cruise van;
premium_suv — premium SUV;
suv — SUV;
personal_driver — personal driver class vehicle;
express — delivery class vehicle;
cargo — a cargo vehicle.
Type: string

Enum: econom, comfort, comfort_plus, business, minivan, vip, wagon, pool, start, standart, child_tariff, ultimate, maybach, promo, premium_van, premium_suv, suv, personal_driver, express, cargo

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

AddressInfo
Name

Description

address

Type: string

Order address

Example: 8 Liberty Street

lat

Type: number

Geographic latitude

lon

Type: number

Geographic longitude

Example
{
  "address": "8 Liberty Street",
  "lat": 55.762235,
  "lon": 37.609651
}

RoutePoints
Type: AddressInfo[]

Example
[
  {
    "address": "8 Liberty Street",
    "lat": 55.762235,
    "lon": 37.609651
  }
]

Event
Name

Description

event_at

Type: DateTime

ISO 8601 with time zone

Example: 2019-08-08T11:58:01+03:00

order_status

Type: OrderStatus

Order status. Possible values:

none — no status;
driving — en route;
waiting — is waiting for the client;
transporting — is on the ride now;
complete — order completed;
cancelled — cancelled;
calling — status for a technical error;
expired — status for a technical error;
failed — status for a technical error;
Enum: none, driving, waiting, transporting, complete, cancelled, calling, expired, failed

Example
{
  "event_at": "2019-08-08T11:58:01+03:00",
  "order_status": "complete"
}

Events
Type: Event[]

Example
[
  {
    "event_at": "2019-08-08T11:58:01+03:00",
    "order_status": "complete"
  }
]

DriverProfile
Name

Description

id

Type: DriverProfileId

Driver ID

Min length: 1

Max length: 100

Example: 33de650c6a1a40bfa78dd981817da866

name

Type: string

Driver's full name

Example: Smith, John Richard

Example
{
  "id": "33de650c6a1a40bfa78dd981817da866",
  "name": "Smith, John Richard"
}

License
Name

Description

number

Type: string

Vehicle registration number

Example: AA01234567

Example
{
  "number": "AA01234567"
}

Callsign
Vehicle code name (short name)

Type: string

Example: 123456789

OrdersListCar
Name

Description

brand_model

Type: string

Vehicle make and model

Example: BMW 5er

callsign

Type: Callsign

Vehicle code name (short name)

Example: 123456789

id

Type: CarId

Vehicle ID

Min length: 1

Max length: 100

Example: 5011ade6ba054dfdb7143c8cc9460dbc

license

Type: License

Example
Example
{
  "id": "5011ade6ba054dfdb7143c8cc9460dbc",
  "brand_model": "BMW 5er",
  "license": {
    "number": "AA01234567"
  },
  "callsign": "123456789"
}

OrderType
Name

Description

id

Type: OrderTypeId

Order type ID

Min length: 1

Example: 4964b852670045b196e526d59915b777

name

Type: string

Order type name

Example: Yandex.Cashless

Example
{
  "id": "4964b852670045b196e526d59915b777",
  "name": "Yandex.Cashless"
}

DriverWorkRule
Driver's working condition

Name

Description

id

Type: string

Working condition ID of the driver

Example: e26a3cf21acfe01198d50030487e046b

name

Type: string

Working condition name of the driver

Example: Rental

Example
{
  "id": "e26a3cf21acfe01198d50030487e046b",
  "name": "Rental"
}

OrderTariff
Taxi company's service classes

Name

Description

id

Type: string

Example: example

name

Type: string

Example: example

Example
{
  "id": "example",
  "name": "example"
}

Passenger
Name

Description

name

Type: string

Example: example

phones

Type: string[]

Min items: 1

Max items: 3

Example
Example
{
  "name": "example",
  "phones": [
    "example"
  ]
}

Company
Name

Description

comment

Type: string

Example: example

id

Type: string

Example: example

name

Type: string

Example: example

slip

Type: string

Example: example

Example
{
  "id": "example",
  "name": "example",
  "slip": "example",
  "comment": "example"
}

ParkDetails
Name

Description

company

Type: Company

Example
passenger

Type: Passenger

Example
tariff

Type: OrderTariff

Taxi company's service classes

Example
Example
{
  "tariff": {
    "id": "example",
    "name": "example"
  },
  "passenger": {
    "name": "example",
    "phones": [
      "example"
    ]
  },
  "company": {
    "id": "example",
    "name": "example",
    "slip": "example",
    "comment": "example"
  }
}

Order
Name

Description

address_from

Type: AddressInfo

Example
{
  "address": "8 Liberty Street",
  "lat": 55.762235,
  "lon": 37.609651
}

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

booked_at

Type: DateTime

ISO 8601 with time zone

Example: 2019-08-08T11:58:01+03:00

created_at

Type: DateTime

ISO 8601 with time zone

Example: 2019-08-08T11:58:01+03:00

events

Type: Events

Example
[
  {
    "event_at": "2019-08-08T11:58:01+03:00",
    "order_status": "complete"
  }
]

id

Type: OrderId

Order ID

Min length: 1

Max length: 100

Example: c8d40acf182b4b32af72f6ad2029031b

provider

Type: Provider

Enum: none, partner, platform

route_points

Type: RoutePoints

Example
[
  {
    "address": "8 Liberty Street",
    "lat": 55.762235,
    "lon": 37.609651
  }
]

short_id

Type: OrderShortId

Index number of the order (with canceled orders taken into account)

Min value: 0

Example: 248

status

Type: OrderStatus

Order status. Possible values:

none — no status;
driving — en route;
waiting — is waiting for the client;
transporting — is on the ride now;
complete — order completed;
cancelled — cancelled;
calling — status for a technical error;
expired — status for a technical error;
failed — status for a technical error;
Enum: none, driving, waiting, transporting, complete, cancelled, calling, expired, failed

cancellation_description

Type: string

Example: example

car

Type: OrdersListCar

Example
{
  "id": "5011ade6ba054dfdb7143c8cc9460dbc",
  "brand_model": "BMW 5er",
  "license": {
    "number": "AA01234567"
  },
  "callsign": "123456789"
}

category

Type: Category

Vehicle category. Possible values:

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
child_tariff — Kids service class;
ultimate — Premier;
maybach — elite class vehicle;
promo — promotion;
premium_van — cruise van;
premium_suv — premium SUV;
suv — SUV;
personal_driver — personal driver class vehicle;
express — delivery class vehicle;
cargo — a cargo vehicle.
Enum: econom, comfort, comfort_plus, business, minivan, vip, wagon, pool, start, standart, child_tariff, ultimate, maybach, promo, premium_van, premium_suv, suv, personal_driver, express, cargo

driver_profile

Type: DriverProfile

Example
{
  "id": "33de650c6a1a40bfa78dd981817da866",
  "name": "Smith, John Richard"
}

driver_work_rule

Type: DriverWorkRule

Driver's working condition

Example
{
  "id": "e26a3cf21acfe01198d50030487e046b",
  "name": "Rental"
}

ended_at

Type: DateTime

ISO 8601 with time zone

Example: 2019-08-08T11:58:01+03:00

mileage

Type: string

Example: example

park_details

Type: ParkDetails

Example
{
  "tariff": {
    "id": "example",
    "name": "example"
  },
  "passenger": {
    "name": "example",
    "phones": [
      "example"
    ]
  },
  "company": {
    "id": "example",
    "name": "example",
    "slip": "example",
    "comment": "example"
  }
}

payment_method

Type: PaymentMethod

Payment method. Possible values:

cash — cash;
cashless — non-cash;
card — card;
internal — internal;
other — other;
corp — corporate account;
prepaid — advance payment.
Enum: cash, cashless, card, internal, other, corp, prepaid

price

Type: Amount

Fixed-point sum

Max length: 20

Example: 12345.1434

type

Type: OrderType

Example
{
  "id": "4964b852670045b196e526d59915b777",
  "name": "Yandex.Cashless"
}

Example
{
  "id": "c8d40acf182b4b32af72f6ad2029031b",
  "short_id": 248,
  "status": "complete",
  "created_at": "2019-08-08T11:58:01+03:00",
  "booked_at": null,
  "provider": "platform",
  "category": "econom",
  "amenities": [
    "wifi"
  ],
  "address_from": {
    "address": "8 Liberty Street",
    "lat": 55.762235,
    "lon": 37.609651
  },
  "route_points": [
    null
  ],
  "events": [
    {
      "event_at": null,
      "order_status": null
    }
  ],
  "ended_at": null,
  "payment_method": "card",
  "driver_profile": {
    "id": "33de650c6a1a40bfa78dd981817da866",
    "name": "Smith, John Richard"
  },
  "car": {
    "id": "5011ade6ba054dfdb7143c8cc9460dbc",
    "brand_model": "BMW 5er",
    "license": {
      "number": "AA01234567"
    },
    "callsign": "123456789"
  },
  "type": {
    "id": "4964b852670045b196e526d59915b777",
    "name": "Yandex.Cashless"
  },
  "price": "12345.1434",
  "driver_work_rule": {
    "id": "e26a3cf21acfe01198d50030487e046b",
    "name": "Rental"
  },
  "mileage": "example",
  "cancellation_description": "example",
  "park_details": {
    "tariff": {
      "id": "example",
      "name": "example"
    },
    "passenger": {
      "name": "example",
      "phones": [
        "example"
      ]
    },
    "company": {
      "id": "example",
      "name": "example",
      "slip": "example",
      "comment": "example"
    }
  }
}

OrdersList
Type: Order[]

Example
[
  {
    "id": "c8d40acf182b4b32af72f6ad2029031b",
    "short_id": 248,
    "status": "complete",
    "created_at": "2019-08-08T11:58:01+03:00",
    "booked_at": null,
    "provider": "platform",
    "category": "econom",
    "amenities": [
      "wifi"
    ],
    "address_from": {
      "address": "8 Liberty Street",
      "lat": 55.762235,
      "lon": 37.609651
    },
    "route_points": [
      null
    ],
    "events": [
      {
        "event_at": null,
        "order_status": null
      }
    ],
    "ended_at": null,
    "payment_method": "card",
    "driver_profile": {
      "id": "33de650c6a1a40bfa78dd981817da866",
      "name": "Smith, John Richard"
    },
    "car": {
      "id": "5011ade6ba054dfdb7143c8cc9460dbc",
      "brand_model": "BMW 5er",
      "license": {
        "number": "AA01234567"
      },
      "callsign": "123456789"
    },
    "type": {
      "id": "4964b852670045b196e526d59915b777",
      "name": "Yandex.Cashless"
    },
    "price": "12345.1434",
    "driver_work_rule": {
      "id": "e26a3cf21acfe01198d50030487e046b",
      "name": "Rental"
    },
    "mileage": "example",
    "cancellation_description": "example",
    "park_details": {
      "tariff": {
        "id": "example",
        "name": "example"
      },
      "passenger": {
        "name": "example",
        "phones": [
          "example"
        ]
      },
      "company": {
        "id": "example",
        "name": "example",
        "slip": "example",
        "comment": "example"
      }
    }
  }
]

ResponseCursor
Cursor for obtaining the next data chunk

Type: string

Example: ``

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

Was the article helpful?
Previous
Getting list of work rules
Next
