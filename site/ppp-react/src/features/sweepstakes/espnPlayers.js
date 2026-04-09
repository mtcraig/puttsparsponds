import axios from 'axios';

function sweepTournLatest(tournLeague) {
  const url = `http://sports.core.api.espn.com/v2/sports/golf/leagues/${tournLeague}/events?lang=en&region=us`;
  return axios.get(url)
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
    })
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

function sweepTournDetails(tournUrl) {
  return axios.get(tournUrl)
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

function sweepTournFetch(req) {
  if (req.tournId) {
    return sweepTournKnown(req)
      .then(url => sweepTournDetails(url));
  } else {
    return sweepTournLatest(req.tournLeague)
      .then(url => sweepTournDetails(url));
  }
}

// sweepTournFetch({ tournLeague: 'pga'})
//   .then(details => {
//     console.log('Tournament Details:', details);
//   })
//   .catch(error => {
//     console.error('Error:', error);
//   })

export { sweepTournLatest, sweepTournKnown, sweepTournDetails, sweepTournFetch };