# OllamaVision GUI

A modern, user-friendly desktop application for AI-powered image analysis and text enhancement using multiple backends including Ollama, OpenAI, OpenRouter, and TextGen through SwarmUI.

## ✨ Features

### 🖼️ Image Analysis
- **Single Image Analysis**: Upload and analyze individual images
- **Batch Processing**: Process entire folders of images automatically
- **Multiple Backends**: Support for Ollama, OpenAI, OpenRouter, and TextGen
- **Real-time Progress**: Visual progress tracking for batch operations
- **Custom Prompts**: Specify custom analysis prompts

### ✨ Text Enhancement
- **Dual Enhancement Types**: Qwen and Wan text enhancement modes
- **System Prompts**: Built-in system prompts for different enhancement styles
- **Custom Input**: Paste any text for enhancement
- **Multiple Backends**: Works with all supported backends

### ⚙️ Advanced Configuration
- **Global Model Settings**: Configure temperature, max tokens, top-p, top-k, and more
- **Persistent Settings**: All settings saved between sessions
- **Model Management**: Search, filter, and select from available models
- **API Key Management**: Secure storage of API keys for different backends

### 🎨 Modern Interface
- **Responsive Design**: Clean, modern UI that adapts to window resizing
- **Tabbed Interface**: Organized workflow with dedicated tabs
- **Real-time Updates**: Live status updates and progress tracking
- **Search & Filter**: Easy model discovery with search functionality

## 🚀 Quick Start

### Method 1: Automated Setup (Recommended)
1. **Download** the OllamaVision GUI folder
2. **Double-click** `setup_ollamavision.bat`
3. **Wait** for the setup to complete (creates virtual environment and installs dependencies)
4. **Find** "OllamaVision GUI" on your desktop
5. **Double-click** the desktop shortcut to launch

### Method 2: Manual Setup
1. **Open Command Prompt** in the OllamaVision GUI folder
2. **Create virtual environment**: `python -m venv venv`
3. **Activate virtual environment**: `venv\Scripts\activate`
4. **Install dependencies**: `pip install -r requirements.txt`
5. **Run the application**: `python ollamavision_gui.py`

### Method 3: Direct Launch
1. **Double-click** `launch_ollamavision.bat`
2. **Note**: Requires virtual environment to be set up first

## 📋 Requirements

### System Requirements
- **Windows 10/11** (tested on Windows 10)
- **Python 3.8+** (for virtual environment creation)
- **Internet Connection** (for API calls and package installation)

### Python Dependencies
- **Pillow** (≥9.0.0): Image processing
- **Requests** (≥2.28.0): HTTP API calls
- **Tkinter**: GUI framework (included with Python)

## 🔧 Installation Methods

### Automated Setup Script
The `setup_ollamavision.bat` script provides a complete automated setup:

```batch
# What it does:
1. Creates isolated virtual environment
2. Installs required Python packages
3. Validates all components
4. Creates desktop shortcut
5. Provides setup confirmation
```

### Virtual Environment
The application uses a self-contained virtual environment:
- **Location**: `OllamaVision GUI/venv/`
- **Isolation**: No impact on system Python
- **Portable**: Move the entire folder anywhere
- **Clean**: Delete folder to uninstall completely

## 🎯 Usage Guide

### 1. Connection Setup
1. **Open** the "Connection" tab
2. **Select** your preferred backend (Ollama, OpenAI, OpenRouter, TextGen)
3. **Enter** API keys if required
4. **Click** "Connect" to establish connection
5. **Select** a model from the available list

### 2. Single Image Analysis
1. **Go** to "Single Image" tab
2. **Click** "Select Image" to choose an image
3. **Modify** the prompt if needed
4. **Click** "Analyze Image" to start analysis
5. **View** results in the results area

### 3. Batch Processing
1. **Go** to "Batch Processing" tab
2. **Click** "Select Folder" to choose image folder
3. **Configure** caption style and trigger word
4. **Click** "Process Batch" to start processing
5. **Monitor** progress in the progress section

### 4. Text Enhancement
1. **Go** to "Text Enhancement" tab
2. **Select** enhancement type (Qwen or Wan)
3. **Enter** text to enhance
4. **Click** "Enhance Text" to process
5. **View** enhanced text in results area

### 5. Model Settings
1. **Go** to "Model Settings" tab
2. **Adjust** global parameters (temperature, max tokens, etc.)
3. **Settings** are automatically saved and applied globally

## 🔑 Backend Configuration

### Ollama
- **URL**: `http://localhost:11434` (default)
- **No API Key**: Required
- **Models**: Local Ollama models

### OpenAI
- **API Key**: Required (get from OpenAI)
- **Models**: GPT-4 Vision, GPT-4, etc.

### OpenRouter
- **API Key**: Required (get from OpenRouter)
- **Models**: Various vision-capable models

### TextGen
- **URL**: `http://localhost:5000` (default)
- **No API Key**: Required
- **Models**: Local TextGen models

## 📁 File Structure

```
OllamaVision GUI/
├── ollamavision_gui.py          # Main application
├── setup_ollamavision.bat       # Automated setup script
├── launch_ollamavision.bat      # Application launcher
├── create_desktop_shortcut.bat  # Shortcut creator
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── venv/                        # Virtual environment (created by setup)
    ├── Scripts/
    │   ├── python.exe           # Isolated Python
    │   └── pip.exe              # Package installer
    └── Lib/
        └── site-packages/       # Installed packages
```

## 🛠️ Troubleshooting

### Common Issues

#### "Virtual environment not found"
- **Solution**: Run `setup_ollamavision.bat` first

#### "Python not found"
- **Solution**: Install Python from https://www.python.org/downloads/
- **Note**: Make sure to check "Add Python to PATH" during installation

#### "Error creating desktop shortcut"
- **Solution**: Use `create_desktop_launcher.bat` instead (creates batch file launcher)

#### "No models available"
- **Solution**: Check backend connection and API keys

#### "API request failed"
- **Solution**: Verify SwarmUI is running and accessible

### Getting Help

1. **Check** the console output for error messages
2. **Verify** all requirements are met
3. **Ensure** SwarmUI is running and accessible
4. **Check** API keys are correct and valid

## 🔄 Updates

To update the application:
1. **Download** the latest version
2. **Replace** the application files
3. **Run** `setup_ollamavision.bat` to update dependencies
4. **Restart** the application

## 📝 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

---

**Note**: This application requires SwarmUI to be running for full functionality. Make sure SwarmUI is installed and running before using the application.
