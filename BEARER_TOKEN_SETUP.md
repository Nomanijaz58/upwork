# ✅ Bearer Token Authentication Setup

## 🎯 What Changed

The backend now supports **Bearer Token authentication** for Vollna webhooks, in addition to the existing X-N8N-Secret header (for backward compatibility with n8n).

### ✅ Both Methods Supported

1. **Bearer Token** (Vollna uses this):
   ```
   Authorization: Bearer <your-token>
   ```

2. **X-N8N-Secret Header** (n8n uses this, backward compatible):
   ```
   X-N8N-Secret: <your-token>
   ```

---

## 🔧 Configuration

### Option 1: Use VOLLNA_BEARER_TOKEN (Recommended)

Add to `backend/.env`:
```bash
VOLLNA_BEARER_TOKEN=9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
```

### Option 2: Use N8N_SHARED_SECRET (Fallback)

If `VOLLNA_BEARER_TOKEN` is not set, the system will use `N8N_SHARED_SECRET` as fallback:
```bash
N8N_SHARED_SECRET=9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
```

**Note**: You can use the same token for both, or set them separately.

---

## 📋 Vollna Configuration

In your Vollna Dashboard/Extension:

1. Go to **Settings → Integrations → Webhooks**
2. Set **Webhook URL**: `https://upwork-xxsc.onrender.com/webhook/vollna`
3. Set **Method**: `POST`
4. Set **Authentication Type**: `Bearer Token`
5. Set **Bearer Token**: `9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394`

**Important**: Use the **same token** you set in `VOLLNA_BEARER_TOKEN` or `N8N_SHARED_SECRET` in your `.env` file.

---

## 🧪 Testing

### Test with Python Script
```bash
python3 test_bearer_token.py
```

### Test with curl
```bash
curl -X POST https://upwork-xxsc.onrender.com/webhook/vollna \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394" \
  -d '{
    "title": "Test Job",
    "url": "https://www.upwork.com/jobs/~test",
    "budget": 50.0,
    "client_name": "Test Client"
  }'
```

**Expected Response**:
```json
{
  "received": 1,
  "inserted": 1,
  "errors": 0,
  "error_details": null
}
```

---

## ✅ Verification Steps

1. **Update `.env` file** with `VOLLNA_BEARER_TOKEN` (or use existing `N8N_SHARED_SECRET`)
2. **Restart backend server** (Render will auto-deploy)
3. **Configure Vollna** with Bearer Token authentication
4. **Test webhook**: Run `python3 test_bearer_token.py`
5. **Check logs**: Look for `✅ Bearer token authentication successful` in Render logs

---

## 🔍 How It Works

### Authentication Flow

1. Vollna sends POST request with `Authorization: Bearer <token>` header
2. Backend checks `Authorization` header for Bearer token
3. If Bearer token matches `VOLLNA_BEARER_TOKEN` (or `N8N_SHARED_SECRET`), request is accepted
4. If no Bearer token, checks `X-N8N-Secret` header (for n8n compatibility)
5. If neither matches, returns `401 Unauthorized`

### Code Implementation

```python
def _check_auth(request: Request, ...):
    # Get expected token
    expected_token = settings.VOLLNA_BEARER_TOKEN or settings.N8N_SHARED_SECRET
    
    # Check Bearer token (from Vollna)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        bearer_token = auth_header.replace("Bearer ", "").strip()
        if bearer_token == expected_token:
            return  # ✅ Authenticated
    
    # Check X-N8N-Secret header (from n8n, backward compatible)
    if x_n8n_secret == expected_token:
        return  # ✅ Authenticated
    
    # ❌ No valid authentication
    raise HTTPException(status_code=401, detail="invalid token")
```

---

## 🚀 Next Steps

1. ✅ **Set `VOLLNA_BEARER_TOKEN` in `.env`** (or use `N8N_SHARED_SECRET`)
2. ✅ **Update Render environment variables** (if deploying)
3. ✅ **Configure Vollna** with Bearer Token
4. ✅ **Test webhook** with `python3 test_bearer_token.py`
5. ✅ **Monitor Render logs** for successful authentication

---

## 📝 Notes

- **Backward Compatible**: X-N8N-Secret header still works for n8n
- **Same Token**: You can use the same token for both Vollna and n8n
- **Security**: Always use strong, random tokens in production
- **Development**: If no token is configured, all requests are allowed (for development only)

---

## ✅ Status

- ✅ Bearer Token authentication implemented
- ✅ X-N8N-Secret header still supported (backward compatible)
- ✅ Test script created: `test_bearer_token.py`
- ✅ Documentation created: `BEARER_TOKEN_SETUP.md`

Once you configure Vollna with the Bearer Token, it will start sending real jobs! 🎉

