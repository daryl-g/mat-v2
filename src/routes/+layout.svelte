<script lang="ts">
	import favicon from '$lib/assets/logos/mat_logo_blue.png';
	import Navbar from '$lib/components/global/Navbar.svelte';
	import { page } from '$app/state';

	let { children } = $props();
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
</style>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if page.url.pathname !== '/'}
	<Navbar />
{/if}

{@render children()}
