# Frontend Documentation: BVN Verification

This document outlines the implementation of the BVN verification endpoint and how the frontend should interact with it.

### Endpoint Details
- **Method**: `POST`
- **URL**: `/api/auth/verify-bvn/`
- **Headers**: `Authorization: Bearer <JWT_ACCESS_TOKEN>`

### Request Payload
```json
{
  "bvn": "22354678934"
}
```

### Response Scenarios

#### 1. Success (Test BVN & Driver Role)
- **Status**: `200 OK`
- **Body**:
```json
{
  "detail": "BVN verified successfully. Your driver account is now active."
}
```
*Effect: The user's `driver_verification_status` is updated to `"ACTIVE"`.*

#### 2. Failure (Invalid BVN)
- **Status**: `400 Bad Request`
- **Body**:
```json
{
  "detail": "Invalid BVN. Please check and try again."
}
```

#### 3. Failure (Rider Role)
- **Status**: `400 Bad Request`
- **Body**:
```json
{
  "detail": "BVN verified, but only driver accounts can be activated via this method."
}
```

### Frontend Implementation Tips
- Add a text input for the BVN in the "Verification Status" page for the "BVN / ID License" card if the status is `"PENDING"`.
- When the user submits the BVN, call the `/api/auth/verify-bvn/` endpoint.
- Upon success, refresh the user's profile or update the local state to change the status to `"ACTIVE"`.
- This will enable the "Publish Ride" feature, which requires an `"ACTIVE"` status.
