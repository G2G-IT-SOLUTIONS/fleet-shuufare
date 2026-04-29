# YANGO Fleet API Reference

1. [Overview](#overview)
2. [Authentication & Headers](#authentication--headers)
3. [API Endpoints](#api-endpoints)
   - [Transactions API](#transactions-api)
     - [Get Transaction Categories](#1-get-transaction-categories)
     - [Get Driver Transactions](#2-get-driver-transactions)
     - [Get Park-Wide Transactions](#3-get-park-wide-transactions)
     - [Get Order-Linked Transactions](#4-get-order-linked-transactions)
     - [Create Transaction](#5-create-transaction)
     - [Check Transaction Status](#6-check-transaction-status)
   - [Driver Profiles API](#driver-profiles-api)
     - [Get Driver Profile](#7-get-driver-profile)
     - [Get List of Driver Profiles](#8-get-list-of-driver-profiles)
   - [Supply Hours API](#supply-hours-api)
     - [Get Driver's Online Time](#9-get-drivers-online-time)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)
8. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## Overview

The YANGO Fleet API provides comprehensive management for fleet operators. It enables real-time balance tracking, transaction history retrieval, manual transaction creation, driver profile management, and supply hours tracking.

---

## Authentication & Headers

### Required Headers

| Name | Description | Example |
|------|-------------|---------|
| `X-API-Key` | API authentication key (Min length: 1) | `<API key>` |
| `X-Client-ID` | Client identifier (Min length: 1) | `<Client ID>` |
| `Content-Type` | Must be `application/json` | `application/json` |

### Optional Headers

| Name | Description | Example |
|------|-------------|---------|
| `Accept-Language` | Preferred language of the response (Min length: 2) | `ru`, `en` |
| `X-Park-ID` | Partner/Park identifier | `ee6f33c4562b4e1f8646d157bd70b2c4` |
| `X-Idempotency-Token` | Prevents duplicate operations (UUID v4) | `550e8400-e29b-41d4-a716-446655440000` |

---

## API Endpoints

### Transactions API

#### 1. Get Transaction Categories

Retrieves all available transaction categories for validation and UI dropdowns.

**Endpoint:** `POST https://fleet-api.yango.tech/v2/parks/transactions/categories/list`

**Request Body:**
```json
{
  "query": {
    "park": {
      "id": "ee6f33c4562b4e1f8646d157bd70b2c4"
    },
    "category": {
      "is_enabled": true,
      "is_editable": true,
      "is_creatable": true,
      "is_affecting_driver_balance": true
    }
  }
}
```

**Request Definitions:**

- **ParkId**: Partner ID. Type: string. Min length: 1, Max length: 100. Example: `ee6f33c4562b4e1f8646d157bd70b2c4`.
- **ParksTransactionsCategoriesListQueryPark**:
    - `id` (Type: `ParkId`): Partner ID.
- **TransactionCategoryIsEnabled**: Whether the transaction category is enabled (false only for partners categories). Type: boolean.
- **TransactionCategoryIsEditable**: Whether the transaction category is editable (true for partners category). Type: boolean.
- **TransactionCategoryIsCreatable**: Whether a new transaction can be created in the category. Type: boolean.
- **TransactionCategoryIsAffectingDriverBalance**: Whether the transaction in the category impacts the driver's account balance. Type: boolean.
- **ParksTransactionsCategoriesListQueryCategory**:
    - `is_affecting_driver_balance` (Type: `TransactionCategoryIsAffectingDriverBalance`)
    - `is_creatable` (Type: `TransactionCategoryIsCreatable`)
    - `is_editable` (Type: `TransactionCategoryIsEditable`)
    - `is_enabled` (Type: `TransactionCategoryIsEnabled`)
- **ParksTransactionsCategoriesListQuery**:
    - `park` (Type: `ParksTransactionsCategoriesListQueryPark`)
    - `category` (Type: `ParksTransactionsCategoriesListQueryCategory`)

**Response (200 OK):**
```json
{
  "categories": [
    {
      "id": "partner_service_manual",
      "name": "Recurring payments",
      "group_id": "partner_other",
      "group_name": "Other payments of the partner",
      "is_enabled": true,
      "is_editable": true,
      "is_creatable": true,
      "is_affecting_driver_balance": true
    }
  ]
}
```

**Response Definitions:**

- **TransactionCategoryId**: Transaction category ID. Type: string. Min length: 1, Max length: 100. Example: `partner_service_manual`.
- **TransactionCategoryName**: Localized name of the transaction category. Type: string. Min length: 1, Max length: 100. Example: `Recurring payments`.
- **TransactionCategoryGroupId**: Group of transaction category. Type: string. Min length: 1, Max length: 100.
    - `cash_collected` — cash;
    - `platform_card` — card payment;
    - `platform_corporate` — corporate payment;
    - `platform_promotion` — promo campaings;
    - `platform_bonus` — bonus;
    - `platform_tip` — tip;
    - `platform_fees` — platform's fees;
    - `partner_fees` — partner's fee;
    - `partner_other` — other payments of the partner;
    - `platform_other` — other payments of the platform;
    - `partner_rides` — payments for partner's rides.
- **TransactionCategoryGroupName**: Localized name of the transaction category group. Type: string. Min length: 1, Max length: 100. Example: `Other payments of the partner`.
- **TransactionCategory**:
    - `group_id` (Type: `TransactionCategoryGroupId`)
    - `group_name` (Type: `TransactionCategoryGroupName`)
    - `id` (Type: `TransactionCategoryId`)
    - `is_affecting_driver_balance` (Type: `TransactionCategoryIsAffectingDriverBalance`)
    - `is_creatable` (Type: `TransactionCategoryIsCreatable`)
    - `is_editable` (Type: `TransactionCategoryIsEditable`)
    - `is_enabled` (Type: `TransactionCategoryIsEnabled`)
    - `name` (Type: `TransactionCategoryName`)

---

#### 2. Get Driver Transactions

Retrieves transaction history for a specific driver/courier.

**Endpoint:** `POST https://fleet-api.yango.tech/v2/parks/driver-profiles/transactions/list`

(Refer to `API_REFERENCE.md` historical sections for full request/response structure).

---

### Driver Profiles API

#### 7. Get Driver Profile

Retrieves detailed information about a specific driver (courier) profile.

**Endpoint:** `GET https://fleet-api.yango.tech/v2/parks/contractors/driver-profile`

**Query Parameters:**
- `contractor_profile_id` (Type: string): Driver's profile ID. Example: `9b17db0cb1f24a38a5c3c8b4f6e4f63b`.

**Response (200 OK):**
```json
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
```

**Data Definitions (api2.md):**

- **BalanceLimit**: Balance limit. Type: string. Example: `50`.
- **WorkRuleId**: Work rule ID. Type: string.
- **PaymentServiceIdUpdate**: ID for payments. Type: string.
- **BlockOrdersOnBalanceBelowLimit**: Disable all orders if balance is below the limit. Type: boolean.
- **AccountOptional**:
    - `balance_limit` (Type: `BalanceLimit`)
    - `block_orders_on_balance_below_limit` (Type: `BlockOrdersOnBalanceBelowLimit`)
    - `payment_service_id` (Type: `PaymentServiceIdUpdate`)
    - `work_rule_id` (Type: `WorkRuleId`)
- **FirstName**: Name. Type: string.
- **MiddleName**: Middle name. Type: string.
- **LastName**: Last name. Type: string.
- **FullNameOptional**:
    - `first_name` (Type: `FirstName`)
    - `last_name` (Type: `LastName`)
    - `middle_name` (Type: `MiddleName`)
- **Address**: Address. Type: string.
- **Email**: Email. Type: string.
- **Phone**: Phone number. Type: string. Pattern: `^\+\d{1,15}$`.
- **ContactInfoOptional**:
    - `address` (Type: `Address`)
    - `email` (Type: `Email`)
    - `phone` (Type: `Phone`)
- **BirthDate**: Birth date in ISO 8601 without time zone. Type: string.
- **CountryCode**: Country of issue (Three-letter code). Type: string.
- **ExpiryDate**: Driver's license expiry date (ISO 8601). Type: string.
- **IssueDate**: Date of issue (ISO 8601). Type: string.
- **Number**: Driver's license series and number. Type: string.
- **DriverLicenseOptional**:
    - `birth_date` (Type: `BirthDate`)
    - `country` (Type: `CountryCode`)
    - `expiry_date` (Type: `ExpiryDate`)
    - `issue_date` (Type: `IssueDate`)
    - `number` (Type: `Number`)
- **Date**: Date without time zone in ISO 8601 format. Type: string.
- **DriverLicenseExperience**:
    - `total_since_date` (Type: `Date`)
- **TaxIdentificationNumber**: Tax identification number. Type: string.
- **EmploymentType**: Driver's employment type.
    - `selfemployed` — Self-employed;
    - `park_employee` — Park employee;
    - `individual_entrepreneur` — Individual entrepreneur;
- **PersonOptional**:
    - `contact_info` (Type: `ContactInfoOptional`)
    - `driver_license` (Type: `DriverLicenseOptional`)
    - `driver_license_experience` (Type: `DriverLicenseExperience`)
    - `employment_type` (Type: `EmploymentType`)
    - `full_name` (Type: `FullNameOptional`)
    - `tax_identification_number` (Type: `TaxIdentificationNumber`)
- **HireDate**: Hiring date (ISO 8601). Type: string.
- **WorkStatus**: `working`, `not_working`, `fired`.
- **FireDate**: Date of dismissal (ISO 8601). Type: string.
- **Comment**: Notes. Type: string.
- **FeedBack**: Notes (available to park employees). Type: string.
- **ProfileOptional**:
    - `comment` (Type: `Comment`)
    - `feedback` (Type: `FeedBack`)
    - `fire_date` (Type: `FireDate`)
    - `hire_date` (Type: `HireDate`)
    - `work_status` (Type: `WorkStatus`)
- **CarId**: Vehicle ID. Type: string.
- **Platform**: Are orders from the platform available. Type: boolean.
- **Partner**: Are orders from a partner available. Type: boolean.
- **OrderProvider**:
    - `partner` (Type: `Partner`)
    - `platform` (Type: `Platform`)

---

#### 8. Get List of Driver Profiles

Returns a list of driver (courier) profiles associated with a given partner.

**Endpoint:** `POST https://fleet-api.yango.tech/v1/parks/driver-profiles/list`

**Request Body:**
```json
{
  "query": {
    "park": {
      "id": "ee6f33c4562b4e1f8646d157bd70b2c4",
      "driver_profile": {
        "id": ["2111ade6gk054dfdb9iu8c8cc9460mks"],
        "work_rule_id": ["bc43tre6ba054dfdb7143ckfgvcby63e"],
        "work_status": ["working"]
      },
      "current_status": {
        "status": ["free"]
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
    "account": ["balance"],
    "car": ["color"],
    "current_status": ["status"],
    "driver_profile": ["last_name"],
    "park": ["name"],
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
```

**Request Data Definitions (api5.md):**

- **ContractorProfileId**: Driver's profile ID. Type: string.
- **WorkStatus**: `working`, `not_working`, `fired`.
- **DriverProfilesListRequestQueryParkDriverProfile**:
    - `id` (Type: `ContractorProfileId[]`)
    - `work_rule_id` (Type: `WorkRuleId[]`)
    - `work_status` (Type: `WorkStatus[]`)
- **DriverStatus**: `offline`, `busy`, `free`, `in_order_free`, `in_order_busy`.
- **DriverProfilesListRequestQueryParkCurrentStatus**:
    - `status` (Type: `DriverStatus[]`)
- **DriverProfilesListRequestQueryParkAccountLastTransactionDate**:
    - `from` (Type: `string<date-time>`)
    - `to` (Type: `string<date-time>`)
- **DriverProfilesListRequestQueryParkAccount**:
    - `last_transaction_date` (Type: `DriverProfilesListRequestQueryParkAccountLastTransactionDate`)
- **DriverProfilesListRequestQueryParkUpdatedAt**:
    - `from` (Type: `string<date-time>`)
    - `to` (Type: `string<date-time>`)
- **DriverProfilesListRequestQueryPark**:
    - `id` (Type: `ParkId`)
    - `account` (Type: `DriverProfilesListRequestQueryParkAccount`)
    - `current_status` (Type: `DriverProfilesListRequestQueryParkCurrentStatus`)
    - `driver_profile` (Type: `DriverProfilesListRequestQueryParkDriverProfile`)
    - `updated_at` (Type: `DriverProfilesListRequestQueryParkUpdatedAt`)
- **DriverProfilesListRequestQuery**:
    - `park` (Type: `DriverProfilesListRequestQueryPark`)
    - `text` (Type: `string`)
- **VehicleField**: `id`, `status`, `amenities`, `category`, `callsign`, `brand`, `model`, `year`, `color`, `number`, `registration_cert`, `vin`.
- **VehicleFields**: Type: `VehicleField[]`.
- **DriverProfileListRequestFields**:
    - `account` (Type: `string[]`): `id`, `type`, `balance`, `balance_limit`, `currency`, `last_transaction_date`.
    - `car` (Type: `VehicleFields`)
    - `current_status` (Type: `string[]`): `status`, `status_updated_at`.
    - `driver_profile` (Type: `string[]`): `id`, `park_id`, `created_date`, `first_name`, `last_name`, `middle_name`, `driver_license`, `phones`, `work_rule_id`, `work_status`, `check_message`, `comment`, `employment_type`, `has_contract_issue`.
    - `park` (Type: `string[]`): `id`, `city`, `name`.
    - `updated_at` (Type: `boolean`)
- **DriverProfileRequestSortOrderField**:
    - `direction` (Type: `string`): `asc`, `desc`.
    - `field` (Type: `string`): `account.current.balance`, `driver_profile.created_date`, `driver_profile.last_name`, `driver_profile.first_name`, `driver_profile.middle_name`, `updated_at`.
- **DriverProfileRequestSortOrder**: Type: `DriverProfileRequestSortOrderField[]`.

**Response Data Definitions (api5.md):**

- **AccountId**: Account ID. Type: string.
- **AccountType**: `current`.
- **AccountBalance**: Fixed-point sum string.
- **Currency**: ISO 4217 code.
- **DriverProfileAccount**:
    - `balance`, `balance_limit`, `currency`, `id`, `type`.
- **VehicleId**: Vehicle ID. Type: string.
- **Status (Vehicle)**: `unknown`, `working`, `not_working`, `repairing`, `no_driver`, `pending`.
- **Amenities**: `conditioner`, `no_smoking`, `child_chair`, `animal_transport`, `universal`, `wifi`, `check`, `card`, `yamoney`, `newspaper`, `coupon`, `creditcard`, `dont_call`, `smoking`, `delivery`, `vip_event`, `woman_driver`, `post_terminal`, `bicycle`, `skiing`, `passenger_plus`, `cargo_clean`, `door_to_door`, `sticker`, `lightbox`.
- **Categories**: `econom`, `comfort`, `comfort_plus`, `business`, `minivan`, `vip`, `wagon`, `pool`, `start`, `standart`, `ultimate`, `maybach`, `promo`, `premium_van`, `premium_suv`, `suv`, `personal_driver`, `express`, `cargo`.
- **ColorEnum**: `Белый`, `Желтый`, `Бежевый`, `Черный`, `Голубой`, `Серый`, `Красный`, `Оранжевый`, `Синий`, `Зеленый`, `Коричневый`, `Фиолетовый`, `Розовый`.
- **LicencePlateNumber**: License plate number string.
- **RegistrationCertificate**: Certificate string.
- **VIN**: VIN string.
- **Vehicle**:
    - `id`, `amenities`, `brand`, `callsign`, `category`, `color`, `model`, `number`, `registration_cert`, `status`, `vin`, `year`.
- **DriverProfileCurrentStatus**:
    - `status`, `status_updated_at`.
- **NormalizedNumber**: Cyrillic-to-Latin replaced license number.
- **DriverLicense**:
    - `country`, `normalized_number`, `number`, `birth_date`, `expiration_date`, `issue_date`.
- **DriverProfileModel**:
    - `check_message`, `comment`, `created_date`, `driver_license`, `employment_type`, `first_name`, `has_contract_issue`, `id`, `last_name`, `middle_name`, `park_id`, `phones`, `work_rule_id`, `work_status`.
- **DriverProfile**:
    - `accounts`, `car`, `current_status`, `driver_profile`.
- **DriverProfilePark**:
    - `city`, `id`, `name`.

---

### Supply Hours API

#### 9. Get Driver's Online Time

Retrieves the amount of time a driver was online during a specified period.

**Endpoint:** `GET https://fleet-api.yango.tech/v2/parks/contractors/supply-hours`

**Query Parameters:**
- `contractor_profile_id` (string): Driver's profile ID.
- `period_from` (string): Start date (ISO 8601). **Must be URL-encoded**.
- `period_to` (string): End date (ISO 8601). **Must be URL-encoded**.

**Note on Encoding:** URL-encoding is required for special characters: colon `:` becomes `%3A`, plus sign `+` becomes `%2B`.
Example: `2019-08-08T11:58:01+03:00` → `2019-08-08T11%3A58%3A01%2B03%3A00`

**Response (200 OK):**
```json
{
  "supply_duration_seconds": 3600,
  "total_seconds": 3600
}
```

---

## Error Handling

### HTTP Status Codes

- **200 OK**: Success.
- **400 Bad Request**: Invalid parameters.
- **401 Unauthorized**: Request authorization parameters are missing.
- **403 Forbidden**: Insufficient rights.
- **404 Not Found**: Resource not found.
- **429 Too Many Requests**: Limit exceeded.
- **500 Internal Server Error**: Server error.

---

## Code Examples

### Python: Get Driver Online Time
```python
import requests
from urllib.parse import quote

def get_supply_hours(api_key, client_id, park_id, driver_id, start_iso, end_iso):
    url = f"https://fleet-api.yango.tech/v2/parks/contractors/supply-hours"
    headers = {"X-API-Key": api_key, "X-Client-ID": client_id, "X-Park-ID": park_id}
    params = {
        "contractor_profile_id": driver_id,
        "period_from": start_iso,
        "period_to": end_iso
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()
```

---

## Best Practices

1. **Pagination**: Use `cursor` for transactions and `limit`/`offset` for profile lists.
2. **Idempotency**: Use `X-Idempotency-Token` for POST/PUT.
3. **URL Encoding**: Ensure date-time query params are correctly encoded.

---

## FAQ & Troubleshooting

- **Q: Why am I getting 403?**  
  A: Check your API key permissions and ensuring `X-Park-ID` is correct.
- **Q: Maximum limit for profiles?**  
  A: The limit is 1000 items per request.
