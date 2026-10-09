# 🔗 Rclone Configuration with Google Drive (Custom Client ID)

Using a custom Client ID is strongly recommended for Google Drive integrations, as it prevents "Rate Limit Exceeded" errors and token revocation caused by sharing Rclone's default public API quota with the global user community.

## Step 1: Create a Project in Google Cloud

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) signed in with the Google account you wish to synchronize.
2. In the top-left corner (next to the Google Cloud logo), click the project dropdown menu and select **New Project**.
3. Enter a project name (e.g., `SyncEngine-Rclone`) and click **Create**.
4. Wait for the completion notification and ensure the newly created project is selected in the top menu.

## Step 2: Enable the Google Drive API

1. In the left navigation menu, go to **APIs & Services** > **Library**.
2. In the search bar, search for `Google Drive API`.
3. Click the matching result, then click the blue **Enable** button.

## Step 3: Configure the OAuth Consent Screen (Updated Interface)

Standard personal `@gmail.com` accounts cannot create "Internal" apps (which are restricted to Google Workspace organizations). You must create an "External" application and fill in basic details to allow publication.

1. In the left menu, navigate to **APIs & Services** > **OAuth consent screen**.
2. Under "User Type", select **External** and click **Create**.
3. Under **App Information** / **Branding**:
   * **App name:** `SyncEngine` (or another name of your preference).
   * **User support email:** Select your email address from the dropdown menu.
   * **App home page:** `https://rclone.org`
   * **Privacy Policy link:** `https://rclone.org`
   * **Authorized domains:** Click "Add domain" and type `rclone.org`.
   * **Developer contact information:** Enter your email address again.
4. Click **Save and Continue** through the subsequent screens (Scopes and Test Users) without making any changes.

## Step 4: Publish the Application (Crucial)

*Note: Skipping this step will cause Google to revoke Rclone's authorization token every 7 days.*

1. In the left navigation menu, click the **Audience** (or Publishing status) tab.
2. Your app status will show as "Testing". Click the **Publish App** button (or *Move to Production*).
3. Google will display a warning stating that the app requires verification. **Ignore the warning and confirm.** Because the application is strictly for your private personal use through Rclone, official Google verification is not required.

## Step 5: Generate Credentials (Client ID and Secret)

1. In the left menu, navigate to **Credentials**.
2. Click **+ CREATE CREDENTIALS** at the top of the page and select **OAuth client ID**.
3. Under "Application type", select **Desktop app**.
4. Enter an identifier name (e.g., `Rclone Desktop`) and click **Create**.
5. A modal will appear displaying your **Client ID** and **Client Secret**. Keep this window open or copy the keys securely.

## Step 6: Link Credentials to Rclone

Open your terminal (as a standard user, without `sudo` or administrator privileges) and start Rclone's setup wizard:

```bash
rclone config
```

Respond to the interactive prompt with the following sequence:

1. **`n`** (New remote)
2. **Name:** `gdrive_secondary` (or any remote name of your choice)
3. **Storage:** Type `drive` (Google Drive)
4. **client_id:** Paste your *Client ID* generated in Step 5.
5. **client_secret:** Paste your *Client Secret* generated in Step 5.
6. **scope:** `1` (Full access to all files)
7. **service_account_file:** Leave blank (press Enter)
8. **Edit advanced config?** `n` (No)
9. **Use auto config?** `y` (Yes)

Rclone will automatically open your default browser to sign in to your Google account.

> **Google Security Warning:** Google will display a red "Google hasn't verified this app" warning screen. This is expected behavior (as we did not submit the app for public audit in Step 4). Click **Advanced**, then click **Go to SyncEngine (unsafe)** to approve the connection.

10. **Configure this as a Shared Drive (Team Drive)?** `n` (No)
11. Confirm the configuration summary with **`y`** (Yes this is OK), then type **`q`** to exit the configuration wizard.