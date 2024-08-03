#!/usr/bin/env python3
"""app package init"""

from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.database import Database
from app.config import Config
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler

# Initialize mail instance globally
mail = Mail()
socketio = SocketIO(cors_allowed_origins="*")
revoked_tokens = set()  # Set to store revoked JWT tokens


# Function to initialize MongoDB client
def init_mongo_client(connection_string: str) -> MongoClient:
    try:
        client = MongoClient(connection_string)
        print("MongoDB client initialized successfully.")
        return client
    except errors.ConnectionFailure as e:
        print(f"Error connecting to MongoDB: {e}")
        raise
    except errors.ConfigurationError as e:
        print(f"Configuration error: {e}")
        raise


# Create a function to initialize collections
def initialize_collections(client: MongoClient, db_name: str):
    database: Database = client.get_database(db_name)
    tenantsCollection: Collection = database.get_collection("tenants")
    adminMessagesCollection: Collection = database.get_collection(
        "adminMessages"
    )
    propertiesCollection: Collection = database.get_collection("properties")
    listingCollection: Collection = database.get_collection("listing")
    logRequestsCollection: Collection = database.get_collection("logRequests")
    adminsCollection: Collection = database.get_collection("admins")
    messagesCollection: Collection = database.get_collection("messages")
    return (
        tenantsCollection, adminMessagesCollection, propertiesCollection,
        listingCollection, logRequestsCollection, adminsCollection,
        messagesCollection
    )

# configuration logging before app creation, for stream handler and file handler
logger = logging.getLogger()
formatter = logging.Formatter(
    '[%(asctime)s] - %(levelname)s - %(module)s: %(message)s'
)
logger.setLevel(logging.INFO)

# add stream handler to the root logger
streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.INFO)
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# add file handler to the root logger
fileHandler = RotatingFileHandler('habitatT.log', backupCount=100, maxBytes=1024)
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


def create_app(config_name='default'):
    """return flask application"""
    app = Flask(__name__)

    # Load configuration from app.config
    if config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object(Config)

    mail.init_app(app)
    jwt = JWTManager(app)
    socketio.init_app(app)

    # Enable CORS for all domains on all routes
    CORS(
        app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}},
        methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"]
    )

    # JWT blocklist loader function
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in revoked_tokens

    # Mongo client initialization
    CONNECTION_STRING = Config.MONGO_URI
    DB_NAME = app.config['MONGO_DB_NAME']

    try:
        mongo_client: MongoClient = init_mongo_client(CONNECTION_STRING)
        (tenantsCollection, adminMessagesCollection, propertiesCollection,
            listingCollection, logRequestsCollection, adminsCollection,
            messagesCollection) = initialize_collections(mongo_client, DB_NAME)
    except (errors.ConnectionFailure, errors.ConfigurationError) as e:
        mongo_client = None
        tenantsCollection = None
        adminMessagesCollection = None
        propertiesCollection = None
        listingCollection = None
        logRequestsCollection = None
        adminsCollection = None
        messagesCollection = None
        print(f"Database initialization failed: {e}")

    # Store collections in the app context
    app.tenantsCollection = tenantsCollection
    app.adminMessagesCollection = adminMessagesCollection
    app.propertiesCollection = propertiesCollection
    app.listingCollection = listingCollection
    app.logRequestsCollection = logRequestsCollection
    app.adminsCollection = adminsCollection
    app.messagesCollection = messagesCollection

    with app.app_context():
        # Import routes here to avoid circular imports
        from app.routes import bp

        # Register blueprints
        app.register_blueprint(bp)

    return app
