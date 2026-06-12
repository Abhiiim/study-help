# Study Saver Extension

Chrome extension for saving study links to the Study Saver API.

## Prerequisites

- Google Chrome or another Chromium browser
- Running Study Saver server at `http://localhost:8000`
- Optional: running client dashboard at `http://localhost:5173`

## Run

1. Open `chrome://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select the `apps/extension` folder.
5. Pin the Study Saver extension and open the popup.

## Configuration

The extension currently points to:

```js
API_BASE_URL = "http://localhost:8000/api/v1";
DASHBOARD_URL = "http://localhost:5173";
```

To change these values, edit `shared/api.js`, then reload the extension from `chrome://extensions`.
