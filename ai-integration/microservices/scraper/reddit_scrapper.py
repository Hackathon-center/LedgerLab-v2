import praw
import os
from datetime import datetime, timedelta, timezone
import pandas as pd
from dotenv import load_dotenv
import time
import schedule

# Load environment variables & reddit variables
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent="MyMemesScraper:v1.0 (by /u/Careful-Extension996)"
)

# Subreddit: /memes
subreddit_name = "memes"

# Fetch posts from subreddit "/memes" from last n days
def fetch_posts(days=7):
    time_frame = datetime.now(timezone.utc) - timedelta(days=days)
    posts = []

    for submission in reddit.subreddit(subreddit_name).new(limit=None):
        if submission.created_utc < time_frame.timestamp():
            break

        post = {
            'title': submission.title,
            'ups': submission.ups,
            'num_comments': submission.num_comments,
            'url': submission.url,
            'created_utc': datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
            'permalink': f"https://www.reddit.com{submission.permalink}"
        }
        posts.append(post)

        # Check rate limit every 10 posts
        if len(posts) % 10 == 0:
            print(f"Rate Limit Remaining: {reddit.auth.limits['remaining']}")
            print(f"Rate Limit Used: {reddit.auth.limits['used']}")
            print(f"Rate Limit Reset Time: {datetime.fromtimestamp(reddit.auth.limits['reset_timestamp'])}")

    return posts

# Update the dataset with new data
def update_dataset():
    posts = fetch_posts()
    df = pd.DataFrame(posts)

    # Save to CSV
    df.to_csv('memes_posts.csv', index=False)
    print(f"Updated dataset with {len(posts)} posts at {datetime.now(timezone.utc)}")

# Schedule the dataset update to run daily
schedule.every().day.at("00:00").do(update_dataset)

update_dataset()

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)