# reddit_scraper.py

import praw
from config import *

# Step 1: Instantiate Reddit API client
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)
print("🔐 Authenticated as read-only. Ready to scrape.")
def extract_comments(comment_list, depth=0):
    comments = []
    for comment in comment_list:
        try:
            if hasattr(comment, "body"):  # Skip MoreComments or deleted ones
                comments.append({
                    "body": comment.body,
                    "depth": depth
                })
                # Recursive call for nested replies
                nested_replies = extract_comments(comment.replies, depth + 1)
                comments.extend(nested_replies)
        except Exception as e:
            print(f"Error while processing comment: {e}")
            continue
    return comments


def fetch_post_data(url):
    submission = reddit.submission(url=url)
    submission.comments.replace_more(limit=0)

    post_data = {
        "title": submission.title,
        "selftext": submission.selftext,
        "comments": extract_comments(submission.comments)
    }
    return post_data


def parse_comment(comment, depth=0):
    return {
        "author": str(comment.author),
        "body": comment.body,
        "depth": depth,
        "replies": [parse_comment(reply, depth + 1) for reply in comment.replies]
    }
