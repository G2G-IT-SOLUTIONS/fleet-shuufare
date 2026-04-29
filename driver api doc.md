Getting driver profile (courier)
Getting driver profile (courier)

Request
GET

https://fleet-api.yango.tech/v2/parks/contractors/driver-profile

Query parameters
Name

Description

contractor_profile_id

Type: string

Driver's profile ID

Example: 9b17db0cb1f24a38a5c3c8b4f6e4f63b

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

X-Park-ID

Type: string

Partner ID

Example: ee6f33c4562b4e1f8646d157bd70b2c4

 Responses
200 OK
Get driver (courier) profile

Body
application/json
{
  "account": {
    "balance_limit": "50",
    "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
    "payment_service_id": "12345",
    "block_orders_on_balance_below_limit": true
  },
  "person": {
    "full_name": {
      "first_name": "Ivan",
      "middle_name": "Ivanovich",
      "last_name": "Ivanov"
    },
    "contact_info": {
      "address": "Moscow, Ivanovskaya Ul., bld. 40/2, appt. 63",
      "email": "example-email@example.com",
      "phone": "+79999999999"
    },
    "driver_license": {
      "birth_date": "1975-10-28",
      "country": "rus",
      "expiry_date": "2050-10-28",
      "issue_date": "2020-10-28",
      "number": "070236"
    },
    "driver_license_experience": {
      "total_since_date": "1970-01-01"
    },
    "tax_identification_number": "7743013902",
    "employment_type": "selfemployed"
  },
  "profile": {
    "hire_date": "2020-10-28",
    "work_status": "working",
    "fire_date": "2020-10-28",
    "comment": "great driver",
    "feedback": "great driver"
  },
  "car_id": "5011ade6ba054dfdb7143c8cc9460dbc",
  "order_provider": {
    "platform": true,
    "partner": true
  }
}

Name

Description

account

Type: AccountOptional

Driver's account

Example
{
  "balance_limit": "50",
  "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
  "payment_service_id": "12345",
  "block_orders_on_balance_below_limit": true
}

order_provider

Type: OrderProvider

Example
{
  "platform": true,
  "partner": true
}

person

Type: PersonOptional

Driver's personal info

Example
{
  "full_name": {
    "first_name": "Ivan",
    "middle_name": "Ivanovich",
    "last_name": "Ivanov"
  },
  "contact_info": {
    "address": "Moscow, Ivanovskaya Ul., bld. 40/2, appt. 63",
    "email": "example-email@example.com",
    "phone": "+79999999999"
  },
  "driver_license": {
    "birth_date": "1975-10-28",
    "country": "rus",
    "expiry_date": "2050-10-28",
    "issue_date": "2020-10-28",
    "number": "070236"
  },
  "driver_license_experience": {
    "total_since_date": "1970-01-01"
  },
  "tax_identification_number": "7743013902",
  "employment_type": "selfemployed"
}

profile

Type: ProfileOptional

Example
{
  "hire_date": "2020-10-28",
  "work_status": "working",
  "fire_date": "2020-10-28",
  "comment": "great driver",
  "feedback": "great driver"
}

car_id

Type: CarId

Vehicle ID

Min length: 1

Max length: 100

Example: 5011ade6ba054dfdb7143c8cc9460dbc

BalanceLimit
Balance limit

Type: string

Example: 50

WorkRuleId
Work rule ID

Type: string

Example: bc43tre6ba054dfdb7143ckfgvcby63e

PaymentServiceIdUpdate
ID for payments

Type: string

Example: 12345

BlockOrdersOnBalanceBelowLimit
Disable all orders if balance is below the limit

Type: boolean

AccountOptional
Driver's account

Name

Description

balance_limit

Type: BalanceLimit

Balance limit

Example: 50

block_orders_on_balance_below_limit

Type: BlockOrdersOnBalanceBelowLimit

Disable all orders if balance is below the limit

Example: true

payment_service_id

Type: PaymentServiceIdUpdate

ID for payments

Example: 12345

work_rule_id

Type: WorkRuleId

Work rule ID

Example: bc43tre6ba054dfdb7143ckfgvcby63e

Example
{
  "balance_limit": "50",
  "work_rule_id": "bc43tre6ba054dfdb7143ckfgvcby63e",
  "payment_service_id": "12345",
  "block_orders_on_balance_below_limit": true
}

FirstName
Name

Type: string

Example: Ivan

MiddleName
Middle name

Type: string

Example: Ivanovich

LastName
Last name

Type: string

Example: Ivanov

FullNameOptional
Driver's full name

Name

Description

first_name

Type: FirstName

Name

Example: Ivan

last_name

Type: LastName

Last name

Example: Ivanov

middle_name

Type: MiddleName

Middle name

Example: Ivanovich

Example
{
  "first_name": "Ivan",
  "middle_name": "Ivanovich",
  "last_name": "Ivanov"
}

Address
Address

Type: string

Example: Moscow, Ivanovskaya Ul., bld. 40/2, appt. 63

Email
Email

Type: string

Example: example-email@example.com

Phone
Phone number

Type: string

Pattern: ^\+\d{1,15}$

Example: +79999999999

ContactInfoOptional
Driver's contact info

Name

Description

address

Type: Address

Address

Example: Moscow, Ivanovskaya Ul., bld. 40/2, appt. 63

email

Type: Email

Email

Example: example-email@example.com

phone

Type: Phone

Phone number

Pattern: ^\+\d{1,15}$

Example: +79999999999

Example
{
  "address": "Moscow, Ivanovskaya Ul., bld. 40/2, appt. 63",
  "email": "example-email@example.com",
  "phone": "+79999999999"
}

BirthDate
Birth date in ISO 8601 format without time zone

Type: string

Example: 1975-10-28

CountryCode
Country of issue (Three-letter code)

Type: string

Example: rus

ExpiryDate
Driver's license expiry date in ISO 8601 format without time zone

Type: string

Example: 2050-10-28

IssueDate
Date of issue of the driver's license in ISO 8601 format without time zone

Type: string

Example: 2020-10-28

Number
Driver's license series and number

Type: string

Example: 070236

DriverLicenseOptional
Driver's license info

Name

Description

birth_date

Type: BirthDate

Birth date in ISO 8601 format without time zone

Example: 1975-10-28

country

Type: CountryCode

Country of issue (Three-letter code)

Example: rus

expiry_date

Type: ExpiryDate

Driver's license expiry date in ISO 8601 format without time zone

Example: 2050-10-28

issue_date

Type: IssueDate

Date of issue of the driver's license in ISO 8601 format without time zone

Example: 2020-10-28

number

Type: Number

Driver's license series and number

Example: 070236

Example
{
  "birth_date": "1975-10-28",
  "country": "rus",
  "expiry_date": "2050-10-28",
  "issue_date": "2020-10-28",
  "number": "070236"
}

Date
Date without time zone in ISO 8601 format

Type: string

Example: 1970-01-01

DriverLicenseExperience
Driving experience since

Name

Description

total_since_date

Type: Date

Date without time zone in ISO 8601 format

Example: 1970-01-01

Example
{
  "total_since_date": "1970-01-01"
}

TaxIdentificationNumber
Tax identification number

Type: string

Min length: 1

Example: 7743013902

EmploymentType
Driver's employment type. Possible values:

selfemployed — Self-employed;
park_employee — Park employee;
individual_entrepreneur — Individual entrepreneur;
Type: string

Enum: selfemployed, park_employee, individual_entrepreneur

PersonOptional
Driver's personal info

Name

Description

contact_info

Type: ContactInfoOptional

Driver's contact info

Example
{
  "address": "Moscow, Ivanovskaya Ul., bld. 40/2, appt. 63",
  "email": "example-email@example.com",
  "phone": "+79999999999"
}

driver_license

Type: DriverLicenseOptional

Driver's license info

Example
{
  "birth_date": "1975-10-28",
  "country": "rus",
  "expiry_date": "2050-10-28",
  "issue_date": "2020-10-28",
  "number": "070236"
}

driver_license_experience

Type: DriverLicenseExperience

Driving experience since

Example
{
  "total_since_date": "1970-01-01"
}

employment_type

Type: EmploymentType

Driver's employment type. Possible values:

selfemployed — Self-employed;
park_employee — Park employee;
individual_entrepreneur — Individual entrepreneur;
Enum: selfemployed, park_employee, individual_entrepreneur

full_name

Type: FullNameOptional

Driver's full name

Example
{
  "first_name": "Ivan",
  "middle_name": "Ivanovich",
  "last_name": "Ivanov"
}

tax_identification_number

Type: TaxIdentificationNumber

Tax identification number

Min length: 1

Example: 7743013902

Example
{
  "full_name": {
    "first_name": "Ivan",
    "middle_name": "Ivanovich",
    "last_name": "Ivanov"
  },
  "contact_info": {
    "address": "Moscow, Ivanovskaya Ul., bld. 40/2, appt. 63",
    "email": "example-email@example.com",
    "phone": "+79999999999"
  },
  "driver_license": {
    "birth_date": "1975-10-28",
    "country": "rus",
    "expiry_date": "2050-10-28",
    "issue_date": "2020-10-28",
    "number": "070236"
  },
  "driver_license_experience": {
    "total_since_date": "1970-01-01"
  },
  "tax_identification_number": "7743013902",
  "employment_type": "selfemployed"
}

HireDate
Hiring date in ISO 8601 format without time zone

Type: string

Example: 2020-10-28

WorkStatus
Driver's working status. Possible values:

working — "Is working" status.
not_working — "Not working" status;
fired — status for dismissed drivers;
Type: string

Enum: working, not_working, fired

FireDate
Date of dismissal in ISO 8601 format without time zone

Type: string

Example: 2020-10-28

Comment
Notes

Type: string

Example: great driver

FeedBack
Notes (available to park employees)

Type: string

Example: great driver

ProfileOptional
Name

Description

comment

Type: Comment

Notes

Example: great driver

feedback

Type: FeedBack

Notes (available to park employees)

Example: great driver

fire_date

Type: FireDate

Date of dismissal in ISO 8601 format without time zone

Example: 2020-10-28

hire_date

Type: HireDate

Hiring date in ISO 8601 format without time zone

Example: 2020-10-28

work_status

Type: WorkStatus

Driver's working status. Possible values:

working — "Is working" status.
not_working — "Not working" status;
fired — status for dismissed drivers;
Enum: working, not_working, fired

Example
{
  "hire_date": "2020-10-28",
  "work_status": "working",
  "fire_date": "2020-10-28",
  "comment": "great driver",
  "feedback": "great driver"
}

CarId
Vehicle ID

Type: string

Min length: 1

Max length: 100

Example: 5011ade6ba054dfdb7143c8cc9460dbc

Platform
Are orders from the platform available

Type: boolean

Partner
Are orders from a partner available

Type: boolean

OrderProvider
Name

Description

partner

Type: Partner

Are orders from a partner available

Example: true

platform

Type: Platform

Are orders from the platform available

Example: true

Example
{
  "platform": true,
  "partner": true
}

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

