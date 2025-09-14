#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

try:
    from backend.app.main import app
    print("App imported successfully")
    
    # Test the forecast endpoint directly
    from backend.app.routes.grid import get_forecast
    print("Testing forecast function...")
    result = get_forecast()
    print("Direct forecast test successful")
    
    # Now try running with uvicorn
    import uvicorn
    print("Starting uvicorn server...")
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
