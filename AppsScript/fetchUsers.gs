function fetchHubSpotUsers() {
  const SHEET_NAME = "hs_users";
  const HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/owners/";
  const PROPERTIES = ['id', 'firstName', 'lastName'];
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
  const headers = ['id', 'Full Name'];
  sheet.appendRow(headers);

  let after = null; // For pagination
  let owners = [];
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
    owners = owners.concat(data.results);
    hasMore = data.paging && data.paging.next && data.paging.next.after;
    after = hasMore ? data.paging.next.after : null;
  }
 
  // Parse and write data to the sheet
  const rows = owners.map(owners => [
    owners.id,
    (owners.firstName || '') + ' ' + (owners.lastName || '')
  ]);
  Logger.log(rows);


  // Append data rows to the sheet
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
  }

  owners.forEach(row => console.log(row));
  Logger.log(`Fetched ${owners.length} owners from HubSpot and added to '${SHEET_NAME}'`);

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
