<script lang="ts">
    // Data
    let { data } = $props();
</script>

<style>
    .teams-container {
        min-height: 91.8vh;
        display: flex;
        justify-content: center;
    }

    .teams-grid {
        width: 90%;
        height: 100%;
        display: grid;
        justify-items: center;
        padding-top: 2rem;
        padding-bottom: 0.5rem;
        gap: 1rem;
    }

    .team-card {
        display: flex;
        flex-direction: row;
        gap: 0.5rem;
        align-items: center;
        justify-content: center;
        width: 70%;
        border-radius: 10px;
        text-decoration: none;
        transition: transform 0.3s, box-shadow 0.3s;
    }

    .team-name {
        padding-top: 1rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: clamp(0.7rem, 1.5vw, 1rem);
        word-break: break-word;
        overflow-wrap: break-word;
    }

    @media (min-width: 768px) {
        .teams-grid {
            flex-direction: row;
        }
    }

    @media (min-width: 1024px) {
        .teams-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }
</style>

<div class="teams-container">
    <div class="teams-grid">
        {#each data.teams as team}
            <a href="/info/teams/{team.id}" class="team-card" style="background-color: {team.primaryColor}; color: {team.textColor}">
                <img src={team.flag} alt="{team.shortName} flag" width=20 class="team-flag" />
                <p class="team-name">{team.fullName}</p>
            </a>
        {/each}
    </div>
</div>