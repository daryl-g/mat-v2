<script>
    import matLogo from '$lib/assets/logos/mat_logo_dark.png';
</script>
<style>
    /* Global styles */
    :global(html, body) {
        margin: 0;
        padding: 0;
        font-family: 'Inter', sans-serif;
        color: #3c3e40;
        height: 100%;
    }

    :global(h1, p) {
        margin-top: 0;
    }

    :global(html) {
        scroll-behavior: smooth;
    }

    :global(body) {
        background: linear-gradient(90deg,rgba(154, 189, 220, 1) 0%, rgba(209, 229, 244, 1) 100%);
        background-image: url('$lib/assets/bg/fm_mat_bg.png');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }

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
            <div class="home-hero-btn">
                <button class="tournament-info-btn">
                    <a href="/info">Tournament Info</a>
                </button>
                <button class="match-analysis-btn">
                    <a href="/match">Match Analysis</a>
                </button>
                <button class="team-analysis-btn">
                    <a href="/team">Team Analysis</a>
                </button>
                <button class="player-analysis-btn">
                    <a href="/player">Player Analysis</a>
                </button>
            </div>
        </div>
    </div>
</div>
