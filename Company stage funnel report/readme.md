HubSpot only offers two types of stage funnel reports - for contacts and deals.

What if you want to report on unique companies?

A simple contact funnel report will show you an incorrect picture. Why? Because the sales process typically includes a broad buying committee and multiple people from the same company will appear in the report.

After all, in B2B it’s a company that is your customer from the perspective of conversion analytics.

➡️ Follow these steps to set up proper stage funnel reporting for your companies and measure your efficiency.

Step 1️⃣.
Create a custom property on Contact. Let’s call it “Opt-in LCS Funnel Analytics”

Step 2️⃣.
Build a company-based workflow triggered when Lifecycle Stage of a company changes

▪️ clear “Opt-in LCS Funnel Analytics” value for all associated contacts
▪️ custom code action to identify ONE representative from a company to include in the report

Step 3️⃣.
Create a Contact funnel report with an additional filter for “Opt-in LCS Funnel Analytics”

⚙️ Custom code logic:
▪️ identify contacts associated to a company where Lifecycle Stage of a contact corresponds to company Lifecycle Stage
▪️ if more than one contact has been found, take the oldest from this group
▪️ set “Opt-in LCS Funnel Analytics” to Yes for the chosen one

➡️ Comment below to get the python code you can paste in your workflow custom code action

✅ This trick assumes you have your CRM set up to sync contact and company lifecycle stages.
Companies have to inherit the stages from the associated contacts and get the most advanced lifecycle stage from the contacts.
DM or comment below if you are curious about how to achieve full automation for it through robust triggers and conditions.
