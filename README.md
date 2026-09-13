# WhatsApp CRM + Automation System 📱

A professional, production-ready WhatsApp CRM and Automation tool built with **FastAPI**, **SQLite**, and the **Meta WhatsApp Business API**. This system allows businesses to manage customer interactions, automate replies, and send bulk broadcasts seamlessly.

## 🚀 Key Features

*   **Premium Web Dashboard**: A modern, responsive interface similar to WhatsApp Web.
*   **Contact Management**:
    *   **Bulk CSV Import**: Import thousands of contacts with tags in seconds.
    *   **Manual Add**: Quick '+' button to add individual contacts.
    *   **Contact Deletion**: Easy trash icon to manage your database.
    *   **Dynamic Tagging**: Categorize users (e.g., Lead, Customer, VIP).
*   **Broadcasting & Marketing**:
    *   **Bulk Broadcast**: Send templates to multiple contacts at once.
    *   **Tag Filtering**: Filter broadcast recipients based on tags.
*   **Automation Engine**:
    *   **Keyword Rules**: Set automatic replies for specific keywords (e.g., 'Price', 'Offer').
    *   **Robot Interface**: Manage your automation rules directly from the dashboard.
*   **Media Support**:
    *   Send **Images** and **PDF Documents** directly through the chat using URLs.
*   **Analytics Dashboard**:
    *   Real-time stats on total contacts, message volume, and inbound/outbound ratio.
*   **Message Templates**:
    *   Support for approved Meta templates with dynamic variable injection.

## 🛠️ Setup & Installation

### 1. Requirements
*   Python 3.9+
*   Meta Developer Account (WhatsApp Business API access)

### 2. Quick Start (Windows)
1.  Clone the repository and install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configure your credentials in the `.env` file (see [Configuration](#configuration) below).
3.  Double-click **`run.bat`** to start the server and open the dashboard.

### 3. Configuration
Edit your `.env` file with the following variables:
*   `WHATSAPP_TOKEN`: Your Meta Access Token.
*   `PHONE_NUMBER_ID`: Your WhatsApp Business Phone Number ID.
*   `VERIFY_TOKEN`: Your custom secret for Webhook verification.

### 4. Webhook Integration
To receive messages in real-time:
1.  Use a tool like **Ngrok** to expose your local port 8000: `ngrok http 8000`.
2.  In the Meta Developer Portal, set your Webhook URL to: `https://<your-ngrok-id>.ngrok-free.app/webhook/`.
3.  Set the **Verify Token** to match your `.env`.
4.  Subscribe to the `messages` field.

## 📂 Project Structure
*   `app/api/`: API Routes for contacts, templates, automation, and analytics.
*   `app/services/`: Core logic for WhatsApp API integration and CRM functions.
*   `app/db/`: Database models and SQLite initialization.
*   `app/static/`: Frontend dashboard (HTML, CSS, JS).
*   `whatsapp_crm.db`: Local SQLite database.

## 👨‍💻 Developer & Credits

* **Developer:** Haresh Kumar Hemani
* **Website:** [www.taxonline24.in](https://www.taxonline24.in)
* **Email:** [contact@taxonline24.in](mailto:contact@taxonline24.in)

## 📄 License
This project is designed for professional enterprise use. All data is stored locally in your SQLite database for maximum privacy.

