from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import shutil
from pathlib import Path
import webbrowser
import threading
import time
import logging
from logging.handlers import RotatingFileHandler
import tempfile
from Code_Visualization_and_Simulation_System.manim_code_generation_from_RAG import ManimFromRAG
from Code_Visualization_and_Simulation_System.run_manim_code import save_and_run_manim_script, extract_manim_code

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up file handler
log_file = 'app.log'
file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure folders
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / 'uploads'
VIDEO_FOLDER = BASE_DIR / 'static' / 'videos'
STATIC_FOLDER = BASE_DIR / 'static'
MEDIA_FOLDER = BASE_DIR / 'media'

# Create necessary directories
for folder in [UPLOAD_FOLDER, VIDEO_FOLDER, STATIC_FOLDER, MEDIA_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

# Initialize RAG system
MANIM_DIR = BASE_DIR / 'data' / 'raw' / 'Manim Docs' / 'Manim Docs'
rag = None

class VideoGenerationError(Exception):
    """Custom exception for video generation errors"""
    pass

def init_rag():
    """Initialize the RAG system with error handling"""
    global rag
    try:
        logger.info("Initializing RAG system...")
        rag = ManimFromRAG(str(MANIM_DIR))
        rag.index_documents()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        raise

def move_file(source: Path, destination: Path) -> Path:
    """
    Move a file from source to destination with proper error handling.
    
    Args:
        source (Path): Source file path
        destination (Path): Destination directory path
        
    Returns:
        Path: Path to the moved file
        
    Raises:
        FileNotFoundError: If source file doesn't exist
        PermissionError: If permission denied
        Exception: For other errors
    """
    try:
        # Ensure destination directory exists
        destination.mkdir(parents=True, exist_ok=True)
        
        # Create full destination path
        dest_file = destination / source.name
        
        # If destination file exists, create a unique name
        if dest_file.exists():
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            dest_file = destination / f"{source.stem}_{timestamp}{source.suffix}"
        
        # Move the file
        shutil.move(str(source), str(dest_file))
        logger.info(f"File moved successfully to: {dest_file}")
        return dest_file
        
    except FileNotFoundError:
        logger.error(f"Source file not found: {source}")
        raise
    except PermissionError:
        logger.error(f"Permission denied while moving file: {source} to {destination}")
        raise
    except Exception as e:
        logger.error(f"Error moving file: {str(e)}")
        raise

def recursively_run_manim_script(rag, code, max_retries=3, attempt=1):
    """
    Recursively generates and runs Manim scripts with error handling.
    
    Args:
        rag: The RAG object for Manim code generation
        code (str): Input code to visualize
        max_retries (int): Maximum number of retry attempts
        attempt (int): Current attempt number
        
    Returns:
        dict: Response containing output or error information
    """
    try:
        logger.info(f"Attempt {attempt}: Generating Manim script...")
        
        # Generate Manim visualization
        result = rag.generate_manim(code)
        
        # Extract and validate Manim code
        manim_code = extract_manim_code(result)
        if not manim_code:
            raise VideoGenerationError("Failed to generate valid Manim code")
        
        # Save and run the Manim code
        response = save_and_run_manim_script(manim_code)
        
        if response.get("error"):
            logger.error(f"Error in attempt {attempt}: {response['error']}")
            
            if attempt >= max_retries:
                logger.warning("Max retries reached")
                return response
            
            # Retry with backoff
            time.sleep(attempt * 2)  # Progressive delay
            return recursively_run_manim_script(rag, code, max_retries, attempt + 1)
            
        logger.info(f"Animation successfully created on attempt {attempt}")
        return response
        
    except Exception as e:
        logger.error(f"Error in Manim script generation: {str(e)}")
        return {"error": str(e)}

# API Routes
@app.route('/')
def index():
    """Serve the main application page"""
    try:
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index page: {str(e)}")
        return jsonify({"error": "Failed to load application"}), 500

@app.route('/api/visualize', methods=['POST'])
def visualize_code():
    """Handle code visualization requests"""
    try:
        # Validate input
        data = request.json
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
            
        code = data['code']
        if not code.strip():
            return jsonify({'error': 'Empty code provided'}), 400
            
        # Generate visualization
        response = recursively_run_manim_script(rag, code)
        
        if response.get('error'):
            return jsonify({'error': response['error']}), 500
        
        # Handle video file
        source_file = Path("media/videos/sample_manim_script/480p15/Visualization.mp4")
        if not source_file.exists():
            return jsonify({'error': 'Generated video file not found'}), 404
            
        try:
            # Move to static directory
            final_location = move_file(source_file, VIDEO_FOLDER)
            video_url = f'/static/videos/{final_location.name}'
            return jsonify({'videoUrl': video_url})
            
        except Exception as e:
            logger.error(f"Error processing video file: {str(e)}")
            return jsonify({'error': 'Failed to process video file'}), 500
            
    except Exception as e:
        logger.error(f"Error in visualization endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    """Serve generated video files"""
    try:
        return send_from_directory(VIDEO_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving video file {filename}: {str(e)}")
        return jsonify({"error": "Video file not found"}), 404

def open_browser():
    """Open the default web browser after a delay"""
    time.sleep(1.5)
    try:
        webbrowser.open('http://127.0.0.1:5000')
    except Exception as e:
        logger.error(f"Failed to open browser: {str(e)}")

def cleanup_old_files():
    """Cleanup old generated files periodically"""
    try:
        # Keep only last 50 videos
        video_files = sorted(VIDEO_FOLDER.glob('*.mp4'), key=lambda x: x.stat().st_mtime)
        if len(video_files) > 50:
            for file in video_files[:-50]:
                file.unlink()
        
        # Clean up temporary files
        temp_dir = Path(tempfile.gettempdir())
        for file in temp_dir.glob('manim_*'):
            if time.time() - file.stat().st_mtime > 86400:  # 24 hours
                file.unlink()
                
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def main():
    """Main application entry point"""
    try:
        # Initialize RAG system
        logger.info("Starting application...")
        init_rag()
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=cleanup_old_files)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        # Open browser automatically
        threading.Thread(target=open_browser).start()
        
        # Start Flask server
        logger.info("Starting server...")
        app.run(debug=False, host='127.0.0.1', port=5000)
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise

if __name__ == '__main__':
    main()