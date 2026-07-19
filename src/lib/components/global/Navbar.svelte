<script lang="ts">
    // Library imports

    // Asset imports
    import navlogo from '$lib/assets/logos/mat_logo_dark.png';

    // Static variables
    let navLinks = [
        { name: 'Tournament Info', href: '/info', icon: 'trophy' },
        { name: 'Match Analysis', href: '/match', icon: 'sports_and_outdoors' },
        { name: 'Team Analysis', href: '/team', icon: 'local_police' },
        { name: 'Player Analysis', href: '/player', icon: 'account_circle' }
    ]

    // State
    let isHamburger = $state<boolean>(false);
</script>
<style>
    .navbar {
        background-color: transparent;
        padding: 1rem 2.5rem;
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
        font-size: 1.2rem;
        color: #333333;
        text-decoration: none;
        margin-top: 0.5rem;
        margin-left: 0.2rem;
    }

    .nav-logo-image {
        height: 2.5rem;
    }

    .hamburger {
        background: none;
        border: none;
        cursor: pointer;
    }

    .hamburger-menu {
        display: block;
        position: absolute;
        top: 4rem;
        right: 2.5rem;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1rem;
        z-index: 1000;
    }

    .nav-links {
        list-style: none;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        width: 100%;
        margin: 0;
        padding: 0;
    }

    .nav-link {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        width: 100%;
        text-decoration: none;
        color: #333333;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        position: relative;
    }

    .nav-link-container {
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
    }

    .nav-link-container:hover {
        background-color: #d1e5f4;
    }
</style>
<nav class="navbar">
    <div class="navbar-container">
        <a href="/" class="nav-logo">
            <img src={navlogo} alt="MAT Dark Logo" class="nav-logo-image" />
            <p>Match Analysis Tool</p>
        </a>
        <button class="hamburger" onclick={() => isHamburger = !isHamburger}>
            <span class="material-symbols-outlined">menu</span>
        </button>
        {#if isHamburger}
            <div class="hamburger-menu">
                <ul class="nav-links">
                    {#each navLinks as link}
                        <div class="nav-link-container">
                            <li>
                                <a href={link.href} class="nav-link">
                                    <span class="material-symbols-outlined">{link.icon}</span>
                                    {link.name}
                                </a>
                            </li>
                        </div>
                    {/each}
                </ul>
            </div>
        {/if}
    </div>
</nav>