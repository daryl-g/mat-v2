const BASE_URL =
  "https://raw.githubusercontent.com/daryl-g/mat-v2/refs/heads/svelte-version/data/opta/2026 ASEAN Championship";

export async function load() {
  const [groupsResponse, standingsResponse] = await Promise.all([
    fetch(`${BASE_URL}/groups.json`),
    fetch(`${BASE_URL}/standings.json`),
  ]);

  const { groups } = await groupsResponse.json();
  const { standings } = await standingsResponse.json();

  // Merge teams from standings into each group by id
  const merged = groups.map((group: Record<string, any>) => {
    const match = standings.find((s: Record<string, any>) => s.id === group.id);
    return { ...group, teams: match?.teams ?? [] };
  });

  return { groups: merged };
}
