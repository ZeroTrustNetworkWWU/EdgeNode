from flask import Flask, make_response, redirect, render_template, request, jsonify, url_for, Response, session
import requests
from EdgeNodeExceptions import MissingTrustData, LowClientTrust
from RequestType import RequestType
from EdgeNodeConfig import EdgeNodeConfig
from datetime import timedelta

# Create a Flask app instance
app = Flask(__name__, static_url_path=None, static_folder=None)

# configure sessios to expire after 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Set the secret key for the session
app.secret_key = EdgeNodeConfig().secretKey

# Class that handles reciving data from the client and verifying the trust of the client before passing it on to the servers
class EdgeNodeReceiver:

    def __init__(self, host, port):
        EdgeNodeReceiver.config = EdgeNodeConfig()
        self.host = host
        self.port = port

    # Route all requests to this function for verification
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD'])
    def receive_request(path):
        print(request.path)
        try:
            data = None
            # Get the data from the request
            if (request.is_json):
                data = request.get_json()
            else:
                # TODO pull trust data from the cookies and add it to the data
                # instead of just redirecting to the login page
                sessionKey = session.get('sessionKey')
                data = {"_trustData" : {"session": sessionKey}}

            
            # Verify the trust data is here
            trustData, data = EdgeNodeReceiver.getTrustData(data)
            EdgeNodeReceiver.validateTrustData(trustData)
            EdgeNodeReceiver.getRemainingTrustData(request, trustData)

            EdgeNodeReceiver.__printTrustData(trustData)
            
            # If the request is not a generic request then it must be handled differently
            requestType = EdgeNodeReceiver.getRequestType(trustData)
            if requestType != RequestType.GENERIC:
                return EdgeNodeReceiver.handleSpecialRequest(requestType, trustData)

            trust = EdgeNodeReceiver.getPEPDecision(trustData)
            if not trust:
                raise LowClientTrust("Trust Engine Denied Access")
            
            # Forward the request to the backend server and return the response
            return EdgeNodeReceiver.forwardToBackendServer(request, data)
        
        except MissingTrustData as e:
            print(e)
            return jsonify({"error": f"{e}"}), 501
        except LowClientTrust as e:
            print(e)
            return jsonify({"error": f"{e}"}), 500
        

    @staticmethod
    def handleSpecialRequest(requestType, trustData):
        match requestType:
            case RequestType.LOGIN:
                session, trust = EdgeNodeReceiver.getPEPLoginDecision(trustData)
                if not trust:
                    raise LowClientTrust("Trust Engine Denied Access")
                return jsonify({"session": session}), 200
            
            case RequestType.LOGOUT:
                trust = EdgeNodeReceiver.getPEPLogoutDecision(trustData)
                if not trust:
                    raise LowClientTrust("Trust Engine Denied Access")
                return jsonify("Logout succesful"), 200

            case RequestType.REGISTER:
                trust = EdgeNodeReceiver.getPEPRegisterDecision(trustData)
                if not trust:
                    raise LowClientTrust("Trust Engine Denied Access")
                return jsonify("Registration succesful"), 200

            case RequestType.REMOVE_ACCOUNT:
                pass

            case _:
                return jsonify({"error": "Invalid request type"}), 500
    
    # Get the Trust engines decision on the trust of the client 
    # returns the trust level of the client if the client is trusted and None if not
    @staticmethod
    def getPEPDecision(trustData):
        try:
            response = requests.post(f"{EdgeNodeReceiver.config.trustEngineUrl}/getDecision", json=trustData, verify="cert.pem")
            if response.status_code == 200:
                return response.json().get("trustLevel")
            else:
                print("Trust Engine failed:", response.status_code)
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    # Get the Trust engines response to a login request
    # returns (session token, trustLevel) if the login was successful and None if not
    @staticmethod
    def getPEPLoginDecision(trustData):
        try:
            response = requests.post(f"{EdgeNodeReceiver.config.trustEngineUrl}/login", json=trustData, verify="cert.pem")
            data = response.json()
            if response.status_code == 200:
                return data.get("session"), data.get("trustLevel")
            else:
                print("Trust Engine failed:", response.status_code)
                return None, None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None
        
    # Get the Trust engines response to a logout request
    @staticmethod
    def getPEPLogoutDecision(trustData):
        try:
            response = requests.post(f"{EdgeNodeReceiver.config.trustEngineUrl}/logout", json=trustData, verify="cert.pem")
            data = response.json()
            if response.status_code == 200:
                return data.get("trustLevel")
            else:
                print("Trust Engine failed:", response.status_code)
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    # Get the Trust engines response to a register request
    @staticmethod
    def getPEPRegisterDecision(trustData):
        try:
            response = requests.post(f"{EdgeNodeReceiver.config.trustEngineUrl}/register", json=trustData, verify="cert.pem")
            data = response.json()
            if response.status_code == 200:
                return data.get("trustLevel")
            else:
                print("Trust Engine failed:", response.status_code)
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    @staticmethod
    def getTrustData(data):
        trustData = data.get("_trustData")
        data.pop("_trustData", None)
        return trustData, data
    
    @staticmethod
    def getRequestType(data):
        type = data.get("requestType")
        match type:
            case "login":
                return RequestType.LOGIN
            case "logout":
                return RequestType.LOGOUT
            case "register":
                return RequestType.REGISTER
            case "removeAccount":
                return RequestType.REMOVE_ACCOUNT
            case _:
                return RequestType.GENERIC
    
    # TODO validate the trust data is complete not just that it exists
    @staticmethod
    def validateTrustData(data):
        if data == None:
            raise MissingTrustData("Trust data is missing")

    # TODO get any remaining trust data that is not provided by the client from the request ie., geolocation, ip, etc.
    @staticmethod  
    def getRemainingTrustData(request, trustData):
        # Add the ip of the request to the trust data
        trustData["ip"] = request.remote_addr

        # Add the path of the request to the trust data
        trustData["resource"] = request.path

        # Add the request method to the trust data
        trustData["action"] = request.method

    # Prints the trust data in a readable format
    @staticmethod
    def __printTrustData(data):
        for key in data:
            print(f"{key}:", end=" ")
            if type(data[key]) == dict:
                print()
                for key2 in data[key]:
                    print(f"  {key2}: {data[key][key2]}")
            else:
                print(f"{data[key]}")
        print()

    @staticmethod
    def forwardToBackendServer(request, data):
        # Forward the request to the backend server
        full_url = EdgeNodeReceiver.config.backendServerUrl + request.path

        # Make the request to the backend server
        response = requests.request(request.method, full_url, data=data, verify="cert.pem")

        # return a clone of the response
        return Response(response.content, status=response.status_code, headers=dict(response.headers), content_type=response.headers['content-type'])

    # Start the Flask app
    def run(self):
        app.run(host=self.host, port=self.port, ssl_context=('cert.pem', 'key.pem'), threaded=False, debug=True)

    # Path for handling logins from a web browser
    @app.route('/login', methods=['GET'])
    def login():
        return redirect(url_for('renderLoginPage'))
        
    # Handle logins from a web browser
    # Any one has access to the login page so no trust data is needed
    @app.route('/verification/loginPage', methods=['GET'])
    def renderLoginPage():
        return render_template('loginPage.html')

    # Add a new route for handling the login form submission
    @app.route('/verification/loginSubmit', methods=['POST'])
    def handleLoginSubmit():
        try:
            # Extract login credentials from the form
            username = request.form.get('username')
            password = request.form.get('password')

            # TODO get the remaining trust data from the request

            # Create trust data with login credentials
            trust_data = {
                "user": username,
                "password": password,
                "requestType": "login"
            }

            # Send login request to the trust engine
            sessionKey, trust = EdgeNodeReceiver.getPEPLoginDecision(trust_data)
            if not trust:
                raise LowClientTrust("Trust Engine Denied Access")

            # Set the session information
            response = make_response(redirect(url_for('successPage')))
            session.update({'sessionKey': sessionKey})
            return response

        except MissingTrustData as e:
            print(e)
            return jsonify({"error": f"{e}"}), 500
        except LowClientTrust as e:
            print(e)
            return redirect(url_for('renderLoginPage'))

        
    # Add a new route for the success page
    # this just returns the page of the resource that was initially requested
    @app.route('/verification/success', methods=['GET'])
    def successPage():
        # Retrieve the session information from the cookie
        sessionKey = session.get('sessionKey')

        # If there is no session or request path return an error
        if not sessionKey:
            return jsonify({"error": "Missing Session"}), 500
        
        # redirect to the root
        return redirect(url_for('receive_request'))

# Entry point
if __name__ == "__main__":
    edge_node = EdgeNodeReceiver(host='0.0.0.0', port=5005)
    edge_node.run()