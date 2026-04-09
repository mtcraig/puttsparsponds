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

async function sweepReadPointSystem(eventId) {
  try {
    await db.connect();
    const res = await db.query(
        'select * from sweepstakes.point_system where event_id = $1'
        ,[eventId]);
    await db.end();
    return res.rows;
  } catch (err) {
    console.error('Error reading score system:', err);
    return [];
  }
}

async function sweepReadPlayerPool(espnEventId) {
  try {
    await db.connect();
    const res = await db.query(
        'select * from sweepstakes.espn_player_pool epp inner join sweepstakes.espn_events ee on epp.espn_event_id = ee.espn_event_id where ee.event_id = $1'
        ,[espnEventId]);
    await db.end();
    return res.rows;
  } catch (err) {
    console.error('Error reading player pool:', err);
    return [];
  }
}

function sweepGetRound(tournSeries,tournId,playerId) {
    const url = `http://sports.core.api.espn.com/v2/sports/golf/leagues/${tournSeries}/events/${tournId}/competitions/${tournId}/competitors/${playerId}/linescores?lang=en&region=us`;
    axios.get(url)
        .then(response => {
            const data = response.data;
            if (!data.items || data.items.length === 0) {
                throw new Error('No items found in the response');
            }
            return {
                    player: playerId,
                    roundDetail: data.tournRoundDetail,
                    roundScore: data.tournRoundScore
            };
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            return null;
        });
}

function sweepGetPlayerRounds(playerPool) {
    const detailPromises = playerPool.map(player =>sweepGetRound(player.tournLeague,player.tournId,player.playerId));
    return Promise.all(detailPromises)
        .then(detailsArray => detailsArray.filter(detail => detail !== null));
}

async function sweepWriteRounds(roundData) {
  try {
    await db.connect();
    const res = await db.query(
        'insert into sweepstakes.espn_round_data (espn_event_id, espn_player_pool_id, round_id, espn_round_data) values ($1, $2, $3, $4)'
        ,[
            roundData.espnEventId,
            roundData.espnPlayerPoolId,
            roundData.roundId,
            roundData.espnRoundData
        ]);
    await db.end();
    return res.rows;
  } catch (err) {
    console.error('Error reading player pool:', err);
    return [];
  }
}

function processRoundData(rawRoundData) {
    // Process the raw round data as needed
    return rawRoundData.map(data => {
        // data.roundDetail;
        return {
            espnEventId: data.espn_event_id,
            espnPlayerPoolId: data.espn_player_pool_id,
            roundId: data.round_id,
            espnRoundData: data.espn_round_data
        };
    });
}

// Test
const espnEventId = 1;
const rawRoundData = sweepReadPlayerPool(espnEventId)
    .then(playerPool => sweepGetPlayerRounds(playerPool))
// End Test

export { sweepReadPointSystem, sweepReadPlayerPool };