from celery import shared_task
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import logging
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    filename="/tmp/crm_report_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

@shared_task
def generate_crm_report():  
    # Set up GraphQL client
    transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # Define GraphQL query
    query = gql("""
        query {
            customers {
                totalCount
            }
            orders {
                totalCount
                edges {
                    node {
                        totalamount
                    }
                }
            }
        }
    """)
    
    try:
        # Execute the query
        result = client.execute(query)
        
        # Extract data
        total_customers = result["customers"]["totalCount"]
        total_orders = result["orders"]["totalCount"]
        total_revenue = sum(edge["node"]["totalamount"] for edge in result["orders"]["edges"])
        
        # Log the report
        report = f"Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"
        logging.info(report)
        
    except Exception as e:
        # Log any errors
        logging.error(f"Error generating CRM report: {str(e)}")
        raise  # Allow Celery to retry if configured