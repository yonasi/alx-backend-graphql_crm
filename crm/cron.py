import logging
from datetime import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


# Configure logging
logging.basicConfig(
    filename="/tmp/crm_heartbeat_log.txt",
    level=logging.INFO,
    format="%(message)s",
    filemode="a",  # Append mode
)

def log_crm_heartbeat():
    # Format timestamp as DD/MM/YYYY-HH:MM:SS
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Log heartbeat message
    logging.info(f"{timestamp} CRM is alive")
    
    # Query GraphQL hello field
    try:
        transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("""
            query {
                hello
            }
        """)
        result = client.execute(query)
        logging.info(f"{timestamp} GraphQL hello response: {result['hello']}")
    except Exception as e:
        logging.error(f"{timestamp} GraphQL query failed: {str(e)}")



# Configure logging
logging.basicConfig(
    filename="/tmp/low_stock_updates_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def update_low_stock():
    # Set up GraphQL client
    transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Define GraphQL mutation
    mutation = gql("""
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    name
                    stock
                }
                message
            }
        }
    """)
    
    try:
        # Execute the mutation
        result = client.execute(mutation)
        updated_products = result["updateLowStockProducts"]["updatedProducts"]
        message = result["updateLowStockProducts"]["message"]
        
        # Log updated products
        for product in updated_products:
            logging.info(f"Updated product: {product['name']}, New stock: {product['stock']}")
        
        # Log success message
        logging.info(message)
        
    except Exception as e:
        # Log any errors
        logging.error(f"Error updating low stock: {str(e)}")