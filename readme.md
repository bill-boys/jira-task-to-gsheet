# Jira Data to Google Sheets

This project retrieves Jira task data and saves it to a Google Sheet.

# Jira Data to Google Sheets

This project automates the process of retrieving Jira task data and exporting it to a Google Sheet. It is designed to help teams track and analyze Jira issues efficiently by leveraging the Google Sheets API.

## Features
- Fetch Jira issues based on specific JQL queries.
- Extract detailed information such as summary, description, assignee, comments, and creation date.
- Export the data to a Google Sheet for easy sharing and analysis.
- Supports authentication for both Jira and Google Sheets.

## Technologies Used
- **Python**: Core programming language.
- **Jira API**: To fetch issue data.
- **Google Sheets API**: To write data to Google Sheets.
- **dotenv**: For managing environment variables.
- **Requests**: For making HTTP requests.

## Use Cases
- Automate reporting of Jira issues.
- Centralize issue tracking in Google Sheets.
- Analyze project data over time.

## Prerequisites

1. Python 3.8 or higher installed.
2. A Google Cloud project with the Sheets API enabled.
3. A Jira account with API access.
4. A `.env` file with the required environment variables.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project directory with the following variables:
```
JIRA_URL=<your-jira-url>
JIRA_USERNAME=<your-jira-username>
JIRA_API_TOKEN=<your-jira-api-token>
PROJECT_KEY=<your-jira-project-key>
APPLICATION=<application-name>
SPREADSHEET_ID=<google-sheet-id>
SHEET_NAME=<sheet-name>
```

### 4. Google Authentication
Run the following command to authenticate with Google Cloud:
```bash
gcloud auth application-default login
```
This will open a browser window to log in with your Google account.

### 5. Run the Script
Execute the script to fetch Jira data and save it to Google Sheets:
```bash
python script_jira.py
```

## Notes
- Ensure your Jira account has the necessary permissions to access the project and data.
- The Google Sheets API requires proper authentication using the service account credentials.

## License
This project is licensed under the MIT License.