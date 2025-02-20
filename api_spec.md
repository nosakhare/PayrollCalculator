
# Salary Calculation System API Specification

## Base URL
`/api/v1`

## Authentication
Bearer token authentication required for all endpoints.

## Endpoints

### 1. Calculate Salary
Calculate salary details for a single employee.

**Endpoint:** `/calculate`
**Method:** POST
**Request Body:**
```json
{
  "account_number": "string",
  "staff_id": "string",
  "email": "string",
  "name": "string",
  "department": "string",
  "job_title": "string",
  "annual_gross_pay": "number",
  "start_date": "string (YYYY-MM-DD)",
  "end_date": "string (YYYY-MM-DD)",
  "contract_type": "string (Full Time|Contract)",
  "reimbursements": "number",
  "other_deductions": "number",
  "voluntary_pension": "number"
}
```

**Response:** `200 OK`
```json
{
  "monthly_gross": "number",
  "prorated_monthly_gross": "number",
  "components": {
    "basic": "number",
    "transport": "number",
    "housing": "number",
    "utility": "number",
    "meal": "number",
    "clothing": "number"
  },
  "pension": {
    "employee": "number",
    "employer": "number",
    "voluntary": "number"
  },
  "tax": {
    "cra": "number",
    "taxable_pay": "number",
    "paye": "number"
  },
  "deductions": {
    "total": "number",
    "other": "number"
  },
  "reimbursements": "number",
  "net_pay": "number"
}
```

### 2. Bulk Calculate
Calculate salary details for multiple employees.

**Endpoint:** `/calculate/bulk`
**Method:** POST
**Request Body:**
```json
{
  "employees": [
    {
      // Same structure as single calculate endpoint
    }
  ],
  "components": {
    "basic": "number",
    "transport": "number",
    "housing": "number",
    "utility": "number",
    "meal": "number",
    "clothing": "number"
  }
}
```

**Response:** `200 OK`
```json
{
  "results": [
    {
      // Same structure as single calculate response
    }
  ]
}
```

## Error Responses

**400 Bad Request**
```json
{
  "error": "string",
  "details": "string"
}
```

**401 Unauthorized**
```json
{
  "error": "Authentication required"
}
```

**422 Validation Error**
```json
{
  "error": "Validation failed",
  "details": {
    "field": "error message"
  }
}
```

## Rate Limiting
- 100 requests per minute per API key
- 1000 employees per bulk calculation request

## Notes
- All monetary values are in Nigerian Naira (NGN)
- Dates must be in ISO 8601 format (YYYY-MM-DD)
- Contract types must be either "Full Time" or "Contract"
- Voluntary pension cannot exceed 1/3 of monthly salary
