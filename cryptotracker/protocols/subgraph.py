import os
import requests

API_KEY_THE_GRAPH = os.environ["API_KEY_THE_GRAPH"]


def send_graphql_query(id: str, query: str, variables=None) -> dict:

    url = f"https://gateway.thegraph.com/api/subgraphs/id/{id}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY_THE_GRAPH}",
    }
    payload = {
        "query": query,
    }
    if variables:
        payload["variables"] = variables

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e} - Status Code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Error connecting to the API.")
    except requests.exceptions.Timeout:
        print("The request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None
