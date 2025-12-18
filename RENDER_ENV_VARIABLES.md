# Render Environment Variables

Copy these environment variables to your Render dashboard.

## Required Environment Variables

### MongoDB Configuration

**MONGODB_URI**
```
mongodb+srv://n4221891_db_user:noman5858@cluster0.jnwiaoi.mongodb.net
```
- **Mark as Secret**: ✅ Yes
- **Description**: MongoDB Atlas connection string

**MONGODB_DB**
```
upwork_proposal_bot
```
- **Mark as Secret**: ❌ No
- **Description**: Database name

### n8n Integration

**N8N_SHARED_SECRET**
```
9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
```
- **Mark as Secret**: ✅ Yes
- **Description**: Secret key for n8n webhook authentication

### OpenAI (Optional - for AI features)

**OPENAI_API_KEY**
```
sk-your-openai-api-key-here
```
- **Mark as Secret**: ✅ Yes
- **Description**: OpenAI API key for AI job ranking and proposal generation
- **Note**: Only needed if using AI features

### Logging

**LOG_LEVEL**
```
INFO
```
- **Mark as Secret**: ❌ No
- **Description**: Logging level (DEBUG, INFO, WARNING, ERROR)

## How to Add in Render

1. Go to your Render service dashboard
2. Click on "Environment" tab
3. Click "Add Environment Variable"
4. For each variable:
   - Enter the **Name** (e.g., `MONGODB_URI`)
   - Enter the **Value** (copy from above)
   - Check "Secret" checkbox for sensitive values
   - Click "Save Changes"

## Complete List (Copy-Paste Ready)

```
MONGODB_URI=mongodb+srv://n4221891_db_user:noman5858@cluster0.jnwiaoi.mongodb.net
MONGODB_DB=upwork_proposal_bot
N8N_SHARED_SECRET=9b9cd907b0d795fef45708c7882138819751729c0ca6f30ac8393f100b2aa394
LOG_LEVEL=INFO
```

**Optional:**
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

## Security Notes

⚠️ **Important**: 
- Mark `MONGODB_URI`, `N8N_SHARED_SECRET`, and `OPENAI_API_KEY` as **Secret** in Render
- Never commit these values to Git
- Rotate secrets periodically

## Verification

After setting environment variables:
1. Restart your Render service
2. Check logs for "MongoDB connected successfully"
3. Test health endpoint: `https://your-service.onrender.com/health`
4. Should return: `{"status": "ok", "database": "connected"}`

