# Grapevine Desktop UI

A PyQt6-based desktop application for managing Grapevine LARP characters, players, and game data.

## Features

- **Character Management**: View, create, edit, and delete characters
- **Player Management**: Manage players with Player Points (PP) tracking
- **APR System**: Manage Actions, Plots, and Rumors
- **Real-time API Integration**: Connects to Grapevine REST API
- **Modern UI**: Clean, intuitive interface with responsive design

## Prerequisites

- Python 3.12+
- Grapevine API server running (default: http://localhost:8000)
- PyQt6 dependencies installed

## Installation

```bash
# From the grapevine-modern directory
pip install -r requirements.txt
```

## Running the Desktop App

1. **Start the API server first:**
   ```bash
   uvicorn src.api.main:app --reload
   ```

2. **Run the Desktop UI:**
   ```bash
   # On Windows
   python ui-desktop/main.py
   
   # On macOS/Linux
   python ui-desktop/main.py
   ```

## Application Structure

```
ui-desktop/
├── main.py              # Entry point
├── api_client.py        # REST API client
├── main_window.py       # Main application window
├── views/
│   ├── character_list.py    # Character list view
│   ├── character_detail.py  # Character edit/create view
│   ├── player_list.py       # Player management view
│   └── apr_view.py          # Actions/Plots/Rumors view
```

## Configuration

The API client connects to `http://localhost:8000` by default. To change this, edit `main.py`:

```python
api_client = APIClient(base_url="http://your-api-url:port")
```

## Screenshots

*Screenshots coming soon*

## Keyboard Shortcuts

- `Ctrl+N`: New Character (when in Characters view)
- `Ctrl+R`: Refresh current view
- `Esc`: Go back (when viewing character details)

## Development

### Adding a New View

1. Create a new file in `ui-desktop/views/`
2. Inherit from `QWidget`
3. Accept `APIClient` in constructor
4. Add to `main_window.py` navigation

### Styling Guidelines

- Use the provided stylesheets for consistency
- Follow the color scheme:
  - Primary Blue: `#3498db`
  - Success Green: `#27ae60`
  - Danger Red: `#e74c3c`
  - Dark Background: `#2c3e50`

## Troubleshooting

### "Could not connect to API" Error

1. Ensure the API server is running
2. Check that the base URL is correct
3. Verify there are no firewall issues blocking the connection

### UI Not Displaying Properly

1. Ensure PyQt6 is installed: `pip install PyQt6`
2. Try updating PyQt6: `pip install --upgrade PyQt6`
3. Check Python version (must be 3.12+)

## Future Enhancements

- [ ] Character sheet generation/printing
- [ ] Query builder UI
- [ ] Report generation
- [ ] Offline mode with local caching
- [ ] Multi-game support
- [ ] Import/Export dialogs for legacy files
