# Web App Guide

## Start the App

```bash
cd web
npm install
npm run dev
```

The app runs in development mode with hot reload.

## Backend Integration

The draft comparison page posts to:

- `http://127.0.0.1:8000/compare`

Ensure your backend API is running at that address or adjust the endpoint in `web/src/app/page.tsx`.

## UX Goals

- Fast draft iteration
- Clear stat cards
- Immediate win-condition visibility
- Side-by-side team comparison
