const BASE_URL =
  "https://raw.githubusercontent.com/daryl-g/mat-v2/refs/heads/svelte-version/data/opta/2026 ASEAN Championship";

export async function load() {
  const [matchesResponse, teamsResponse, groupsResponse] = await Promise.all([
    fetch(`${BASE_URL}/matches.json`),
    fetch(`${BASE_URL}/teams.json`),
    fetch(`${BASE_URL}/groups.json`),
  ]);

  const { matches } = await matchesResponse.json();
  const { teams } = await teamsResponse.json();
  const { groups } = await groupsResponse.json();

  // Merge team details into the contestants fields
  const teamsMap = new Map(teams.map((t: Record<string, any>) => [t.id, t]));

  const merged = matches.map((match: Record<string, any>) => ({
    ...match,
    matchInfo: {
      ...match.matchInfo,
      stage: {
        ...match.matchInfo.stage,
        group: {
          ...match.matchInfo.stage.group,
          ...groups.find(
            (g: Record<string, any>) => g.id === match.matchInfo.stage.group.id,
          ),
        },
      },
      contestants: match.matchInfo.contestants.map(
        (contestant: Record<string, any>) => ({
          ...contestant,
          ...((teamsMap.get(contestant.id) as Record<string, any>) ?? {}),
        }),
      ),
    },
  }));

  return { matches: merged };
}
