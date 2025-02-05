# Telegram Group Activity Analyzer

## Overview

This project provides a Python-based tool for analyzing the activity within a Telegram group.  It leverages the Telethon library to interact with the Telegram API, retrieves user data and recent messages, and then performs a series of analyses to provide insights into group dynamics, user engagement, and potential spam activity. The results are presented through both console output and interactive visualizations using `matplotlib` and `seaborn`.

## Features

*   **Data Acquisition:**
    *   Connects to the Telegram API using your provided credentials (`API_ID`, `API_HASH`).
    *   Fetches a comprehensive list of group participants.
    *   Retrieves a specified number of recent messages (currently set to 2000) from the target group.  This limit is configurable.
    *   Handles edge cases, such as messages without sender IDs, to prevent errors.

*   **User Activity Metrics:**
    *   **Message Count:** Tracks the number of messages sent by each user.
    *   **Character Count:** Calculates the total number of characters sent by each user.
    *   **Media Count:** Counts the number of media files (images, videos, etc.) sent by each user.
    *   **Link Count:** Determines the number of URLs shared by each user.
    *   **Reaction Count:**  Counts the number of reactions received by each user's messages (requires that reactions are enabled in the group).
    *   **Timestamps:** Records the timestamps of all messages from each user.

*   **Engagement Analysis:**
    *   **Average Message Length:** Calculates the average length of messages (in characters) for each user. This can provide insights into communication styles.
    *   **Activity Rate:**  Measures the frequency of messages sent by a user over a given period.  This helps identify users who are consistently active versus those who post sporadically. It's calculated as the number of messages divided by the time difference (in hours) between the user's first and last message (with a minimum of 1 hour to avoid division by zero).

*   **Spam Detection:**
    *   Implements a custom `spam_score` algorithm. This algorithm is a weighted combination of several factors:
        *   **Message Count (40% weight):**  A high message count can be an indicator of spam, but it's balanced by other factors.
        *   **Average Message Length (30% weight):**  Very short messages are often associated with spam.  The algorithm uses `(1 - df['avg_length']/100)`, so lower average lengths result in higher spam scores. The `/100` acts as a scaling factor; you might want to adjust this based on typical message lengths in your target group.
        *   **Media Proportion (20% weight):**  Spammers often send text-only messages. The algorithm uses `(1 - df['media']/df['messages'].clip(lower=1))`. The `.clip(lower=1)` prevents division by zero if a user has sent no messages.  A lower proportion of media contributes to a higher spam score.
        *   **Link Count (10% weight):**  A large number of links, especially if combined with other factors, can indicate spam.

*   **Data Visualization:**
    *   **Top Active Users:**  Generates a bar chart showing the top 10 users with the highest message counts.  The usernames are displayed alongside the bars.
    *   **Spam Score Distribution:**  Creates a scatter plot that visualizes the relationship between message count, spam score, average message length (represented by point size), and media count (represented by color). This helps identify potential outliers and patterns in spam-like behavior.
    *   **Hourly Activity Pattern:**  Produces a histogram showing the distribution of messages across different hours of the day. This reveals peak activity times for the group.
    *   **Content Type Distribution:**  Displays a stacked bar chart summarizing the total number of media files and links shared in the group.

*   **Data Output:**
    *   Prints a table to the console showing the top 10 users based on their `spam_score`, along with their username, message count, `spam_score`, media count, and link count. This allows for quick identification of potential spammers.
    *   Uses `pandas` DataFrames for efficient data handling and analysis.

## Setup and Configuration

1.  **Prerequisites:**
    *   **Python 3.7+:** This project is written in Python and requires a compatible version.
    *   **Telegram Account:** You need a Telegram account to use the Telegram API.
    *   **API Credentials:** You must obtain an `API_ID` and `API_HASH` from Telegram.  Follow the instructions here: [https://core.telegram.org/api/obtaining_api_id](https://core.telegram.org/api/obtaining_api_id)
    * **Install the required libraries:**
        ```bash
        pip install telethon pandas matplotlib seaborn
        ```
        Alternatively, if you have a `requirements.txt` file, you can use:
        ```bash
        pip install -r requirements.txt
        ```
2.  **Configuration (`config.py`):**
    *   Create a file named `config.py` in the same directory as your script.
    *   **Important:**  *Do not* commit `config.py` to your public GitHub repository, as it contains sensitive credentials. Add `config.py` to your `.gitignore` file.
    *   Add the following variables to `config.py`, replacing the placeholders with your actual values:

        ```python
        API_ID = 1234567  # Your API ID (integer)
        API_HASH = 'your_api_hash'  # Your API hash (string)
        GROUP_USERNAME = '@your_group_username'  # The username of the target group (including the @)
        SESSION_NAME = 'group_analyzer'  # A name for your Telethon session file
        ```

## Usage

1.  After setting up the prerequisites and configuring `config.py`, run the script:

    ```bash
    python main.py
    ```

2.  The script will connect to Telegram, fetch the data, perform the analysis, display the visualizations, and print the results to the console.

## Code Structure

*   **`config.py`:**  Holds configuration settings and API credentials.  *This file should be kept private.*
*   **`main.py`:** Contains the main logic of the project.
    *   **`fetch_group_data()`:** An asynchronous function that uses Telethon to connect to the Telegram API, retrieve group participants and messages, and calculate basic user activity metrics. It returns a dictionary containing user activity data.
    *   **`analyze_activity()`:**  Takes the user activity dictionary, converts it into a pandas DataFrame, calculates engagement metrics (average message length, activity rate), and computes the `spam_score`.  It returns the DataFrame, sorted by `spam_score` in descending order.
    *   **`visualize_results()`:**  Generates the four visualizations (top users, spam distribution, hourly activity, content type) using `matplotlib` and `seaborn`.
    *   **`main()`:** The main asynchronous function that calls the other functions in sequence: fetches data, analyzes it, visualizes the results, and prints a summary table.
    *   **`if __name__ == '__main__':` block:**  Ensures that the `main()` function is executed only when the script is run directly (not imported as a module).  It uses `asyncio.run()` to run the asynchronous `main()` function.

## Important Considerations

*   **API Rate Limits:**  Be mindful of Telegram's API rate limits.  Fetching large amounts of data too quickly can result in your application being temporarily blocked.  If you encounter issues, consider adding delays or using a more sophisticated rate-limiting strategy.
*   **Error Handling:**  The provided code includes basic error handling (checking for `msg.sender_id`), but you should add more robust error handling to handle potential network issues, API errors, and unexpected data formats.
*   **Spam Algorithm Tuning:**  The `spam_score` algorithm is a heuristic and may need to be adjusted based on the specific characteristics of your target group.  Experiment with different weights and factors to improve its accuracy. Consider adding more features, such as checking for repeated messages, similar messages, or known spam patterns.
*   **Privacy:**  Be respectful of user privacy.  If you plan to share or publish your analysis, consider anonymizing user data appropriately.
*   **Asynchronous Programming:**  The use of `asyncio` and `async with` allows the script to handle network operations efficiently without blocking.  This is crucial for interacting with the Telegram API.
* **Comments and Docstrings**: For future edits, adding comprehensive docstrings to functions and clear comments within the code is crucial for maintainability.

## Contributing

Contributions to this project are welcome! If you have suggestions for improvements, bug fixes, or new features, please feel free to:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear, descriptive commit messages.
4.  Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE) (you should create a LICENSE file with the MIT License text). This is a permissive open-source license that allows for reuse and modification.
