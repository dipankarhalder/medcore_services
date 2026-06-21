# MedCore API Gateway Endpoints Reference

All service endpoints are proxied through the NGINX API Gateway on port `8000`.

- **Admin Authentication / Management Service**: Routed via `/api/v1/auth/` $\rightarrow$ `admin_auth:8000`
- **Patient Authentication Service**: Routed via `/api/v1/patients/` $\rightarrow$ `patient_auth:8000`
- **User Profile Service**: Routed via `/api/v1/profiles/` $\rightarrow$ `profiles:8000`

---

## 1. Admin Authentication Service

### 1.1 Register User
- **Route**: `POST /api/v1/auth/register/`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>` *(Optional/Required)*: Only required for non-bootstrap registrations. The very first user registering does not require authentication and is automatically set as `super_admin`.
- **Request Payload**:
  ```json
  {
    "username": "adminuser",
    "email": "adminuser@example.com",
    "password": "SecurePassword123",
    "phone_number": "1234567890",
    "role": "admin"
  }
  ```
  *(Roles can be: `super_admin`, `admin`, `account_manager`, `accountent`, `department_manager`, `receptionist`, `stuff`, `Doctor`, `staff`)*
- **Response (201 Created - Bootstrap / Self Logged In)**:
  ```json
  {
    "token": "1:56b3a85c-a087-4504-8811-1e3f7bb1abf2:1wbFL2:qCEw5ft...",
    "user": {
      "id": 1,
      "username": "superadmin",
      "email": "superadmin@example.com",
      "role": "super_admin"
    }
  }
  ```
- **Response (201 Created - Regular creation by Admin/Super Admin)**:
  ```json
  {
    "message": "User registered successfully.",
    "user": {
      "id": 2,
      "username": "adminuser",
      "email": "adminuser@example.com",
      "role": "admin"
    }
  }
  ```
- **Response Errors**:
  - `400 Bad Request`: `{"error": "Username is already taken."}` or `{"error": "Email is already registered."}`
  - `403 Forbidden`: `{"error": "Admins cannot create Super Admin users."}` or `{"error": "Permission denied. Only Super Admins or Admins can register new users."}`

### 1.2 Login User
- **Route**: `POST /api/v1/auth/login/`
- **Headers**:
  - `Content-Type: application/json`
- **Request Payload**:
  ```json
  {
    "username": "adminuser", // OR "email": "adminuser@example.com"
    "password": "SecurePassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "token": "2:c2c5ecaf-3688-41c0-aa4d-010643dbebe5:1wbFNM:hrluNJ...",
    "user": {
      "id": 2,
      "username": "adminuser",
      "email": "adminuser@example.com",
      "role": "admin"
    }
  }
  ```
- **Response Errors**:
  - `400 Bad Request`: `{"error": "Device session limit exceeded. Maximum 4 active devices allowed."}` (Enforced for `super_admin` and `admin` roles) or `{"error": "Invalid credentials."}`
  - `403 Forbidden`: `{"error": "Account is disabled."}`

### 1.3 Logout Session
- **Route**: `POST /api/v1/auth/logout/`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "message": "Logged out successfully."
  }
  ```

### 1.4 List Active Sessions
- **Route**: `GET /api/v1/auth/sessions/`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "sessions": [
      {
        "session_key": "56b3a85c-a087-4504-8811-1e3f7bb1abf2",
        "device_name": "curl/8.7.1",
        "ip_address": "172.19.0.10",
        "created_at": "2026-06-21T10:23:40.739Z",
        "last_activity": "2026-06-21T10:23:40.739Z"
      }
    ]
  }
  ```

### 1.5 Logout Specific Device Session
- **Route**: `POST /api/v1/auth/sessions/logout-device/`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>`
- **Request Payload**:
  ```json
  {
    "session_key": "56b3a85c-a087-4504-8811-1e3f7bb1abf2"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Device logged out."
  }
  ```

### 1.6 Logout All Device Sessions
- **Route**: `POST /api/v1/auth/sessions/logout-all/`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "message": "All devices logged out."
  }
  ```

### 1.7 Forgot Password (Stub)
- **Route**: `POST /api/v1/auth/forgot-password/`
- **Response (200 OK)**:
  ```json
  {
    "message": "Reset link dispatched (Stub)."
  }
  ```

### 1.8 Service Health Check
- **Route**: `GET /api/v1/auth/health/`
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "service": "admin_auth"
  }
  ```

---

## 2. Patient Authentication Service

### 2.1 Register Patient
- **Route**: `POST /api/v1/patients/register/`
- **Headers**:
  - `Content-Type: application/json`
- **Request Payload**:
  ```json
  {
    "username": "patient1",
    "email": "patient1@example.com",
    "password": "PatientPassword123",
    "phone_number": "+1999999999"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "token": "patient:1:1wbFNM:hrluNJh_...",
    "patient": {
      "id": 1,
      "username": "patient1",
      "email": "patient1@example.com"
    }
  }
  ```
- **Response Errors**:
  - `400 Bad Request`: `{"error": "Username is already taken."}` or `{"error": "Email is already registered."}`

### 2.2 Login Patient
- **Route**: `POST /api/v1/patients/login/`
- **Headers**:
  - `Content-Type: application/json`
- **Request Payload**:
  ```json
  {
    "email": "patient1@example.com",
    "password": "PatientPassword123"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "token": "patient:1:1wbFNM:hrluNJh_...",
    "patient": {
      "id": 1,
      "username": "patient1",
      "email": "patient1@example.com"
    }
  }
  ```
- **Response Errors**:
  - `400 Bad Request`: `{"error": "Invalid credentials."}`

### 2.3 Service Health Check
- **Route**: `GET /api/v1/patients/health/`
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "service": "patient_auth"
  }
  ```

---

## 3. Profiles Service

### 3.1 Get User Profile
- **Route**: `GET /api/v1/profiles/profile/`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "profile": {
      "user_id": 1,
      "first_name": "Super",
      "last_name": "Admin",
      "bio": "System Administrator",
      "photo": "/media/profiles/photo.jpg" // OR null
    }
  }
  ```

### 3.2 Update User Profile
- **Route**: `POST /api/v1/profiles/profile/update/`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>`
- **Request Payload**:
  ```json
  {
    "first_name": "Super",
    "last_name": "Admin",
    "bio": "Updated bio text here"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Profile updated successfully.",
    "profile": {
      "user_id": 1,
      "first_name": "Super",
      "last_name": "Admin",
      "bio": "Updated bio text here"
    }
  }
  ```

### 3.3 Upload Profile Photo
- **Route**: `POST /api/v1/profiles/profile/upload-photo/`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Request Payload**:
  - Form-data multipart parameter: `photo` (File binary)
- **Response (200 OK)**:
  ```json
  {
    "message": "Profile photo uploaded.",
    "photo_url": "/media/profile_photos/image.jpg"
  }
  ```

### 3.4 Send Verification OTP
Generates a random 6-digit OTP code, stores it in the shared Redis cache (expires in 5 minutes), and dispatches an event via Kafka to the Notification Service.
- **Route**: `POST /api/v1/profiles/otp/send/`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>`
- **Request Payload**:
  ```json
  {
    "channel": "email", // OR "sms"
    "target": "superadmin@example.com"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "Verification code generated and sent."
  }
  ```

### 3.5 Verify Verification OTP
Checks the provided code against the cached OTP inside Redis.
- **Route**: `POST /api/v1/profiles/otp/verify/`
- **Headers**:
  - `Content-Type: application/json`
  - `Authorization: Bearer <token>`
- **Request Payload**:
  ```json
  {
    "otp_code": "123456"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "message": "OTP verified successfully."
  }
  ```
- **Response Errors**:
  - `400 Bad Request`: `{"error": "OTP expired or not requested."}` or `{"error": "Invalid OTP code."}`

### 3.6 Service Health Check
- **Route**: `GET /api/v1/profiles/health/`
- **Response (200 OK)**:
  ```json
  {
    "status": "healthy",
    "service": "profiles"
  }
  ```
