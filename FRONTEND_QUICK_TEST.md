# 🎨 Frontend Testing - Quick Start

**Your Setup:** Next.js 15 with TypeScript

---

## ✅ Step-by-Step Testing

### Step 1: Check Node.js ✅

You already have Node.js installed! Version check complete.

### Step 2: Install Dependencies

```bash
cd frontend
npm install
```

**Note:** Your `node_modules` already exists, so dependencies may be installed. Run this to ensure everything is up-to-date.

### Step 3: Start Development Server

```bash
npm run dev
```

**Expected:** Server starts at http://localhost:3000

### Step 4: Test in Browser

1. Open: **http://localhost:3000**
2. The application should load
3. Check browser console (F12) for errors

---

## 🧪 What Your Frontend Has

Based on `package.json`:

**Framework:** Next.js 15.1.6  
**Language:** TypeScript  
**Styling:** Tailwind CSS  

**Available Commands:**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint  
```

---

## 🚀 Quick Test Now

**Run these commands:**

```bash
# Navigate to frontend
cd "C:\Users\sujal\Documents\Projects\Cheeating Detector\frontend"

# Start the dev server
npm run dev
```

**Then:**
1. Open browser to http://localhost:3000
2. You should see your application!

---

## 🔍 Testing Checklist

Once running, verify:

- [ ] Homepage loads without errors
- [ ] No console errors (check F12 → Console)
- [ ] Styling looks correct
- [ ] Navigation works
- [ ] Can interact with UI elements

---

## 🛠️ Common npm Commands

```bash
# Development
npm run dev           # Hot-reload development

# Linting
npm run lint          # Check code quality

# Production
npm run build         # Create optimized build
npm start             # Run production build

# Dependencies
npm install           # Install packages
npm update            # Update packages
```

---

## 📊 Testing with Backend

For full system test:

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Then test:** Full application at http://localhost:3000

---

## 🎯 Next Steps

1. ✅ Read: [FRONTEND_TESTING.md](file:///c:/Users/sujal/Documents/Projects/Cheeating%20Detector/FRONTEND_TESTING.md) for detailed guide
2. 🚀 Run: `npm run dev` to start testing
3. 🌐 Open: http://localhost:3000
4. ✅ Verify: Everything works!

---

**Ready? Just run:** `cd frontend && npm run dev` 🎉
