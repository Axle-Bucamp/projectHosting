---
sidebar_position: 1
---

# API Overview

The ProjectHosting API provides comprehensive access to all platform features through RESTful endpoints. All API responses are in JSON format and follow consistent patterns for error handling and data structure.

## Base URL

```
https://api.projecthosting.dev/api
```

For local development:
```
http://localhost:8000/api
```

## Authentication

Most API endpoints require authentication using JWT (JSON Web Tokens). Include the token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Getting a Token

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "your-username",
    "email": "user@example.com",
    "role": "admin"
  }
}
```

## Response Format

All API responses follow this structure:

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation failed |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248600
```

## Pagination

List endpoints support pagination using query parameters:

```http
GET /api/projects?page=1&limit=20&sort=created_at&order=desc
```

Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `sort`: Sort field (default: id)
- `order`: Sort order - `asc` or `desc` (default: asc)

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Search

Many endpoints support filtering and search:

```http
GET /api/projects?status=online&search=react&category=web
```

Common filter parameters:
- `search`: Full-text search across relevant fields
- `status`: Filter by status
- `category`: Filter by category
- `created_after`: Filter by creation date
- `updated_after`: Filter by update date

## API Endpoints

### Core Resources

| Endpoint | Description |
|----------|-------------|
| [Projects](./projects.md) | Manage project listings |
| [Store](./store.md) | Manage store items and products |
| [Contacts](./contacts.md) | Handle contact form submissions |
| [Users](./users.md) | User management and authentication |
| [Images](./images.md) | Image upload and management |

### Admin Resources

| Endpoint | Description |
|----------|-------------|
| [System](./admin/system.md) | System monitoring and control |
| [Logs](./admin/logs.md) | Application logs and debugging |
| [Settings](./admin/settings.md) | Application configuration |
| [Metrics](./admin/metrics.md) | Performance metrics and analytics |

### Utility Endpoints

| Endpoint | Description |
|----------|-------------|
| [Health](./health.md) | Service health checks |
| [Metrics](./metrics.md) | Prometheus metrics |
| [Upload](./upload.md) | File upload services |

## SDKs and Libraries

Official SDKs are available for popular programming languages:

### JavaScript/Node.js
```bash
npm install @projecthosting/api-client
```

```javascript
import { ProjectHostingAPI } from '@projecthosting/api-client';

const api = new ProjectHostingAPI({
  baseURL: 'https://api.projecthosting.dev',
  token: 'your-jwt-token'
});

const projects = await api.projects.list();
```

### Python
```bash
pip install projecthosting-api
```

```python
from projecthosting import ProjectHostingAPI

api = ProjectHostingAPI(
    base_url='https://api.projecthosting.dev',
    token='your-jwt-token'
)

projects = api.projects.list()
```

### cURL Examples

Get all projects:
```bash
curl -H "Authorization: Bearer <token>" \
     https://api.projecthosting.dev/api/projects
```

Create a new project:
```bash
curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"name":"My Project","status":"online"}' \
     https://api.projecthosting.dev/api/projects
```

## Webhooks

ProjectHosting supports webhooks for real-time notifications:

```http
POST /api/webhooks
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://your-app.com/webhook",
  "events": ["project.created", "project.updated", "project.deleted"],
  "secret": "your-webhook-secret"
}
```

Webhook payload example:
```json
{
  "event": "project.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "project": {
      "id": 123,
      "name": "New Project",
      "status": "online"
    }
  }
}
```

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "name",
        "message": "Name is required"
      },
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

Common error codes:
- `VALIDATION_ERROR`: Input validation failed
- `AUTHENTICATION_ERROR`: Invalid or missing authentication
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Testing

Use our interactive API explorer to test endpoints:

- **Swagger UI**: https://api.projecthosting.dev/docs
- **Postman Collection**: [Download](./postman-collection.json)

## Support

For API support:
- **Documentation**: This documentation site
- **GitHub Issues**: Report bugs and request features
- **Discord**: Real-time community support
- **Email**: api-support@projecthosting.dev

