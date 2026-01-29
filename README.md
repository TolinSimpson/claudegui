# Claude CLI GUI

A graphical user interface for configuring and launching [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) sessions on Windows.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Full CLI Coverage**: Configure all Claude CLI options through an intuitive tabbed interface
- **Live Command Preview**: See the generated command in real-time as you make changes
- **One-Click Launch**: Launch Claude CLI directly in a new console window
- **Copy to Clipboard**: Copy the configured command for use elsewhere
- **Configurable Paths**: Set custom Claude CLI executable path and working directory
- **No Dependencies**: Uses only Python standard library (Tkinter)

## Screenshots

The GUI is organized into tabs for easy navigation:

- **Core**: Model selection, prompts, and session controls
- **Agent**: Custom agent configuration
- **Tools**: Tool permissions and restrictions
- **Prompts**: System prompt customization
- **Input/Output**: Print mode and format settings
- **MCP & Plugins**: MCP server configuration and plugins
- **Advanced**: Permissions, debug options, and more

## Requirements

- Python 3.x (with Tkinter - included by default on Windows)
- [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) installed

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/claude-cli-gui.git
   cd claude-cli-gui
   ```

2. Ensure Claude CLI is installed. You can install it via npm:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

3. Run the GUI:
   ```bash
   python claude_gui.py
   ```

## Usage

1. **Set Claude CLI Path**: The GUI will auto-detect the Claude CLI path. If not found, use the "Browse..." button or "Auto-detect" to locate it manually.

2. **Set Working Directory**: Choose the directory where Claude CLI should run.

3. **Configure Options**: Use the tabs to configure your desired options:
   - Select a model (defaults to "opus")
   - Set session options (continue, resume, etc.)
   - Configure tools, prompts, and permissions
   - Set up MCP servers and plugins

4. **Preview & Launch**: 
   - The command preview at the bottom updates in real-time
   - Click "Copy Command" to copy to clipboard
   - Click "Launch" to start Claude CLI in a new window

## Configuration Options

### Core Tab
| Option | CLI Flag | Description |
|--------|----------|-------------|
| Prompt | (positional) | Initial prompt to send |
| Model | `--model` | Model to use (sonnet, opus, or full name) |
| Fallback Model | `--fallback-model` | Fallback when default is overloaded |
| Continue | `-c` | Continue most recent conversation |
| Resume | `-r` | Resume by session ID |
| Fork Session | `--fork-session` | Create new session when resuming |
| Session ID | `--session-id` | Use specific session UUID |

### Agent Tab
| Option | CLI Flag | Description |
|--------|----------|-------------|
| Agent | `--agent` | Agent for current session |
| Agents JSON | `--agents` | Custom agents definition |

### Tools Tab
| Option | CLI Flag | Description |
|--------|----------|-------------|
| Tools | `--tools` | Available tools list |
| Allowed Tools | `--allowedTools` | Tools to allow |
| Disallowed Tools | `--disallowedTools` | Tools to deny |
| Disable Slash Commands | `--disable-slash-commands` | Disable skills |

### Prompts Tab
| Option | CLI Flag | Description |
|--------|----------|-------------|
| System Prompt | `--system-prompt` | Custom system prompt |
| Append System Prompt | `--append-system-prompt` | Append to default prompt |

### Input/Output Tab
| Option | CLI Flag | Description |
|--------|----------|-------------|
| Print Mode | `-p` | Non-interactive output mode |
| Input Format | `--input-format` | Input format (text, stream-json) |
| Output Format | `--output-format` | Output format (text, json, stream-json) |
| JSON Schema | `--json-schema` | Structured output validation |

### MCP & Plugins Tab
| Option | CLI Flag | Description |
|--------|----------|-------------|
| MCP Config | `--mcp-config` | MCP server configuration file |
| Strict MCP | `--strict-mcp-config` | Only use specified MCP servers |
| Plugin Directories | `--plugin-dir` | Plugin directories to load |

### Advanced Tab
| Option | CLI Flag | Description |
|--------|----------|-------------|
| Permission Mode | `--permission-mode` | Permission mode for session |
| Skip Permissions | `--dangerously-skip-permissions` | Bypass permission checks |
| Additional Dirs | `--add-dir` | Additional directories to allow |
| Max Budget | `--max-budget-usd` | Maximum API spend limit |
| Debug | `--debug` | Enable debug mode with filter |
| Verbose | `--verbose` | Verbose output |

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) for Claude and Claude CLI
- Built with Python and Tkinter
