from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import json

app = Flask(__name__)

data = {
    "type": "service_account",
    "project_id": "aiytm-9ee9b",
    "private_key_id": "76bd4f89377f35316985df2e45e1c365e97dbb1b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDiISAXRQRGfw/y\ndpSbzOb21+9B6IQoPRXN/kl76tAtJYl5iBnme24p6x+2DXVliIBD4UBq2nPrt6mo\ncctD/2/1vpEpWAG2gwnuEhPvHDJ2a+EWM0ftGthXCHZTXygj0sYU3uKTmCnR6msp\n8egznCVeow3lfzFqpchBBwm3yX57cjJxMpR+k3IPArcHA2+IgWLoUiZOqjV4JOcq\nwuxg6MsdvPUrQr/mUxLgJT13gz9hzYNAOsIIiew+/Yzi0hFtwC6xZaEAUqUg8/27\nqjmmf3iF4uEDPD6V72EYQx7fCpexmSMXgi5MjlwwSQzQe1+eMTVHBJJqYczvihGB\njpnxZzOdAgMBAAECggEAWluJMrMp26+PJEAc7sqoKc+sM6ZhFKEgEuF+5Iy2Jawf\nrFflnZMJuKdS0xC6rdknA7jA4FGtS23m1b+uzNuHledRovcfLBpdf+tqWrvmMCq4\nVQIlxglZlCF2Aqd95x6kdxd+6yI857vnmWmn8uN8jT3TYjZ6fRaEl/NjfzR9HX8K\nb9jDzL/i0zgGly2mnEk8xzCXjntiSd5xi+6fp8s9EUjY5qPFeAqH0TP7VAHNCDgZ\ngdt4K3et6Laov2OURVcy+/YW74h2+OrOAc2pbNPcy2DAV/QpGvSpoNHqnEDwlpzs\nkWEBSylgIz8p4ABvZ4Zln0nBkVUkw9pqyclE0rKJswKBgQD2tKRfyVu5KPqO+B8G\noDXTJORqGY7ljeTJRjyf0hwR+1KhjpJFMxEUo4O5N2WyURCht6SPKIyPoqsfYCom\n2+3Li9eWPnwcLRk9UOPSEAHgMbZU7RMlCkfQuyhJTyxQ3wkjazlN36Rvl/bhuXt+\nZApPQc8N4cp6XFW8tMhP1fMXowKBgQDqpgkJG7pvzNEn1hLhZJqY3YBovz8/7etA\nD0+c+SFruwYhE7JPqOuHYJK2CHicY3aIfM1pT7KVhoqJGMhJbHCkaEwj8+ZvXa2b\nv180qCNDCytBMXlDtPB9T6Svsv8hGQU6BBqDkJpgczMp5AV2bbIvfgwQwTRqmUX4\nVHmLbHI7vwKBgQDxmeSj3bkS8tu16a3QulMb7TQ358G2cyhMKJm0Vnqg7YR1rP73\n/9PJZ3zXhTX11Ee6Z/MjM627+K0m8/Ezzwvo25GMlLLMkSn3j2Ec1gpQOb77GpU2\nIARGmRMSABRBOrtjUV10MwGBO8xOMGyNUYF7LtKMIMQ+4nAgdtb4wGjpiwKBgCWI\nh3t4fvrxJSedG4oIIJ6BF9Apf0GHmhC2IkL2qrzjvpg94VDSsVIHRZBujHRfiI9O\nf0DwKZ23VqOVXjw4Z1A1CrDZi6uWrXVzSBRRLMrFl5anBkGpSKqSucIM/LhbmzVr\ngJ443Ci/ZJi3y5Pk+hKUs/NeJDdE6ydMw+BkaWVbAoGBAOuLAVomOqjnEUCPOJ64\nV6Ye0uvwwii64VqSw/A4ArUyfIf/Sm7B4vXK4BR4ozfE2pbd4WWzGwk+cI8SwcvK\nOjklLBTL7azusmJVHKhDNSjoyKxivAV9AHORsxoZcEl9+YVz/7cnDqSRt/GXs98H\nkh2X3lRWXZfVwCuEHMb5OLQz\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-idppk@aiytm-9ee9b.iam.gserviceaccount.com",
    "client_id": "114789384302384552795",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-idppk%40aiytm-9ee9b.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

with open('firebase.json', 'w') as f:
    json.dump(data, f)

# Firebase Admin SDK credentials (replace with your actual path)
cred = credentials.Certificate("./firebase.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Function to get Firestore reference for the users collection
def get_users_collection():
    return db.collection("users")

# Initialize Firestore and create the users collection if it doesn't exist
def init_db():
    pass

# Initialize the database
init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '')

    try:
        users_ref = get_users_collection()

        # If there's a search query, filter users by name, email, niche, or country
        if search_query:
            query = users_ref.where('name', '>=', search_query).where('name', '<=', search_query + '\uf8ff') \
                              .limit(10)  # You can adjust the limit as needed
            results = query.stream()
        else:
            results = users_ref.stream()

        users = [user.to_dict() for user in results]

        return render_template('index.html', users=users, search_query=search_query)
    except Exception as e:
        return f"Error: {e}"

@app.route('/get_user')
def get_user():
    user_id = request.args.get('id')

    if not user_id:
        return jsonify({"error": "UUID is required."})

    try:
        user_ref = get_users_collection().document(user_id)
        user = user_ref.get()

        if user.exists:
            return jsonify(user.to_dict())
        else:
            return jsonify({"error": "User not found."})
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve data: {e}"})

@app.route('/save_user', methods=['POST'])
def save_user():
    name = request.form.get('name')
    email = request.form.get('email')
    niche = request.form.get('niche')
    country = request.form.get('country')

    if not name or not email or not niche or not country:
        return jsonify({"error": "All fields (name, email, niche, country) are required."})

    user_id = f"uuid-{str(hash(name + email))}"  # Simulating UUID generation

    try:
        # Reference to the user document
        user_ref = get_users_collection().document(user_id)

        # Set or update the user data
        user_ref.set({
            'name': name,
            'email': email,
            'niche': niche,
            'country': country
        })

        return jsonify({"id": user_id})
    except Exception as e:
        return jsonify({"error": f"Failed to save data: {e}"})

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=5000)
