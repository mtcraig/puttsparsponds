import axios from 'axios';
import pg from 'pg';
import dotenv from 'dotenv';
dotenv.config({ path: './site/ppp-react/db/.env' })

const db = new pg.Client({
  user: String(process.env.user),
  host: String(process.env.host),
  database: String(process.env.database),
  password: String(process.env.password),
  port: parseInt(process.env.port)
});

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
      const tournPlayers = data.competitors;
      return [tournId, tournName, tournCourse, tournAddress, tournPlayers];
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

function sweepPlayerDetails(player) {
  const playerUrl = player.athlete['$ref'];
  axios.get(playerUrl)
    .then(response => {
      const data = response.data;
      if (!data.id) {
        throw new Error('No player found in the response');
      }
      // Extract key player details as needed
      const playerId = data.id;
      const playerName = data.fullName;
      const playerCountry = data.citizenship;
      return { playerId, playerName, playerCountry };
    })
    .catch(error => {
      console.error('Error fetching player data:', error);
    })
}

function sweepTournPlayers(sweepTournData) {
  const players = sweepTournData.players;
  // Map each player to a promise that resolves to their details
  const detailPromises = players.map(player => sweepPlayerDetails(player));
  // Wait for all promises to resolve and return the array
  return Promise.all(detailPromises)
    .then(detailsArray => detailsArray.filter(detail => detail !== null));
}

async function sweepWriteTourn(tournData) {
  try {
    await db.connect();
    await db.query(
      'insert into sweepstakes.espn_events (espn_event_id, event_name, event_series) values ($1, $2, $3)',
      [tournData.tournId, tournData.tournName, sweepReq.tournLeague]
    );
    console.log('Sweepstake tournament data inserted successfully');
    await db.end();
  } catch (error) {
    console.error('Error inserting Sweepstake tournament data:', error);
  }
}

async function sweepWritePlayers(tournData,playerData) {
  try {
    await db.connect();
    await db.query(
      'insert into sweepstakes.espn_events (espn_event_id, espn_player_id, espn_player_name) values ($1, $2, $3)',
      [tournData.tournId, playerData.playerId, playerData.playerName]
    );
    console.log('Sweepstake tournament data inserted successfully');
    await db.end();
  } catch (error) {
    console.error('Error inserting Sweepstake tournament data:', error);
  }
}

// Start of test
const sweepReq = { tournLeague: 'pga', tournId: 401703521 };

const sweepTournData = sweepTournFetch(sweepReq)
  .then(details => {
    console.log('Tournament Details:', details);
  })
  .catch(error => {
    console.error('Error:', error);
  })

const sweepPlayerData = sweepTournPlayers(sweepTournData)
  .then(playerDetails => {
    console.log('Player Details:', playerDetails);
  })
  .catch(error => {
    console.error('Error:', error);
  })

await sweepWriteTourn(sweepTournData);
await sweepWritePlayers(sweepTournData,sweepPlayerData);
// End of test

export { sweepTournLatest, sweepTournKnown, sweepTournDetails, sweepTournFetch };