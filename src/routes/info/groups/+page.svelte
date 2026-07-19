<script lang="ts">
    // Custom components
    import GroupCard from '$lib/components/schedule/GroupCard.svelte';

    // Data
    let { data } = $props();
</script>

<style>
    .groups-grid {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 0px 0px 10px 10px;
        width: 100%;
        height: 100%;
        display: grid;
        justify-items: center;
        padding-top: 2rem;
        padding-bottom: 0.5rem;
        gap: 1rem;
    }

    @media (min-width: 768px) {
        .groups-grid {
            flex-direction: row;
            
        }
    }

    @media (min-width: 1024px) {
        .groups-grid {
            grid-template-columns: repeat(var(--cols), minmax(200px, 1fr));
        }
    }
</style>

<div class="groups-grid" style="--cols: {Math.min(data.groups.length, 4)};">
    {#each data.groups as group}
        <GroupCard
            id={group.id}
            name={group.name}
            primaryColor={group.primaryColor}
            textColor={group.textColor}
            teams={group.teams}
        />
    {/each}
</div>