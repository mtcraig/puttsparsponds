async function tournLatest(tournLeague) {
  // Base URL for fetching the latest tournament for the requested league
  const url = `http://sports.core.api.espn.com/v2/sports/golf/leagues/${tournLeague}/events?lang=en&region=us`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('No response from ESPN');
    }
    const data = await response.json();
    if (!data.items || data.items.length === 0) {
      throw new Error('No items found in the response');
    }
    // Return the tournament URL of the latest tournament
    return data.items[0]['$ref'];
  } catch (error) {
    console.error('Error fetching data:', error);
    return null;
  }
}

export default tournLatest;