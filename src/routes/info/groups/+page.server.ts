const BASE_URL =
  "https://raw.githubusercontent.com/daryl-g/world-cup-2026-app/refs/heads/main/data";

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
