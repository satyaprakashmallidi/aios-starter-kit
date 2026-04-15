# OutboundOS Configuration

> Fill in your n8n webhook URLs and personal info.
> Claude reads this file to trigger your outreach workflows.

---

## n8n Webhook URLs

Find these in your existing n8n workflows. Look for the "Webhook" trigger node — it will show you the URL.

### WhatsApp

- **Send WhatsApp Message:**
  `https://your-n8n-instance/webhook/whatsapp-send`

### Gmail

- **Send Gmail Message:**
  `https://your-n8n-instance/webhook/gmail-send`

### Bitrix24

- **Create Lead in Bitrix24:**
  `https://your-n8n-instance/webhook/bitrix-lead`

---

## Personal Info

- **Your Name:** [FILL IN — e.g., "Alex"]
- **Your WhatsApp Number:** [FILL IN — e.g., "+1234567890"]
- **Your Email:** [FILL IN — e.g., "alex@yourdomain.com"]
- **Your Website:** [FILL IN — e.g., "https://yourwebsite.com"]
- **What You Do (1-liner):** [FILL IN — e.g., "I help businesses automate repetitive tasks using n8n, saving 10+ hours per week"]

---

## Outreach Preferences

- **Follow-up delay:** 3 days (WhatsApp → Gmail if no reply)
- **Second follow-up:** 7 days after Gmail (optional)
- **Max follow-ups before archiving:** 3
- **Bitrix24 pipeline:** [FILL IN — e.g., "Leads" or pipeline ID from your Bitrix24]

---

## Notes

- Your n8n instance URL: `https://your-n8n-instance/` (e.g., cloud.n8n.io or your self-hosted URL)
- All webhook URLs use POST method with JSON body
- Test each webhook individually before running a campaign
