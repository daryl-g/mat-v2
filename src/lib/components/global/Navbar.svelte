<script lang="ts">
    import { page } from '$app/state';
    import navlogo from '$lib/assets/logos/mat_logo_dark.png';
</script>
<style>
    .navbar {
        background-color: #9abddc;
        padding: 0.8rem 2.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .navbar-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .nav-logo {
        display: flex;
        flex-direction: row;
        align-items: left;
        margin-top: 0.5rem;
        gap: 0.5rem;
        text-decoration: none;
    }

    .nav-logo p {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #333333;
        text-decoration: none;
        margin-top: 0.5rem;
        margin-left: 0.1rem;
    }

    .nav-logo-image {
        height: 2.5rem;
    }

    .nav-links {
        list-style: none;
        display: flex;
        gap: 1.5rem;
        margin: 0;
        padding: 0;
    }

    .nav-link {
        text-decoration: none;
        color: #333333;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        position: relative;
    }

    .nav-link:hover {
        color: #ffffff;
    }

    .nav-link.active::after {
        content: '';
        position: absolute;
        left: 0;
        bottom: -5px;
        width: 100%;
        height: 2px;
        background-color: #d1e5f4;
    }
</style>
<nav class="navbar">
    <div class="navbar-container">
        <a href="/" class="nav-logo">
            <img src={navlogo} alt="MAT Dark Logo" class="nav-logo-image" />
            <p>Match Analysis Tool</p>
        </a>
        <ul class="nav-links">
            <li class="nav-item">
                <a href="/info" class="nav-link" class:active={page.url.pathname.startsWith('/info')}>
                    Tournament Info
                </a>
            </li>
            <li class="nav-item">
                <a href="/match" class="nav-link" class:active={page.url.pathname.startsWith('/match')}>
                    Match Analysis
                </a>
            </li>
            <li class="nav-item">
                <a href="/team" class="nav-link" class:active={page.url.pathname.startsWith('/team')}>
                    Team Analysis
                </a>
            </li>
            <li class="nav-item">
                <a href="/player" class="nav-link" class:active={page.url.pathname.startsWith('player')}>
                    Player Analysis
                </a>
            </li>
        </ul>
    </div>
</nav>