<script lang="ts">
    // Library imports
    import { setContext } from 'svelte';

    // Asset imports
    import matLogo from '$lib/assets/logos/mat_logo_dark.png';

    // Static types and variables
    type Tournament = '2022 AFC Asian Cup' | '2026 ASEAN Championship';
    let selectedTournament: Tournament = $state<Tournament>('2026 ASEAN Championship');
    setContext('selectedTournament', () => selectedTournament);
</script>

<style>
    /* Home page styles */
    .home-content {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        text-align: left;
        color: white;
    }

    .home-content > img {
        margin-right: 2rem;
    }

    .home-hero {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .home-hero-title > p {
        font-size: 4rem;
        color: #3c3e40;
        margin-bottom: 0.1rem;
        letter-spacing: -2%;
    }

    /* Button styles */
    .home-hero-btn {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
    }

    .home-hero-btn button {
        padding: 0.7rem 0.9rem;
        font-size: 1rem;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 450;
    }

    .home-hero-btn button:hover {
        background-color: #9abddc;
        transition: background-color 0.3s ease;
    }

    .home-hero-btn button a {
        color: black;
        font-family: 'Inter', sans-serif;
        text-decoration: none;
    }

    .tournament-selector {
        display: flex;
        justify-content: left;
    }

    .tournament-selector label {
        color: #3c3e40;
        padding-top: 0.5rem;
        margin-right: 0.5rem;
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
    }

    .tournament-selector select {
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid rgba(0, 0, 0, 0.1);
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
    }

    /* Info button styles */
    .home-info-btn {
        position: absolute;
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        top: 0.5rem;
        right: 0.5rem;
        line-height: 0;
    }

    .info-popup {
        display: none;
        position: absolute;
        top: 2.5rem;
        right: 0.5rem;
        align-items: center;
        justify-content: center;
        background-color: rgba(0, 0, 0, 0.8);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        color: white;
        padding: 1.5rem 0.8rem 0.5rem;
        border-radius: 10px;
        width: max-content;
    }

    .home-info-btn:hover + .info-popup {
        display: block;
    }
</style>

<div class="home-hero-container">
    <div class="home-info-btn">
        <button class="home-info-btn" aria-label="Info">
            <span class="material-symbols-outlined">
                info
            </span>
        </button>
        <div class="info-popup">
            <p>Made with ❤️ by Daryl</p>
            <br />
            <p>https://daryldao.com</p>
        </div>
    </div>
    <div class="home-content">
        <img class="app-logo" src={matLogo} alt="MAT Logo" width="150" />
        <div class="home-hero">
            <div class="home-hero-title">
                <p><b>Match Analysis Tool</b></p>
            </div>
            <div class="tournament-selector">
                <label for="tournament-select">Select tournament:</label>
                <select bind:value={selectedTournament}>
                    <option value="2022 AFC Asian Cup">2022 AFC Asian Cup</option>
                    <option value="2026 ASEAN Championship">2026 ASEAN Championship</option>
                </select>
            </div>
            <div class="home-hero-btn">
                <button class="tournament-info-btn">
                    <a href="/info">Tournament Info</a>
                </button>
                <!-- {#if selectedTournament !== '2026 ASEAN Championship'} -->
                    <button class="match-analysis-btn">
                        <a href="/match">Match Analysis</a>
                    </button>
                    <button class="team-analysis-btn">
                        <a href="/team">Team Analysis</a>
                    </button>
                    <button class="player-analysis-btn">
                        <a href="/player">Player Analysis</a>
                    </button>
                <!-- {/if} -->
            </div>
        </div>
    </div>
</div>
