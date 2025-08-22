import axios from 'axios';

async function sweepTournLatest(tournLeague) {
  const url = `http://sports.core.api.espn.com/v2/sports/golf/leagues/${tournLeague}/events?lang=en&region=us`;
  axios.get(url)
    .then(response => {
      const data = response.data;
      if (!data.items || data.items.length === 0) {
        throw new Error('No items found in the response');
      }
      return data.items[0]['$ref'];
    })
    .catch(error => {
      console.error('Error fetching data:', error);
      return null;
    });
}

function sweepTournKnown(req) {
  try {
    if (!req.body.tournLeague || !req.body.tournID) {
      throw new Error('Tournament League or ID not provided');
    }
    return `http://sports.core.api.espn.com/v2/sports/golf/leagues/${req.tournLeague}/events/${req.tournID}/competitions/${req.tournID}?lang=en&region=us`;  
  } catch (error) {
    console.error('Error forming URL:', error);
    return null;
  }
}

async function sweepTournDetails(tournUrl) {
  axios.get(tournUrl)
    .then(response => {
      const data = response.data;
      if (!data.id || data.id.length === 0) {
        throw new Error('No items found in the response');
      }
      // Extract key details as needed
      const tournId = data.id;
      const tournName = data.name;
      const tournCourse = data.courses[0].name;
      const tournAddress = data.courses[0].address;
      return [tournId, tournName, tournCourse, tournAddress];
    })
    .catch(error => {
      console.error('Error fetching data:', error);
      return null;
    });
}


async function sweepTournFetch(req) {
  if (req.tournId) {
    try {
      return await sweepTournDetails(sweepTournKnown(req));
    } catch (error) {
      console.error('Error fetching known tournament details:', error);
      return null;
    }
  } else {
    try {
      return await sweepTournDetails(sweepTournLatest());
    } catch (error) {
      console.error('Error fetching latest tournament details:', error);
      return null;
    }
  }
}

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
    try {
      const tournData = await tournDetails(data.items[0]['$ref']);
      // Extract key details from tournData as needed
      const tournId = tournData.id;
      const tournName = tournData.name;
      const tournCourse = tournData.courses[0].name;
      const tournAddress = tournData.courses[0].address;
      return [tournId, tournName, tournCourse, tournAddress];
    } catch (error) {
      console.error('Error fetching tournament details:', error);
      return null;
    }
  } catch (error) {
    console.error('Error fetching data:', error);
    return null;
  }
}

async function tournDetails(tournUrl) {
  try {
    const response = await fetch(tournUrl);
    if (!response.ok) {
      throw new Error('No response from ESPN');
    }
    const data = await response.json();
    if (!data.id || data.id.length === 0) {
      throw new Error('No items found in the response');
    }
    // Return the tournament details
    return data;
    // return data.items[0]['$ref'];
  } catch (error) {
    console.error('Error fetching data:', error);
    return null;
  }
}

await tournDetails('pga');

// export { tournLatest, tournDetails };