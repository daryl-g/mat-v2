<script lang="ts">
	import favicon from '$lib/assets/logos/mat_logo_blue.png';
	import Navbar from '$lib/components/global/Navbar.svelte';
	import { page } from '$app/state';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if page.url.pathname !== '/'}
	<Navbar />
{/if}

{@render children()}
