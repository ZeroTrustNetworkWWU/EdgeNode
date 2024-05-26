# EdgeNode

## Description:
The Edge Node provides a secure entry point into the Zero Trust Network. It acts as a reverse proxy that forwards requests to the appropriate backend server once the Trust Engine has verified the request. This README provides an overview of the project structure and how to navigate through its components.

## Prerequisites:
- Python 3.10 or higher
- Git (for cloning the repository)
- Windows or Linux OS

## Installation
Clone the repository by running the following command:
```bash
git clone https://github.com/ZeroTrustNetworkWWU/EdgeNode
```

To run the EdgeNode server, you can do so by running the following command:
```bash
./start.bat
```

Or if your on a linux system:
```bash
./start.sh
```

## Structure:

The project is structured as follows:
- `EdgeNode.py`: Contains the main code for the EdgeNode server. This server is responsible for handling requests from the client and forwarding them to the appropriate backend server.
- `EdgeNodeExceptions.py`: Contains custom exceptions that are raised by the EdgeNode server. These exceptions are used to handle errors that occur during the request processing.
- `EdgeNodeConfig.py`: Contains the configuration settings for the EdgeNode server. These settings include the IP address and port number of the backend server, as well as the IP address and port number of the Trust Engine server.
- `IPReputationChecker.py`: Contains a simple interface for sending requests to a third-party IP reputation service. This service is used to determine the reputation of the client IP address.
- `templates/`: Contains the HTML templates that are used to render the login page

# HTTP Request Flow

## Processing a Generic Request

1. The client sends an HTTP request to the EdgeNode server.
2. If the request is JSON, the EdgeNode extracts the `_trustData` key. If the request is not JSON, the session cookie is checked for the sessionKey.
3. The EdgeNode sends the trust data and info about the request to the Trust Engine.
4. The Trust Engine processes the trust data and returns a decision to the EdgeNode.
5. If the Trust Engine approves the request, the EdgeNode forwards the request to the backend server.
6. The backend server processes the request and sends a response back to the EdgeNode.
7. The EdgeNode forwards the response back to the client.

## Processing a Login Request from HTTP

1. The client sends a login request to the EdgeNode server.
2. The EdgeNode extracts the username and password from the request.
3. The EdgeNode sends the username and password to the Trust Engine.
4. The Trust Engine processes the username and password and returns a session key to the EdgeNode if the login is successful.
5. The EdgeNode returns the session key to the client.
6. The client stores the session key in a cookie and uses it to authenticate future requests.

## Processing a Login Request from a Web Browser

1. The client sends a web request pre-login.
2. The EdgeNode detects that the client is not logged in and redirects the client to the login page.
3. The client enters their username and password and submits the login form.
4. The EdgeNode processes the login request as described above, except the session key is stored in a cookie.
5. The EdgeNode redirects the client back to the base URL after a successful login.

# Important Security Improvements to be Made

- The EdgeNode should use HTTPS to encrypt the communication between the client and the server.
- The EdgeNode should store the session key in a secure session cookie or another secure storage mechanism, instead of the current method of storing it in a plaintext cookie.
- Web browser requests should have more trust data taken from them, as it is currently only taking the session key from the cookie. This is a security risk as the session key is not enough to determine the trust level of the client.

