#!/usr/bin/env python3
"""
OllamaVision GUI Application
A desktop application for interacting with OllamaVision through SwarmUI API
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import base64
import json
import os
import threading
from pathlib import Path
import webbrowser
from PIL import Image, ImageTk
import io
import uuid
import time

class OllamaVisionAPI:
    """API client for SwarmUI OllamaVision extension"""
    
    def __init__(self, base_url="http://localhost:7801"):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Content-Type": "application/json"}
        self.session_id = None
    
    def get_swarmui_session(self):
        """Get a new session ID from SwarmUI"""
        try:
            url = f"{self.base_url}/API/GetNewSession"
            response = requests.post(url, headers=self.headers, json={}, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if "session_id" in data:
                self.session_id = data["session_id"]
                return {"success": True, "session_id": self.session_id, "data": data}
            else:
                return {"success": False, "message": "No session_id in response"}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Failed to get SwarmUI session: {str(e)}"}
    
    def get_session_id(self):
        """Get current session ID"""
        return self.session_id
    
    def reset_session(self):
        """Get a new session ID from SwarmUI"""
        result = self.get_swarmui_session()
        if result["success"]:
            return self.session_id
        else:
            raise Exception(f"Failed to get new session: {result['message']}")
    
    def make_request(self, endpoint, data):
        """Make a request to the OllamaVision API"""
        url = f"{self.base_url}/API/{endpoint}"
        
        # Add session ID to all API calls if available
        data_with_session = data.copy()
        if self.session_id:
            data_with_session["session_id"] = self.session_id  # SwarmUI expects "session_id" not "sessionId"
        
        try:
            response = requests.post(url, headers=self.headers, json=data_with_session, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def connect_ollama(self, ollama_url="http://localhost:11434", show_all=False):
        """Connect to Ollama and get available models"""
        return self.make_request("ConnectToOllamaAsync", {
            "ollamaUrl": ollama_url,
            "showAllModels": show_all
        })
    
    def connect_textgen(self, textgen_url="http://localhost:5000"):
        """Connect to TextGen WebUI"""
        return self.make_request("ConnectToTextGenAsync", {
            "textgenUrl": textgen_url
        })
    
    def analyze_image(self, image_data, model, backend_type="ollama", prompt="Describe this image in detail", 
                     temperature=0.8, max_tokens=500, ollama_url="http://localhost:11434", 
                     api_key=None, site_name="SwarmUI", system_prompt=None):
        """Analyze a single image"""
        data = {
            "model": model,
            "backendType": backend_type,
            "imageData": image_data,
            "prompt": prompt,
            "temperature": temperature,
            "maxTokens": max_tokens
        }
        
        # Add system prompt if provided
        if system_prompt:
            data["systemPrompt"] = system_prompt
        
        if backend_type == "ollama":
            data["ollamaUrl"] = ollama_url
        elif backend_type in ["openai", "openrouter"]:
            data["apiKey"] = api_key
            if backend_type == "openrouter":
                data["siteName"] = site_name
        
        return self.make_request("AnalyzeImageAsync", data)
    
    def batch_caption_images(self, folder_path, model, backend_type="ollama", 
                           caption_style="Danbooru Tags", trigger_word="", 
                           temperature=0.8, max_tokens=500, ollama_url="http://localhost:11434",
                           api_key=None, site_name="SwarmUI"):
        """Batch caption multiple images"""
        data = {
            "folderPath": folder_path,
            "model": model,
            "backendType": backend_type,
            "captionStyle": caption_style,
            "triggerWord": trigger_word,
            "temperature": temperature,
            "maxTokens": max_tokens
        }
        
        if backend_type == "ollama":
            data["ollamaUrl"] = ollama_url
        elif backend_type in ["openai", "openrouter"]:
            data["apiKey"] = api_key
            if backend_type == "openrouter":
                data["siteName"] = site_name
        
        return self.make_request("BatchCaptionImagesAsync", data)
    
    
    def enhance_text_prompt(self, model, backend_type="ollama", prompt="", 
                           temperature=0.8, max_tokens=500, ollama_url="http://localhost:11434",
                           api_key=None, site_name="SwarmUI", system_prompt=None):
        """Enhance a text prompt"""
        data = {
            "model": model,
            "backendType": backend_type,
            "prompt": prompt,
            "temperature": temperature,
            "maxTokens": max_tokens
        }
        
        if system_prompt:
            data["systemPrompt"] = system_prompt
        
        if backend_type == "ollama":
            data["ollamaUrl"] = ollama_url
        elif backend_type in ["openai", "openrouter"]:
            data["apiKey"] = api_key
            if backend_type == "openrouter":
                data["siteName"] = site_name
        
        return self.make_request("EnhanceTextPromptAsync", data)
    
    def get_openai_models(self, api_key):
        """Get available models from OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Return ALL available models from OpenAI (no filtering)
            all_models = []
            for model in data.get("data", []):
                model_id = model.get("id", "")
                if model_id:  # Only include models with valid IDs
                    all_models.append(model_id)
            
            return {"success": True, "models": all_models}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Failed to fetch OpenAI models: {str(e)}"}
    
    def get_openrouter_models(self, api_key):
        """Get available models from OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Return ALL available models from OpenRouter (no filtering)
            all_models = []
            for model in data.get("data", []):
                model_id = model.get("id", "")
                if model_id:  # Only include models with valid IDs
                    all_models.append(model_id)
            
            return {"success": True, "models": all_models}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Failed to fetch OpenRouter models: {str(e)}"}

class OllamaVisionGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("OllamaVision GUI")
        self.root.geometry("1000x900")
        self.root.resizable(True, False)  # Allow horizontal resize, disable vertical resize
        
        # Configure modern styling
        self.setup_styles()
        
        # API client
        self.api = OllamaVisionAPI()
        
        # Variables
        self.current_image = None
        self.current_image_data = None
        self.available_models = []
        self.batch_results = []
        
        # API key storage for different backends
        self.openai_api_key = ""
        self.openrouter_api_key = ""
        self.textgen_url = "http://localhost:5000"
        
        # Selected model storage
        self.selected_model = None
        
        # Connection state
        self.is_connected = False
        
        # Model filtering
        self.all_models = []  # Store all models for filtering
        self.filtered_models = []  # Store filtered models
        
        # Global model settings (persistent across all tabs)
        self.temperature_var = tk.DoubleVar(value=0.8)
        self.max_tokens_var = tk.IntVar(value=500)
        self.top_p_var = tk.DoubleVar(value=0.7)
        self.top_k_var = tk.IntVar(value=40)
        self.repeat_penalty_var = tk.DoubleVar(value=1.1)
        self.seed_var = tk.IntVar(value=-1)
        self.frequency_penalty_var = tk.DoubleVar(value=0.0)
        self.presence_penalty_var = tk.DoubleVar(value=0.0)
        self.min_p_var = tk.DoubleVar(value=0.0)
        self.top_a_var = tk.DoubleVar(value=0.0)
        
        # Application settings
        self.default_model_var = tk.StringVar()
        
        # Wan I2V Enhancement
        self.wan_i2v_var = tk.BooleanVar(value=False)
        
        # Create GUI
        self.create_widgets()
        self.load_settings()
        
        # Initialize session ID display
        self.update_session_id_display()
    
    def setup_styles(self):
        """Configure modern styling for the application"""
        # Configure ttk styles
        style = ttk.Style()
        
        # Set theme
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 10, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Arial', 9), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Arial', 9), foreground='#27ae60')
        style.configure('Warning.TLabel', font=('Arial', 9), foreground='#f39c12')
        style.configure('Error.TLabel', font=('Arial', 9), foreground='#e74c3c')
        
        # Button styles
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'), foreground='white')
        style.configure('Secondary.TButton', font=('Arial', 9))
        
        # Frame styles
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        style.configure('Header.TFrame', background='#ecf0f1')
        
        # Notebook styles
        style.configure('TNotebook', tabposition='n')
        
        # Configure tab states for different sizes
        style.map('TNotebook.Tab',
                 padding=[('selected', [20, 12]), ('!selected', [12, 8])],
                 font=[('selected', ('Arial', 11, 'bold')), ('!selected', ('Arial', 9, 'bold'))])
        
        # Entry styles
        style.configure('Modern.TEntry', font=('Arial', 10), relief='solid', borderwidth=1)
        
        # Combobox styles
        style.configure('Modern.TCombobox', font=('Arial', 10), relief='solid', borderwidth=1)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure root window for proper resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create tabs
        self.create_connection_tab()
        self.create_settings_tab()
        self.create_single_image_tab()
        self.create_batch_processing_tab()
        self.create_text_enhancement_tab()
    
    def create_connection_tab(self):
        """Create connection management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔌 Connection")
        
        # Configure frame to expand
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Main container with padding
        main_container = ttk.Frame(frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection settings
        conn_frame = ttk.LabelFrame(main_container, text="⚙️ Connection Settings", padding=12)
        conn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # SwarmUI URL
        ttk.Label(conn_frame, text="🌐 SwarmUI URL:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.swarmui_url_var = tk.StringVar(value="http://localhost:7801")
        url_entry = ttk.Entry(conn_frame, textvariable=self.swarmui_url_var, width=40, style='Modern.TEntry')
        url_entry.grid(row=0, column=1, sticky=tk.W, padx=(8, 0), pady=5)
        
        # Backend selection
        ttk.Label(conn_frame, text="🔧 Backend:", style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.backend_var = tk.StringVar(value="ollama")
        backend_combo = ttk.Combobox(conn_frame, textvariable=self.backend_var, 
                                   values=["ollama", "openai", "openrouter", "textgen"], 
                                    state="readonly", width=18, style='Modern.TCombobox')
        backend_combo.grid(row=1, column=1, sticky=tk.W, padx=(8, 0), pady=5)
        backend_combo.bind('<<ComboboxSelected>>', self.on_backend_change)
        
        # Initialize variables first
        self.ollama_url_var = tk.StringVar(value="http://localhost:11434")
        self.api_key_var = tk.StringVar()
        self.site_name_var = tk.StringVar(value="SwarmUI")
        
        # Ollama URL (only for Ollama backend)
        self.ollama_url_label = ttk.Label(conn_frame, text="Ollama URL:")
        self.ollama_url_entry = ttk.Entry(conn_frame, textvariable=self.ollama_url_var, width=40)
        
        # API Key (for OpenAI/OpenRouter)
        self.api_key_label = ttk.Label(conn_frame, text="API Key:")
        self.api_key_entry = ttk.Entry(conn_frame, textvariable=self.api_key_var, width=40, show="*")
        self.api_key_entry.bind('<KeyRelease>', self.on_api_key_change)
        
        # Initial layout
        self.update_connection_fields()
        
        # Session ID (hidden from user but functionality preserved)
        self.session_id_var = tk.StringVar()
        
        # Connect/Disconnect button (dynamic)
        self.connect_button = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection, 
                                        style='Primary.TButton', width=18)
        self.connect_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Models list
        models_frame = ttk.LabelFrame(main_container, text="🤖 Available Models", padding=12)
        models_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search section with modern styling
        search_section = ttk.LabelFrame(models_frame, text="🔍 Search Models", padding=10)
        search_section.pack(fill=tk.X, pady=(0, 10))
        
        # Search input with icon-like styling
        search_input_frame = ttk.Frame(search_section)
        search_input_frame.pack(fill=tk.X, pady=8)
        
        ttk.Label(search_input_frame, text="🔍", font=("Arial", 14)).pack(side=tk.LEFT, padx=(0, 8))
        self.model_search_var = tk.StringVar()
        self.model_search_var.trace('w', self.filter_models)
        search_entry = ttk.Entry(search_input_frame, textvariable=self.model_search_var, 
                               font=("Arial", 11), width=45, style='Modern.TEntry')
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        # Clear search button with modern styling
        clear_btn = ttk.Button(search_input_frame, text="✕ Clear", command=self.clear_model_search, 
                              width=12, style="Secondary.TButton")
        clear_btn.pack(side=tk.RIGHT)
        
        # Model count display
        self.model_count_var = tk.StringVar(value="No models loaded")
        count_label = ttk.Label(search_section, textvariable=self.model_count_var, 
                               style='Info.TLabel')
        count_label.pack(pady=(8, 0))
        
        # Models list with modern styling
        list_section = ttk.LabelFrame(models_frame, text="📋 Model List", padding=10)
        list_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox with modern styling
        listbox_frame = ttk.Frame(list_section)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        self.models_listbox = tk.Listbox(listbox_frame, height=12, font=("Consolas", 9),
                                       selectbackground="#0078d4", selectforeground="white",
                                       bg="#f8f9fa", fg="#212529", relief="flat",
                                       borderwidth=1, highlightthickness=1)
        self.models_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Scrollbar for models list
        models_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.models_listbox.yview)
        models_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.models_listbox.config(yscrollcommand=models_scrollbar.set)
        
        # Selection info section
        selection_section = ttk.LabelFrame(models_frame, text="✅ Selection", padding=10)
        selection_section.pack(fill=tk.X)
        
        # Model selection info with better styling
        self.model_info_var = tk.StringVar(value="No model selected")
        info_label = ttk.Label(selection_section, textvariable=self.model_info_var, 
                              style='Title.TLabel')
        info_label.pack(pady=8)
        
        # Action buttons section
        actions_section = ttk.Frame(selection_section)
        actions_section.pack(fill=tk.X, pady=8)
        
        # Set as default button with modern styling
        default_btn = ttk.Button(actions_section, text="⭐ Set as Default Model", 
                                command=self.set_as_default_model, width=22, style="Accent.TButton")
        default_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Default model display with better styling
        self.default_model_display_var = tk.StringVar(value="No default model set")
        default_label = ttk.Label(actions_section, textvariable=self.default_model_display_var, 
                                 style='Success.TLabel')
        default_label.pack(side=tk.LEFT)
        
        # Configure grid weights for responsive layout
        conn_frame.columnconfigure(1, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)  # Models frame should expand
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Bind selection
        self.models_listbox.bind('<<ListboxSelect>>', self.on_model_select)
    
    def create_settings_tab(self):
        """Create global model settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚙️ Model Settings")
        
        # Configure frame to expand
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Main settings frame
        main_frame = ttk.Frame(frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Core parameters section
        core_frame = ttk.LabelFrame(main_frame, text="🎯 Core Parameters", padding=12)
        core_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Temperature
        ttk.Label(core_frame, text="🌡️ Temperature (0.0 - 2.0):", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=6, pady=5)
        temp_scale = ttk.Scale(core_frame, from_=0.0, to=2.0, variable=self.temperature_var, orient=tk.HORIZONTAL)
        temp_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=6, pady=5)
        temp_entry = ttk.Entry(core_frame, textvariable=self.temperature_var, width=8, style='Modern.TEntry')
        temp_entry.grid(row=0, column=2, padx=6, pady=5)
        
        # Max Tokens
        ttk.Label(core_frame, text="🔢 Max Tokens (1 - 4096):", style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, padx=6, pady=5)
        max_tokens_scale = ttk.Scale(core_frame, from_=1, to=4096, variable=self.max_tokens_var, orient=tk.HORIZONTAL)
        max_tokens_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=6, pady=5)
        max_tokens_entry = ttk.Entry(core_frame, textvariable=self.max_tokens_var, width=8, style='Modern.TEntry')
        max_tokens_entry.grid(row=1, column=2, padx=6, pady=5)
        
        # Top P
        ttk.Label(core_frame, text="🎯 Top P (0.0 - 1.0):", style='Subtitle.TLabel').grid(row=2, column=0, sticky=tk.W, padx=6, pady=5)
        top_p_scale = ttk.Scale(core_frame, from_=0.0, to=1.0, variable=self.top_p_var, orient=tk.HORIZONTAL)
        top_p_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=6, pady=5)
        top_p_entry = ttk.Entry(core_frame, textvariable=self.top_p_var, width=8, style='Modern.TEntry')
        top_p_entry.grid(row=2, column=2, padx=6, pady=5)
        
        # Top K
        ttk.Label(core_frame, text="🔢 Top K (1 - 100):", style='Subtitle.TLabel').grid(row=3, column=0, sticky=tk.W, padx=6, pady=5)
        top_k_scale = ttk.Scale(core_frame, from_=1, to=100, variable=self.top_k_var, orient=tk.HORIZONTAL)
        top_k_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=6, pady=5)
        top_k_entry = ttk.Entry(core_frame, textvariable=self.top_k_var, width=8, style='Modern.TEntry')
        top_k_entry.grid(row=3, column=2, padx=6, pady=5)
        
        # Seed
        ttk.Label(core_frame, text="🎲 Seed (-1 for random):", style='Subtitle.TLabel').grid(row=4, column=0, sticky=tk.W, padx=6, pady=5)
        seed_scale = ttk.Scale(core_frame, from_=-1, to=1000, variable=self.seed_var, orient=tk.HORIZONTAL)
        seed_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=6, pady=5)
        seed_entry = ttk.Entry(core_frame, textvariable=self.seed_var, width=8, style='Modern.TEntry')
        seed_entry.grid(row=4, column=2, padx=6, pady=5)
        
        # Advanced parameters section
        advanced_frame = ttk.LabelFrame(main_frame, text="⚙️ Advanced Parameters", padding=12)
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Repeat Penalty
        ttk.Label(advanced_frame, text="🔄 Repeat Penalty (0.0 - 2.0):", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)
        repeat_penalty_scale = ttk.Scale(advanced_frame, from_=0.0, to=2.0, variable=self.repeat_penalty_var, orient=tk.HORIZONTAL)
        repeat_penalty_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=8, pady=8)
        repeat_penalty_entry = ttk.Entry(advanced_frame, textvariable=self.repeat_penalty_var, width=10, style='Modern.TEntry')
        repeat_penalty_entry.grid(row=0, column=2, padx=8, pady=8)
        
        # Frequency Penalty
        ttk.Label(advanced_frame, text="📊 Frequency Penalty (-2.0 - 2.0):", style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, padx=8, pady=8)
        freq_penalty_scale = ttk.Scale(advanced_frame, from_=-2.0, to=2.0, variable=self.frequency_penalty_var, orient=tk.HORIZONTAL)
        freq_penalty_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=8, pady=8)
        freq_penalty_entry = ttk.Entry(advanced_frame, textvariable=self.frequency_penalty_var, width=10, style='Modern.TEntry')
        freq_penalty_entry.grid(row=1, column=2, padx=8, pady=8)
        
        # Presence Penalty
        ttk.Label(advanced_frame, text="🎯 Presence Penalty (-2.0 - 2.0):", style='Subtitle.TLabel').grid(row=2, column=0, sticky=tk.W, padx=8, pady=8)
        pres_penalty_scale = ttk.Scale(advanced_frame, from_=-2.0, to=2.0, variable=self.presence_penalty_var, orient=tk.HORIZONTAL)
        pres_penalty_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=8, pady=8)
        pres_penalty_entry = ttk.Entry(advanced_frame, textvariable=self.presence_penalty_var, width=10, style='Modern.TEntry')
        pres_penalty_entry.grid(row=2, column=2, padx=8, pady=8)
        
        # Min P
        ttk.Label(advanced_frame, text="📉 Min P (0.0 - 1.0):", style='Subtitle.TLabel').grid(row=3, column=0, sticky=tk.W, padx=8, pady=8)
        min_p_scale = ttk.Scale(advanced_frame, from_=0.0, to=1.0, variable=self.min_p_var, orient=tk.HORIZONTAL)
        min_p_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=8, pady=8)
        min_p_entry = ttk.Entry(advanced_frame, textvariable=self.min_p_var, width=10, style='Modern.TEntry')
        min_p_entry.grid(row=3, column=2, padx=8, pady=8)
        
        # Top A
        ttk.Label(advanced_frame, text="🔝 Top A (0.0 - 1.0):", style='Subtitle.TLabel').grid(row=4, column=0, sticky=tk.W, padx=8, pady=8)
        top_a_scale = ttk.Scale(advanced_frame, from_=0.0, to=1.0, variable=self.top_a_var, orient=tk.HORIZONTAL)
        top_a_scale.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=8, pady=8)
        top_a_entry = ttk.Entry(advanced_frame, textvariable=self.top_a_var, width=10, style='Modern.TEntry')
        top_a_entry.grid(row=4, column=2, padx=8, pady=8)
        
        # Configure grid weights for responsive layout
        core_frame.columnconfigure(1, weight=1)
        advanced_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        # Application settings section
        app_frame = ttk.LabelFrame(main_frame, text="Application Settings", padding=10)
        app_frame.pack(fill=tk.X, pady=(0, 10))
        
        
        # Default model
        ttk.Label(app_frame, text="Default Model:").pack(anchor=tk.W, pady=2)
        ttk.Entry(app_frame, textvariable=self.default_model_var, width=30).pack(anchor=tk.W, pady=2)
        
        # Save settings button
        ttk.Button(main_frame, text="Save Settings", command=self.save_settings).pack(pady=10)
        
        # Settings info
        info_text = """
These settings apply globally to all tabs and operations.
• Temperature: Controls randomness (0.0 = deterministic, 2.0 = very random)
• Max Tokens: Maximum number of tokens to generate
• Top P: Nucleus sampling parameter (0.0-1.0)
• Top K: Limit to top K most likely tokens
• Seed: Random seed (-1 for random, any other number for reproducible results)
• Repeat Penalty: Penalty for repeating tokens
• Frequency/Presence Penalty: OpenAI-specific penalties
• Min P/Top A: Advanced sampling parameters
        """
        info_label = ttk.Label(main_frame, text=info_text.strip(), justify=tk.LEFT, foreground="gray")
        info_label.pack(pady=10)
    
    def create_single_image_tab(self):
        """Create single image analysis tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🖼️ Single Image")
        
        # Configure frame to expand
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ttk.Frame(frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Analysis settings at the top
        analysis_frame = ttk.LabelFrame(main_container, text="⚙️ Analysis Settings", padding=12)
        analysis_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Prompt section
        prompt_section = ttk.Frame(analysis_frame)
        prompt_section.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(prompt_section, text="💬 Prompt:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 8))
        self.prompt_var = tk.StringVar(value="Describe this image in detail")
        prompt_entry = ttk.Entry(prompt_section, textvariable=self.prompt_var, width=60, style='Modern.TEntry')
        prompt_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Wan I2V Enhancement option
        enhancement_section = ttk.Frame(analysis_frame)
        enhancement_section.pack(fill=tk.X, pady=(0, 10))
        
        self.wan_i2v_var = tk.BooleanVar()
        wan_checkbox = ttk.Checkbutton(enhancement_section, text="🎬 Use Wan I2V Enhancement", 
                                      variable=self.wan_i2v_var, command=self.on_wan_i2v_toggle)
        wan_checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        # Instructions for Wan I2V
        instructions_text = ("This option uses a specialized system prompt for Image-to-Video (I2V) generation. "
                           "Set your prompt to describe the video scene you want to create from the image. "
                           "The system will enhance your prompt with detailed motion and camera movements.")
        instructions_label = ttk.Label(enhancement_section, text=instructions_text, 
                                     style='Info.TLabel', wraplength=600)
        instructions_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Model status and settings info
        info_section = ttk.Frame(analysis_frame)
        info_section.pack(fill=tk.X, pady=(0, 10))
        
        # Model status
        model_info = ttk.Frame(info_section)
        model_info.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(model_info, text="🤖 Selected Model:", style='Subtitle.TLabel').pack(side=tk.LEFT)
        self.single_image_model_var = tk.StringVar(value="None selected")
        ttk.Label(model_info, textvariable=self.single_image_model_var, style='Info.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        
        # Global settings info
        ttk.Label(info_section, text="⚙️ Model parameters are managed globally in the 'Model Settings' tab.", 
                 style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        settings_info = ttk.Label(info_section, text=f"Current: Temp={self.temperature_var.get():.1f}, Max Tokens={self.max_tokens_var.get()}", 
                                 style='Info.TLabel')
        settings_info.pack(anchor=tk.W)
        
        # Analyze button
        analyze_btn = ttk.Button(analysis_frame, text="🔍 Analyze Image", command=self.analyze_single_image, 
                                style='Primary.TButton', width=20)
        analyze_btn.pack(pady=10)
        
        # Side-by-side content area
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Image selection and preview (fixed width)
        left_frame = ttk.LabelFrame(content_frame, text="🖼️ Image Selection & Preview", padding=12)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_frame.pack_propagate(False)  # Prevent left frame from changing size
        
        # Set a fixed width for the left frame
        left_frame.configure(width=450)
        
        # Top section with button and path
        top_section = ttk.Frame(left_frame)
        top_section.pack(fill=tk.X, pady=(0, 10))
        
        select_btn = ttk.Button(top_section, text="📂 Select Image", command=self.select_image, 
                               style='Primary.TButton', width=18)
        select_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.image_path_var = tk.StringVar()
        path_label = ttk.Label(top_section, textvariable=self.image_path_var, style='Info.TLabel')
        path_label.pack(side=tk.LEFT)
        
        # Image preview area with fixed size
        preview_area = ttk.Frame(left_frame)
        preview_area.pack(fill=tk.X, pady=(0, 10))
        
        # Create a canvas for the image with fixed size
        self.image_canvas = tk.Canvas(preview_area, width=400, height=300, 
                                    bg="#f8f9fa", relief="solid", borderwidth=1)
        self.image_canvas.pack(pady=10)
        
        # Show initial placeholder text on canvas
        self.image_canvas.create_text(200, 150, text="No image selected", 
                                    font=("Arial", 12), fill="gray", anchor=tk.CENTER)
        
        # Right side - Results display (takes remaining space)
        right_frame = ttk.LabelFrame(content_frame, text="📊 Analysis Results", padding=12)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.image_analysis_text = scrolledtext.ScrolledText(right_frame, height=15, width=50, 
                                                           font=("Consolas", 10))
        self.image_analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive layout
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)  # Content frame should expand
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
    
    def on_wan_i2v_toggle(self):
        """Handle Wan I2V Enhancement checkbox toggle"""
        if self.wan_i2v_var.get():
            # Set I2V-specific prompt when enabled
            self.prompt_var.set("Create a video scene with motion and camera movement")
        else:
            # Reset to default prompt when disabled
            self.prompt_var.set("Describe this image in detail")
    
    def create_batch_processing_tab(self):
        """Create batch processing tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📦 Batch Processing")
        
        # Configure frame to expand
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ttk.Frame(frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Folder selection
        folder_frame = ttk.LabelFrame(main_container, text="📁 Folder Selection", padding=12)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        folder_section = ttk.Frame(folder_frame)
        folder_section.pack(fill=tk.X)
        
        select_btn = ttk.Button(folder_section, text="📂 Select Folder", command=self.select_folder, 
                               style='Primary.TButton', width=18)
        select_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.folder_path_var = tk.StringVar()
        path_label = ttk.Label(folder_section, textvariable=self.folder_path_var, style='Info.TLabel')
        path_label.pack(side=tk.LEFT)
        
        # Batch settings
        batch_frame = ttk.LabelFrame(main_container, text="⚙️ Batch Settings", padding=12)
        batch_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Settings grid
        settings_grid = ttk.Frame(batch_frame)
        settings_grid.pack(fill=tk.X, pady=(0, 10))
        
        # Caption style
        ttk.Label(settings_grid, text="🎨 Caption Style:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=8, pady=8)
        self.caption_style_var = tk.StringVar(value="Danbooru Tags")
        caption_combo = ttk.Combobox(settings_grid, textvariable=self.caption_style_var,
                                   values=["Danbooru Tags", "Simple Description", "Detailed Analysis"],
                                   state="readonly", width=25, style='Modern.TCombobox')
        caption_combo.grid(row=0, column=1, sticky=tk.W, padx=8, pady=8)
        
        # Trigger word
        ttk.Label(settings_grid, text="🔤 Trigger Word:", style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, padx=8, pady=8)
        self.trigger_word_var = tk.StringVar(value="1girl")
        trigger_entry = ttk.Entry(settings_grid, textvariable=self.trigger_word_var, width=25, style='Modern.TEntry')
        trigger_entry.grid(row=1, column=1, sticky=tk.W, padx=8, pady=8)
        
        # Model status and settings info
        info_section = ttk.Frame(batch_frame)
        info_section.pack(fill=tk.X, pady=(0, 10))
        
        # Model status
        model_info = ttk.Frame(info_section)
        model_info.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(model_info, text="🤖 Selected Model:", style='Subtitle.TLabel').pack(side=tk.LEFT)
        self.batch_model_var = tk.StringVar(value="None selected")
        ttk.Label(model_info, textvariable=self.batch_model_var, style='Info.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        
        # Global settings info
        ttk.Label(info_section, text="⚙️ Model parameters are managed globally in the 'Model Settings' tab.", 
                 style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        settings_info = ttk.Label(info_section, text=f"Current: Temp={self.temperature_var.get():.1f}, Max Tokens={self.max_tokens_var.get()}", 
                                 style='Info.TLabel')
        settings_info.pack(anchor=tk.W)
        
        # Process button
        process_btn = ttk.Button(batch_frame, text="🚀 Process Batch", command=self.process_batch, 
                                style='Primary.TButton', width=20)
        process_btn.pack(pady=10)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_container, text="📊 Processing Progress", padding=12)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Progress counter
        self.progress_counter_var = tk.StringVar(value="Ready to process")
        ttk.Label(progress_frame, textvariable=self.progress_counter_var, style='Title.TLabel').pack(pady=(0, 5))
        
        # Progress label
        self.progress_label_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_label_var, style='Info.TLabel').pack()
        
        # Info message about file saving
        info_frame = ttk.LabelFrame(main_container, text="ℹ️ Batch Processing Info", padding=12)
        info_frame.pack(fill=tk.X)
        
        info_text = """📁 Batch processing will analyze all images in the selected folder.
📄 Individual caption files (.txt) will be created for each image.
✅ Processing status will be shown in the progress section above."""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, style='Info.TLabel')
        info_label.pack()
        
        # Configure grid weights for responsive layout
        main_container.columnconfigure(0, weight=1)
        settings_grid.columnconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
    
    def create_text_enhancement_tab(self):
        """Create text enhancement tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="✨ Text Enhancement")
        
        # Configure frame to expand
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ttk.Frame(frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text input section
        input_frame = ttk.LabelFrame(main_container, text="📝 Text Input", padding=12)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Enhancement type selection
        type_section = ttk.Frame(input_frame)
        type_section.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_section, text="🔧 Enhancement Type:", style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(0, 15))
        self.enhancement_type_var = tk.StringVar(value="qwen")
        enhancement_combo = ttk.Combobox(type_section, textvariable=self.enhancement_type_var,
                                       values=["qwen", "wan"], state="readonly", width=20, style='Modern.TCombobox')
        enhancement_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Type description
        self.type_description_var = tk.StringVar(value="Qwen: General text enhancement for images")
        type_desc_label = ttk.Label(type_section, textvariable=self.type_description_var, style='Info.TLabel')
        type_desc_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Bind type change
        enhancement_combo.bind('<<ComboboxSelected>>', self.on_enhancement_type_change)
        
        # Text input area
        ttk.Label(input_frame, text="💬 Text to Enhance:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.text_input = scrolledtext.ScrolledText(input_frame, height=6, width=70, font=("Consolas", 10))
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Settings and model info
        settings_section = ttk.Frame(input_frame)
        settings_section.pack(fill=tk.X, pady=(0, 10))
        
        # Model status
        model_info = ttk.Frame(settings_section)
        model_info.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(model_info, text="🤖 Selected Model:", style='Subtitle.TLabel').pack(side=tk.LEFT)
        self.text_model_var = tk.StringVar(value="None selected")
        ttk.Label(model_info, textvariable=self.text_model_var, style='Info.TLabel').pack(side=tk.LEFT, padx=(10, 0))
        
        # Global settings info
        ttk.Label(settings_section, text="⚙️ Model parameters are managed globally in the 'Model Settings' tab.", 
                 style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        settings_info = ttk.Label(settings_section, text=f"Current: Temp={self.temperature_var.get():.1f}, Max Tokens={self.max_tokens_var.get()}", 
                                 style='Info.TLabel')
        settings_info.pack(anchor=tk.W)
        
        # Enhance button
        enhance_btn = ttk.Button(input_frame, text="✨ Enhance Text", command=self.enhance_text, 
                                style='Primary.TButton', width=20)
        enhance_btn.pack(pady=10)
        
        # Results display
        results_frame = ttk.LabelFrame(main_container, text="📊 Enhancement Results", padding=12)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_results_text = scrolledtext.ScrolledText(results_frame, height=10, width=70, 
                                                         font=("Consolas", 10))
        self.text_results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive layout
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)  # Results frame should expand
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
    
    
    
    def toggle_connection(self):
        """Toggle connection state"""
        if self.is_connected:
            self.disconnect_backend()
        else:
            self.connect_backend()
    
    def connect_backend(self):
        """Connect to the selected backend"""
        try:
            self.api = OllamaVisionAPI(self.swarmui_url_var.get())
            
            # Get session ID from SwarmUI first
            session_result = self.api.get_swarmui_session()
            if not session_result["success"]:
                messagebox.showerror("Error", f"Failed to get SwarmUI session: {session_result['message']}")
                return
            
            self.update_session_id_display()
            
            if self.backend_var.get() == "ollama":
                result = self.api.connect_ollama(
                    ollama_url=self.ollama_url_var.get(),
                    show_all=True
                )
            elif self.backend_var.get() == "textgen":
                # For TextGen, validate URL first
                textgen_url = self.ollama_url_var.get()
                if not textgen_url:
                    messagebox.showerror("Error", "TextGen URL is required")
                    return
                result = self.api.connect_textgen(textgen_url)
            elif self.backend_var.get() in ["openai", "openrouter"]:
                # For OpenAI/OpenRouter, validate API key first
                api_key = self.api_key_var.get()
                if not api_key:
                    messagebox.showerror("Error", "API key is required for external APIs")
                    return
                result = {"success": True, "message": "Connected to external API"}
            else:
                result = {"success": False, "message": "Unknown backend type"}
            
            if result.get("success", False):
                self.load_models()
                
                # Update default model display
                self.update_default_model_display()
                
                # Try to select default model if available
                if self.available_models:
                    current_default = self.default_model_var.get().strip()
                    if current_default and current_default in self.available_models:
                        # Default model is available, select it
                        self.selected_model = current_default
                        self.update_model_status_display()
                        # Connected successfully - status shown in UI
                    else:
                        # No default or default not available, select first model
                        first_model = self.available_models[0]
                        self.selected_model = first_model
                        self.update_model_status_display()
                        # Connected successfully - status shown in UI
                else:
                    # Connected successfully - status shown in UI
                    pass
                
                # Update connection state and button
                self.is_connected = True
                self.update_connection_button()
            else:
                messagebox.showerror("Error", f"Connection failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
    
    def disconnect_backend(self):
        """Disconnect from the current backend"""
        try:
            # Clear connection state
            self.is_connected = False
            self.selected_model = None
            self.available_models = []
            self.all_models = []
            self.filtered_models = []
            
            # Clear API client
            self.api = None
            
            # Update UI
            self.update_connection_button()
            self.update_model_status_display()
            self.update_models_display()
            self.update_default_model_display()
            
        except Exception as e:
            print(f"Error during disconnect: {str(e)}")
    
    def update_connection_button(self):
        """Update the connect/disconnect button appearance"""
        if self.is_connected:
            self.connect_button.config(text="🔴 Disconnect", style="Accent.TButton")
        else:
            self.connect_button.config(text="Connect", style="TButton")
    
    def reset_session(self):
        """Reset the session ID (internal function, no UI)"""
        if hasattr(self, 'api'):
            try:
                new_session_id = self.api.reset_session()
                self.update_session_id_display()
                # Session reset silently - no popup
            except Exception as e:
                print(f"Failed to reset session: {str(e)}")
        else:
            print("No connection available for session reset")
    
    def update_session_id_display(self):
        """Update the session ID display"""
        if hasattr(self, 'api'):
            self.session_id_var.set(self.api.get_session_id())
        else:
            self.session_id_var.set("Not connected")
    
    def update_connection_fields(self):
        """Update which connection fields are visible based on backend"""
        backend = self.backend_var.get()
        
        # Clear all fields first
        self.ollama_url_label.grid_remove()
        self.ollama_url_entry.grid_remove()
        self.api_key_label.grid_remove()
        self.api_key_entry.grid_remove()
        
        if backend == "ollama":
            # Show Ollama URL field
            self.ollama_url_label.grid(row=2, column=0, sticky=tk.W, pady=2)
            self.ollama_url_entry.grid(row=2, column=1, padx=5, pady=2)
        elif backend in ["openai", "openrouter"]:
            # Show API Key field
            self.api_key_label.grid(row=2, column=0, sticky=tk.W, pady=2)
            self.api_key_entry.grid(row=2, column=1, padx=5, pady=2)
        elif backend == "textgen":
            # Show Ollama URL field (used for TextGen URL)
            self.ollama_url_label.config(text="TextGen URL:")
            self.ollama_url_label.grid(row=2, column=0, sticky=tk.W, pady=2)
            self.ollama_url_entry.grid(row=2, column=1, padx=5, pady=2)
    
    def on_backend_change(self, event=None):
        """Handle backend selection change"""
        backend = self.backend_var.get()
        
        # Update field visibility
        self.update_connection_fields()
        
        # Update field values based on selected backend
        if backend == "openai":
            self.api_key_var.set(self.openai_api_key)
        elif backend == "openrouter":
            self.api_key_var.set(self.openrouter_api_key)
        elif backend == "textgen":
            self.ollama_url_var.set(self.textgen_url)
        else:  # ollama
            self.api_key_var.set("")  # Clear API key for Ollama
    
    def on_api_key_change(self, event=None):
        """Handle API key changes and auto-save"""
        # Update the stored API key for the current backend
        current_backend = self.backend_var.get()
        if current_backend == "openai":
            self.openai_api_key = self.api_key_var.get()
        elif current_backend == "openrouter":
            self.openrouter_api_key = self.api_key_var.get()
        
        # Auto-save settings
        self.auto_save_settings()
    
    def auto_save_settings(self):
        """Auto-save settings without showing message"""
        try:
            # Update stored API keys based on current backend
            current_backend = self.backend_var.get()
            if current_backend == "openai":
                self.openai_api_key = self.api_key_var.get()
            elif current_backend == "openrouter":
                self.openrouter_api_key = self.api_key_var.get()
            elif current_backend == "textgen":
                self.textgen_url = self.ollama_url_var.get()
            
            settings = {
                "swarmui_url": self.swarmui_url_var.get(),
                "backend": self.backend_var.get(),
                "ollama_url": self.ollama_url_var.get(),
                "api_key": self.api_key_var.get(),
                "default_model": self.default_model_var.get(),
                "session_id": self.session_id_var.get() if hasattr(self, 'session_id_var') else "",
                "openai_api_key": self.openai_api_key,
                "openrouter_api_key": self.openrouter_api_key,
                "textgen_url": self.textgen_url
            }
            
            with open("ollamavision_settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Auto-save failed: {e}")
    
    def load_models(self):
        """Load available models"""
        self.models_listbox.delete(0, tk.END)
        self.available_models = []
        
        try:
            if self.backend_var.get() == "ollama":
                result = self.api.connect_ollama(show_all=True)
                if result.get("success") and "models" in result:
                    models = result["models"]
                    # Sort models alphabetically
                    models.sort()
                    self.all_models = models.copy()
                    self.filtered_models = models.copy()
                    self.update_models_display()
            elif self.backend_var.get() == "openai":
                api_key = self.api_key_var.get()
                if not api_key:
                    messagebox.showerror("Error", "API key is required for OpenAI")
                    return
                
                result = self.api.get_openai_models(api_key)
                if result.get("success"):
                    models = result["models"]
                    # Sort models alphabetically
                    models.sort()
                    self.all_models = models.copy()
                    self.filtered_models = models.copy()
                    self.update_models_display()
                else:
                    messagebox.showerror("Error", f"Failed to fetch OpenAI models: {result.get('message', 'Unknown error')}")
            elif self.backend_var.get() == "openrouter":
                api_key = self.api_key_var.get()
                if not api_key:
                    messagebox.showerror("Error", "API key is required for OpenRouter")
                    return
                
                result = self.api.get_openrouter_models(api_key)
                if result.get("success"):
                    models = result["models"]
                    # Sort models alphabetically
                    models.sort()
                    self.all_models = models.copy()
                    self.filtered_models = models.copy()
                    self.update_models_display()
                else:
                    messagebox.showerror("Error", f"Failed to fetch OpenRouter models: {result.get('message', 'Unknown error')}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")
    
    def on_model_select(self, event):
        """Handle model selection"""
        selection = self.models_listbox.curselection()
        if selection:
            model = self.available_models[selection[0]]
            self.selected_model = model  # Store selected model globally
            
            # Update model status in all tabs
            self.update_model_status_display()
    
    def set_as_default_model(self):
        """Set the currently selected model as the default"""
        if not self.selected_model:
            messagebox.showwarning("No Model Selected", "Please select a model first")
            return
        
        # Set as default
        self.default_model_var.set(self.selected_model)
        
        # Update displays
        self.update_default_model_display()
        self.update_model_status_display()
        
        # Auto-save settings
        self.auto_save_settings()
        
        messagebox.showinfo("Default Model Set", f"'{self.selected_model}' has been set as your default model")
    
    def update_default_model_display(self):
        """Update the default model display"""
        default_model = self.default_model_var.get().strip()
        if default_model:
            self.default_model_display_var.set(f"Default: {default_model}")
        else:
            self.default_model_display_var.set("No default model set")
    
    def get_selected_model(self):
        """Get the currently selected model"""
        if self.selected_model:
            return self.selected_model
        
        # Fallback: try to get from listbox selection
        selection = self.models_listbox.curselection()
        if selection and selection[0] < len(self.available_models):
            return self.available_models[selection[0]]
        
        return None
    
    def update_model_status_display(self):
        """Update model status display in all tabs"""
        model = self.get_selected_model()
        default_model = self.default_model_var.get().strip()
        
        if model:
            # Check if this is the default model
            if default_model and model == default_model:
                model_name = f"Default model: {model}"
            else:
                model_name = model
        else:
            model_name = "None selected"
        
        # Update all tab model status indicators
        if hasattr(self, 'single_image_model_var'):
            self.single_image_model_var.set(model_name)
        if hasattr(self, 'batch_model_var'):
            self.batch_model_var.set(model_name)
        if hasattr(self, 'text_model_var'):
            self.text_model_var.set(model_name)
        
        # Update connection tab model info
        if hasattr(self, 'model_info_var'):
            self.model_info_var.set(model_name)
    
    def filter_models(self, *args):
        """Filter models based on search text"""
        search_text = self.model_search_var.get().lower()
        
        if not search_text:
            # Show all models if no search text
            self.filtered_models = self.all_models.copy()
        else:
            # Filter models that contain search text
            self.filtered_models = [model for model in self.all_models if search_text in model.lower()]
        
        # Update the listbox
        self.update_models_display()
    
    def clear_model_search(self):
        """Clear the search and show all models"""
        self.model_search_var.set("")
    
    def update_models_display(self):
        """Update the models listbox display"""
        # Clear current selection
        self.models_listbox.selection_clear(0, tk.END)
        
        # Clear the listbox
        self.models_listbox.delete(0, tk.END)
        
        # Add filtered models to listbox
        for model in self.filtered_models:
            self.models_listbox.insert(tk.END, model)
        
        # Update available_models to match filtered list
        self.available_models = self.filtered_models.copy()
        
        # Update model count display
        total_models = len(self.all_models)
        filtered_count = len(self.filtered_models)
        
        if total_models == 0:
            self.model_count_var.set("No models loaded")
        elif filtered_count == total_models:
            self.model_count_var.set(f"Showing {total_models} models")
        else:
            self.model_count_var.set(f"Showing {filtered_count} of {total_models} models")
    
    def select_image(self):
        """Select an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff")]
        )
        if file_path:
            print(f"Image selected: {file_path}")  # Debug print
            self.image_path_var.set(file_path)
            self.load_image_preview(file_path)
    
    def load_image_preview(self, file_path):
        """Load and display image preview"""
        try:
            # Load image
            image = Image.open(file_path)
            
            # Resize for preview to fit canvas (400x300)
            image.thumbnail((380, 280), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Clear canvas and display image
            self.image_canvas.delete("all")
            self.image_canvas.create_image(200, 150, image=photo, anchor=tk.CENTER)
            self.image_canvas.image = photo  # Keep a reference
            
            print(f"Image loaded successfully: {file_path}")  # Debug print
            
            # Convert to base64 for API
            with open(file_path, "rb") as f:
                image_data = f.read()
            
            # Get file extension
            ext = Path(file_path).suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            elif ext == '.png':
                mime_type = "image/png"
            elif ext == '.gif':
                mime_type = "image/gif"
            else:
                mime_type = "image/jpeg"
            
            self.current_image_data = f"data:{mime_type};base64,{base64.b64encode(image_data).decode()}"
            
        except Exception as e:
            # Clear canvas and show placeholder text
            self.image_canvas.delete("all")
            self.image_canvas.create_text(200, 150, text="Failed to load image", 
                                        font=("Arial", 12), fill="red", anchor=tk.CENTER)
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def analyze_single_image(self):
        """Analyze a single image"""
        if not self.current_image_data:
            messagebox.showerror("Error", "Please select an image first")
            return
        
        if not self.available_models:
            messagebox.showerror("Error", "Please connect to a backend first")
            return
        
        # Get selected model
        model = self.get_selected_model()
        if not model:
            messagebox.showerror("Error", "Please select a model from the Connection tab")
            return
        
        # Run analysis in thread
        thread = threading.Thread(target=self._analyze_image_thread, args=(model,))
        thread.daemon = True
        thread.start()
    
    def _analyze_image_thread(self, model):
        """Analyze image in separate thread"""
        try:
            self.root.after(0, lambda: self.progress_label_var.set("Analyzing image..."))
            
            # Wan I2V system prompt
            wan_i2v_system_prompt = None
            if self.wan_i2v_var.get():
                wan_i2v_system_prompt = ("You are a movie director. You can take a single image and turn it into a full thought out scene. "
                                       "Instead of screenplays you write video generation prompts for image to video. You don't need to describe the image. "
                                       "Just analyze the image and describe a scene with motion and camera movements based on the image given to you. "
                                       "The user may give a short prompt for direction. Enhance that prompt and flesh out the users idea. Don't be vague. "
                                       "Describe action and movement don't' just say \"moves, runs, walks\" give action words to the action itself. "
                                       "Do not describe sounds as the video will not have sound. Mention things in the image but there is no need to describe them. "
                                       "If you want a man in a green shirt that is in the image to move simply say something like this example shows: "
                                       "\"the man in the green shirt begins to walk briskly...\". Begin your prompt with what the image shows. "
                                       "The image sent to you will be the first frame of the video so you should make your prompt with this in mind. "
                                       "Do not begin the scene with anything other than the image sent to you. Take the first frame image and expand from that. "
                                       "The video will be on average about 5 seconds in length. Make your prompt fit within this constraint. "
                                       "Do not make the prompt so long that it can't fit into a 5 second video clip. Be descriptive but concise. "
                                       "Don't use phrasing like \"the camera pivots behind a hovering helicopter\" instead say \"the camera pivots behind the hovering helicopter\" "
                                       "use what's in the image to build the prompt.\n\n"
                                       "Return only the prompt you make from the image. Do not explain yourself or give any extra information other than the prompt you make from the image. "
                                       "Do not describe the image or give any information about the image other than the video prompt. The prompt should not include any description of the image.")
            
            result = self.api.analyze_image(
                image_data=self.current_image_data,
                model=model,
                backend_type=self.backend_var.get(),
                prompt=self.prompt_var.get(),
                temperature=self.temperature_var.get(),
                max_tokens=self.max_tokens_var.get(),
                ollama_url=self.ollama_url_var.get(),
                api_key=self.api_key_var.get() if self.backend_var.get() in ["openai", "openrouter"] else None,
                system_prompt=wan_i2v_system_prompt
            )
            
            # Display result in the same tab
            self.root.after(0, lambda: self.display_image_analysis_result(result))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {error_msg}"))
        finally:
            self.root.after(0, lambda: self.progress_label_var.set("Ready"))
    
    def display_image_analysis_result(self, result):
        """Display image analysis result in the single image tab"""
        # Clear previous results
        self.image_analysis_text.delete("1.0", tk.END)
        
        if isinstance(result, dict) and result.get("success"):
            # Show only the LLM response
            response = result.get("response", "")
            if response:
                self.image_analysis_text.insert("1.0", response)
            else:
                self.image_analysis_text.insert("1.0", "No analysis response received.")
        else:
            # Show error message
            error_msg = result.get('message', 'Unknown error occurred') if isinstance(result, dict) else str(result)
            self.image_analysis_text.insert("1.0", f"Error: {error_msg}")
        
        self.image_analysis_text.see(tk.END)
    
    def select_folder(self):
        """Select folder for batch processing"""
        folder_path = filedialog.askdirectory(title="Select Folder with Images")
        if folder_path:
            self.folder_path_var.set(folder_path)
    
    def process_batch(self):
        """Process batch of images"""
        if not self.folder_path_var.get():
            messagebox.showerror("Error", "Please select a folder first")
            return
        
        if not self.available_models:
            messagebox.showerror("Error", "Please connect to a backend first")
            return
        
        # Get selected model
        model = self.get_selected_model()
        if not model:
            messagebox.showerror("Error", "Please select a model from the Connection tab")
            return
        
        # Reset progress display
        self.progress_var.set(0)
        self.progress_counter_var.set("Preparing batch processing...")
        self.progress_label_var.set("Ready")
        
        # Run batch processing in thread
        thread = threading.Thread(target=self._process_batch_thread, args=(model,))
        thread.daemon = True
        thread.start()
    
    def _process_batch_thread(self, model):
        """Process batch in separate thread"""
        try:
            folder_path = self.folder_path_var.get()
            
            # Count images first
            self.root.after(0, lambda: self.progress_label_var.set("Scanning folder for images..."))
            self.root.after(0, lambda: self.progress_var.set(0))
            
            # Get list of image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
            image_files = []
            
            for file in os.listdir(folder_path):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(file)
            
            total_images = len(image_files)
            
            if total_images == 0:
                self.root.after(0, lambda: self.progress_counter_var.set("No images found in folder"))
                self.root.after(0, lambda: self.progress_label_var.set("No image files found in the selected folder."))
                return
            
            # Update progress display
            self.root.after(0, lambda: self.progress_counter_var.set(f"Found {total_images} images to process"))
            self.root.after(0, lambda: self.progress_label_var.set("Starting batch processing..."))
            
            # Process images
            result = self.api.batch_caption_images(
                folder_path=folder_path,
                model=model,
                backend_type=self.backend_var.get(),
                caption_style=self.caption_style_var.get(),
                trigger_word=self.trigger_word_var.get(),
                temperature=self.temperature_var.get(),
                max_tokens=self.max_tokens_var.get(),
                ollama_url=self.ollama_url_var.get(),
                api_key=self.api_key_var.get() if self.backend_var.get() in ["openai", "openrouter"] else None
            )
            
            # Update progress to complete
            self.root.after(0, lambda: self.progress_var.set(100))
            
            # Get actual processed count from result
            actual_processed = result.get('processed', total_images)
            actual_successful = result.get('successful', 0)
            actual_failed = result.get('failed', 0)
            
            self.root.after(0, lambda: self.progress_counter_var.set(f"Completed: {actual_processed}/{total_images} images (✓{actual_successful} ✗{actual_failed})"))
            self.root.after(0, lambda: self.progress_label_var.set("Batch processing complete!"))
            
            # Display result
            self.root.after(0, lambda: self.display_batch_result(result))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Batch processing failed: {error_msg}"))
        finally:
            self.root.after(0, lambda: self.progress_label_var.set("Ready"))
    
    
    def enhance_text(self):
        """Enhance text"""
        if not self.available_models:
            messagebox.showerror("Error", "Please connect to a backend first")
            return
        
        # Get selected model
        model = self.get_selected_model()
        if not model:
            messagebox.showerror("Error", "Please select a model from the Connection tab")
            return
        
        # Get text from input
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "Please enter text to enhance")
            return
        
        # Run enhancement in thread
        thread = threading.Thread(target=self._enhance_text_thread, args=(model, text))
        thread.daemon = True
        thread.start()
    
    def _enhance_text_thread(self, model, text):
        """Enhance text in separate thread"""
        try:
            self.root.after(0, lambda: self.progress_label_var.set("Enhancing text..."))
            
            # Get the system prompt for the selected enhancement type
            enhancement_type = self.enhancement_type_var.get()
            system_prompt = self.get_enhancement_system_prompt(enhancement_type)
            
            result = self.api.enhance_text_prompt(
                model=model,
                backend_type=self.backend_var.get(),
                prompt=text,
                temperature=self.temperature_var.get(),
                max_tokens=self.max_tokens_var.get(),
                ollama_url=self.ollama_url_var.get(),
                api_key=self.api_key_var.get() if self.backend_var.get() in ["openai", "openrouter"] else None,
                system_prompt=system_prompt
            )
            
            # Display result in text results text area
            self.root.after(0, lambda: self.display_text_result(result))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Text enhancement failed: {error_msg}"))
        finally:
            self.root.after(0, lambda: self.progress_label_var.set("Ready"))
    
    def display_result(self, operation, result):
        """Display result in results tab"""
        self.notebook.select(5)  # Switch to results tab
        
        timestamp = tk.datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result_text = f"\n{'='*60}\n"
        result_text += f"{operation} - {timestamp}\n"
        result_text += f"{'='*60}\n"
        
        if isinstance(result, dict):
            if "success" in result:
                result_text += f"Success: {result['success']}\n"
            if "message" in result:
                result_text += f"Message: {result['message']}\n"
            if "result" in result:
                result_text += f"Result: {result['result']}\n"
            if "processedCount" in result:
                result_text += f"Processed: {result['processedCount']} images\n"
            if "results" in result:
                result_text += f"Results:\n{json.dumps(result['results'], indent=2)}\n"
        else:
            result_text += f"Result: {str(result)}\n"
        
        result_text += f"\n{'-'*60}\n"
        
        self.results_text.insert(tk.END, result_text)
        self.results_text.see(tk.END)
        
    
    def display_batch_result(self, result):
        """Handle batch processing result"""
        if not result.get('success'):
            # Only show error popup for actual errors
            error_msg = result.get('error', 'Unknown error occurred')
            messagebox.showerror("Batch Processing Error", f"Error: {error_msg}")
    
    
    def display_text_result(self, result):
        """Display text enhancement result in the text tab"""
        # Clear previous results
        self.text_results_text.delete(1.0, tk.END)
        
        if result.get('success'):
            if 'response' in result:
                # Show only the LLM response
                self.text_results_text.insert(tk.END, result['response'])
            else:
                self.text_results_text.insert(tk.END, "No enhanced text received.")
        else:
            # Show error message
            error_msg = result.get('message', 'Unknown error occurred')
            self.text_results_text.insert(tk.END, f"Error: {error_msg}")
        
        self.text_results_text.see(tk.END)
    
    def on_enhancement_type_change(self, event=None):
        """Handle enhancement type change"""
        enhancement_type = self.enhancement_type_var.get()
        if enhancement_type == "qwen":
            self.type_description_var.set("Qwen: General text enhancement for images")
        elif enhancement_type == "wan":
            self.type_description_var.set("Wan: Motion prompt enhancement for video generation")
    
    def get_enhancement_system_prompt(self, enhancement_type):
        """Get the system prompt for the selected enhancement type"""
        if enhancement_type == "qwen":
            return """# Qwen Prompt Enhancement System

You are an expert prompt enhancement specialist designed to transform brief, basic prompts into rich, detailed, and comprehensive instructions that will produce superior results from AI image generation models.

## Core Function

Your primary role is to receive short, simple prompts from users and expand them into fully-fleshed, detailed prompts that include:
- Rich visual descriptions
- Technical specifications
- Artistic direction
- Contextual details
- Quality enhancers
- Style specifications

## Enhancement Framework

### Visual Detail Expansion
**Transform basic subjects into rich descriptions:**
- Simple: "a cat" 
- Enhanced: "a majestic Maine Coon cat with luxurious silver-gray fur, piercing amber eyes, sitting regally with perfect posture, whiskers catching soft light"

**Add environmental context:**
- Specify lighting conditions (golden hour, studio lighting, natural daylight, dramatic shadows)
- Include atmospheric elements (mist, rain, snow, dust particles, lens flares)
- Describe backgrounds and settings in detail
- Add weather and seasonal indicators

### Technical Quality Specifications
Always include technical parameters to ensure high-quality output:
- **Resolution indicators:** "8K resolution," "ultra high definition," "crisp detail"
- **Camera specifications:** "shot with professional DSLR," "50mm lens," "shallow depth of field"
- **Lighting setup:** "three-point lighting," "soft box lighting," "natural window light"
- **Composition rules:** "rule of thirds," "centered composition," "dynamic angle"

### Artistic Style Integration
Enhance prompts with specific artistic directions:
- **Photography styles:** portrait, landscape, macro, street photography, documentary
- **Artistic movements:** impressionistic, photorealistic, surreal, minimalist, baroque
- **Color palettes:** warm tones, cool blues, monochromatic, vibrant saturated colors
- **Mood descriptors:** serene, dramatic, mysterious, energetic, melancholic

### Quality Enhancement Keywords
Include power words that improve AI generation:
- **Clarity enhancers:** "sharp focus," "crystal clear," "highly detailed," "intricate"
- **Professional markers:** "award-winning," "masterpiece," "professional grade," "gallery quality"
- **Texture descriptors:** "smooth," "rough," "glossy," "matte," "textured surface"
- **Depth indicators:** "bokeh background," "layered composition," "foreground and background separation"

## Enhancement Process

### Step 1: Subject Analysis
- Identify the core subject or concept
- Determine the likely intent (artistic, commercial, documentary, etc.)
- Assess what visual elements would enhance the concept

### Step 2: Context Building
- Add relevant environmental details
- Include time of day/season if appropriate
- Specify location or setting characteristics
- Consider cultural or historical context

### Step 3: Technical Specification
- Add camera and lens specifications
- Include lighting setup details
- Specify composition guidelines
- Add quality and resolution markers

### Step 4: Artistic Direction
- Define visual style and aesthetic
- Add color palette guidance
- Include mood and atmosphere descriptors
- Specify any artistic influences or techniques

### Step 5: Quality Assurance
- Include professional quality indicators
- Add detail enhancement keywords
- Specify any technical perfection requirements
- Include output format preferences

## Enhancement Examples

**Basic Prompt:** "sunset over mountains"
**Enhanced Prompt:** "Breathtaking golden hour sunset over majestic snow-capped mountain peaks, dramatic cloud formations painted in brilliant oranges, purples, and magentas, alpine landscape with pristine lakes reflecting the colorful sky, shot with telephoto lens creating compressed perspective, professional landscape photography, award-winning composition following rule of thirds, crystal clear 8K detail, HDR lighting capturing full dynamic range, serene and awe-inspiring atmosphere"

**Basic Prompt:** "woman reading"
**Enhanced Prompt:** "Elegant woman in her thirties with flowing auburn hair, wearing a cream-colored cashmere sweater, peacefully reading a leather-bound book in a cozy library corner, warm afternoon sunlight streaming through tall windows creating gentle shadows, surrounded by towering mahogany bookshelves filled with classic literature, shot with 85mm portrait lens, shallow depth of field with beautiful bokeh, soft natural lighting, intimate and contemplative mood, photorealistic detail, professional portraiture style"

## Output Format Requirements

Structure enhanced prompts as single, flowing descriptions that include:
1. **Main Subject** (detailed description)
2. **Setting/Environment** (contextual details)
3. **Lighting/Atmosphere** (mood and technical lighting)
4. **Technical Specifications** (camera, quality, resolution)
5. **Artistic Style** (aesthetic direction and mood)
6. **Quality Enhancers** (professional markers and detail specifications)

## Key Enhancement Principles

### Specificity Over Generality
- Replace vague terms with precise descriptors
- Add measurable qualities (colors, sizes, textures)
- Include specific rather than generic elements

### Visual Richness
- Layer multiple descriptive elements
- Include sensory details that translate visually
- Add elements that create depth and interest

### Professional Standards
- Include industry-standard terminology
- Add technical specifications that matter
- Reference professional photography/art concepts

### Contextual Relevance
- Ensure all additions serve the core concept
- Maintain logical consistency throughout
- Balance detail with focus on the main subject

## Response Guidelines

- Always expand significantly on the original prompt
- Maintain the user's original intent while enriching it
- Provide prompts that are immediately usable for image generation
- Include diverse enhancement elements in every response
- Structure the enhanced prompt for optimal AI interpretation
- Balance technical precision with creative inspiration
- Only respong with the enhanced prompt, do not respond with anything like "here is your enhanced prompt" or any other description"""

        elif enhancement_type == "wan":
            return """You are a motion prompt enhancement assistant for WAN 2.2 video generation. The user will give you a motion prompt describing what happens in the video. Do not add new elements or change the actions, characters, or events. Your task is to rewrite the prompt with clearer, more vivid, and more cinematic language so the video generation model can better capture the motion. Focus on fluidity, atmosphere, and visual clarity. Keep the sequence of actions identical to the user's original prompt. Respond only with the enhanced motion prompt—no explanations, lists, or meta commentary

Now enhance the following motion prompt:"""
        else:
            return "Enhance the following text:"
    
    
    def save_settings(self):
        """Save application settings"""
        # Update stored API keys based on current backend
        current_backend = self.backend_var.get()
        if current_backend == "openai":
            self.openai_api_key = self.api_key_var.get()
        elif current_backend == "openrouter":
            self.openrouter_api_key = self.api_key_var.get()
        elif current_backend == "textgen":
            self.textgen_url = self.ollama_url_var.get()
        
        settings = {
            "swarmui_url": self.swarmui_url_var.get(),
            "backend": self.backend_var.get(),
            "ollama_url": self.ollama_url_var.get(),
            "api_key": self.api_key_var.get(),
            "default_model": self.default_model_var.get(),
            "session_id": self.session_id_var.get() if hasattr(self, 'session_id_var') else "",
            # Save API keys for different backends
            "openai_api_key": self.openai_api_key,
            "openrouter_api_key": self.openrouter_api_key,
            "textgen_url": self.textgen_url,
            # Global model settings
            "temperature": self.temperature_var.get(),
            "max_tokens": self.max_tokens_var.get(),
            "top_p": self.top_p_var.get(),
            "top_k": self.top_k_var.get(),
            "repeat_penalty": self.repeat_penalty_var.get(),
            "seed": self.seed_var.get(),
            "frequency_penalty": self.frequency_penalty_var.get(),
            "presence_penalty": self.presence_penalty_var.get(),
            "min_p": self.min_p_var.get(),
            "top_a": self.top_a_var.get()
        }
        
        try:
            with open("ollamavision_settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def load_settings(self):
        """Load application settings"""
        try:
            if os.path.exists("ollamavision_settings.json"):
                with open("ollamavision_settings.json", 'r') as f:
                    settings = json.load(f)
                
                self.swarmui_url_var.set(settings.get("swarmui_url", "http://localhost:7801"))
                self.backend_var.set(settings.get("backend", "ollama"))
                self.ollama_url_var.set(settings.get("ollama_url", "http://localhost:11434"))
                self.api_key_var.set(settings.get("api_key", ""))
                self.default_model_var.set(settings.get("default_model", ""))
                
                # Load session ID if available
                if hasattr(self, 'session_id_var'):
                    saved_session_id = settings.get("session_id", "")
                    if saved_session_id:
                        self.session_id_var.set(saved_session_id)
                
                # Load API keys for different backends
                self.openai_api_key = settings.get("openai_api_key", "")
                self.openrouter_api_key = settings.get("openrouter_api_key", "")
                self.textgen_url = settings.get("textgen_url", "http://localhost:5000")
                
                # Load global model settings
                self.temperature_var.set(settings.get("temperature", 0.8))
                self.max_tokens_var.set(settings.get("max_tokens", 500))
                self.top_p_var.set(settings.get("top_p", 0.7))
                self.top_k_var.set(settings.get("top_k", 40))
                self.repeat_penalty_var.set(settings.get("repeat_penalty", 1.1))
                self.seed_var.set(settings.get("seed", -1))
                self.frequency_penalty_var.set(settings.get("frequency_penalty", 0.0))
                self.presence_penalty_var.set(settings.get("presence_penalty", 0.0))
                self.min_p_var.set(settings.get("min_p", 0.0))
                self.top_a_var.set(settings.get("top_a", 0.0))
                
                # Set the appropriate API key based on the loaded backend
                self.on_backend_change()
                
                # Update default model display
                self.update_default_model_display()
                
                # Update connection button state
                self.update_connection_button()
        except Exception as e:
            print(f"Failed to load settings: {e}")

def main():
    """Main function"""
    root = tk.Tk()
    app = OllamaVisionGUI(root)
    
    # Add datetime import for timestamp
    import datetime
    tk.datetime = datetime
    
    root.mainloop()

if __name__ == "__main__":
    main()
