# Backend API Format (Local Server + Base64 Output)

This API format is optimized for **local development**, with all image outputs returned as **base64 strings** instead of CDN URLs.

---

# ✅ Global API Rules

* Base URL: `/api/v1/`
* All endpoints use **POST**
* No CDN, no cloud storage
* All images returned as base64 PNG strings
* Response format: JSON
* Authentication disabled for local (can be added later)

---

# **1. AI Image Generator**

### **Endpoint**

`POST /api/v1/image/generate`

### **Request**

```json
{
  "prompt": "a futuristic city with neon lights",
  "style": "cinematic",
  "aspect_ratio": "9:16",
  "num_images": 2
}
```

### **Response**

```json
{
  "status": "success",
  "images": [
    "data:image/png;base64, <BASE64_STRING>",
    "data:image/png;base64, <BASE64_STRING>"
  ]
}
```

---

# **2. AI Logo Generator**

### **Endpoint**

`POST /api/v1/logo/generate`

### **Request**

```json
{
  "business_name": "SkyTech",
  "slogan": "Innovate Tomorrow",
  "style": "minimal",
  "color_palette": "blue-gradient",
  "logo_type": "icon_text",
  "num_images": 4
}
```

### **Response**

```json
{
  "status": "success",
  "logos": [
    "data:image/png;base64,<BASE64>",
    "data:image/png;base64,<BASE64>"
  ]
}
```

---

# **3. Avatar Generator**

### **Endpoint**

`POST /api/v1/avatar/generate`

### **Request**

```json
{
  "image_base64": "data:image/png;base64,<USER_IMAGE>",
  "style": "anime",
  "num_images": 3
}
```

### **Response**

```json
{
  "status": "success",
  "avatars": ["data:image/png;base64,<BASE64>"]
}
```

---

# **4. Background Remover**

### **Endpoint**

`POST /api/v1/background/remove`

### **Request**

```json
{
  "image_base64": "data:image/png;base64,<USER_IMAGE>"
}
```

### **Response**

```json
{
  "status": "success",
  "output": "data:image/png;base64,<BASE64>"
}
```

---

# **5. Product Image Generator**

### **Endpoint**

`POST /api/v1/product/generate`

### **Request**

```json
{
  "product_image_base64": "data:image/png;base64,<PRODUCT>",
  "scene_prompt": "studio white background",
  "style": "minimal",
  "num_images": 3
}
```

### **Response**

```json
{
  "status": "success",
  "images": ["data:image/png;base64,<BASE64>"]
}
```

---

# **6. AI Upscaler**

### **Endpoint**

`POST /api/v1/upscale`

### **Request**

```json
{
  "image_base64": "data:image/png;base64,<LOW_RES>",
  "scale": 4
}
```

### **Response**

```json
{
  "status": "success",
  "output": "data:image/png;base64,<HD_IMAGE>"
}
```

---

# **7. Magic Eraser**

### **Endpoint**

`POST /api/v1/magic-eraser`

### **Request**

```json
{
  "image_base64": "data:image/png;base64,<ORIGINAL>",
  "mask_base64": "data:image/png;base64,<MASK>"
}
```

### **Response**

```json
{
  "status": "success",
  "output": "data:image/png;base64,<CLEANED_IMAGE>"
}
```

---

# **8. AI Template Generator**

### **Endpoint**

`POST /api/v1/template/generate`

### **Request**

```json
{
  "category": "poster",
  "title": "Grand Opening",
  "style": "modern",
  "aspect_ratio": "4:5",
  "num_images": 2
}
```

### **Response**

```json
{
  "status": "success",
  "templates": ["data:image/png;base64,<BASE64>"]
}
```

---

# **9. Mascot / Character Creator**

### **Endpoint**

`POST /api/v1/character/generate`

### **Request**

```json
{
  "prompt": "cute 3D tiger mascot",
  "color_theme": "orange",
  "num_images": 2
}
```

### **Response**

```json
{
  "status": "success",
  "characters": ["data:image/png;base64,<BASE64>"]
}
```

---

# **10. UI Mockup Generator**

### **Endpoint**

`POST /api/v1/ui-mockup/generate`

### **Request**

```json
{
  "prompt": "finance app login screen",
  "style": "material",
  "platform": "mobile",
  "num_images": 1
}
```

### **Response**

```json
{
  "status": "success",
  "mockups": ["data:image/png;base64,<BASE64>"]
}
```

---

# ✅ Optional: Async Tasks for Local

`GET /api/v1/jobs/{id}`

```json
{
  "status": "completed",
  "output": ["data:image/png;base64,<BASE64>"]
}
```

---

Want me to generate **FastAPI live code** for all these endpoints with base64 output?
