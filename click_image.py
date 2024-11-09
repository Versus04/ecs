import subprocess

def capture_image(filename="test_image.jpg"):
    try:
        # Use espeak to announce the start of the image capture process
        subprocess.run(["espeak", "Clicking picture"], check=True)

        # Capture image using libcamera-still without preview
        subprocess.run(["sudo", "libcamera-still", "-o", filename], check=True)
        
        # Use espeak to announce completion of image capture
        subprocess.run(["espeak", "Picture clicked"], check=True)
        
        print(f"Image captured and saved as {filename}")
    
    except subprocess.CalledProcessError as e:
        print("Failed to capture image:", e)

# Call the capture function
capture_image("test_image.jpg")
