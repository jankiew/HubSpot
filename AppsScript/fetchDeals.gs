function fetchHubSpotDeals() {
  const SHEET_NAME = "hs_deals";
  const HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/objects/deals";
  const PROPERTIES = ['id', 'dealname', 'dealstage', 'po_number', 'hubspot_owner_id', 'deal_currency_code', 'amount', 'amount_in_home_currency', 'hs_projected_amount', 'hs_projected_amount_in_home_currency', 'start_date', 'end_date__new_', 'closedate', 'dealtype', 'primary_company_sync', 'hs_deal_stage_probability', 'hs_priority', 'customer_country', 'customer_industry', 'billing_type', 'fte_engineering', 'fte_consulting', 'account_tier', 'services_positioned', 'technology_stack', 'deal_source'];
  const LIMIT = 100; // Max items per request (HubSpot limit)

  // Retrieve Access Token from PropertiesService
  const HUBSPOT_ACCESS_TOKEN = PropertiesService.getScriptProperties().getProperty("HUBSPOT_API_KEY");
  if (!HUBSPOT_ACCESS_TOKEN) {
    throw new Error("HubSpot access token not found in PropertiesService. Please set it using the `setHubSpotAccessToken` function.");
  }

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) {
    throw new Error(`Sheet named '${SHEET_NAME}' does not exist.`);
  }

  // Clear the sheet and set headers
  sheet.clear();
  const headers = ['id', 'dealname', 'dealstage', 'po_number', 'hubspot_owner_id', 'deal_currency_code', 'amount', 'amount_in_home_currency', 'hs_projected_amount', 'hs_projected_amount_in_home_currency', 'start_date', 'end_date__new_', 'closedate', 'dealtype', 'primary_company_sync', 'hs_deal_stage_probability', 'hs_priority', 'country', 'industry', 'billing_type', 'fte_engineering', 'fte_consulting', 'account_tier', 'services_positioned', 'technology_stack', 'deal_source'];
  sheet.appendRow(headers);

  let after = null; // For pagination
  let deals = [];
  let hasMore = true;

  // Fetch data from HubSpot
  while (hasMore) {
    const url = `${HUBSPOT_API_URL}?limit=${LIMIT}&properties=${PROPERTIES.join(",")}` + 
                (after ? `&after=${after}` : "");
    const options = {
      method: "get",
      headers: {
        "Authorization": `Bearer ${HUBSPOT_ACCESS_TOKEN}`,
        "Content-Type": "application/json"
      },
      muteHttpExceptions: true
    };

    const response = UrlFetchApp.fetch(url, options);
    if (response.getResponseCode() !== 200) {
      throw new Error(`Failed to fetch data from HubSpot. Response: ${response.getContentText()}`);
    }

    const data = JSON.parse(response.getContentText());
    deals = deals.concat(data.results);
    hasMore = data.paging && data.paging.next && data.paging.next.after;
    after = hasMore ? data.paging.next.after : null;
  }
  

  // Parse and write data to the sheet
  const rows = deals.map(deal => [
    deal.id,
    deal.properties.dealname || '',
    deal.properties.dealstage || '',
    deal.properties.po_number || '',
    deal.properties.hubspot_owner_id || '',
    deal.properties.deal_currency_code || '',
    deal.properties.amount || '',
    deal.properties.amount_in_home_currency || '',
    deal.properties.hs_projected_amount || '',
    deal.properties.hs_projected_amount_in_home_currency || '',
    new Date(deal.properties.start_date || null).getTime(),
    //deal.properties.start_date || '',
    deal.properties.end_date__new_ || '',
    new Date(deal.properties.closedate || null).getTime(),
    //deal.properties.closedate || '',
    deal.properties.dealtype || '',
    deal.properties.primary_company_sync || '',
    deal.properties.hs_deal_stage_probability || '',
    deal.properties.hs_priority || '',
    deal.properties.customer_country || '',
    deal.properties.customer_industry || '',
    deal.properties.billing_type || '',
    deal.properties.fte_engineering || '',
    deal.properties.fte_consulting || '',
    deal.properties.account_tier || '',
    deal.properties.services_positioned || '',
    deal.properties.technology_stack || '',
    deal.properties.deal_source || ''
  ]);



  // Append data rows to the sheet
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
  }
  //Logger.log(deals);
  deals.forEach(row => console.log(row));
  Logger.log(`Fetched ${deals.length} deals from HubSpot and added to '${SHEET_NAME}'`);

  normalizeCompanyNames(SHEET_NAME);

}


/**
 * Set the HubSpot API key in PropertiesService.
 * Run this function once to store the API key securely.
 */
function setHubSpotApiKey() {
  // const API_KEY = "api_key"; // Uncomment and Replace with your actual API key
  PropertiesService.getScriptProperties().setProperty("api_key", API_KEY);
  Logger.log("HubSpot API key has been saved to PropertiesService.");
}

/**
 * Delete the HubSpot API key from PropertiesService (if needed).
 */
function deleteHubSpotApiKey() {
  PropertiesService.getScriptProperties().deleteProperty("HUBSPOT_API_KEY");
  Logger.log("HubSpot API key has been deleted from PropertiesService.");
}

function normalizeCompanyNames(SHEET_NAME) {
  // Get the active sheet (change the sheet name if needed)
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return; // No data to process if only header exists

  // Get all values from column O (assuming header is in row 1)
  var dataRange = sheet.getRange("O2:O" + lastRow);
  var data = dataRange.getValues(); // This returns a 2D array

  // Define our replacement rules using an array of objects
  // Each rule has a regex pattern and the unified name
  var replacements = [
    { pattern: /^XYZ.*$/i, replacement: "XYZ" },
    { pattern: /ABC/i, replacement: "ABC" }
    // Add additional rules as needed
  ];

  // Process each row using the Array.map function
  var newData = data.map(function(row) {
    var company = row[0];
    if (company && typeof company === 'string') {
      replacements.forEach(function(rule) {
        if (rule.pattern.test(company)) {
          company = rule.replacement;
        }
      });
    }
    return [company]; // Return as a single-element array to match the 2D structure
  });

  // Write the updated data back to the sheet
  dataRange.setValues(newData);
}
