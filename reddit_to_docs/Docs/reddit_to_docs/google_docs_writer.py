import os
import sys
from editor_contextual import edit_comment  # Your profanity/grammar edit module

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Replace this with your actual Reddit fetching function
def fetch_comments_dummy():
    # This should return a list of comment strings from the Reddit thread
    # For demo, some dummy comments
    return [
        "This is a sample original comment.",
        "Fuck this is bad.",
        "Thank you for me",
        "I saw 1000 people yesterday.",
        "Another clean comment."
    ]

def flatten_comments(comments):
    flat = []
    for c in comments:
        if isinstance(c, list):
            flat.extend(flatten_comments(c))
        else:
            flat.append(c)
    return flat

def create_google_docs_service():
    SCOPES = ['https://www.googleapis.com/auth/documents']
    SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'  # <-- Update with your file path

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"ERROR: Service account file '{SERVICE_ACCOUNT_FILE}' not found.")
        sys.exit(1)

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('docs', 'v1', credentials=credentials)
    return service

def create_document(service, title):
    body = {'title': title}
    doc = service.documents().create(body=body).execute()
    return doc['documentId']

def write_text_to_document(service, document_id, text):
    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': text
            }
        }
    ]
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

def main():
    reddit_url = input("Enter Reddit URL: ").strip()
    print("Fetching comments...")
    # Replace fetch_comments_dummy() with your real reddit_fetch function
    comments = fetch_comments_dummy()

    # Flatten nested comments if any
    comments = flatten_comments(comments)

    # Filter empty/non-string comments safely
    original_texts = [c.strip() for c in comments if isinstance(c, str) and c.strip()]
    print(f"Fetched {len(original_texts)} comments.")

    # Edit comments
    edited_texts = [edit_comment(c) for c in original_texts]

    # Prepare content blocks for Google Doc
    original_block = "Original Comments:\n\n" + "\n\n---\n\n".join(original_texts)
    edited_block = "Edited Comments:\n\n" + "\n\n---\n\n".join(edited_texts)

    combined_text = f"{original_block}\n\n\n{'='*40}\n\n\n{edited_block}"

    print("Connecting to Google Docs API...")
    service = create_google_docs_service()

    doc_title = "Reddit Comments - Original & Edited"
    print("Creating Google Document...")
    document_id = create_document(service, doc_title)

    print("Writing comments to Google Document...")
    write_text_to_document(service, document_id, combined_text)

    print(f"Google Doc created successfully! Open it here:\nhttps://docs.google.com/document/d/{document_id}/edit")

if __name__ == "__main__":
    main()
