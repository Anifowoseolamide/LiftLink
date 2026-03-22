# Frontend Query Filters Guide for Rides

This document explains how the frontend should call the `GET /api/rides/` endpoint to match the UI filters seen on the "Find a Ride" page.

## The Base Endpoint ("All Rides" Mode)

If the user clicks **"All Rides"** (or clears all filters), you simply call the endpoint without any extra query parameters:

```http
GET /api/rides/
```

- **Behavior:** This automatically returns *all* rides in the database that have a status of `PENDING` and a departure time *in the future*. Expired rides are automatically omitted by the backend.

---

## Filtering Using Query Parameters

You can apply filters individually or stack them together by appending query parameters.

### 1. Verified Driver (`is_verified_driver`)
If the user clicks the "Verified Driver" pill, pass `is_verified_driver=true`. The backend will filter for rides where the driver's `driver_verification_status` is `"ACTIVE"`.
```http
GET /api/rides/?is_verified_driver=true
```

### 2. Instant Book (`instant_book`)
If the user clicks the "Instant Book" pill:
```http
GET /api/rides/?instant_book=true
```

### 3. Price Filter (`max_price`)
When the user uses a price slider or enters a maximum budget per seat:
```http
GET /api/rides/?max_price=3500.00
```

### 4. Search Bar Filters (Origin & Destination text)
When the user types location strings into the "Leaving from" or "Going to" inputs:
```http
GET /api/rides/?origin=Yaba&destination=VI
```

### 5. Date Filter (`date`)
If the user picks a departure date from a calendar:
```http
GET /api/rides/?date=2024-03-25
```

---

## Stacking Filters (The Real World Use Case)

The frontend can safely stack any combination of these parameters! 

For example, if a user searches for rides from "Yaba" to "VI" today, requires a Verified Driver, and needs an Instant Book option that costs less than 2000 NGN:

```http
GET /api/rides/?origin=Yaba&destination=VI&date=2024-03-25&is_verified_driver=true&instant_book=true&max_price=2000
```

The Django backend safely handles validation for all params natively. Make sure to fetch `GET /api/rides/` with these query parameters encoded in the URL.
