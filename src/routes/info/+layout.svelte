<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/state';
    let { children } = $props();
</script>

<style>
    .schedule-container {
        background-image: url('$lib/assets/bg/fm_mat_bg.png');
        background-size: cover;
        background-position: center;
        min-height: 100vh;
        max-height: 100vh;
    }

    .schedule-content {
        padding: 2rem;
        color: white;
    }

    .schedule-tabs {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        border-bottom: 3px solid rgba(255, 255, 255, 0.7);
    }

    .schedule-tabs button {
        background: rgba(255, 255, 255);
        border: none;
        border-radius: 10px 10px 0 0;
        padding: 0.5rem 1.25rem;
        color: black;
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.3s;
    }

    .schedule-tabs button.active,
    .schedule-tabs button:hover {
        background: rgba(0, 0, 0, 0.7);
        color: white;
    }
</style>

<div class="schedule-container">
    <div class="schedule-content">
        <div class="schedule-tabs">
            <button onclick={() => goto('/info/groups')} class:active={page.url.pathname === '/info/groups'}>Groups</button>
            <button onclick={() => goto('/info/bracket')} class:active={page.url.pathname === '/info/bracket'}>Bracket</button>
            <button onclick={() => goto('/info/matches')} class:active={page.url.pathname === '/info/matches'}>Matches</button>
        </div>

        {@render children()}
    </div>
</div>