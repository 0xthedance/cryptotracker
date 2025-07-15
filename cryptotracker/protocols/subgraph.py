import os

import requests

import logging

THE_GRAPH_API_KEY = os.environ.get("THE_GRAPH_API_KEY")


def send_graphql_query(id: str, query: str, variables=None) -> dict:
    """
    Sends a GraphQL query to The Graph API and returns the response as a dictionary.
    """
    url = f"https://gateway.thegraph.com/api/subgraphs/id/{id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {THE_GRAPH_API_KEY}",
    }
    payload = {
        "query": query,
    }
    if variables:
        payload["variables"] = variables

    try:
        logging.debug(f"Sending GraphQL query to {url} with payload: {payload}")
        response = requests.post(url, headers=headers, json=payload)
        logging.debug(f"Received response: {response.json()}")
        response.raise_for_status()
        if "errors" in response.json():
            logging.error(f"GraphQL errors: {response.json()['errors']}")
            return {}
        return response.json()

    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e} - Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logging.error("Error connecting to the API.")
    except requests.exceptions.Timeout:
        logging.error("The request timed out.")
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    # Return an empty dictionary in case of an error
    return {}
