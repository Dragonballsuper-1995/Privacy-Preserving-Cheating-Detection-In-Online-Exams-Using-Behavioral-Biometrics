# Frontend Testing Guide - Cheating Detector

**Quick Start:** Get your frontend up and running in 5 minutes!

---

## 🎯 Two Types of Testing

### 1. **Manual Testing** (Visual/Interactive)
Run the development server and interact with the UI

### 2. **Automated Testing** (Unit/Integration)
Run automated tests with Jest/Testing Library

---

## 🚀 Quick Start - Manual Testing

### Step 1: Check Node.js Installation

```bash
# Check Node.js version (need 18+)
node --version

# Check npm version
npm --version
```

**Don't have Node.js?** Download from: https://nodejs.org/ (LTS version)

### Step 2: Navigate to Frontend

```bash
cd frontend
```

### Step 3: Install Dependencies

```bash
# Install all packages (first time only)
npm install
```

**Expected:** This will download all React/Next.js packages (~2-3 minutes)

### Step 4: Start Development Server

```bash
# Start the dev server
npm run dev
```

**Expected Output:**
```
> frontend@0.1.0 dev
> next dev

  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

 ✓ Ready in 2.5s
```

### Step 5: Open in Browser

1. Open your browser
2. Navigate to: **http://localhost:3000**
3. You should see the application!

---

## 🧪 Automated Testing (If Frontend Tests Exist)

### Check for Tests

```bash
cd frontend

# Check if tests exist
ls src/**/*.test.* 2>$null || ls __tests__/* 2>$null

# Or check package.json for test scripts
npm run test --if-present
```

### Run Tests (If Available)

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

---

## 🔍 Manual Testing Checklist

Once the frontend is running at http://localhost:3000, test these features:

### Core Functionality

- [ ] **Homepage loads** - No errors in browser console
- [ ] **Navigation works** - Can navigate between pages
- [ ] **Authentication** - Login/logout functionality
- [ ] **Session creation** - Can create exam sessions
- [ ] **Event logging** - Events are captured and sent
- [ ] **Dashboard** - Admin dashboard displays data
- [ ] **Real-time updates** - WebSocket updates work
- [ ] **Responsive design** - Works on different screen sizes

### Browser Console Check

1. Press **F12** to open Developer Tools
2. Click **Console** tab
3. Look for errors (red text)
4. **Expected:** No critical errors, maybe some warnings

### Network Tab Check

1. Open Developer Tools (F12)
2. Click **Network** tab
3. Interact with the app
4. **Expected:** API calls to http://localhost:8000/api/*

---

## 🛠️ Testing with Backend

For full functionality testing, run both frontend and backend:

### Terminal 1: Backend

```bash
cd backend
uvicorn app.main:app --reload
```

**Expected:** Backend running at http://localhost:8000

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

**Expected:** Frontend running at http://localhost:3000

### Now Test:

1. Open http://localhost:3000
2. Create a test session
3. Simulate exam taking behavior
4. Check admin dashboard
5. Verify data is flowing correctly

---

## 🐛 Common Issues & Solutions

### Issue 1: `npm install` Fails

**Error:** `EACCES` permission errors

**Solution:**
```bash
# Windows: Run as Administrator
# Or clear npm cache
npm cache clean --force
npm install
```

### Issue 2: Port 3000 Already in Use

**Error:** `Port 3000 is already in use`

**Solution:**
```bash
# Option 1: Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <pid> /F

# Option 2: Use different port
npm run dev -- -p 3001
```

### Issue 3: Module Not Found

**Error:** `Cannot find module 'react'`

**Solution:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Issue 4: API Connection Failed

**Error:** `Failed to fetch from http://localhost:8000`

**Solution:**
1. Make sure backend is running
2. Check CORS configuration
3. Verify API URL in frontend config

---

## 📱 Testing on Different Devices

### Desktop Testing

- ✅ Test on Chrome
- ✅ Test on Firefox
- ✅ Test on Edge/Safari

### Responsive Testing

```bash
# In browser DevTools (F12)
# Click "Toggle device toolbar" (Ctrl+Shift+M)
# Test different screen sizes:
# - Mobile: 375x667 (iPhone SE)
# - Tablet: 768x1024 (iPad)
# - Desktop: 1920x1080
```

### Mobile Testing

**Option 1: Same Network**
1. Find your computer's IP address
2. On mobile browser, navigate to: `http://<your-ip>:3000`

**Option 2: ngrok (Public URL)**
```bash
# Install ngrok: https://ngrok.com/
ngrok http 3000
# Use provided URL on any device
```

---

## 🎨 Visual Testing

### Check These Elements:

1. **Layout** - Proper alignment, no overlapping
2. **Colors** - Consistent theme, readable contrast
3. **Typography** - Clear, readable fonts
4. **Spacing** - Proper margins and padding
5. **Buttons** - Clear hover states, clickable
6. **Forms** - Proper validation, error messages
7. **Loading States** - Spinners/skeletons display
8. **Error States** - Error messages clear

---

## 🔄 Hot Reload Testing

The dev server supports hot reload:

1. Make a change to any component
2. Save the file
3. Browser should automatically refresh
4. See changes instantly

**Test it:**
```javascript
// Edit any component file
// Change some text
// Save
// Browser should update automatically
```

---

## 📊if Present Testing Workflow

### Daily Development

```bash
# 1. Start backend
cd backend && uvicorn app.main:app --reload

# 2. Start frontend (new terminal)
cd frontend && npm run dev

# 3. Make changes and test
# 4. Check browser console for errors
# 5. Test features manually
```

### Before Committing

```bash
# 1. Run linter
npm run lint

# 2. Run tests (if available)
npm test

# 3. Build for production
npm run build

# 4. Test production build
npm start
```

---

## 🏗️ Production Build Testing

Test the production build locally:

```bash
# Build for production
npm run build

# Start production server
npm start

# Test at: http://localhost:3000
```

**Check:**
- ✅ Build completes without errors
- ✅ Production site loads correctly
- ✅ All features work
- ✅ Performance is good (fast load times)

---

## 📈 Performance Testing

### Lighthouse Audit

1. Open site in Chrome
2. Open DevTools (F12)
3. Click "Lighthouse" tab
4. Click "Generate report"
5. Review scores for:
   - Performance
   - Accessibility
   - Best Practices
   - SEO

**Target Scores:** >80 in all categories

---

## 🎯 Testing Scenarios

### Scenario 1: Student Taking Exam

1. Navigate to exam page
2. Start session
3. Type answers
4. Copy/paste text (test detection)
5. Switch tabs (test focus detection)
6. Navigate questions
7. Submit exam

**Verify:** Events are logged, risk score updates

### Scenario 2: Instructor Dashboard

1. Login as instructor
2. View active sessions
3. Monitor real-time risk scores
4. View flagged sessions
5. Export reports

**Verify:** Data displays correctly, updates in real-time

### Scenario 3: Admin Analytics

1. Login as admin
2. View dashboard statistics
3. Check trend charts
4. Review system health
5. Export data

**Verify:** Charts render, data accurate

---

## 🔐 Security Testing (Manual)

### Test These:

- [ ] **Authentication** - Can't access protected routes without login
- [ ] **Authorization** - Students can't access admin features
- [ ] **CSRF** - Forms have protection
- [ ] **XSS** - Input is sanitized
- [ ] **SSL** - HTTPS in production

---

## 📝 Testing Checklist Summary

### Before Deployment

- [ ] All pages load without errors
- [ ] Authentication works
- [ ] API calls successful
- [ ] Real-time updates functional
- [ ] Dashboard displays correctly
- [ ] Forms validate properly
- [ ] Error messages clear
- [ ] Responsive on mobile/tablet
- [ ] Production build works
- [ ] Lighthouse score >80

---

## 🆘 Getting Help

**If frontend doesn't exist:**
```bash
# Check if frontend directory exists
ls frontend

# If not, you might be using a different setup
# Or need to create the frontend
```

**If something doesn't work:**
1. Check browser console (F12)
2. Check network tab for failed requests
3. Check terminal for errors
4. Review error messages
5. Ask for help with specific error message

---

## 🎓 Next Steps

1. **Start Simple:** Just get the dev server running
2. **Visual Test:** Click around, check for errors
3. **Feature Test:** Test core functionality
4. **Performance Test:** Run Lighthouse
5. **Production Test:** Build and test production version

---

## Quick Commands Reference

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Format code
npm run format
```

---

**Ready to test?** Start with: `cd frontend && npm run dev` 🚀
