# 🚗 Liftlink (RideShare Lagos)

**Liftlink** is a robust, production-ready backend system for a peer-to-peer ridesharing platform. It acts as the digital mediator for drivers offering open seats and riders looking to carpool, ensuring trust through a wallet-based atomic escrow system, driver verification, and dynamic penalty logic.

---

## ✨ System Architecture & Core Logics

### 1. The Wallet & Escrow Payment Flow
To build a system where strangers can trust each other, all payments flow through an atomic Escrow system rather than sitting in limbo. 

**How it works:**
- **Top Up**: Riders deposit funds via Paystack (`POST /wallet/deposit/`), which instantly gets credited to their internal `Wallet.balance`.
- **Booking**: When a rider books a seat (`POST /bookings/create/`), the system wraps the request in a database lock (`transaction.atomic()`). It validates the rider has enough balance, dynamically takes seats from the ride to prevent overbooking, deducts the money from the wallet, and generates an `EscrowRecord` holding the funds. 
- **Refunds**: If the driver rejects the booking, the escrow reverses entirely without ever touching external Paystack APIs.

### 2. Ride Lifecycle endpoints
The state machine of a ride prevents edge cases and ensures fair payouts:
- **`PENDING`**: The ride is published by the driver and visible to all users querying `GET /api/rides/`.
- **`ACTIVE`**: The ride has begun. Drivers call `POST /rides/<id>/start/`.
- **`COMPLETED`**: The driver calls `POST /rides/<id>/complete/`. This is the final state. **Reaching this state triggers the Escrow release**, officially sweeping all locked funds for `ACCEPTED` bookings straight into the driver's available Wallet balance.

### 3. Automated Cancellation Penalties
The backend uses a dynamic penalty mechanism to protect driver earnings:
- Drivers can `REJECT` a booking or riders can `CANCEL` a pending request, resulting in a **100% Refund** from escrow.
- However, if a Rider decides to `CANCEL` an already `ACCEPTED` booking within **2 hours** of the ride departure time (`departure_time`), a late penalty is triggered. 
- The ride's open seats are restored, but **50% of the rider's escrow is penalized and given to the driver's wallet**, while the remaining 50% is returned to the rider.

### 4. Trust Mechanisms: KYC & Ratings
- **Verification**: Admin can change `driver_verification_status` to `"ACTIVE"` to allow offering rides.
- **Driver Ratings**: After a ride concludes (`COMPLETED`), riders use `POST /auth/reviews/` to leave 1-5 star ratings with an optional comment. The backend recalculates the driver's lifetime average rating instantly and stores it on their public profile.

---

## 🛠️ Technology Stack

- **Framework**: Django 5.x + Django REST Framework
- **Concurrency**: PostgreSQL + Django Select For Update (Locks rows against double-booking race conditions).
- **Authentication**: JWT (SimpleJWT)
- **Payments**: Paystack API integration via Webhooks.
- **WebSockets**: Django Channels for Live Location Tracking and Real-Time Chatting.

---

## 🚀 Getting Started

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Liftlink
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate    # Windows
    source venv/bin/activate  # macOS/Linux
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Database Setup
1.  **Run migrations** to generate the User, Booking, Ride, Wallet, Escrow, and Review tables:
    ```bash
    python manage.py migrate
    ```

2.  **Start the server**:
    ```bash
    python manage.py runserver
    ```

---

## 📚 API Reference
For a complete list of endpoints, payloads, HTTP methods, and missing frontend components required, refer to the [api_reference.md](file:///c:/Users/USER/pythonProject/Liftlink/api_reference.md) document in this directory.
