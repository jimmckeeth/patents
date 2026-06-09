# Google Cloud Service Account Setup Guide

This guide walks you through setting up a Google Cloud Platform (GCP) Service Account and configuring your local environment to run the patent citation query tool.

---

## 🔑 Step 1: Access the GCP Console
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your Google Account.
3. At the top left (next to the menu icon), select your existing Project or click **New Project** to create one.

---

## ⚡ Step 2: Enable the BigQuery API
1. In the console search bar at the top, type **BigQuery API**.
2. Select **BigQuery API** under Marketplace/Services.
3. Click the **Enable** button (if it isn't enabled already).

---

## 👤 Step 3: Create a Service Account
1. In the search bar at the top, type **Service Accounts** and select the IAM/Service Accounts section.
2. Click **➕ Create Service Account** at the top.
3. Enter a name (e.g., `patent-citation-analyzer`).
4. Click **Create and Continue**.

---

## 🛡️ Step 4: Grant Project Permissions
You must assign two specific roles to this service account so it can submit queries and read the public patent dataset:

1. Click **Select a role** and choose:
   * **BigQuery** ➔ **BigQuery Data Viewer** (to read datasets).
2. Click **➕ Add Another Role**.
3. Select the second role:
   * **BigQuery** ➔ **BigQuery Job User** (to execute query jobs).
4. Click **Continue**, then click **Done**.

---

## 🗝️ Step 5: Generate the JSON Key
1. Find your newly created service account in the Service Accounts list.
2. Under the **Actions** column (three vertical dots), click **Manage keys** (or click the email link and select the **Keys** tab).
3. Click **Add Key** ➔ **Create new key**.
4. Select **JSON** as the key type.
5. Click **Create**. A `.json` file will automatically download to your computer.

---

## ⚙️ Step 6: Configure your Project
To link your downloaded credentials to the local analyzer tool, choose one of these methods:

### Method A: Replace the placeholder file (Recommended)
1. Rename downloaded `.json` credentials file `service-account-key.json`
4. Set the environment variable to point to this file:
   * **Windows (PowerShell)**:
     
     ```powershell
     $env:GOOGLE_APPLICATION_CREDENTIALS="$HOME\service-account-key.json"
     ```
   * **Linux/macOS (Bash/Zsh)**:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="$HOME/service-account-key.json"
     ```

### Method B: Reference the downloaded file directly
Set the environment variable pointing directly to the download path:
* **Windows (PowerShell)**:
  ```powershell
  $env:GOOGLE_APPLICATION_CREDENTIALS="$HOME\downloads\your-downloaded-key.json"
  ```
* **Linux/macOS (Bash/Zsh)**:
  
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="$HOME/downloads/your-downloaded-key.json"
  ```
  
  
