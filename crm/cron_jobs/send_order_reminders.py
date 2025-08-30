#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    filename="/tmp/order_reminders_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# GraphQL client
transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# GraphQL query
query = gql("""
    query GetPendingOrders($date: DateTime!) {
        orders(orderDate_Gte: $date) {
            id
            customer {
                email
            }
        }
    }
""")

# Calculate orders within the last 7 days
date_threshold = datetime.now() - timedelta(days=7)

try:
    # Execute the query
    result = client.execute(query, variable_values={"date": date_threshold.isoformat()})
    
    # Log order's ID and customer email
    for order in result["orders"]:
        logging.info(f"Order ID: {order['id']}, Customer Email: {order['customer']['email']}")
    
    # ompletion message
    print("Order reminders processed!")

except Exception as e:
    # Log errors
    logging.error(f"Error processing order reminders: {str(e)}")
    print(f"Error occurred: {str(e)}")