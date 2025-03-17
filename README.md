# MindRoot Computer Use Plugin

This plugin enables AI agents to control a virtual desktop environment via Docker. It provides a set of commands for controlling the virtual machine and a web interface for viewing and interacting with the desktop.

## Features

- Containerized Linux desktop environment
- Visual interaction with desktop through screenshots
- Commands for mouse/keyboard control
- Web viewer with VNC support
- Pre-built Docker image support

## Prerequisites

- Docker installed and running
- MindRoot server

## Installation

```bash
pip install -e /path/to/mr_computer_use
```

Or if installed as a package:

```bash
pip install mr_computer_use
```

## Configuration

By default, the plugin will use the pre-built Docker image `mindroot/computer-use:latest`. You can customize settings by creating a configuration file at `~/.mindroot/computer_use_config.json`:

```json
{
  "docker_image": "mindroot/computer-use:latest",
  "container_name": "mindroot_computer_use",
  "ports": {
    "8080/tcp": 8080,
    "5900/tcp": 5900,
    "6080/tcp": 6080
  },
  "build_if_not_found": true,
  "repo_url": "https://github.com/bytebot-ai/bytebot.git"
}
```

## Commands for AI Agents

### Check Docker

```json
{ "computer_check_docker": {} }
```
Checks if Docker is installed and running.

### Start VM

```json
{ "computer_start": {} }
```
Starts the virtual desktop container and returns a screenshot.

### Stop VM

```json
{ "computer_stop": {} }
```
Stops the running VM container.

### Take Screenshot

```json
{ "computer_screenshot": {} }
```
Captures and returns a screenshot of the current VM state.

### Click

```json
{ "computer_click": {"x": 100, "y": 200} }
```
Clicks at the specified coordinates (x, y) in the VM.

### Type Text

```json
{ "computer_type": {"text": "Hello, world!"} }
```
Types the specified text in the VM.

### Press Key

```json
{ "computer_press_key": {"key": "enter"} }
```
Presses the specified key (e.g., "enter", "tab", "escape").

### Navigate to URL

```json
{ "computer_navigate": {"url": "https://www.example.com"} }
```
Navigates to the specified URL in the browser.

### Scroll

```json
{ "computer_scroll": {"amount": 300} }
```

Scrolls the page vertically (default) or horizontally. Positive values scroll down/right, negative values scroll up/left.

Parameters:
- `amount`: Integer. The amount to scroll in pixels
- `axis`: String. Optional. 'v' for vertical (default), 'h' for horizontal

### Move Mouse

```json
{ "computer_mouse_move": {"x": 100, "y": 200} }
```

Moves the mouse cursor to the specified coordinates without clicking.

### Right Click

```json
{ "computer_right_click": {} }
```

Performs a right-click at the current cursor position. Use `computer_mouse_move` first to position the cursor.

### Double Click

```json
{ "computer_double_click": {} }
```

Performs a double-click at the current cursor position. Use `computer_mouse_move` first to position the cursor.

### Drag

```json
{ "computer_drag": {"start_x": 100, "start_y": 200, "end_x": 300, "end_y": 400} }
```

Performs a drag operation from the start coordinates to the end coordinates.

### Get Cursor Position

```json
{ "computer_get_cursor_position": {} }
```

Returns the current cursor position as `{"x": number, "y": number}`.

## Web Interface

The plugin adds a collapsible section to the chat interface for viewing and interacting with the VM. It also provides a standalone page at `/computer_use`.

## Usage Example

Here's an example workflow for an AI agent:

1. Check if Docker is running
2. Start the VM
3. Open a browser
4. Navigate to a website
5. Fill out a form
6. Click a button
7. Take a screenshot of the result

## Architecture

The plugin consists of:

- Docker container management (via docker-py)
- Bytebot API client for VM control
- Web component for UI interactions
- Command system integration for AI agents

## Troubleshooting

- **VM not starting**: Check Docker is running and has sufficient permissions
- **Cannot connect to VM**: Verify ports are not in use by other applications
- **Screenshot fails**: Ensure the VM has fully initialized (wait a few seconds)

## Development

To contribute to this plugin:

1. Clone the repository
2. Install in development mode: `pip install -e .`
3. Make your changes
4. Test thoroughly before submitting

## Credits

This plugin is based on the [bytebot-ai/bytebot](https://github.com/bytebot-ai/bytebot) project, which provides the containerized desktop environment.
