<script lang="ts">
    // Data
    let {
        matches,
        filter,
        value
    }: {
        matches: any[];
        filter: 'date' | 'group' | 'team';
        value: string;
    } = $props();

    // Custom function
    function getContestant(match: any, position: 'home' | 'away') {
        return match.matchInfo.contestants.find((contestant: any) => contestant.position === position);
    }

    // Filter matches
    const filteredMatches = $derived(
        matches.filter((match: any) => {
            if (filter === 'date') {
                return match.matchInfo.localStartDate === value;
            } else if (filter === 'group') {
                return match.matchInfo.stage.group.name === value;
            } else if (filter === 'team') {
                const homeTeam = getContestant(match, 'home');
                const awayTeam = getContestant(match, 'away');
                return homeTeam.id === value || awayTeam.id === value;
            }
            return true;
        })
    );
</script>

<style>
    .match-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 1rem 2rem 1rem 1rem;
    }

    .match-item {
        color: black;
        border-radius: 10px;
        padding: 0.7rem;
        border-bottom: 2px solid rgba(0, 0, 0, 0.1);
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 0.5rem;
        width: 100%;
    }

    .match-group {
        display: flex;
        width: fit-content;
        border-radius: 10px;
        justify-content: center;
        font-family: 'Inter', sans-serif;
        font-weight: bold;
        font-size: 0.9rem;
        padding: 0.2rem;
    }

    .match-group p {
        margin: 0;
    }

    .match-description {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 1rem;
    }

    .home-team, .away-team {
        display: flex;
        gap: 0.3rem;
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
    }

    .home-team {
        justify-content: flex-end;
    }

    .away-team {
        justify-content: flex-start;
    }

    .match-status {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
    }

    .match-info {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        text-align: right;
    }
</style>

<div class="match-list">
    {#each filteredMatches as match (match.matchInfo.id)}
        {@const homeTeam = getContestant(match, 'home')}
        {@const awayTeam = getContestant(match, 'away')}
        <div class="match-item">
            <div class="match-group" style="background-color: {match.matchInfo.stage.group.primaryColor}; color: {match.matchInfo.stage.group.textColor};">
                <p>{match.matchInfo.stage.group.name}</p>
            </div>
            <div class="match-description">
                <div class="home-team">
                    <span>{homeTeam.name}</span>
                    <img class="home-team-flag" src={homeTeam.flag} alt="{homeTeam.name} logo" width="22" height="22" />
                </div>
                <div class="match-status">
                    {#if match.matchData.matchStatus === 'Fixture'}
                        <span>{match.matchInfo.localStartTime}</span>
                    {:else}
                        <span>{match.matchData.scores.total.home} - {match.matchData.scores.total.away}</span>
                    {/if}
                </div>
                <div class="away-team">
                    <img class="away-team-flag" src={awayTeam.flag} alt="{awayTeam.name} logo" width="22" height="22" />
                    <span>{awayTeam.name}</span>
                </div>
            </div>
            <div class="match-info">
                <div class="match-datetime">
                    <span>{match.matchInfo.localStartDate}</span>
                </div>
                <div class="match-venue">
                    <span>{match.matchInfo.venue}</span>
                </div>
            </div>
        </div>
    {/each}
</div>