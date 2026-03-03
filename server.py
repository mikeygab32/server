from flask import Flask, request, jsonify
import face_recognition
import os
import socket

app = Flask(__name__)

# --- CONFIGURATION (FIXED) ---
# 1. Find where server.py is living right now
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. Look for the uploads folder relative to THIS file
UPLOADS_FOLDER = os.path.join(BASE_DIR, "../uploads")

print("\n🧠 AI SERVER STARTING...")
print(f"📂 Looking for student photos in: {os.path.abspath(UPLOADS_FOLDER)}")

# 1. LOAD FACES FROM DATABASE
known_encodings = []
known_ids = []

if os.path.exists(UPLOADS_FOLDER):
    files = os.listdir(UPLOADS_FOLDER)
    print(f"🔎 Found {len(files)} files. Learning faces...")
    
    for filename in files:
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # The filename (without extension) is the Student ID
            student_id = os.path.splitext(filename)[0]
            path = os.path.join(UPLOADS_FOLDER, filename)
            
            try:
                # Load image and find face
                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)
                
                if len(encodings) > 0:
                    known_encodings.append(encodings[0])
                    known_ids.append(student_id)
                    print(f"   ✅ Learned Face: ID {student_id}")
                else:
                    print(f"   ⚠️ No face found in {filename} (skipping)")
            except Exception as e:
                print(f"   ❌ Error reading {filename}: {e}")
else:
    print(f"❌ ERROR: Folder {UPLOADS_FOLDER} does not exist!")

print(f"🤖 BRAIN READY! I know {len(known_ids)} students.\n")

@app.route('/scan', methods=['POST'])
def scan():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No image uploaded"})

    file = request.files['file']
    print(f"📸 Received photo request...")

    try:
        uploaded_image = face_recognition.load_image_file(file)
        unknown_encodings = face_recognition.face_encodings(uploaded_image)

        if len(unknown_encodings) > 0:
            unknown_face = unknown_encodings[0]
            results = face_recognition.compare_faces(known_encodings, unknown_face)
            
            if True in results:
                match_index = results.index(True)
                student_id = known_ids[match_index]
                print(f"   ✅ MATCH FOUND: {student_id}")
                return jsonify({"status": "success", "student_id": student_id})
            else:
                print("   ❌ Face not recognized")
                return jsonify({"status": "fail", "message": "Face not recognized"})
        else:
            print("   ⚠️ No face detected in camera photo")
            return jsonify({"status": "fail", "message": "No face detected"})

    except Exception as e:
        print(f"   💥 Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    # Note: If this IP is wrong, use ipconfig to find the real one!
    print(f"🚀 SERVER RUNNING! Connect your phone to: http://{local_ip}:5000/scan")
    app.run(host='0.0.0.0', port=5000)