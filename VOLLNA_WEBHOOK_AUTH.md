# Vollna Webhook Authentication Setup

## Current Backend Authentication

Your backend endpoint `/vollna/jobs` expects:
- **Header**: `X-N8N-Secret`
- **Value**: Your secret key (from `N8N_SHARED_SECRET`)

## Vollna Authentication Options

### Option 1: Use "Bearer Token" (Recommended)

**Select**: "Bearer Token"

**Configuration**:
- **Token**: `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`

**Note**: Vollna will send this as `Authorization: Bearer <token>` header, but our backend expects `X-N8N-Secret` header. We need to update the backend to accept Bearer token OR use a proxy.

### Option 2: Use "None" (Less Secure)

**Select**: "None"

**Note**: This means no authentication. You'll need to either:
1. Update the backend to make authentication optional for Vollna
2. Or rely on the webhook URL being secret (not recommended)

### Option 3: Use "Basic Auth" (Not Recommended)

**Select**: "Basic Auth"

**Note**: This uses HTTP Basic Authentication, which is different from what our backend expects.

## Recommended Solution

Since Vollna sends `Authorization: Bearer <token>` but our backend expects `X-N8N-Secret`, we have two options:

### Solution A: Update Backend to Accept Bearer Token

Modify the endpoint to accept both:
- `Authorization: Bearer <token>` (from Vollna)
- `X-N8N-Secret: <token>` (from n8n)

### Solution B: Use "None" and Update Backend

1. Select "None" in Vollna
2. Update backend to make authentication optional for direct Vollna webhooks
3. Keep authentication required for n8n webhooks

## Quick Answer

**For now, select "None"** and we'll update the backend to handle it, OR select "Bearer Token" and we'll update the backend to accept Bearer tokens.

