<p>HubSpot only offers two types of stage funnel reports - for contacts and deals.</p>

<p>What if you want to report on unique companies?</p>

<p>A simple contact funnel report will show you an incorrect picture. Why? Because the sales process typically includes a broad buying committee and multiple people from the same company will appear in the report.</p>

<p>After all, in B2B it’s a company that is your customer from the perspective of conversion analytics.</p>

<p>➡️ Follow these steps to set up proper stage funnel reporting for your companies and measure your efficiency.</p>

<p>Step 1️⃣.<br>
▪️  Create a custom property on Contact. Let’s call it “Opt-in LCS Funnel Analytics”
</p>
<p>Step 2️⃣.<br>
Build a company-based workflow triggered when Lifecycle Stage of a company changes
<ul>
<li>▪️ clear “Opt-in LCS Funnel Analytics” value for all associated contacts</li>
<li>▪️ custom code action to identify ONE representative from a company to include in the report</li>
</ul>
</p>

<p>Step 3️⃣.
Create a Contact funnel report with an additional filter for “Opt-in LCS Funnel Analytics”</p>

<p>⚙️ Custom code logic:<br>
<ul>
<li>▪️ identify contacts associated to a company where Lifecycle Stage of a contact corresponds to company Lifecycle Stage</li>
<li>▪️ if more than one contact has been found, take the oldest from this group</li>
<li>▪️ set “Opt-in LCS Funnel Analytics” to Yes for the chosen one</li>
</ul>

<p>✅ This trick assumes you have your CRM set up to sync contact and company lifecycle stages.<br>
Companies have to inherit the stages from the associated contacts and get the most advanced lifecycle stage from the contacts.<br>
DM or comment below if you are curious about how to achieve full automation for it through robust triggers and conditions.
</p>
