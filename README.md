# 🚗 Liftlink (RideShare Lagos)

**Liftlink** (also known as *RideShare Lagos*) is a robust backend system designed for a peer-to-peer ridesharing platform. It facilitates ride sharing, real-time tracking, secure payments, and instant messaging between drivers and riders.

---

## ✨ Core Features

- **🚗 Ride Management**: Drivers can publish rides with specific routes, dates, and available seats. Riders can search for available rides based on origin, destination, and date.
- **📅 Booking System**: Seamless booking flow for riders to request seats and drivers to manage those requests (Accept/Reject/Complete).
- **💰 Wallet & Payments**: Integrated wallet system using **Paystack** for secure deposits, withdrawals, and automated transaction logging.
- **💬 Real-time Messaging**: Instant chat functionality between users using **Django Channels** and WebSockets.
- **📍 Live Tracking**: Real-time driver location updates and tracking for active rides.
- **🔔 Notifications**: Automated system notifications for booking status updates, messages, and wallet activity.
- **🔐 Secure Authentication**: JWT-based authentication (SimpleJWT) with support for RIDER and DRIVER roles.

---

## 🛠️ Technology Stack

- **Framework**: [Django 5.x](https://www.djangoproject.com/)
- **API**: [Django REST Framework](https://www.django-rest-framework.org/)
- **Real-time**: [Django Channels](https://channels.readthedocs.io/) (WebSockets)
- **Authentication**: JWT (SimpleJWT)
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Payments**: [Paystack API](https://paystack.com/)
- **Task Queue**: Channels Layer (InMemory for dev, Redis recommended for prod)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Redis (Optional for local dev, required for production WebSockets)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Liftlink
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Database Setup

1.  **Run migrations**:
    ```bash
    python manage.py migrate
    ```

2.  **Create a superuser**:
    ```bash
    python manage.py createsuperuser
    ```

### Running the Application

1.  **Start the development server**:
    ```bash
    python manage.py runserver
    ```

2.  The API will be available at `http://127.0.0.1:8000/`.

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory and add the following:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
PAYSTACK_SECRET_KEY=your-paystack-secret-key
```

---

## 📚 API Reference

A detailed API reference is available in [api_reference.md.resolved](file:///c:/Users/USER/pythonProject/Liftlink/api_reference.md.resolved).

### Key Endpoints Summary:
- `/api/auth/`: Registration, Login, Profile.
- `/api/rides/`: Search and Publish rides.
- `/api/bookings/`: Manage seat requests.
- `/api/wallet/`: Deposits, Withdrawals, History.
- `/api/messages/`: Conversation history.

---

## ⚡ WebSockets

- **Chat**: `ws://<host>/ws/chat/<room_name>/`
- **Tracking**: `ws://<host>/ws/tracking/<ride_id>/`

---

## 📜 License

This project is licensed under the MIT License.
