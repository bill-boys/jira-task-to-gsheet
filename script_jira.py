import requests
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import os

import google.auth

def extract_text_from_comment(comment_body):
    """Extracts plain text from a Jira comment body."""
    text_content = ""
    if isinstance(comment_body, dict) and 'type' in comment_body and comment_body['type'] == 'doc' and 'content' in comment_body:
        for content_item in comment_body['content']:
            if content_item['type'] == 'paragraph' and 'content' in content_item:
                for paragraph_item in content_item['content']:
                    if paragraph_item['type'] == 'text':
                        text_content += paragraph_item['text'] + " "  # Add space between text elements
    return text_content.strip()  # Remove leading/trailing spaces

def extract_text_from_description(description):
  """Extracts plain text from a Jira description field."""
  text_content = ""
  if isinstance(description, dict) and 'type' in description and description['type'] == 'doc' and 'content' in description:
    for content_item in description['content']:
      if content_item['type'] == 'paragraph' and 'content' in content_item:
        for paragraph_item in content_item['content']:
          if paragraph_item['type'] == 'text':
            text_content += paragraph_item['text'] + " "
      elif content_item['type'] == 'bulletList':
        for list_item in content_item['content']:
          for list_item_content in list_item['content']:
            text_content += extract_text_from_description(list_item_content) + " "  # Recursive call for nested lists
  return text_content.strip()

def get_jira_data(jira_url, jira_username, jira_api_token, project_key, application):
    """Retrieves Jira task data (title, assignee, category) for a given project and assignee within the last 3 months."""

    three_months_ago = datetime.now() - timedelta(days=90)  # Approximate 3 months
    formatted_date = three_months_ago.strftime('%Y-%m-%d')

    jql = f"project = '{project_key}' AND \"application[short text]\" ~ '{application}' AND created >= '{formatted_date}' ORDER BY created DESC"
    print('jql:', jql)
    url = f"{jira_url}/rest/api/3/search/jql"
    print('url:', url)

    auth = HTTPBasicAuth(jira_username, jira_api_token)
    headers = {
        "Accept": "application/json"
    }
    query = {
        'jql': jql,
        'fields': 'created,description,summary,assignee,issuetype,comment,issuelinks',
        'maxResults': 100
    }

    try:
        response = requests.get(url, headers=headers, params=query, auth=auth)
        response.raise_for_status()
        data = response.json()
        # print(data)
        issues = data.get("issues", [])

        results = []

        for issue in issues:
            title = issue["fields"]["summary"]
            description = extract_text_from_description(issue["fields"]["description"])  # Extract plain text from description
            created_at = issue["fields"]["created"]

            issue_url = 'https://jurnal.atlassian.net/jira/software/c/projects/ITG/issues/?filter=allissues&jql=textfields ~ \'' + title + "'"
            issue_url = issue_url.replace(' ', '%20')
            assignee = issue["fields"]["assignee"]["displayName"] if issue["fields"]["assignee"] else "Unassigned"
        
            comments = issue["fields"]["comment"]["comments"]  # Access the comments array
            all_comments = ''
            for comment in comments:
                # all_comments += f"{comment['author']['displayName']}: {comment['body']}\n"  # Add newline for separation
                comment_text = extract_text_from_comment(comment["body"])  # Extract plain text
                all_comments += f"{comment['author']['displayName']}: {comment_text}\n"

            results.append([title, description, assignee, all_comments, issue_url, created_at])
        return results

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Jira data: {e}")
        return []
    except KeyError as e:
        print(f"Error parsing Jira data: Missing key {e}. Check JQL and field names.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

def save_to_google_sheets(data, spreadsheet_id, sheet_name):
    """Saves data to a Google Sheet."""
    
    creds, _ = google.auth.default(scopes=[
      'https://www.googleapis.com/auth/analytics.readonly',
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/spreadsheets',
    ])
    
    try:
        service = build("sheets", "v4", credentials=creds)

        # Prepare the data including header
        values = [["title", "description", "assignee", "comment", "url", "created_at"]] + data if data else []
        
        body = {
            'values': values
        }

        # Clear the sheet first
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=sheet_name
        ).execute()

        # Write the new data
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"{result.get('updatedCells')} cells updated.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error



# Load environment variables from .env file
load_dotenv()

# Get variables from environment
jira_url = os.getenv('JIRA_URL')
jira_username = os.getenv('JIRA_USERNAME')
jira_api_token = os.getenv('JIRA_API_TOKEN')
project_key = os.getenv('PROJECT_KEY')
application = os.getenv('APPLICATION')
spreadsheet_id = os.getenv('SPREADSHEET_ID')
sheet_name = os.getenv('SHEET_NAME')

# Get Jira data and save to sheets
jira_data = get_jira_data(jira_url, jira_username, jira_api_token, project_key, application)
# print(jira_data)
save_to_google_sheets(jira_data, spreadsheet_id, sheet_name)
