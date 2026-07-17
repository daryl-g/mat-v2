<script lang="ts">
    // Custom component
    import MatchList from '$lib/components/schedule/MatchList.svelte';

    // Static types and variables
    type Filter = 'date' | 'group';
    let activeFilter: Filter = $state<Filter>('date');
    let filteredValue: string = $state<string>('');

    // Data
    let { data } = $props();

    // Filtering values
    const uniqueDates = $derived([...new Set(data.matches.map((m: any) => m.matchInfo.localStartDate))].sort());
    const uniqueGroups = $derived([...new Set(data.matches.map((m: any) => m.matchInfo.stage.group.name))].sort());
    const defaultValue = $derived(activeFilter === 'date' ? uniqueDates[0] : uniqueGroups[0]);

    $effect(() => {
        filteredValue = defaultValue as string ?? '';
    });
</script>

<style>
    .matches-content {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 0px 0px 10px 10px;
        width: 100%;
        height: 100%;
    }

    .matches-filter {
        display: flex;
        color: black;
        gap: 0.5rem;
        padding: 1rem;
    }

    .matches-filter button {
        background: rgba(255, 255, 255);
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        color: black;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.3s;
    }

    .matches-filter button:hover, .matches-filter button.active {
        background: rgba(0, 0, 0, 0.8);
        color: white;
    }

    .filtering-options {
        display: flex;
        justify-content: center;
    }

    .filtering-options select {
        padding: 0.5rem;
        border-radius: 10px;
        border: 1px solid rgba(0, 0, 0, 0.1);
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
    }
</style>

<div class="matches-content">
    <div class="matches-filter">
        <button onclick={() => activeFilter = 'date'} class:active={activeFilter === 'date'}>By date</button>
        <button onclick={() => activeFilter = 'group'} class:active={activeFilter === 'group'}>By group</button>
    </div>
    {#if activeFilter === 'date'}
        <div class="filtering-options">
            <select bind:value={filteredValue}>
                {#each uniqueDates as date}
                    <option value={date}>{new Date(date as string).toLocaleDateString(undefined, { month: 'short', day: 'numeric'})}</option>
                {/each}
            </select>
        </div>
    {:else if activeFilter === 'group'}
        <div class="filtering-options">
            <select bind:value={filteredValue}>
                {#each uniqueGroups as group}
                    <option value={group}>{group}</option>
                {/each}
            </select>
        </div>
    {/if}

    <MatchList matches={data.matches} filter={activeFilter} value={filteredValue} />
</div>