# Start Outreach

> Start a new outbound lead generation campaign. Triggers WhatsApp messages via n8n, logs leads to Bitrix24, and sets up Gmail follow-up reminders.

---

## Instructions

You are running the **OutboundOS** lead generation campaign starter.

---

## Step 1: Load Context

Read the following files:

1. `outreach/config.md` — Get n8n webhook URLs and your personal info
2. `outreach/templates/whatsapp-intro.md` — Load WhatsApp message template
3. `outreach/templates/gmail-followup.md` — Load Gmail follow-up template
4. `outreach/campaigns.md` — Current campaign status
5. `outreach/config.md` — Verify webhooks are configured

**If webhooks are not configured:**
- Tell the user: "I see your n8n webhook URLs aren't set up yet. Please fill in `outreach/config.md` with your webhook URLs first, then run `/start-outreach` again."
- Stop here.

---

## Step 2: Get Lead Information

**Ask the user for their lead list.** The user should provide:
- Lead names
- Company names
- WhatsApp numbers
- Email addresses (optional, for Gmail follow-up)
- Any personal context or reason for reaching out (e.g., "They run a SaaS startup", "Found them on LinkedIn", "Referred by X")

Accept input as:
- Direct text in the chat
- A list pasted into the chat
- Reference to a file in `outreach/leads/`
- CSV format: `name, company, whatsapp, email, context`

---

## Step 3: Validate Leads

For each lead, verify:
- WhatsApp number is present and looks valid
- Name is present
- Context is clear enough to personalize

If any lead is missing required info, ask the user to provide it before proceeding.

---

## Step 4: Personalize Messages

For each lead, customize the WhatsApp template:

1. Replace `{{lead_name}}` with their name
2. Replace `{{personalized_opening}}` — craft a personalized opening based on their context
3. Replace `{{relevant_context}}` — relate your automation services to their specific situation
4. Replace `{{your_name}}` with the user's name from config

---

## Step 5: Send WhatsApp Messages

For each lead, trigger the n8n WhatsApp webhook:

```
POST {{n8n_webhook_url}}
Content-Type: application/json

{
  "phone": "{{lead_whatsapp}}",
  "message": "{{personalized_message}}",
  "lead_name": "{{lead_name}}",
  "lead_company": "{{lead_company}}"
}
```

**Important:** Before sending, confirm with the user:
- "I'm about to send WhatsApp messages to [N] leads. This will trigger your n8n workflow. Ready to proceed? (yes/no)"
- If no, stop
- If yes, proceed

**If n8n is unavailable:** Log the message in `outreach/campaigns.md` as "Pending" and tell the user which messages couldn't be sent.

---

## Step 6: Log to Bitrix24

For each lead, trigger the Bitrix24 n8n webhook to create a lead:

```
POST {{bitrix24_webhook_url}}
Content-Type: application/json

{
  "name": "{{lead_name}}",
  "company": "{{lead_company}}",
  "phone": "{{lead_whatsapp}}",
  "email": "{{lead_email}}",
  "source": "WhatsApp Outreach",
  "campaign": "{{campaign_name}}",
  "status": "NEW",
  "notes": "{{personalization_context}}"
}
```

---

## Step 7: Update Campaign Tracker

In `outreach/campaigns.md`:
1. Create a new campaign section with today's date
2. Add each lead as a row in the campaign table
3. Record: name, WhatsApp sent date, Gmail follow-up status, Bitrix24 status, current status
4. Calculate and update campaign stats (sent, replied, converted)

---

## Step 8: Schedule Gmail Follow-Ups

For each lead, set a reminder for Gmail follow-up in 3 days if no reply.

In `outreach/campaigns.md`, mark the Gmail Follow-up as "⏳ Scheduled" with the follow-up date.

Tell the user:
- "I'll remind you in 3 days to send Gmail follow-ups to leads who haven't replied."
- "When that reminder comes, run `/start-outreach --follow-up` to get the list."

---

## Step 9: Wrap Up

Report to the user:
- Campaign name and start date
- Number of leads contacted
- Confirmation of WhatsApp sends
- Confirmation of Bitrix24 logs
- List of Gmail follow-ups scheduled
- Link to `outreach/dashboard.md` for full stats

---

## Critical Rules

- **Always confirm before sending** — Never send messages without user approval
- **Personalize every message** — No generic blast messages
- **Log everything** — Every lead goes to Bitrix24, nothing falls through
- **Follow up systematically** — 3 days, then 7 days, then archive
- **Track reply status** — User should update status when leads reply
