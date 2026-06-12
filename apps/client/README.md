# Study Saver Client

React + Vite web dashboard for Study Saver.

## Prerequisites

- Node.js 18+
- npm
- Running Study Saver server at `http://localhost:8000`

## Setup

```bash
cd apps/client
npm install
cp .env.example .env
```

Update `.env` if your API URL is different:

```env
VITE_API_BASE_URL="http://localhost:8000/api/v1"
```

## Run

```bash
npm run dev
```

Open `http://localhost:5173`.

## Build

```bash
npm run build
npm run preview
```
