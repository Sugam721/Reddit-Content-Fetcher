import praw
from reddit_config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from editor_contextual import edit_comment

def save_comments_to_md(filename, title, comments):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        for i, comment in enumerate(comments, 1):
            f.write(f"## Story {i}\n\n{comment}\n\n")


def get_submission_title(post_url):
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        submission = reddit.submission(url=post_url)
        return submission.title
    except Exception as e:
        print(f"[ERROR] Fetching thread title failed: {e}")
        return "Reddit Thread"


def get_top_comments(post_url, min_words=50, total_words_target=11000):
    comments_raw = []
    comments_edited = []
    total_words = 0

    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        submission = reddit.submission(url=post_url)
        submission.comment_sort = "best"
        submission.comments.replace_more(limit=0)

        for comment in submission.comments:
            if comment.body in ["[deleted]", "[removed]"]:
                continue

            word_count = len(comment.body.split())
            if word_count >= min_words:
                raw = comment.body.strip()
                bolded_orig, edited = edit_comment(raw)

                if edited.strip():
                    comments_raw.append(bolded_orig)
                    comments_edited.append(edited)
                    total_words += word_count

            if total_words >= total_words_target:
                break

    except Exception as e:
        print(f"[ERROR] Fetching comments failed: {e}")

    return comments_raw, comments_edited


def format_comments_for_doc(comments):
    formatted = []
    for i, comment in enumerate(comments, 1):
        formatted.append(f"Story {i}\n\n{comment}\n")
    return "\n".join(formatted)


if __name__ == "__main__":
    url = input("Enter Reddit post URL: ").strip()
    title = get_submission_title(url)
    raw_comments, edited_comments = get_top_comments(url)

    print(f"\n--- Thread Title: {title} ---\n")
    print("--- ORIGINAL COMMENTS ---\n")
    print(format_comments_for_doc(raw_comments))

    print("\n--- EDITED COMMENTS ---\n")
    print(format_comments_for_doc(edited_comments))

    save_comments_to_md("bolded_original_comments.md", title, raw_comments)
    save_comments_to_md("edited_comments.md", title, edited_comments)

    print("\n[Saved bolded original comments to 'bolded_original_comments.md']")
    print("[Saved edited comments to 'edited_comments.md']")
