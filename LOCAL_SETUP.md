# Local File Loading Setup

## Quick Start

To view the application with local file loading:

1. **Start the local server:**
   ```bash
   ./start-server.sh
   ```

   Or manually:
   ```bash
   python3 -m http.server 8000
   ```

2. **Open in browser:**
   Navigate to: http://localhost:8000

3. **Files will auto-load:**
   The application will automatically load all JSON files from `/data/critical_thinking/` when the page loads.

## Manual Loading

You can also click the "Load from Local Files" button to reload the data at any time.

## How It Works

- The local loader reads JSON files from `data/critical_thinking/`
- Files are served through the HTTP server (browsers cannot access local filesystem directly)
- All the same functionality as GitHub loading, but from your local directory
- Results are automatically displayed after loading

## Current Data Files

The following files will be loaded:
- a1_gen_chatgpt.json
- a1_gen_chatgpt_score_claude.json
- a1_gen_chatgpt_score_gemini.json
- a1_gen_chatgpt_score_grok.json
- a1_reflection_chatgpt.json
- a1_tune_chatgpt.json
- a1_tune_chatgpt_score_claude.json
- a1_tune_chatgpt_score_gemini.json
- a1_tune_chatgpt_score_grok.json

## Troubleshooting

**If loading shows "0 files":**
- Make sure you're accessing via http://localhost:8000 (not file://)
- Ensure the server is running
- Check browser console for errors (F12 → Console)

**If files aren't updating:**
- The browser may cache files; use Ctrl+Shift+R (hard refresh) to clear cache
- Or add new files to the `knownFiles` array in `src/js/local-loader.js`
