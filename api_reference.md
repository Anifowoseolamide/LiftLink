# RideShare Lagos – API Reference

All REST endpoints are prefixed with `/api/`.

## 🔐 Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register/` | Register as RIDER or DRIVER. |
| `POST` | `/auth/login/` | Get JWT `access` and `refresh` tokens. |
| `POST` | `/auth/logout/` | Blacklist refresh token to logout. |
| `GET \| PATCH` | `/auth/profile/` | Get/Update current user's details. |
| `POST` | `/auth/token/refresh/` | Get new access token using refresh token. |
| `POST` | `/auth/reviews/` | Rate a driver after a completed ride (1-5 stars). |

### Register Payload (`POST /auth/register/`)
```json
{
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+2348012345678",
  "role": "RIDER",
  "password": "securepassword123",
  "password2": "securepassword123"
}
```

### Login Response (`POST /auth/login/`)
```json
{
  "access": "JWT_ACCESS_TOKEN",
  "refresh": "JWT_REFRESH_TOKEN",
  "user": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "+2348012345678",
    "role": "DRIVER",
    "driver_verification_status": "ACTIVE",
    "rating": "5.00",
    "avatar_url": ""
  }
}
```

### Logout Payload (`POST /auth/logout/`)
```json
{
  "refresh": "<refresh_token>"
}
```

### Create Review Payload (`POST /api/auth/reviews/`)
```json
{
  "ride": 1,
  "rating": 5,
  "comment": "Great driver, very punctual! Highly recommended."
}
```

---

## 🚗 Rides
| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| `GET` | `/rides/` | `origin`, `destination`, `date`, `seats` | Search pending rides (excludes expired). |
| `POST` | `/rides/` | - | Driver publishes a ride (Requires `driver_verification_status`="ACTIVE"). |
| `GET` | `/rides/<id>/` | - | Get specific ride details. |
| `POST` | `/rides/<id>/start/` | - | Driver changes status to ACTIVE. |
| `POST` | `/rides/<id>/complete/` | - | Driver changes status to COMPLETED (releases escrow). |

### Create Ride Payload (`POST /api/rides/`)
```json
{
  "origin_name": "Lekki Phase 1",
  "destination_name": "Ikeja City Mall",
  "origin_coords": "6.448,3.473",
  "destination_coords": "6.619,3.358",
  "departure_time": "2024-03-25T08:00:00Z",
  "total_seats": 3,
  "price_per_seat": 2500.00,
  "vehicle_details": "Toyota Corolla (Blue) - ABC-123-XY"
}
```

---

## 📅 Bookings
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/bookings/` | List current user's bookings (Rider/Driver view). |
| `POST` | `/bookings/create/` | Rider books seats (deducts wallet into escrow). |
| `PATCH` | `/bookings/<id>/status/` | Update booking. Riders can cancel. Drivers can accept/reject. |

### Create Booking Payload (`POST /api/bookings/create/`)
```json
{
  "ride_id": 1,
  "seats_booked": 2
}
```

### Update Status Payload (`PATCH /api/bookings/<id>/status/`)
```json
{
  "status": "CANCELLED"
}
```
*Valid statuses: `ACCEPTED`, `REJECTED`, `CANCELLED`, `COMPLETED`*
*Note on Cancellations: If a rider cancels an `ACCEPTED` booking < 2 hours before departure time, 50% of the escrow is partially refunded to the rider, and 50% is released to the driver as a penalty compensation.*

---
**Frontend Mapping: New Buttons Needed**
- **Rider Dashboard:** "Cancel Booking" button on all pending and accepted bookings.
- **Driver Profile / Publishing:** "Verify Driver Account" workflow. The frontend should hide or disable "Publish Ride" until `user.driver_verification_status == "ACTIVE"`.
- **Admin Panel:** Needs a button to review driver credentials and manually toggle `driver_verification_status` to `"ACTIVE"`.

---

## 💰 Wallet & Paystack
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/wallet/history/` | Transaction ledger. |
| `POST` | `/wallet/deposit/` | Init Paystack payment. |
| `POST` | `/wallet/withdraw/` | Submit withdrawal request. |

### Deposit Payload (`POST /api/wallet/deposit/`)
```json
{
  "amount": 5000.00,
  "email": "user@example.com"
}
```

### Withdraw Payload (`POST /api/wallet/withdraw/`)
```json
{
  "amount": 2000.00,
  "bank_code": "058",
  "account_number": "0123456789",
  "account_name": "John Doe"
}
```

---

## 💬 Messaging & Notifications
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/messages/<user_id>/` | Fetch conversation history. |
| `GET` | `/notifications/` | List current user's notifications. |
| `PATCH` | `/notifications/<id>/read/` | Mark a notification as read. |

---

## ⚡ WebSockets (Django Channels)

### 1. Real-time Chat
**URL**: `ws://<host>/ws/chat/<room_name>/`
- **Event**: `send_message`
  ```json
  {"event": "send_message", "content": "Hello!", "receiver_id": 2}
  ```

### 2. Live Tracking
**URL**: `ws://<host>/ws/tracking/<ride_id>/`
- **Driver Send**:
  ```json
  {"event": "location_update", "lat": 6.52, "lng": 3.37}
  ```
