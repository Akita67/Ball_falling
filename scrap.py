import os
import requests
import re
from TikTokApi import TikTokApi

# --- Configuration ---
# The folder where profile pictures will be saved.
SKINS_FOLDER = "skins"
# How many followers you want to attempt to download.
MAX_FOLLOWERS_TO_FETCH = 10


def sanitize_filename(username):
    """
    Removes characters from a username that are not allowed in filenames.
    """
    return re.sub(r'[\\/*?:"<>|]', "", username)


def download_profile_pictures(username):
    """
    Downloads the profile pictures of a given TikTok user's followers.
    """
    print(f"Attempting to fetch followers for: {username}")

    # Create the 'skins' directory if it doesn't exist
    if not os.path.exists(SKINS_FOLDER):
        print(f"Creating directory: {SKINS_FOLDER}")
        os.makedirs(SKINS_FOLDER)

    downloaded_count = 0

    try:
        # Initialize the API directly without a 'with' statement.
        api = TikTokApi()

        # Get the user object from the username
        user = api.user(username)

        print(f"Found user: {user.username} ({user.nickname})")
        print(f"They have {user.stats.follower_count} followers.")
        print("-" * 30)

        # The .followers() method is a generator that yields user data.
        for i, follower in enumerate(user.followers(count=MAX_FOLLOWERS_TO_FETCH)):
            follower_username = follower.username
            image_url = follower.avatar_larger

            filename = sanitize_filename(follower_username) + ".jpg"
            filepath = os.path.join(SKINS_FOLDER, filename)

            if os.path.exists(filepath):
                print(f"({i + 1}) Skipping {follower_username} (already downloaded).")
                continue

            print(f"({i + 1}) Downloading profile for {follower_username}...")

            try:
                response = requests.get(image_url, stream=True)
                response.raise_for_status()

                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded_count += 1

            except requests.exceptions.RequestException as e:
                print(f"    - Could not download image for {follower_username}: {e}")
            except Exception as e:
                print(f"    - An error occurred while saving the file for {follower_username}: {e}")

    except Exception as e:
        print("\n" + "=" * 30)
        print("An error occurred. This can happen for several reasons:")
        print(f"Error details: {e}")
        print("- The user may not exist or is private.")
        print("- You might need to solve a CAPTCHA in the browser window that opens.")
        print("- TikTok may have temporarily blocked requests. Try again later.")
        print("=" * 30 + "\n")

    print("\n" + "-" * 30)
    print("Process finished.")
    print(f"Successfully downloaded {downloaded_count} new profile pictures.")
    print(f"Files are saved in the '{SKINS_FOLDER}' folder.")


if __name__ == "__main__":
    target_username = "okslollo"
    if target_username:
        download_profile_pictures(target_username)
    else:
        print("No username entered. Exiting.")

